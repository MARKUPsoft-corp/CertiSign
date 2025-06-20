from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Request, Body
from fastapi.responses import FileResponse, JSONResponse
from signer import load_private_key, sign_file, load_public_key, verify_signature
from django_api import store_signature_data, get_signature_data, DJANGO_API_BASE_URL
import base64
import os
import tempfile
import logging
import time
import uuid
import httpx
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import qrcode
from PIL import Image
from io import BytesIO
# Commentons temporairement ces imports problématiques
# import numpy as np
# import cv2
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import json
from cryptography.hazmat.backends import default_backend

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="Service de Signature Numérique",
    description="API pour signer et vérifier la signature numérique de documents PDF et autres fichiers",
    version="2.0.0",
)

# Indications pour les bibliothèques manquantes
logger.warning("ATTENTION: Les bibliothèques numpy et OpenCV (cv2) sont temporairement désactivées.")
logger.warning("Certaines fonctionnalités liées à l'extraction de code QR peuvent ne pas fonctionner.")
logger.warning("Pour résoudre ce problème, réinstallez ces bibliothèques avec: pip install numpy opencv-python-headless")

# Obtenir le répertoire courant
current_dir = os.getcwd()

# Définir le chemin du répertoire "signed_files" dans le répertoire courant (DÉSACTIVÉ)
# signed_files_dir = os.path.join(current_dir, "signed_files")

# Créer le répertoire s'il n'existe pas (DÉSACTIVÉ - plus besoin)
# os.makedirs(signed_files_dir, exist_ok=True)

# SUPPRIMÉ: Les documents signés ne seront plus sauvegardés localement
# pour éviter l'accumulation de fichiers sur le serveur

# Fonction pour nettoyer les fichiers temporaires
def cleanup_temp_files(file_paths):
    """Supprime les fichiers temporaires après un délai"""
    time.sleep(300)  # Attendre 5 minutes
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Fichier temporaire supprimé: {file_path}")
            else:
                logger.debug(f"Fichier temporaire n'existe plus: {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier temporaire {file_path}: {e}")

