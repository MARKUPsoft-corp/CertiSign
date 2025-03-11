from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import requests
from OpenSSL import crypto

app = FastAPI()

# Modèle pour les données de validation
class CertValidationRequest(BaseModel):
    not_valid_after: str  # Date d'expiration
    crl_url: str          # URL de la CRL
    ocsp_url: str         # URL de l'OCSP
    serial_number: str    # Numéro de série du certificat

# Vérification de l'expiration
def is_cert_expired(not_valid_after: str) -> bool:
    cert_expiration_date = datetime.strptime(not_valid_after, "%Y-%m-%d %H:%M:%S")
    return cert_expiration_date < datetime.now()

# Vérification dans la CRL
def check_crl(serial_number: str, crl_url: str) -> bool:
    try:
        response = requests.get(crl_url, timeout=5)
        response.raise_for_status()
        crl = crypto.load_crl(crypto.FILETYPE_PEM, response.content)
        serial_number_int = int(serial_number, 16)

        for revoked in crl.get_revoked():
            if int(revoked.get_serial(), 16) == serial_number_int:
                return False  # Certificat révoqué
        return True  # Certificat valide
    except Exception as e:
        print(f"Erreur lors de la vérification CRL : {e}")
        return False  # Considérer le certificat invalide en cas d'erreur

# Vérification via OCSP
def check_ocsp(serial_number: str, ocsp_url: str) -> bool:
    try:
        response = requests.post(ocsp_url, json={"serial_number": serial_number}, timeout=5)
        response.raise_for_status()
        return response.json().get("status") != "revoked"
    except Exception as e:
        print(f"Erreur lors de la vérification OCSP : {e}")
        return False  # Considérer le certificat invalide en cas d'erreur

# Endpoint pour valider le certificat
@app.post("/validate_cert/")
async def validate_cert(request: Request):
    try:
        # Récupérer les données envoyées par l'API Gateway
        cert_data = await request.json()
        cert = CertValidationRequest(**cert_data)  # Convertir en objet Pydantic

        # Étape 1 : Vérification de l'expiration
        if is_cert_expired(cert.not_valid_after):
            return {"status": "Certificat expiré"}

        # Étape 2 : Vérification CRL
        if not check_crl(cert.serial_number, cert.crl_url):
            return {"status": "Certificat révoqué (CRL)"}

        # Étape 3 : Vérification OCSP
        if not check_ocsp(cert.serial_number, cert.ocsp_url):
            return {"status": "Certificat révoqué (OCSP)"}

        # Si toutes les vérifications passent
        return {"status": "Certificat valide"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
