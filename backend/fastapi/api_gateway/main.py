import httpx  # Importation du module httpx pour effectuer des requêtes HTTP asynchrones
from fastapi import FastAPI, Form, UploadFile, File  # Importation des composants de FastAPI nécessaires
from pydantic import BaseModel  # Importation de BaseModel pour définir des modèles de données pour les réponses

# Création de l'application FastAPI pour l'API Gateway
app = FastAPI()  # Initialisation de l'application FastAPI

# Modèle de données pour la réponse JSON
class CertInfo(BaseModel):  # Définition d'un modèle de réponse pour l'information extraite du certificat
    subject: str  # Le sujet du certificat (ex: le propriétaire)
    issuer: str  # L'émetteur du certificat (ex: l'autorité de certification)
    serial_number: str  # Le numéro de série du certificat
    not_valid_before: str  # Date de début de validité du certificat
    not_valid_after: str  # Date de fin de validité du certificat

# URL du microservice d'extraction (peut être modifiée selon la configuration)
EXTRACTION_SERVICE_URL = "http://localhost:8001/extract_cert_info"  # L'URL où l'API d'extraction des informations du certificat est disponible

@app.post("/extract_cert_info", response_model=CertInfo)  # Définition de l'endpoint POST pour extraire les informations du certificat
async def extract_cert_info_from_pfx(cert: UploadFile = File(...), password: str = Form(...)):  
    # Cette fonction est appelée lorsque l'endpoint "/extract_cert_info" est sollicité avec un fichier et un mot de passe
    # 'cert' est un fichier de type UploadFile et 'password' est récupéré en tant que champ de formulaire
    
    data = {'password': password}  # Préparation des données pour envoyer le mot de passe à l'API de microservice
    files = {'cert': (cert.filename, cert.file, 'application/octet-stream')}  # Préparation du fichier à envoyer à l'API

    # Faire une requête HTTP asynchrone vers le microservice d'extraction pour extraire les informations du certificat
    async with httpx.AsyncClient() as client:  # Crée un client HTTP asynchrone
        response = await client.post(EXTRACTION_SERVICE_URL, data=data, files=files)  # Envoi de la requête POST avec les données et fichiers

    # Vérification de la réponse du microservice d'extraction
    if response.status_code == 200:  # Si la réponse du microservice a un statut 200 (succès)
        return response.json()  # Retourne les informations extraites du certificat sous forme de JSON
    else:  # Si une erreur est survenue lors de l'extraction
        return {"error": "Erreur dans l'extraction du certificat."}  # Retourne un message d'erreur
