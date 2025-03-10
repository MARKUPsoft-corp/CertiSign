# Importation des modules nécessaires de FastAPI et requests
from fastapi import FastAPI, File, UploadFile  # FastAPI pour l'API
import requests  # Pour envoyer des requêtes HTTP au microservice

# Création de l'application FastAPI
app = FastAPI()

# Définition de l'URL du microservice qui lit les certificats
CERT_SERVICE_URL = "http://127.0.0.1:8001/read-cert"

# Définition d'une route POST pour envoyer le certificat au microservice
@app.post("/upload-cert")
async def upload_certificate(cert_file: UploadFile = File(...)):  
    """
    Cette fonction reçoit un fichier via l'API Gateway et le transmet au microservice de lecture de certificats.
    """
    # Lire le fichier et préparer les données pour l'envoi HTTP
    files = {"cert_file": (cert_file.filename, await cert_file.read(), cert_file.content_type)}

    # Envoyer le fichier au microservice via une requête POST
    response = requests.post(CERT_SERVICE_URL, files=files)

    # Retourner la réponse obtenue du microservice
    return response.json()