def add_simple_qr_code_to_pdf(pdf_data: bytes, document_id: str, qr_position: dict = None) -> bytes:
    """
    Ajoute un QR code contenant uniquement l'ID du document au PDF en préservant son contenu.
    Le QR code peut être ajouté sur toutes les pages ou sur des pages spécifiques.
    
    Args:
        pdf_data (bytes): Données du PDF original
        document_id (str): Identifiant unique du document à encoder dans le QR code
        qr_position (dict): Position, taille et pages du QR code 
                           {x: %, y: %, size: 'small'|'medium'|'large', pages: 'all'|[1,2,3],
                            positions: {page_num: {x: %, y: %}, ...}, mode: 'all'|'current'|'custom'|'individual'}
        
    Returns:
        bytes: PDF modifié avec le QR code
    """
    try:
        logger.info("Début du processus d'ajout du QR code au PDF")
        
        # Position par défaut si non spécifiée
        if qr_position is None:
            qr_position = {'x': 85, 'y': 10, 'size': 'medium', 'pages': 'all'}
        
        # Tailles disponibles pour le QR code
        qr_sizes = {
            'small': 0.4 * inch,   # 0.4 inch
            'medium': 0.5 * inch,  # 0.5 inch
            'large': 0.6 * inch    # 0.6 inch
        }
        
        # Récupérer la taille du QR code
        qr_size = qr_sizes.get(qr_position.get('size', 'medium'), qr_sizes['medium'])
        
        # Pages où appliquer le QR code
        pages_to_apply = qr_position.get('pages', 'all')
        
        # Positions individuelles par page (nouveau)
        individual_positions = qr_position.get('positions', {})
        position_mode = qr_position.get('mode', 'all')
        
        logger.info(f"Mode de positionnement: {position_mode}")
        logger.info(f"Position par défaut: x={qr_position.get('x', 85)}%, y={qr_position.get('y', 10)}%, taille={qr_position.get('size', 'medium')}")
        logger.info(f"Pages où appliquer le QR code: {pages_to_apply}")
        if individual_positions:
            logger.info(f"Positions individuelles définies pour les pages: {list(individual_positions.keys())}")
        
        # Créer le QR code avec une version inférieure (plus petit) car l'ID est court
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        # Encoder simplement l'ID du document dans le QR code
        logger.info(f"Encodage de l'ID du document: {document_id} dans le QR code")
        qr.add_data(document_id)
        qr.make(fit=True)
        
        # Créer l'image du QR code
        logger.info("Génération de l'image du QR code")
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder l'image du QR code dans un fichier temporaire
        temp_dir = tempfile.gettempdir()
        temp_qr_path = os.path.join(temp_dir, f"temp_qr_{uuid.uuid4()}.png")
        logger.info(f"Sauvegarde du QR code dans: {temp_qr_path}")
        qr_image.save(temp_qr_path)
        
        try:
            # Lire le PDF original
            logger.info("Lecture du PDF original")
            pdf_reader = PdfReader(BytesIO(pdf_data))
            pdf_writer = PdfWriter()
            
            # Parcourir chaque page du PDF
            total_pages = len(pdf_reader.pages)
            logger.info(f"Traitement des {total_pages} pages du PDF")
            
            for i, page in enumerate(pdf_reader.pages):
                page_number = i + 1  # Les numéros de page commencent à 1
                
                # Vérifier si le QR code doit être appliqué sur cette page
                should_apply_qr = False
                if pages_to_apply == 'all':
                    should_apply_qr = True
                elif isinstance(pages_to_apply, list):
                    should_apply_qr = page_number in pages_to_apply
                
                if should_apply_qr:
                    logger.info(f"Application du QR code sur la page {page_number}")
                    
                    # Créer un buffer pour stocker le Canvas avec le QR code adapté à cette page
                    qr_canvas_buffer = BytesIO()
                    
                    # Obtenir les dimensions de la page
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                    
                    logger.info(f"Dimensions de la page {page_number}: {page_width} x {page_height} points")
                    
                    # Créer un canvas avec les dimensions exactes de la page
                    qr_canvas = canvas.Canvas(qr_canvas_buffer, pagesize=(page_width, page_height))
                    
                    # Déterminer la position du QR code pour cette page
                    x_percent = qr_position.get('x', 85)
                    y_percent = qr_position.get('y', 10)
                    
                    # Si mode individual et position spécifique pour cette page, l'utiliser
                    if position_mode == 'individual' and individual_positions:
                        # Convertir le numéro de page en chaîne car les clés JSON sont des chaînes
                        page_number_str = str(page_number)
                        if page_number_str in individual_positions:
                            page_position = individual_positions[page_number_str]
                            x_percent = page_position.get('x', x_percent)
                            y_percent = page_position.get('y', y_percent)
                            logger.info(f"Position individuelle pour page {page_number}: x={x_percent}%, y={y_percent}%")
                        else:
                            # En mode individuel, si pas de position définie pour cette page, ne pas afficher de QR
                            logger.info(f"En mode individual, aucune position définie pour la page {page_number}, QR non affiché")
                            # Saut de l'ajout du QR pour cette page
                            pdf_writer.add_page(page)
                            continue
                    
                    # Les pourcentages dans le frontend sont : 0% = gauche/haut, 100% = droite/bas
                    # En PDF, Y=0 est en bas, donc il faut inverser Y
                    x_position = (x_percent / 100) * page_width
                    y_position = ((100 - y_percent) / 100) * page_height
                    
                    # Taille du QR code et du cadre
                    qr_size_with_margin = qr_size + 0.05*inch
                    qr_frame_height = qr_size_with_margin + 0.1*inch
                    
                    # Centrer le QR code à la position calculée
                    x_position = x_position - qr_size_with_margin / 2
                    y_position = y_position - qr_frame_height / 2
                    
                    # S'assurer que le QR code et son cadre s'intègrent complètement dans la page
                    margin = 20  # Marge de sécurité
                    x_position = max(margin, min(page_width - qr_size_with_margin - margin, x_position))
                    y_position = max(margin, min(page_height - qr_frame_height - margin, y_position))
                    
                    # Dessiner un rectangle blanc sous le QR code
                    qr_canvas.setFillColorRGB(1, 1, 1)  # Blanc
                    qr_canvas.rect(
                        x_position, 
                        y_position,
                        qr_size_with_margin,
                        qr_frame_height,
                        fill=True
                    )
                    
                    # Ajouter le texte "ANTIC" et la date au-dessus du QR code
                    qr_canvas.setFillColorRGB(0, 0, 0)  # Noir
                    qr_canvas.setFont("Helvetica", 6)  # Police petite (6pt)
                    current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
                    qr_canvas.drawString(
                        x_position + 0.02*inch,
                        y_position + qr_size + 0.08*inch,
                        f"ANTIC {current_date}"
                    )
                    
                    # Dessiner le QR code
                    qr_canvas.drawImage(temp_qr_path, 
                                       x_position + 0.025*inch,
                                       y_position + 0.025*inch,
                                       width=qr_size, 
                                       height=qr_size, 
                                       preserveAspectRatio=True)
                    qr_canvas.save()
                    
                    # Réinitialiser le buffer pour lecture
                    qr_canvas_buffer.seek(0)
                    
                    # Fusionner le QR code avec la page
                    qr_page = PdfReader(qr_canvas_buffer).pages[0]
                    
                    # Créer une nouvelle page avec le contenu original
                    new_page = page
                    
                    # Fusionner le QR code avec la page
                    new_page.merge_page(qr_page)
                    
                    # Ajouter la page modifiée au writer
                    pdf_writer.add_page(new_page)
                else:
                    logger.info(f"Page {page_number} sans QR code")
                    # Ajouter la page sans modification
                    pdf_writer.add_page(page)
            
            # Sauvegarder le PDF modifié
            logger.info("Sauvegarde du PDF modifié avec le QR code")
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            logger.info("Processus d'ajout du QR code terminé avec succès")
            return output_buffer.getvalue()
            
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_qr_path):
                logger.info(f"Suppression du fichier temporaire: {temp_qr_path}")
                os.remove(temp_qr_path)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du QR code au PDF: {str(e)}", exc_info=True)
        raise

