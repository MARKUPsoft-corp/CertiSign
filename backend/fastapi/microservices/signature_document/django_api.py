"""
Module pour la communication avec l'API Django.
"""
import base64
import httpx
import logging
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration du logging avec niveau DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ajouter un handler qui affiche les logs dans la sortie standard
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# URL de base de l'API Django (peut être configurée par variable d'environnement)
# Utiliser directement l'URL complète sans passer par les routes API
DJANGO_API_BASE_URL = os.environ.get("DJANGO_API_URL", "https://192.168.4.131:8000") 

# Clé API simple pour l'authentification entre services
# Doit correspondre à la clé configurée dans le backend Django
MICROSERVICE_API_KEY = os.environ.get("MICROSERVICE_API_KEY", "certisign_microservice_key_2025")

# Credentials pour l'authentification JWT (maintenu pour compatibilité)
ADMIN_USERNAME = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("DJANGO_ADMIN_PASSWORD", "admin123")

# Cache pour le token JWT
_jwt_token_cache = None
_token_expiry = None

async def get_jwt_token() -> str:
    """
    Obtient un token JWT en authentifiant le microservice auprès de l'API Django.
    Réutilise le token mis en cache s'il est toujours valide.
    
    Returns:
        str: Token JWT valide
    """
    global _jwt_token_cache, _token_expiry
    
    # Vérifier si nous avons un token en cache qui est toujours valide
    now = datetime.now()
    if _jwt_token_cache and _token_expiry and _token_expiry > now:
        logger.debug("Utilisation du token JWT en cache")
        return _jwt_token_cache
    
    # Préparer les données d'authentification
    auth_url = f"{DJANGO_API_BASE_URL}/api/users/token/"
    
    # Afficher les informations d'identification pour le débogage
    logger.debug(f"Tentative d'authentification avec username={ADMIN_USERNAME}")
    
    auth_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    try:
        logger.debug(f"Authentification auprès de l'API Django: {auth_url}")
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.post(auth_url, data=auth_data)  # Utiliser data au lieu de json
            
            # Afficher la réponse complète pour le débogage
            logger.debug(f"Réponse d'authentification: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                _jwt_token_cache = token_data.get("access")
                
                if not _jwt_token_cache:
                    logger.error(f"Le token d'accès n'a pas été trouvé dans la réponse: {token_data}")
                    raise Exception("Token d'accès non trouvé dans la réponse")
                
                # Définir une expiration du token (15 minutes)
                _token_expiry = now + timedelta(minutes=15)
                
                logger.info("Token JWT obtenu avec succès")
                return _jwt_token_cache
            else:
                logger.error(f"Erreur d'authentification: {response.status_code} - {response.text}")
                raise Exception(f"Erreur d'authentification: {response.status_code}")
    except Exception as e:
        logger.error(f"Exception lors de l'authentification: {str(e)}")
        raise

async def store_signature_data(
    document_id: str,
    original_hash: str,
    signature: str,
    public_key_pem: str,
    document_file_data: bytes,
    signed_file_data: bytes,
    owner_id: Optional[str] = None,
    document_title: Optional[str] = None,
    metadata: Optional[str] = None,
    jwt_token: Optional[str] = None,
    organization_id: Optional[str] = None,
    signer_role: Optional[str] = None
) -> Dict[str, Any]:
    """
    Stocke les données de signature dans la base de données Django.
    
    Args:
        document_id (str): Identifiant unique du document
        original_hash (str): Hash du document original
        signature (str): Signature en base64
        public_key_pem (str): Clé publique PEM utilisée pour signer
        document_file_data (bytes): Contenu du document original
        signed_file_data (bytes): Contenu du document signé
        owner_id (str, optional): ID de l'utilisateur propriétaire
        document_title (str, optional): Titre du document
        jwt_token (str, optional): Token JWT pour l'authentification
        
    Returns:
        Dict[str, Any]: Réponse de l'API Django ou message d'erreur
    """
    # Utiliser la route publique spéciale au niveau du projet qui contourne les middleware d'authentification
    url = f"{DJANGO_API_BASE_URL}/api/public/store_signature/?api_key={MICROSERVICE_API_KEY}"
    logger.info(f"URL pour stocker la signature (route publique spéciale): {url}")
    
    try:
        # Utiliser des en-têtes minimaux pour éviter tout conflit avec le middleware d'authentification
        headers = {}
        
        # Nous avons déjà inclus la clé API comme paramètre de requête
        logger.info(f"Clé API utilisée (en paramètre URL): {MICROSERVICE_API_KEY}")
        
        # Ne pas inclure d'en-tête Authorization pour éviter toute tentative d'authentification JWT
        
        # Préparer les données multipart
        files = {
            "original_file": ("original.pdf", document_file_data, "application/pdf"),
            "signed_file": ("signed.pdf", signed_file_data, "application/pdf")
        }
        
        # Ajouter des informations de débogage sur les fichiers
        logger.debug(f"Fichier original: taille={len(document_file_data)} octets")
        logger.debug(f"Fichier signé: taille={len(signed_file_data)} octets")
        
        data = {
            "document_id": document_id,
            "original_hash": original_hash,
            "signature": signature,
            "public_key_pem": public_key_pem
        }
        
        # Ajouter les métadonnées utilisateur si disponibles
        if metadata:
            try:
                # Si les métadonnées sont une chaîne JSON, les convertir en dictionnaire
                if isinstance(metadata, str):
                    user_data = json.loads(metadata)
                    data["user_metadata"] = metadata
                    # Si les métadonnées contiennent un ID utilisateur et qu'aucun owner_id n'est fourni,
                    # utiliser l'ID utilisateur des métadonnées
                    if 'user_id' in user_data and not owner_id:
                        data["owner_id"] = user_data['user_id']
                        logger.debug(f"ID utilisateur extrait des métadonnées: {user_data['user_id']}")
            except Exception as e:
                logger.warning(f"Erreur lors du traitement des métadonnées utilisateur: {str(e)}")
                # Ne pas échouer complètement si les métadonnées sont mal formatées
        
        # N'envoyer l'owner_id que s'il s'agit d'une valeur valide (pas "string")
        if owner_id and owner_id != "string":
            data["owner_id"] = owner_id
            logger.debug(f"Propriétaire du document: {owner_id}")
        else:
            logger.debug("Aucun propriétaire spécifié ou valeur invalide")
        
        # Ajouter l'organization_id si fourni
        if organization_id and organization_id != "string":
            data["organization_id"] = organization_id
            logger.debug(f"Organisation du document: {organization_id}")
        
        # Ajouter le rôle du signataire si fourni
        if signer_role:
            data["signer_role"] = signer_role
            logger.debug(f"Rôle du signataire: {signer_role}")
        
        if document_title:
            data["title"] = document_title
            logger.debug(f"Titre du document: {document_title}")
        
        # Débugger les données envoyées
        logger.debug(f"En-têtes: {headers}")
        logger.debug(f"Données: document_id={document_id}, hash={original_hash}, taille signature={len(signature)}, titre={document_title}")
        
        # Faire la requête à l'API Django
        logger.info(f"Envoi des données de signature à l'API Django pour le document {document_id}")
        try:
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.post(url, files=files, data=data, headers=headers)
                
                # Débugger la réponse complète
                logger.debug(f"Statut de la réponse: {response.status_code}")
                logger.debug(f"Corps de la réponse: {response.text}")
                logger.debug(f"En-têtes de réponse: {response.headers}")
                
                # Vérifier la réponse
                if response.status_code == 201:
                    logger.info(f"Données de signature stockées avec succès pour le document {document_id}")
                    return response.json()
                else:
                    logger.error(f"Erreur lors du stockage des données de signature: {response.status_code} - {response.text}")
                    return {"error": f"Erreur {response.status_code}: {response.text}"}
        except Exception as e:
            error_msg = f"Exception lors de la communication avec Django: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
            
    except Exception as e:
        error_msg = f"Exception lors du stockage des données de signature: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

async def get_signature_data(document_id: str, jwt_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Récupère les données de signature depuis la base de données Django.
    Utilise l'endpoint public spécial pour éviter les problèmes d'authentification JWT.
    
    Args:
        document_id (str): Identifiant unique du document
        jwt_token (str, optional): Token JWT pour l'authentification (non utilisé avec l'endpoint public)
        
    Returns:
        Dict[str, Any]: Données de signature ou message d'erreur
    """
    # Vérifier que document_id est bien spécifié et n'est pas "string"
    if not document_id or document_id == "string":
        error_msg = f"ID de document invalide ou manquant: {document_id}"
        logger.error(error_msg)
        return {"error": error_msg}
    
    # Nettoyer l'ID du document (supprimer les espaces blancs)
    document_id = document_id.strip()
    logger.info(f"ID du document nettoyé: '{document_id}'")
        
    # Utiliser l'endpoint public avec authentification par clé API
    url = f"{DJANGO_API_BASE_URL}/api/public/get_signature/?api_key={MICROSERVICE_API_KEY}&document_id={document_id}"
    
    logger.info(f"URL pour récupérer la signature (route publique spéciale): {url}")
    logger.info(f"Clé API utilisée (en paramètre URL): {MICROSERVICE_API_KEY}")
    
    try:
        # Pas besoin d'en-têtes d'autorisation car nous utilisons la clé API dans l'URL
        headers = {}
            
        # Faire la requête à l'API Django
        logger.info(f"Récupération des données de signature pour le document {document_id}")
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(url, headers=headers)
            
        # Vérifier la réponse
        if response.status_code == 200:
            logger.info(f"Données de signature récupérées avec succès pour le document {document_id}")
            return response.json()
        else:
            logger.error(f"Erreur lors de la récupération des données de signature: {response.status_code} - {response.text}")
            return {"error": f"Erreur {response.status_code}: {response.text}"}
            
    except Exception as e:
        error_msg = f"Exception lors de la récupération des données de signature: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
