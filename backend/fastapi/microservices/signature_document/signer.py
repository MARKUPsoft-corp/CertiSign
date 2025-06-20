import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import hashlib
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_private_key(pfx_data: bytes, password: str):
    """
    Extrait la clé privée d'un certificat PFX.
    
    Args:
        pfx_data (bytes): Données du certificat PFX
        password (str): Mot de passe du certificat
        
    Returns:
        La clé privée ou None en cas d'erreur
    """
    try:
        # Chargement de la clé privée à partir du fichier PFX
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, password.encode(), default_backend()
        )
        logger.info(f"Clé privée chargée avec succès: {certificate.subject}")
        return private_key
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la clé privée: {str(e)}")
        return None

def sign_file(file_data: bytes, private_key):
    """
    Signe un fichier (PDF ou autre) avec la clé privée en utilisant un algorithme déterministe.
    
    Args:
        file_data (bytes): Données du fichier à signer
        private_key: Clé privée utilisée pour la signature
        
    Returns:
        bytes: Signature du fichier
    """
    try:
        # Création d'un hash SHA-256 du fichier pour optimiser la signature
        # (plus efficace que de signer directement un gros fichier PDF)
        digest = hashlib.sha256(file_data).digest()
        
        # Création de la signature déterministe (PKCS#1 v1.5) du hash avec la clé privée
        # Cette méthode est déterministe contrairement à PSS avec salt aléatoire
        signature = private_key.sign(
            digest,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        logger.info(f"Fichier signé avec succès, taille de la signature: {len(signature)} octets")
        return signature
    except Exception as e:
        logger.error(f"Erreur lors de la signature: {str(e)}")
        raise ValueError(f"Erreur lors de la signature: {str(e)}")

def load_public_key(pfx_data: bytes, password: str):
    """
    Charge la clé publique à partir d'un certificat PFX.
    
    Args:
        pfx_data (bytes): Données du certificat PFX
        password (str): Mot de passe du certificat
        
    Returns:
        La clé publique ou None en cas d'erreur
    """
    try:
        # Chargement de la clé publique à partir du fichier PFX
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, password.encode(), default_backend()
        )
        logger.info(f"Clé publique chargée avec succès: {certificate.subject}")
        return certificate.public_key()
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la clé publique: {str(e)}")
        return None

def verify_signature(file_data: bytes, signature: bytes, public_key):
    """
    Vérifie la signature d'un fichier avec la clé publique en utilisant un algorithme déterministe.
    
    Args:
        file_data (bytes): Données du fichier original
        signature (bytes): Signature à vérifier
        public_key: Clé publique utilisée pour la vérification
        
    Returns:
        bool: True si la signature est valide, False sinon
    """
    try:
        # Calcul du hash SHA-256 du fichier
        digest = hashlib.sha256(file_data).digest()
        
        # Vérification de la signature avec la clé publique en utilisant PKCS#1 v1.5
        # Cette méthode est déterministe, correspondant à la méthode de signature
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

# Pour maintenir la compatibilité avec l'ancien code
sign_text_file = sign_file