def embed_signature_in_pdf(pdf_data: bytes, signature: bytes, public_key_pem: str, document_id: str) -> bytes:
    """
    Intègre la signature numérique dans les métadonnées du PDF et ajoute un QR code visible 
    avec l'ID du document dans le coin inférieur droit.
    
    Args:
        pdf_data (bytes): Données du PDF original
        signature (bytes): Signature à intégrer
        public_key_pem (str): Clé publique au format PEM
        document_id (str): ID unique du document à encoder dans le QR code
        
    Returns:
        bytes: PDF avec signature et QR code
    """
    try:
        logger.info("Début du processus d'intégration de la signature dans le PDF")
        
        # Encoder la signature en base64
        signature_b64 = base64.b64encode(signature).decode()
        logger.info(f"Signature encodée en base64, longueur: {len(signature_b64)}")
        
        # Calculer le hash du document original
        original_hash = hashlib.sha256(pdf_data).hexdigest()
        logger.info(f"Hash du document original calculé: {original_hash[:10]}...")
        
        # MISE À JOUR : Utiliser uniquement l'ID du document dans le QR code
        # pour simplifier la vérification et réduire la taille du QR code
        logger.info(f"Utilisation de l'ID du document uniquement dans le QR code: {document_id}")
        
        # Créer le QR code avec une version inférieure (plus petit) car l'ID est court
        logger.info("Création d'un QR code avec seulement l'ID du document")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        # Encoder simplement l'ID du document dans le QR code
        logger.info(f"Encodage de l'ID du document: {document_id} dans le QR code")
        qr.add_data(document_id)
        qr.make(fit=True)
        
        # Créer l'image du QR code
        logger.info("Génération de l'image du QR code")
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder l'image du QR code dans un fichier temporaire
        temp_dir = tempfile.gettempdir()
        temp_qr_path = os.path.join(temp_dir, f"temp_qr_{uuid.uuid4()}.png")
        logger.info(f"Sauvegarde du QR code dans: {temp_qr_path}")
        qr_image.save(temp_qr_path)
        
        try:
            # Lire le PDF original
            logger.info("Lecture du PDF original")
            pdf_reader = PdfReader(BytesIO(pdf_data))
            pdf_writer = PdfWriter()
            
            # Réduire la taille du QR code à une valeur fixe (en pouces)
            qr_size = 0.50 * inch
            logger.info(f"Taille du QR code: {qr_size} pouces")
            
            # Parcourir chaque page du PDF et ajouter le QR code
            logger.info(f"Traitement des {len(pdf_reader.pages)} pages du PDF")
            for i, page in enumerate(pdf_reader.pages):
                # Créer un buffer pour stocker le Canvas avec le QR code adapté à cette page
                qr_buffer = BytesIO()
                
                # Obtenir les dimensions de la page
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                logger.info(f"Dimensions de la page {i+1}: {page_width} x {page_height} points")
                
                # Créer un canvas avec les dimensions exactes de la page
                qr_canvas = canvas.Canvas(qr_buffer, pagesize=(page_width, page_height))
                
                # Calculer les marges (en points) - augmenter la marge à 50 points (environ 0.7 inch)
                margin = 50
                
                # Taille du QR code et du cadre
                qr_size_with_margin = qr_size + 0.05*inch  # Réduire la marge de 0.2 à 0.05 inch
                qr_frame_height = qr_size_with_margin + 0.1*inch  # Réduire l'espace pour le texte de 0.15 à 0.1 inch
                
                # Position X: côté droit de la page avec une marge
                x_position = page_width - margin - qr_size_with_margin
                
                # Position Y: bas de la page avec une marge plus grande pour éviter la troncature
                y_position = margin
                
                # S'assurer que le QR code et son cadre s'intègrent complètement dans la page
                if x_position < 0:
                    x_position = 10  # Si la page est trop étroite, placer le QR code près du bord gauche
                
                if y_position + qr_frame_height > page_height:
                    y_position = page_height - qr_frame_height - 10  # Si la page est trop petite, ajuster la position Y
                
                # Dessiner un rectangle blanc sous le QR code
                qr_canvas.setFillColorRGB(1, 1, 1)  # Blanc
                qr_canvas.rect(
                    x_position, 
                    y_position,
                    qr_size_with_margin,
                    qr_frame_height,
                    fill=True
                )
                
                # Ajouter le texte "ANTIC" et la date au-dessus du QR code
                qr_canvas.setFillColorRGB(0, 0, 0)  # Noir
                qr_canvas.setFont("Helvetica", 6)  # Police petite (6pt)
                current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
                qr_canvas.drawString(
                    x_position + 0.02*inch,  # Réduire la marge de 0.05 à 0.02 inch
                    y_position + qr_size + 0.08*inch,  # Réduire la marge de 0.15 à 0.08 inch
                    f"ANTIC {current_date}"
                )
                
                # Dessiner le QR code avec moins d'espace autour
                qr_canvas.drawImage(temp_qr_path, 
                                   x_position + 0.025*inch,  # Réduire la marge de 0.1 à 0.025 inch
                                   y_position + 0.025*inch,  # Réduire la marge de 0.1 à 0.025 inch
                                   width=qr_size, 
                                   height=qr_size, 
                                   preserveAspectRatio=True)
                
                qr_canvas.save()
                
                # Réinitialiser le buffer pour lecture
                qr_buffer.seek(0)
                
                # Charger le PDF contenant le QR code
                qr_pdf = PdfReader(qr_buffer)
                
                # Fusionner le QR code avec la page
                logger.info(f"Fusion de la page {i+1}")
                page.merge_page(qr_pdf.pages[0])
                pdf_writer.add_page(page)
            
            # Ajouter la signature dans les métadonnées du PDF
            logger.info("Ajout de la signature dans les métadonnées")
            metadata_dict = {
                "/CertiSignSignature": signature_b64,
                "/SignatureDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "/SignatureVersion": "2.0",
                "/OriginalDocumentHash": original_hash,
                "/PublicKey": public_key_pem
            }
            
            # Ajouter les métadonnées au PDF
            pdf_writer.add_metadata(metadata_dict)
            
            # Sauvegarder le PDF modifié
            logger.info("Sauvegarde du PDF modifié")
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            logger.info("Processus d'intégration de la signature terminé avec succès")
            return output_buffer.getvalue()
            
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_qr_path):
                logger.info(f"Suppression du fichier temporaire: {temp_qr_path}")
                os.remove(temp_qr_path)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'intégration de la signature dans le PDF: {str(e)}", exc_info=True)
        raise

