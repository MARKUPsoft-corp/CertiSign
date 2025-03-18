from fastapi import FastAPI, File, UploadFile, Form
from signer import load_private_key, sign_text_file
from signer import load_public_key, verify_signature
import base64
import os
from fastapi.responses import FileResponse


app = FastAPI()

# Obtenir le répertoire courant
current_dir = os.getcwd()

# Définir le chemin du répertoire "signed_files" dans le répertoire courant
signed_files_dir = os.path.join(current_dir, "signed_files")

# Créer le répertoire s'il n'existe pas
os.makedirs(signed_files_dir, exist_ok=True)

@app.post("/sign", include_in_schema=False)
async def sign_document(
    certificate: UploadFile = File(...),
    password: str = Form(...),
    document: UploadFile = File(...)
):
    """API pour signer un fichier TXT avec un certificat PFX"""
    try:
        # Lire le contenu des fichiers
        pfx_data = await certificate.read()
        txt_data = await document.read()

        # Charger la clé privée
        private_key = load_private_key(pfx_data, password)
        if not private_key:
            return {"error": "Impossible de charger la clé privée."}

        # Signer le fichier
        signature = sign_text_file(txt_data, private_key)

        # Encoder la signature en Base64 pour affichage
        signature_b64 = base64.b64encode(signature).decode()

        # Nom du fichier signé basé sur le fichier original
        original_filename = document.filename
        signed_filename = f"signed_{original_filename}.sig"

        # Créer le chemin complet du fichier signé
        output_filepath = os.path.join(signed_files_dir, signed_filename)

        # Sauvegarder le fichier signé
        with open(output_filepath, "w") as f:
            f.write(f"{signature_b64}") 

        return FileResponse(output_filepath, filename=signed_filename, media_type="application/octet-stream")

    except Exception as e:
        return {"error": str(e)}


@app.post("/verify")
async def verify_document(
    certificate: UploadFile = File(...),
    password: str = Form(...),
    document: UploadFile = File(...),
    signature: UploadFile = File(...)  # Accepter un fichier pour la signature
):
    """API pour vérifier la signature d'un fichier TXT avec un certificat PFX"""
    try:
        # Lire les fichiers
        pfx_data = await certificate.read()
        txt_data = await document.read()
        signature_b64 = await signature.read()  # Lire le fichier de signature

        # Charger la clé publique
        public_key = load_public_key(pfx_data, password)
        if not public_key:
            return {"error": "Impossible de charger la clé publique."}

        # Décoder la signature Base64
        signature = base64.b64decode(signature_b64.strip())  # Nettoyer et décoder

        # Vérifier la signature
        is_valid = verify_signature(txt_data, signature, public_key)

        if is_valid:
            return {"message": "La signature est valide."}
        else:
            return {"error": "La signature est invalide."}

    except Exception as e:
        return {"error": str(e)}
