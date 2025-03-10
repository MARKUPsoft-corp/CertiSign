# Importation des modules nécessaires de FastAPI et cryptography
from fastapi import FastAPI, UploadFile, File  # FastAPI pour créer l'API REST
from cryptography import x509  # Pour manipuler les certificats X.509
from cryptography.hazmat.backends import default_backend  # Backend pour charger les certificats

# Création de l'application FastAPI
app = FastAPI()

# Définition d'une route POST pour lire un certificat X.509
@app.post("/read-cert")
async def read_certificate(cert_file: UploadFile = File(...)):  
    """
    Cette fonction reçoit un fichier de certificat, l'analyse et retourne ses informations essentielles.
    """
    try:
        # Lire le contenu du fichier téléchargé en binaire
        cert_bytes = await cert_file.read()
        
        # Charger le certificat en supposant qu'il est au format PEM
        cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())

        # Extraction des informations clés du certificat
        cert_info = {
            "subject": cert.subject.rfc4514_string(),  # Identité du propriétaire du certificat
            "issuer": cert.issuer.rfc4514_string(),  # Autorité qui a signé le certificat
            "serial_number": str(cert.serial_number),  # Numéro de série unique
            "not_valid_before": cert.not_valid_before.isoformat(),  # Date de début de validité
            "not_valid_after": cert.not_valid_after.isoformat(),  # Date d'expiration
        }

        # Retourner les informations sous forme de JSON
        return cert_info

    except Exception as e:
        # Gestion des erreurs si le fichier n'est pas un certificat valide
        return {"error": str(e)}