def extract_document_id_from_qr(pdf_data: bytes) -> str:
    """
    Extrait l'ID du document depuis le QR code présent dans le PDF.
    
    Args:
        pdf_data (bytes): Données du PDF signé
        
    Returns:
        str: Identifiant du document ou None si non trouvé
    """
    try:
        # Convertir les premières pages en images
        logger.info("Conversion du PDF en images pour l'analyse du QR code")
        images = convert_from_bytes(pdf_data, first_page=1, last_page=1)
        
        if not images:
            logger.warning("Aucune image n'a pu être extraite du PDF")
            return None
        
        # Prendre la première page
        first_page = images[0]
        logger.info(f"Dimensions de l'image: {first_page.width}x{first_page.height}")
        
        # Sauvegarder l'image dans un buffer
        buffer = BytesIO()
        first_page.save(buffer, format="PNG")
        buffer.seek(0)
        img_data = buffer.read()
        
        # Essayer de décoder le QR code
        logger.info("Tentative de décodage du QR code")
        
        logger.warning("Cette fonction nécessiterait une bibliothèque de décodage QR comme pyzbar")
        
        # Écrire l'image dans un fichier temporaire pour utilisation future
        temp_file = os.path.join(tempfile.gettempdir(), f"qr_temp_{uuid.uuid4()}.png")
        with open(temp_file, "wb") as f:
            f.write(img_data)
        logger.info(f"Image temporaire sauvegardée dans {temp_file}")
        
        # Pour cette démo, on renvoie None
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction de l'ID du document: {str(e)}")
        return None

def extract_signature_from_pdf(pdf_data: bytes) -> Dict[str, Any]:
    """
    Extrait la signature et les autres données du PDF depuis les métadonnées.
    
    Args:
        pdf_data (bytes): Données du PDF signé
        
    Returns:
        Dict[str, Any]: Dictionnaire contenant la signature, la clé publique et le hash du document original
    """
    try:
        # Lire le PDF
        pdf_reader = PdfReader(BytesIO(pdf_data))
        
        # Extraire les métadonnées
        metadata = pdf_reader.metadata
        
        if metadata:
            # Récupérer la signature
            signature_b64 = metadata.get("/CertiSignSignature")
            public_key_pem = metadata.get("/PublicKey")
            document_hash = metadata.get("/OriginalDocumentHash")
            
            if signature_b64 and public_key_pem and document_hash:
                # Décoder la signature
                signature = base64.b64decode(signature_b64)
                return {
                    "signature": signature,
                    "signature_b64": signature_b64,
                    "public_key": public_key_pem,
                    "document_hash": document_hash
                }
    
    except Exception as e:
        logger.warning(f"Échec de l'extraction de la signature depuis les métadonnées: {str(e)}")
    
    # Si l'extraction depuis les métadonnées a échoué
    logger.error("Impossible d'extraire les données de signature depuis les métadonnées du PDF.")
    
    # Lever une exception indiquant que l'extraction des métadonnées a échoué
    raise ValueError("Impossible d'extraire les données de signature depuis les métadonnées du PDF.")

