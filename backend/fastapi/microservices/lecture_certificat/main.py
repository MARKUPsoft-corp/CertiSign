# Importation des modules nécessaires pour l'API, la manipulation des certificats et des dates
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response  # Modules FastAPI pour créer l'API
from cryptography import x509  # Pour manipuler les certificats X.509
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PublicFormat  # Pour charger les certificats PKCS#12 et les convertir en PEM
from cryptography.hazmat.primitives import hashes  # Pour calculer les empreintes nécessaires à OCSP
from cryptography.x509 import ocsp  # Pour construire et analyser les requêtes OCSP
from datetime import datetime  # Pour gérer les dates de validité
import json  # Pour formater la réponse en JSON
import requests  # Pour effectuer des requêtes HTTP (télécharger la CRL et envoyer la requête OCSP)
import ldap  # Importation du module LDAP pour interagir avec un serveur LDAP
import base64

# Création de l'application FastAPI
app = FastAPI()

def check_crl(crl_url, serial_number):
    """
    Vérifie si un certificat est révoqué via une requête LDAP.

    Args:
        crl_url (str): L'URL du point de distribution de la CRL (LDAP).
        serial_number (str): Le numéro de série du certificat (sous forme de chaîne).

    Returns:
        bool: True si le certificat est révoqué, False sinon.
    """
    try:
        # Extraction des informations de l'URL LDAP
        uri_parts = crl_url.split('/')  # Découpe l'URL en une liste d'éléments
        ldap_server = uri_parts[2]  # Récupère le serveur LDAP à partir de l'URL (ex: ldap.example.com)
        base_dn = '/'.join(uri_parts[3:])  # Construit le DN de base à partir du reste de l'URL
        
        # Connexion au serveur LDAP
        ldap_connection = ldap.initialize(f"ldap://{ldap_server}")  # Initialise la connexion avec le serveur LDAP
        ldap_connection.protocol_version = 3  # Définit la version du protocole LDAP (LDAPv3)
        
        # Construction du filtre de recherche
        search_filter = f"(&(objectClass=certificateRevocationList)(serialNumber={serial_number}))"
        # Ce filtre recherche un objet de type 'certificateRevocationList' ayant le numéro de série spécifié

        # Recherche LDAP
        results = ldap_connection.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
        # Effectue une recherche récursive (SCOPE_SUBTREE) dans le LDAP à partir de base_dn avec le filtre search_filter

        # Retourne True si le certificat est trouvé (donc révoqué), sinon False
        return bool(results)  # Si des résultats sont trouvés, cela signifie que le certificat est révoqué

    except ldap.LDAPError:
        return False  # En cas d'erreur (serveur inaccessible, mauvais DN, etc.), retourner False (certificat non révoqué)

    finally:
        if 'ldap_connection' in locals():  # Vérifie si la connexion a été créée
            ldap_connection.unbind_s()  # Ferme proprement la connexion LDAP
            

def check_ocsp(ocsp_url, cert, issuer_cert):
    """
    Vérifie l'état d'un certificat via OCSP (Online Certificate Status Protocol).
    Construit une requête OCSP, l'envoie au serveur OCSP, et analyse la réponse.
    :param ocsp_url: URL du serveur OCSP.
    :param cert: Certificat à vérifier.
    :param issuer_cert: Certificat de l'autorité émettrice.
    :return: True si révoqué, False si valide, None si la vérification échoue.
    """
    try:
        # Construction de la requête OCSP en utilisant OCSPRequestBuilder
        builder = ocsp.OCSPRequestBuilder()
        # Ajout du certificat à vérifier, de son émetteur, et de l'algorithme de hash SHA1
        builder = builder.add_certificate(cert, issuer_cert, hashes.SHA1())
        # Construction de l'objet OCSPRequest
        ocsp_request = builder.build()
        # Encodage de la requête OCSP en format DER
        ocsp_request_bytes = ocsp_request.public_bytes(Encoding.DER)
        
        # Définition de l'en-tête HTTP pour indiquer le type de contenu (OCSP)
        headers = {"Content-Type": "application/ocsp-request"}
        # Envoi de la requête OCSP via HTTP POST au serveur OCSP
        response = requests.post(ocsp_url, data=ocsp_request_bytes, headers=headers, timeout=5)
        
        if response.status_code == 200:
            # Charger la réponse OCSP depuis le contenu DER
            ocsp_response = ocsp.load_der_ocsp_response(response.content)
            # Vérifier que la réponse OCSP est réussie
            if ocsp_response.response_status == ocsp.OCSPResponseStatus.SUCCESSFUL:
                # Retourner True si le certificat est marqué comme révoqué
                if ocsp_response.certificate_status == ocsp.OCSPCertStatus.REVOKED:
                    return True
                # Retourner False si le certificat est marqué comme valide
                elif ocsp_response.certificate_status == ocsp.OCSPCertStatus.GOOD:
                    return False
                else:
                    return None  # Statut inconnu
        return None  # Si le code HTTP n'est pas 200 ou en cas de problème, retourner None
    except Exception:
        return None  # En cas d'erreur lors de la vérification OCSP, retourner None

