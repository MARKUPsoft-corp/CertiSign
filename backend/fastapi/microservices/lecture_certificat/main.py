# Importation des modules nécessaires pour l'application FastAPI et la gestion des fichiers et des certificats
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response
from cryptography import x509  # Permet d'analyser les certificats X.509
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, PublicFormat  # Gestion des formats PKCS12 et PEM
import json  # Pour manipuler des objets JSON
import base64  # Pour encoder en base64

# Création de l'application FastAPI
app = FastAPI()

# Définition de la route POST qui permet d'extraire les informations d'un certificat
@app.post("/extract-cert-info/")
async def extract_cert_info(file: UploadFile = File(...), password: str = Form(...)):
    try:
        # Lecture du fichier envoyé et stockage des octets du certificat
        cert_bytes = await file.read()

        # Chargement du certificat et de la clé privée à partir des données PKCS12
        private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
            cert_bytes, password.encode()  # Mot de passe pour déchiffrer le fichier .pfx
        )

        # Si le certificat est nul, on renvoie une erreur HTTP avec le message approprié
        if cert is None:
            raise HTTPException(status_code=400, detail="Certificat invalide ou mot de passe incorrect.")

        # Extraction des informations principales du certificat
        subject = cert.subject.rfc4514_string()  # Récupération de l'identité du sujet du certificat
        issuer = cert.issuer.rfc4514_string()  # Récupération de l'autorité émettrice du certificat
        serial_number = cert.serial_number  # Récupération du numéro de série du certificat
        valid_from = cert.not_valid_before  # Date de début de validité du certificat
        valid_to = cert.not_valid_after  # Date de fin de validité du certificat
        signature_algo = cert.signature_algorithm_oid.dotted_string  # Algorithme de signature du certificat

        # Encodage du certificat en format PEM
        cert_pem = cert.public_bytes(Encoding.PEM).decode("utf-8")  # Le certificat est converti en format PEM et décodé en UTF-8
        # Encodage de la clé publique en format PEM
        public_key_pem = cert.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode("utf-8")

        # Initialisation des listes pour stocker les URLs OCSP, CRL et TSA
        ocsp_urls = []  # URLs de l'OCSP (Online Certificate Status Protocol)
        crl_urls = []  # URLs des listes de révocation de certificats (CRL)
        tsa_urls = []  # URLs du serveur de timestamp (TSA)

        # Parcours des extensions du certificat pour en extraire les informations supplémentaires
        for ext in cert.extensions:
            # Vérification si l'extension est une autorité d'information
            if isinstance(ext.value, x509.AuthorityInformationAccess):
                for access_desc in ext.value:
                    # Si l'extension est OCSP, on ajoute l'URL à la liste ocsp_urls
                    if access_desc.access_method == x509.OID_OCSP:
                        ocsp_urls.append(access_desc.access_location.value)
                    # Si l'extension est une autorité de certificats, on ajoute l'URL à la liste tsa_urls
                    elif access_desc.access_method == x509.OID_CA_ISSUERS:
                        tsa_urls.append(access_desc.access_location.value)

            # Vérification si l'extension est une distribution de CRL
            elif isinstance(ext.value, x509.CRLDistributionPoints):
                for point in ext.value:
                    for name in point.full_name:
                        crl_urls.append(name.value)  # Ajout des URLs CRL

        # Création de la réponse JSON avec toutes les informations extraites
        response_data = {
            "subject": subject,  # Sujet du certificat
            "issuer": issuer,  # Émetteur du certificat
            "serial_number": serial_number,  # Numéro de série du certificat
            "valid_from": valid_from.isoformat(),  # Date de début de validité
            "valid_to": valid_to.isoformat(),  # Date de fin de validité
            "signature_algorithm": signature_algo,  # Algorithme de signature
            "public_key_pem": public_key_pem,  # Clé publique en format PEM
            "certificate_pem": cert_pem,  # Certificat en format PEM
            "ocsp_urls": ocsp_urls,  # Liste des URLs OCSP
            "crl_urls": crl_urls,  # Liste des URLs CRL
            "tsa_urls": tsa_urls  # Liste des URLs TSA
        }

        # Retourner la réponse formatée en JSON avec indentation (format joli avec des retours à la ligne)
        return Response(
            content=json.dumps(response_data, indent=4),  # Format JSON avec un retour à la ligne (indentation)
            media_type="application/json"  # Type MIME pour JSON
        )

    except Exception as e:
        # Si une exception survient, retourner une erreur HTTP 500 avec le message de l'exception
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du certificat: {str(e)}")
