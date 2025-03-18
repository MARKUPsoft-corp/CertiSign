import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

def load_private_key(pfx_data: bytes, password: str):
    """Extrait la clé privée d'un certificat PFX."""
    try:
        # Chargement de la clé privée à partir du fichier PFX
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, password.encode(), default_backend()
        )
        return private_key
    except Exception as e:
        raise ValueError("Erreur lors du chargement de la clé privée : " + str(e))

def sign_text_file(file_data: bytes, private_key):
    """Signe un fichier texte avec la clé privée."""
    try:
        # Création de la signature du fichier avec la clé privée
        signature = private_key.sign(
            file_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature
    except Exception as e:
        raise ValueError("Erreur lors de la signature : " + str(e))

def load_public_key(pfx_data: bytes, password: str):
    """Charge la clé publique à partir d'un certificat PFX."""
    try:
        # Chargement de la clé publique à partir du fichier PFX
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pfx_data, password.encode(), default_backend()
        )
        return certificate.public_key()
    except Exception as e:
        raise ValueError("Erreur lors du chargement de la clé publique : " + str(e))

def verify_signature(file_data: bytes, signature: bytes, public_key):
    """Vérifie la signature d'un fichier avec la clé publique."""
    try:
        # Vérification de la signature avec la clé publique
        public_key.verify(
            signature,
            file_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        # La signature est invalide
        return False
    except Exception as e:
        raise ValueError("Erreur lors de la vérification de la signature : " + str(e))