@app.post("/extract-cert-info/")
async def extract_cert_info(file: UploadFile = File(...), password: str = Form(...)):
    """
    API pour extraire les informations d'un certificat PKCS#12 (.p12 ou .pfx).
    Vérifie l'expiration du certificat et effectue deux vérifications de révocation :
    une via CRL et une via OCSP.
    
    :param file: Fichier de certificat uploadé.
    :param password: Mot de passe du fichier PKCS#12.
    :return: JSON contenant les informations extraites et les statuts de révocation (CRL et OCSP).
    """
    try:
        # Lire le contenu du fichier de certificat et convertir le mot de passe en bytes
        cert_bytes = await file.read()
        password_bytes = password.encode()

        # Charger le certificat PKCS#12 (retourne la clé privée, le certificat et des certificats additionnels, par ex. l'émetteur)
        private_key, cert, additional_certs = pkcs12.load_key_and_certificates(cert_bytes, password_bytes)

        # Vérifier que le certificat a été extrait correctement
        if cert is None:
            raise HTTPException(status_code=400, detail="Certificat invalide ou mot de passe incorrect.")

        # Extraction des informations de base du certificat
        subject = cert.subject.rfc4514_string()  # Nom du titulaire du certificat
        issuer = cert.issuer.rfc4514_string()  # Nom de l'autorité émettrice
        serial_number = cert.serial_number  # Numéro de série unique du certificat
        valid_from = cert.not_valid_before  # Date de début de validité
        valid_to = cert.not_valid_after  # Date d'expiration du certificat
        signature_algo = cert.signature_algorithm_oid.dotted_string  # Algorithme de signature utilisé
        signature_issiuer = base64.b64encode(cert.signature).decode('utf-8')


        # Vérifier l'expiration du certificat en comparant la date actuelle avec la date d'expiration
        current_date = datetime.utcnow()  # Date actuelle (UTC)
        status = "valide" if current_date < valid_to else "expiré"  # Statut de validité du certificat

        # Initialiser les variables pour extraire des informations supplémentaires
        vid = None            # Identifiant virtuel (souvent trouvé dans le Subject Alternative Name)
        oid_list = []         # Liste des Object Identifiers (OID) des extensions
        crl_urls = []         # Liste des URLs de la CRL
        ocsp_urls = []        # Liste des URLs OCSP

        # Parcourir les extensions du certificat pour extraire les informations
        for ext in cert.extensions:
            # Extraction du VID depuis l'extension Subject Alternative Name (SAN)
            if isinstance(ext.value, x509.SubjectAlternativeName):
                for san in ext.value:
                    if isinstance(san, x509.DNSName):
                        vid = san.value  # On prend le premier DNSName comme VID

            # Extraction des OID de chaque extension (chaque extension a un identifiant unique)
            if hasattr(ext, "oid"):
                oid_list.append(ext.oid.dotted_string)

            # Extraction des URLs de la CRL à partir de l'extension CRLDistributionPoints
            if isinstance(ext.value, x509.CRLDistributionPoints):
                for point in ext.value:
                    if point.full_name:
                        crl_urls.append(point.full_name[0].value)  # On prend la première URL trouvée

            # Extraction des URLs OCSP à partir de l'extension AuthorityInformationAccess
            if isinstance(ext.value, x509.AuthorityInformationAccess):
                for access in ext.value:
                    if access.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                        ocsp_urls.append(access.access_location.value)  # On prend la première URL trouvée

        # Vérification de la révocation via CRL
        if crl_urls:
            crl_result = check_crl(crl_urls[0], serial_number)  # Utilisation de la première URL CRL disponible
            if crl_result is True:
                revocation_status_crl = "révoqué"
            elif crl_result is False:
                revocation_status_crl = "non révoqué"
            else:
                revocation_status_crl = "inconnu"
        else:
            revocation_status_crl = "Aucune url crl n'est présente"  # Si aucune URL CRL n'est présente

        # Vérification de la révocation via OCSP
        if ocsp_urls and additional_certs:
            ocsp_result = check_ocsp(ocsp_urls[0], cert, additional_certs[0])  # Utilisation de la première URL OCSP et du certificat de l'émetteur
            if ocsp_result is True:
                revocation_status_ocsp = "révoqué"
            elif ocsp_result is False:
                revocation_status_ocsp = "non révoqué"
            else:
                revocation_status_ocsp = "inconnu"
        else:
            revocation_status_ocsp = "aucune url ocsp n'est présente"  # Si aucune URL OCSP n'est présente ou pas de certificat émetteur

        # Conversion du certificat et de la clé publique en format PEM pour une lecture aisée
        cert_pem = cert.public_bytes(Encoding.PEM).decode("utf-8")  # Certificat en format PEM
        public_key_pem = cert.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode("utf-8")  # Clé publique en format PEM

        # Construction du dictionnaire de réponse contenant toutes les informations extraites
        response_data = {
            "subject": subject,                     # Titulaire du certificat
            "issuer": issuer,                       # Autorité émettrice
            "serial_number": serial_number,         # Numéro de série
            "valid_from": valid_from.isoformat(),   # Date de début de validité (format ISO)
            "valid_to": valid_to.isoformat(),       # Date d'expiration (format ISO)
            "status": status,                       # Statut du certificat (valide ou expiré)
            "revocation_status_crl": revocation_status_crl,  # Statut de révocation via CRL
            "revocation_status_ocsp": revocation_status_ocsp,  # Statut de révocation via OCSP
            "signature_algorithm": signature_algo,  # Algorithme de signature utilisé
            "issuer_signature" : signature_issiuer,
            "public_key_pem": public_key_pem,         # Clé publique en format PEM
            "certificate_pem": cert_pem,              # Certificat complet en format PEM
            "vid": vid,                             # Identifiant virtuel (si présent)
            "oid_list": oid_list,                   # Liste des OID extraits des extensions
            "crl_urls": crl_urls,                     # Liste des URLs de la CRL
            "ocsp_urls": ocsp_urls                    # Liste des URLs OCSP
        }

        # Retourner la réponse JSON avec une indentation pour une meilleure lisibilité
        return Response(
            content=json.dumps(response_data, indent=4),
            media_type="application/json"
        )

    except Exception as e:
        # En cas d'erreur, lever une exception HTTP 500 avec le détail de l'erreur
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du certificat: {str(e)}")