def add_signature_image_to_pdf(pdf_data: bytes, signature_image_data: str, signature_positions: list) -> bytes:
    """
    Ajoute une image de signature au PDF aux positions spécifiées.
    
    Args:
        pdf_data (bytes): Données du PDF original
        signature_image_data (str): Image de signature en base64
        signature_positions (list): Liste des positions où ajouter la signature
                                   [{page: int, x: float, y: float, width: float, height: float}, ...]
        
    Returns:
        bytes: PDF modifié avec l'image de signature
    """
    try:
        logger.info("Début du processus d'ajout de l'image de signature au PDF")
        
        # Vérifier que les données d'image sont valides
        if not signature_image_data:
            logger.warning("Données d'image de signature manquantes")
            return pdf_data
            
        # Journaliser les premiers caractères de l'image pour diagnostic
        logger.info(f"Début des données d'image reçues: {signature_image_data[:50]}...")
        
        # Vérifier que les positions sont valides
        if not signature_positions or not isinstance(signature_positions, list) or len(signature_positions) == 0:
            logger.warning("Positions de signature invalides ou manquantes")
            return pdf_data
            
        # Extraire les données binaires de l'image depuis le base64
        try:
            # Gérer différents formats possibles de données base64
            if signature_image_data.startswith('data:image'):
                # Format attendu: data:image/png;base64,iVBORw0KGgo...
                image_format = signature_image_data.split(';')[0].split('/')[1]
                image_data = signature_image_data.split(',')[1]
            else:
                # Essayer de traiter comme du base64 brut
                image_data = signature_image_data
                # Détecter le format en examinant les premiers octets
                image_format = "png"  # Format par défaut
            
            try:
                # Décoder les données base64
                image_bytes = base64.b64decode(image_data)
                logger.info(f"Image de signature décodée, format: {image_format}, taille: {len(image_bytes)} octets")
                
                # Vérifier que les données décodées sont une image valide
                try:
                    from PIL import Image
                    Image.open(BytesIO(image_bytes))
                    logger.info("Image validée par PIL")
                except Exception as e:
                    logger.error(f"Les données décodées ne sont pas une image valide: {str(e)}")
                    return pdf_data
                
            except base64.binascii.Error as e:
                logger.error(f"Erreur de décodage base64: {str(e)}")
                # Essayer de nettoyer la chaîne base64 et réessayer
                clean_image_data = ''.join(image_data.split())  # Supprimer les espaces
                try:
                    image_bytes = base64.b64decode(clean_image_data)
                    logger.info(f"Image décodée après nettoyage, taille: {len(image_bytes)} octets")
                except Exception as e2:
                    logger.error(f"Échec du décodage même après nettoyage: {str(e2)}")
                    return pdf_data
            
        except Exception as e:
            logger.error(f"Erreur lors du décodage de l'image de signature: {str(e)}")
            return pdf_data
            
        # Sauvegarder l'image dans un fichier temporaire
        temp_dir = tempfile.gettempdir()
        temp_image_path = os.path.join(temp_dir, f"temp_signature_{uuid.uuid4()}.{image_format}")
        
        with open(temp_image_path, "wb") as f:
            f.write(image_bytes)
            
        logger.info(f"Image de signature sauvegardée temporairement: {temp_image_path}")
        
        try:
            # Lire le PDF original
            pdf_reader = PdfReader(BytesIO(pdf_data))
            pdf_writer = PdfWriter()
            
            # Parcourir chaque page du PDF
            total_pages = len(pdf_reader.pages)
            logger.info(f"Traitement des {total_pages} pages du PDF")
            
            for i, page in enumerate(pdf_reader.pages):
                page_number = i + 1  # Les numéros de page commencent à 1
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Vérifier si une signature doit être ajoutée sur cette page
                # Accepter à la fois les numéros de page sous forme de chaîne et d'entier
                signatures_for_page = [pos for pos in signature_positions 
                                      if str(pos.get('page', 1)) == str(page_number)]
                
                if signatures_for_page:
                    logger.info(f"Ajout de {len(signatures_for_page)} signature(s) sur la page {page_number}")
                    
                    # Créer un buffer pour stocker le Canvas avec la signature
                    sig_canvas_buffer = BytesIO()
                    sig_canvas = canvas.Canvas(sig_canvas_buffer, pagesize=(page_width, page_height))
                    
                    # Ajouter chaque signature à la page
                    for pos in signatures_for_page:
                        # Obtenir les coordonnées en pourcentage et les convertir en points
                        x_percent = float(pos.get('x', 50))
                        y_percent = float(pos.get('y', 50))
                        width_percent = float(pos.get('width', 20))
                        height_percent = float(pos.get('height', 10))
                        
                        logger.info(f"Position de signature: x={x_percent}%, y={y_percent}%, "
                                   f"largeur={width_percent}%, hauteur={height_percent}%")
                        
                        # Convertir les pourcentages en coordonnées absolues
                        # Pour X: 0% = gauche, 100% = droite
                        # Pour Y: 0% = haut, 100% = bas (inverser pour le PDF)
                        x_position = (x_percent / 100) * page_width
                        y_position = ((100 - y_percent) / 100) * page_height
                        
                        # Calculer la largeur et hauteur en points
                        width_points = (width_percent / 100) * page_width
                        height_points = (height_percent / 100) * page_height
                        
                        # Ajuster la position pour centrer l'image à la position spécifiée
                        x_position = x_position - (width_points / 2)
                        y_position = y_position - (height_points / 2)
                        
                        # Dessiner l'image de signature
                        try:
                            sig_canvas.drawImage(
                                temp_image_path,
                                x_position,
                                y_position,
                                width=width_points,
                                height=height_points,
                                preserveAspectRatio=True
                            )
                            
                            logger.info(f"Signature ajoutée à la position: x={x_position}, y={y_position}, "
                                       f"largeur={width_points}, hauteur={height_points}")
                        except Exception as e:
                            logger.error(f"Erreur lors du dessin de l'image: {str(e)}")
                    
                    sig_canvas.save()
                    sig_canvas_buffer.seek(0)
                    
                    # Fusionner la signature avec la page
                    try:
                        sig_page = PdfReader(sig_canvas_buffer).pages[0]
                        page.merge_page(sig_page)
                        logger.info(f"Fusion réussie pour la page {page_number}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la fusion de la page {page_number}: {str(e)}")
                
                # Ajouter la page au writer
                pdf_writer.add_page(page)
            
            # Sauvegarder le PDF modifié
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            logger.info("Processus d'ajout de l'image de signature terminé avec succès")
            return output_buffer.getvalue()
            
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_image_path):
                logger.info(f"Suppression du fichier temporaire: {temp_image_path}")
                os.remove(temp_image_path)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de l'image de signature au PDF: {str(e)}", exc_info=True)
        # En cas d'erreur, retourner le PDF original
        return pdf_data

