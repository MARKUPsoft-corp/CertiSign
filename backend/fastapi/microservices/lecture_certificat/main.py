from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response
from cryptography import x509  # Module pour manipuler les certificats X.509
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PublicFormat  # Import des outils de manipulation des certificats PKCS#12
import json  # Module pour convertir les données en JSON
from datetime import datetime  # Pour gérer les dates

# Création de l'application FastAPI
app = FastAPI()

# Définition de l'endpoint pour extraire les informations du certificat
@app.post("/extract-cert-info/")
async def extract_cert_info(file: UploadFile = File(...), password: str = Form(...)):
    try:
        # Lire le fichier du certificat PFX/P12 envoyé par l'utilisateur
        cert_bytes = await file.read()
        # Encoder le mot de passe en bytes
        password_bytes = password.encode()

        # Charger le certificat PFX/P12 avec sa clé privée et les certificats additionnels
        private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
            cert_bytes, password_bytes
        )

        # Vérifier si le certificat est bien chargé
        if cert is None:
            raise HTTPException(status_code=400, detail="Certificat invalide ou mot de passe incorrect.")

        # Extraction des informations principales du certificat
        subject = cert.subject.rfc4514_string()  # Nom du sujet (titulaire du certificat)
        issuer = cert.issuer.rfc4514_string()  # Nom de l'autorité de certification émettrice
        serial_number = cert.serial_number  # Numéro de série du certificat
        valid_from = cert.not_valid_before  # Date de début de validité du certificat
        valid_to = cert.not_valid_after  # Date d'expiration du certificat
        signature_algo = cert.signature_algorithm_oid.dotted_string  # Algorithme de signature utilisé

        # Vérification de l'expiration du certificat
        current_date = datetime.utcnow()
        status = "valide" if current_date < valid_to else "expiré"

        # Initialisation des variables pour stocker le VID, les OID, la CRL et l'OCSP
        vid = None  # Identifiant virtuel (s'il est défini dans le certificat)
        oid_list = []  # Liste des OID présents dans le certificat
        crl_urls = []  # Liste des URLs des CRL (Certificate Revocation List)
        ocsp_urls = []  # Liste des URLs des serveurs OCSP (Online Certificate Status Protocol)

        # Parcourir toutes les extensions du certificat
        for ext in cert.extensions:
            # Vérifier si l'extension est une Subject Alternative Name (SAN)
            if isinstance(ext.value, x509.SubjectAlternativeName):
                for san in ext.value:
                    if isinstance(san, x509.DNSName):  # Vérifier si c'est un DNSName
                        vid = san.value  # Récupérer le VID

            # Vérifier si l'extension contient un OID et l'ajouter à la liste
            if hasattr(ext, "oid"):
                oid_list.append(ext.oid.dotted_string)

            # Vérifier si l'extension contient une liste de distribution CRL
            if isinstance(ext.value, x509.CRLDistributionPoints):
                for point in ext.value:
                    if point.full_name:
                        crl_urls.append(point.full_name[0].value)  # Ajouter l'URL de la CRL

            # Vérifier si l'extension contient des informations d'accès pour OCSP
            if isinstance(ext.value, x509.AuthorityInformationAccess):
                for access in ext.value:
                    if access.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                        ocsp_urls.append(access.access_location.value)  # Ajouter l'URL OCSP

        # Convertir le certificat en format PEM (lisible sous forme de texte)
        cert_pem = cert.public_bytes(Encoding.PEM).decode("utf-8")
        # Extraire la clé publique du certificat au format PEM
        public_key_pem = cert.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode("utf-8")

        # Construire la réponse JSON avec toutes les informations extraites
        response_data = {
            "subject": subject,  # Titulaire du certificat
            "issuer": issuer,  # Autorité de certification émettrice
            "serial_number": serial_number,  # Numéro de série
            "valid_from": valid_from.isoformat(),  # Date de début de validité
            "valid_to": valid_to.isoformat(),  # Date d'expiration
            "status": status,  # Statut du certificat (valide ou expiré)
            "signature_algorithm": signature_algo,  # Algorithme de signature
            "public_key_pem": public_key_pem,  # Clé publique du certificat en format PEM
            "certificate_pem": cert_pem,  # Certificat complet en format PEM
            "vid": vid,  # Identifiant virtuel (s'il existe)
            "oid_list": oid_list,  # Liste des OID trouvés dans le certificat
            "crl_urls": crl_urls,  # Liste des URLs de la CRL
            "ocsp_urls": ocsp_urls  # Liste des URLs OCSP
        }

        # Retourner la réponse JSON formatée
        return Response(
            content=json.dumps(response_data, indent=4),
            media_type="application/json"
        )

    # Gestion des erreurs lors du traitement du certificat
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du certificat: {str(e)}")
