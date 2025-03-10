from fastapi import FastAPI, File, UploadFile, Form  # Importation des modules nécessaires de FastAPI pour gérer les fichiers et les formulaires
from pydantic import BaseModel  # Importation de BaseModel pour définir un modèle de réponse JSON
from cryptography.hazmat.primitives.serialization import pkcs12  # Importation de pkcs12 pour traiter les fichiers PFX
from cryptography.hazmat.backends import default_backend  # Importation du backend par défaut pour cryptographie
import os  # Importation du module os pour la gestion des fichiers

# Création de l'application FastAPI
app = FastAPI()  # Initialisation de l'application FastAPI

# Modèle de données pour la réponse JSON
class CertInfo(BaseModel):  # Création d'un modèle Pydantic pour structurer la réponse
    subject: str  # Le sujet du certificat (ex: le propriétaire)
    issuer: str  # L'émetteur du certificat (ex: l'autorité de certification)
    serial_number: str  # Le numéro de série du certificat
    not_valid_before: str  # La date de début de validité du certificat
    not_valid_after: str  # La date de fin de validité du certificat

# Fonction pour extraire les informations d'un certificat PFX
def extract_cert_info_from_pfx(pfx_path, password=None):
    with open(pfx_path, 'rb') as f:  # Ouvre le fichier PFX en mode binaire
        pfx_data = f.read()  # Lit tout le contenu du fichier PFX

    # Charger le certificat et la clé privée à partir des données PFX
    private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
        pfx_data, password.encode() if password else None, backend=default_backend()
    )

    # Extraire des informations essentielles du certificat
    cert_info = {
        "subject": str(certificate.subject),  # Extraire le sujet du certificat
        "issuer": str(certificate.issuer),  # Extraire l'émetteur du certificat
        "serial_number": str(certificate.serial_number),  # Extraire le numéro de série du certificat
        "not_valid_before": str(certificate.not_valid_before),  # Extraire la date de début de validité
        "not_valid_after": str(certificate.not_valid_after),  # Extraire la date de fin de validité
    }

    return cert_info  # Retourne les informations extraites du certificat

# Point d'entrée de l'API d'extraction des informations du certificat
@app.post("/extract_cert_info", response_model=CertInfo)  # Définit un endpoint POST pour extraire les infos du certificat
async def extract_cert_info_from_pfx_endpoint(cert: UploadFile = File(...), password: str = Form(...)):  
    # 'cert' est un fichier téléchargé via l'API et 'password' est le mot de passe du certificat, reçu via un formulaire
    
    # Sauvegarder le fichier .pfx temporairement pour pouvoir l'utiliser dans la fonction d'extraction
    cert_path = f"temp_{cert.filename}"  # Crée un chemin temporaire pour le fichier téléchargé
    with open(cert_path, "wb") as f:  # Ouvre le fichier temporaire en mode écriture binaire
        f.write(await cert.read())  # Écrit le contenu du fichier téléchargé dans le fichier temporaire

    # Appeler la fonction pour extraire les informations du certificat
    cert_info = extract_cert_info_from_pfx(cert_path, password)  # Récupère les infos extraites du certificat

    # Supprimer le fichier temporaire après l'extraction des informations
    os.remove(cert_path)  # Supprime le fichier temporaire une fois l'extraction terminée

    return cert_info  # Retourne les informations extraites du certificat dans la réponse de l'API