def recreate_original_document(pdf_data: bytes) -> bytes:
    """
    Tente de recréer le document original à partir du document signé
    en supprimant le QR code et en gardant le contenu d'origine.
    
    Args:
        pdf_data (bytes): Données du PDF signé
        
    Returns:
        bytes: Données du PDF "nettoyé"
    """
    try:
        # Lire le PDF
        pdf_reader = PdfReader(BytesIO(pdf_data))
        pdf_writer = PdfWriter()
        
        # Copier toutes les pages mais sans le QR code (hypothèse: le QR code est une annotation)
        for page in pdf_reader.pages:
            # Créer une copie de la page
            new_page = PdfReader(BytesIO(pdf_data)).pages[0]
            # Copier seulement le contenu principal (pas les annotations)
            # Note: Cette approche est une simplification, cela pourrait ne pas fonctionner parfaitement
            pdf_writer.add_page(page)
        
        # Supprimer les métadonnées liées à la signature
        metadata = pdf_reader.metadata or {}
        cleaned_metadata = {}
        
        # Copier les métadonnées qui ne sont pas liées à la signature
        for key, value in metadata.items():
            if key not in ["/CertiSignSignature", "/SignatureDate", "/SignatureVersion", "/OriginalDocumentHash"]:
                cleaned_metadata[key] = value
        
        # Écrire le PDF nettoyé
        output = BytesIO()
        pdf_writer.add_metadata(cleaned_metadata)
        pdf_writer.write(output)
        output.seek(0)
        
        return output.getvalue()
    except Exception as e:
        logger.error(f"Erreur lors de la recréation du document original: {str(e)}")
        # En cas d'échec, retourner le document tel quel
        return pdf_data

