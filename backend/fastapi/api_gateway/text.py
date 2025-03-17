from pathlib import Path
import json
from typing import Dict, Any
from cryptography.x509 import Certificate, load_der_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec

def load_der_certificate(file_path: str) -> Certificate:
    """
    Charge un certificat au format DER depuis un fichier.
    
    Args:
        file_path: Chemin vers le fichier certificat
    
    Returns:
        Certificate: L'objet certificat chargé
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si le certificat est invalide
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Le fichier certificat {file_path} n'existe pas")
        
    try:
        with open(file_path, 'rb') as f:
            cert_data = f.read()
        return load_der_x509_certificate(cert_data, default_backend())
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du certificat: {str(e)}")

def display_certificate_info(cert: Certificate) -> str:
    """
    Génère une représentation JSON des informations du certificat.
    
    Args:
        cert: L'objet certificat à analyser
        
    Returns:
        str: Les informations du certificat au format JSON
    """
    try:
        cert_info: Dict[str, Any] = {}

        # Informations principales
        cert_info["Subject"] = str(cert.subject)
        cert_info["Issuer"] = str(cert.issuer)
        cert_info["Serial Number"] = cert.serial_number
        cert_info["Not Valid Before"] = cert.not_valid_before_utc.isoformat()  # Utilisation de not_valid_before_utc
        cert_info["Not Valid After"] = cert.not_valid_after_utc.isoformat()  # Utilisation de not_valid_after_utc
        cert_info["Version"] = cert.version.value  # Conversion de la version en entier

        # Extensions (si présentes)
        extensions = []
        for ext in cert.extensions:
            extensions.append({
                "OID": str(ext.oid),
                "Value": str(ext.value)
            })
        cert_info["Extensions"] = extensions

        # Clé publique
        public_key = cert.public_key()
        public_key_info = {
            "Algorithm": "Unknown",
            "Key Info": {}
        }
        
        if isinstance(public_key, rsa.RSAPublicKey):
            public_key_info.update({
                "Algorithm": "RSA",
                "Key Info": {
                    "Key Size": public_key.key_size,
                    "Public Numbers": public_key.public_numbers().__dict__
                }
            })
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key_info.update({
                "Algorithm": "ECDSA",
                "Key Info": {
                    "Curve": str(public_key.curve),
                    "Public Numbers": public_key.public_numbers().__dict__
                }
            })
            
        cert_info["Public Key"] = public_key_info

        # Empreinte SHA256
        cert_info["SHA256 Fingerprint"] = cert.fingerprint(cert.signature_hash_algorithm).hex()

        return json.dumps(cert_info, indent=4)
    except Exception as e:
        raise ValueError(f"Erreur lors de l'analyse du certificat: {str(e)}")

# Utilisation avec gestion des erreurs
def main():
    CERT_PATH = "/home/markup/Documents/crl/CN=CamRootCA,OU=Cameroon Root Certification Authority,O=ANTIC,C=CM.der"
    
    try:
        certificate = load_der_certificate(CERT_PATH)
        certificate_info_json = display_certificate_info(certificate)
        print(certificate_info_json)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    main()