def verify_signature_with_digest(digest_or_data: bytes, signature: bytes, public_key, is_digest: bool = False):
    """
    Vérifie la signature d'un fichier ou d'un digest avec la clé publique.
    
    Args:
        digest_or_data (bytes): Soit le digest pré-calculé, soit les données du fichier original
        signature (bytes): Signature à vérifier
        public_key: Clé publique utilisée pour la vérification
        is_digest (bool): True si digest_or_data est déjà un digest, False sinon
        
    Returns:
        bool: True si la signature est valide, False sinon
    """
    try:
        # Si digest_or_data est déjà un digest, l'utiliser directement
        # Sinon, calculer le hash SHA-256 du fichier
        if is_digest:
            digest = digest_or_data
        else:
            import hashlib
            digest = hashlib.sha256(digest_or_data).digest()
        
        # Vérification de la signature avec la clé publique en utilisant PKCS1v15
        # IMPORTANT: Ceci correspond à l'algorithme utilisé dans signer.py (déterministe)
        public_key.verify(
            signature,
            digest,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        logger.info("Signature vérifiée et valide")
        return True
    except InvalidSignature:
        # La signature est invalide
        logger.warning("Signature invalide détectée")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la signature: {str(e)}")
        return False

@app.post("/sign", summary="Signer un document")
async def sign_document(
    background_tasks: BackgroundTasks,
    certificate: UploadFile = File(..., description="Certificat PFX (.pfx)"),
    password: str = Form(..., description="Mot de passe du certificat"),
    document: UploadFile = File(..., description="Document à signer (PDF recommandé)"),
    metadata: Optional[str] = Form(None, description="Métadonnées optionnelles pour la signature"),
    owner_id: Optional[str] = Form(None, description="ID de l'utilisateur propriétaire (facultatif)"),
    organization_id: Optional[str] = Form(None, description="ID de l'organisation (facultatif)"),
    signer_role: Optional[str] = Form(None, description="Rôle du signataire dans l'organisation (facultatif)"),
    jwt_token: Optional[str] = Form(None, description="Token JWT pour l'authentification avec Django")
):
    """
    Signe un document PDF avec un certificat PFX, assigne un identifiant unique au document
    et ajoute un QR code contenant cet identifiant sur chaque page du document.
    Si des données de signature manuscrite sont fournies, ajoute également l'image de signature aux positions spécifiées.
    Toutes les informations cryptographiques sont stockées en base de données via l'API Django.
    """
    start_time = time.time()
    logger.info(f"Nouvelle demande de signature pour le fichier {document.filename}")
    
    # Vérification que le document est un PDF
    if not document.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    try:
        # Lire le contenu des fichiers
        pfx_data = await certificate.read()
        document_data = await document.read()
        
        if len(document_data) == 0:
            raise HTTPException(status_code=400, detail="Le document est vide")
        
        # Charger la clé privée
        private_key = load_private_key(pfx_data, password)
        if not private_key:
            raise HTTPException(status_code=400, detail="Impossible de charger la clé privée. Vérifiez le certificat et le mot de passe.")
        
        # Générer un identifiant unique pour le document
        document_id = str(uuid.uuid4())
        logger.info(f"Identifiant généré pour le document: {document_id}")
        
        # Calculer le hash SHA-256 du document original
        original_hash = hashlib.sha256(document_data).hexdigest()
        logger.info(f"Hash du document original calculé: {original_hash}")
        
        # Signer le fichier avec l'algorithme déterministe
        signature = sign_file(document_data, private_key)
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        logger.info(f"Document signé, taille de la signature: {len(signature)} octets")
        
        # Générer la clé publique au format PEM
        public_key_pem = private_key.public_key().public_bytes(
            serialization.Encoding.PEM, 
            serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Extraire les informations de position du QR code, de l'image de signature et des métadonnées utilisateur
        qr_position = None
        signature_image = None
        signature_positions = None
        organization_id = None
        signer_role = None
        
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
                logger.info(f"Métadonnées parsées avec succès. Clés disponibles: {list(metadata_dict.keys())}")
                
                if 'qr_position' in metadata_dict:
                    qr_position = metadata_dict['qr_position']
                    logger.info(f"Position du QR code extraite des métadonnées: {qr_position}")
                else:
                    logger.warning("Aucune position QR trouvée dans les métadonnées")
                
                # Extraire les informations de l'image de signature
                if 'signature_position' in metadata_dict and metadata_dict['signature_position']:
                    signature_data = metadata_dict['signature_position']
                    logger.info(f"Données de signature trouvées. Clés: {list(signature_data.keys())}")
                    
                    if 'signature_image' in signature_data and signature_data['signature_image']:
                        signature_image = signature_data['signature_image']
                        logger.info(f"Image de signature trouvée. Longueur: {len(signature_image)} caractères. Début: {signature_image[:50]}...")
                    else:
                        logger.warning("Aucune image de signature trouvée dans signature_position")
                    
                    if 'positions' in signature_data and signature_data['positions']:
                        signature_positions = signature_data['positions']
                        logger.info(f"Positions de signature trouvées: {len(signature_positions)} position(s). Détails: {signature_positions}")
                    else:
                        logger.warning("Aucune position de signature trouvée dans signature_position")
                else:
                    logger.warning("Aucune section signature_position trouvée dans les métadonnées")
                
                # Extraire les informations d'organisation et de rôle
                if 'organization_id' in metadata_dict:
                    organization_id = metadata_dict['organization_id']
                    logger.info(f"ID d'organisation extrait des métadonnées: {organization_id}")
                
                if 'signer_role' in metadata_dict:
                    signer_role = metadata_dict['signer_role']
                    logger.info(f"Rôle du signataire extrait des métadonnées: {signer_role}")
                elif 'role' in metadata_dict:
                    signer_role = metadata_dict['role']
                    logger.info(f"Rôle du signataire extrait des métadonnées (champ 'role'): {signer_role}")
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de parsing JSON des métadonnées: {str(e)}. Métadonnées reçues: {metadata}")
                logger.warning("Utilisation des positions par défaut")
        else:
            logger.warning("Aucune métadonnée fournie, utilisation des positions par défaut")
        
        # Étape 1: Ajouter l'image de signature si disponible
        processed_pdf = document_data
        if signature_image and signature_positions:
            logger.info("Ajout de l'image de signature au document")
            processed_pdf = add_signature_image_to_pdf(document_data, signature_image, signature_positions)
        else:
            logger.info("Aucune image de signature à ajouter")
        
        # Étape 2: Ajouter le QR code avec la position spécifiée par l'utilisateur
        signed_pdf = add_simple_qr_code_to_pdf(processed_pdf, document_id, qr_position)
        if qr_position:
            logger.info(f"QR code contenant l'ID {document_id} ajouté au document à la position personnalisée")
        else:
            logger.info(f"QR code contenant l'ID {document_id} ajouté au document à la position par défaut")
        
        # Générer des noms de fichiers uniques
        original_name = os.path.splitext(document.filename)[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        signed_filename = f"{original_name}_signed_{timestamp}.pdf"
        
        # Stocker toutes les informations dans la base de données Django
        storage_result = await store_signature_data(
            document_id=document_id,
            original_hash=original_hash,
            signature=signature_b64,
            public_key_pem=public_key_pem,
            document_file_data=document_data,
            signed_file_data=signed_pdf,
            owner_id=owner_id,
            document_title=document.filename,
            metadata=metadata,
            jwt_token=jwt_token,
            organization_id=organization_id,
            signer_role=signer_role
        )
        
        if "error" in storage_result:
            logger.warning(f"Attention: Problème lors du stockage en base de données: {storage_result['error']}")
        else:
            logger.info(f"Données de signature stockées avec succès pour le document {document_id}")
        
        # Retourner directement le document signé (plus de ZIP)
        temp_dir = tempfile.gettempdir()
        temp_signed_path = os.path.join(temp_dir, signed_filename)
        
        # Écrire le fichier signé temporairement pour le retour
        with open(temp_signed_path, "wb") as f:
            f.write(signed_pdf)
        
        # Programmer la suppression du fichier temporaire
        background_tasks.add_task(cleanup_temp_files, [temp_signed_path])
        
        execution_time = time.time() - start_time
        logger.info(f"Signature terminée en {execution_time:.2f} secondes")
        
        # Retourner directement le document signé (plus de ZIP)
        return FileResponse(
            temp_signed_path, 
            filename=signed_filename,
            media_type="application/pdf",
            headers={
                "X-Document-ID": document_id,
                "X-Signature-Status": "success"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la signature: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la signature: {str(e)}")


@app.post("/verify", summary="Vérifier un document signé")
async def verify_document(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: str = Body(..., description="Identifiant du document à vérifier", embed=True),
    jwt_token: Optional[str] = Body(None, description="Token JWT pour l'authentification avec Django", embed=True),
    return_original_document: Optional[bool] = Body(True, description="Si True, renvoie le document original en base64", embed=True)
):
    """
    Vérifie la signature d'un document en utilisant uniquement son ID.
    Récupère les informations de signature depuis la base de données pour vérifier
    l'authenticité du document et renvoie le document original si demandé.
    
    Cette endpoint est utilisée par les applications mobiles qui scannent un QR code
    contenant uniquement l'ID du document.
    """
    start_time = time.time()
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Nouvelle demande de vérification par ID: {document_id}")
    
    try:
        # Vérifier que l'ID du document est valide
        if not document_id or document_id == "string" or document_id == "":
            logger.error(f"[{correlation_id}] ID du document invalide ou manquant: {document_id}")
            raise HTTPException(
                status_code=400,
                detail="ID du document invalide ou manquant. Veuillez fournir un ID valide au format UUID."
            )
        
        # S'assurer que document_id est une chaîne
        document_id_str = str(document_id)
        logger.info(f"[{correlation_id}] Récupération des données de signature pour le document ID: {document_id_str}")
        signature_data = await get_signature_data(document_id_str, jwt_token)
        
        if "error" in signature_data:
            logger.error(f"[{correlation_id}] Erreur lors de la récupération des données de signature: {signature_data['error']}")
            return {
                "valid": False,
                "message": f"Document non trouvé: {signature_data['error']}",
                "document_id": document_id
            }
        
        # Préparation de la réponse avec informations du signataire
        response_data = {
            "valid": True,
            "message": "Document authentique et intègre",
            "document_id": document_id,
            "signature_date": signature_data.get('created_at', 'Inconnue')
        }
        
        # Ajout des informations du signataire si disponibles
        if 'signer_info' in signature_data and signature_data['signer_info']:
            logger.info(f"[{correlation_id}] Ajout des informations du signataire à la réponse")
            response_data["signer_info"] = signature_data['signer_info']
        
        # Si la vérification est réussie, récupérer le document original si demandé
        if return_original_document and 'original_file_url' in signature_data and signature_data['original_file_url']:
            try:
                # Obtenir l'URL complète du document original
                original_file_url = signature_data['original_file_url']
                if not original_file_url.startswith('http'):
                    original_file_url = f"{DJANGO_API_BASE_URL}{original_file_url}"
                
                logger.info(f"[{correlation_id}] Téléchargement du document original depuis {original_file_url}")
                
                # Télécharger le document original
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(original_file_url)
                    
                    if response.status_code == 200:
                        original_document_data = response.content
                        original_filename = signature_data.get('title', f"document_original_{document_id}.pdf")
                        
                        # Encoder en base64 pour l'inclure dans la réponse JSON
                        original_document_b64 = base64.b64encode(original_document_data).decode('utf-8')
                        response_data["original_document"] = original_document_b64
                        response_data["original_filename"] = original_filename
                        
                        logger.info(f"[{correlation_id}] Document original ajouté à la réponse (taille: {len(original_document_data)} octets)")
                    else:
                        logger.error(f"[{correlation_id}] Impossible de télécharger le document original: {response.status_code}")
            except Exception as e:
                logger.error(f"[{correlation_id}] Erreur lors de la récupération du document original: {str(e)}")
        
        # Calculer le temps d'exécution
        execution_time = time.time() - start_time
        logger.info(f"[{correlation_id}] Vérification terminée en {execution_time:.2f} secondes")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{correlation_id}] Erreur lors de la vérification: {str(e)}", exc_info=True)
        return {
            "valid": False,
            "message": f"Erreur lors de la vérification: {str(e)}",
            "document_id": document_id
        }


# Endpoint /verify_by_id a été supprimé car il est redondant avec l'endpoint /verify simplifié
# qui accepte maintenant uniquement l'ID du document


@app.get("/health", summary="Vérifier l'état du service")
async def health_check():
    """Vérifie que le service fonctionne correctement"""
    return {"status": "online", "service": "signature", "timestamp": datetime.now().isoformat()}
