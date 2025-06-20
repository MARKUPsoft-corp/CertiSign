from fastapi import FastAPI, HTTPException, Request, Response, File, Form, UploadFile  # Importation des classes et fonctions nécessaires de FastAPI
import httpx  # Plus précis que d'importer tout httpx
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
import logging
import uuid  # Importation de uuid pour générer des identifiants de corrélation uniques
import base64  # Pour encoder/décoder en base64
import os  # Pour générer des valeurs aléatoires
import json  # Pour manipuler les données JSON
from cryptography.hazmat.primitives.asymmetric import ec  # Utilisation de l'ECDH au lieu de DH
from cryptography.hazmat.primitives import hashes  # Pour les fonctions de hachage
from cryptography.hazmat.primitives.kdf.hkdf import HKDF  # Pour dériver la clé de session
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_public_key  # Pour sérialiser/désérialiser les clés
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # Pour le chiffrement symétrique
from cryptography.hazmat.backends import default_backend  # Pour le backend cryptographique
from typing import Optional
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import io
from PIL import Image

# Configuration du logger pour l'API Gateway
logger = logging.getLogger("api_gateway")  # Création d'un logger nommé "api_gateway"
logger.setLevel(logging.INFO)  # Définition du niveau de log à INFO

# Création d'une instance de l'application FastAPI
app = FastAPI()  # Initialisation de l'application FastAPI

# Configuration du middleware CORS pour autoriser les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,  # Middleware pour gérer le Cross-Origin Resource Sharing
    allow_origins=["*"],  # Autorise toutes les origines en développement
    allow_credentials=True,  # Autorise l'envoi des credentials (cookies, authentification)
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Autorise tous les en-têtes
)

# Configuration du rate limiting avec slowapi
# Ici, on limite les requêtes par adresse IP du client (extrait de request.client.host)
limiter = Limiter(key_func=lambda request: request.client.host)

# Lors du démarrage de l'application, on stocke le limiteur dans l'état de l'application
@app.on_event("startup")
async def startup():
    app.state.limiter = limiter  # Ajoute le limiteur à l'état global de l'application
    app.state.client_sessions = {}  # Initialisation du dictionnaire pour stocker les sessions des clients

# Gestionnaire d'exception pour les erreurs de dépassement de rate limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_error(request: Request, exc: RateLimitExceeded):
    # Renvoie une réponse JSON avec le code 429 (Too Many Requests)
    return JSONResponse(
        status_code=429,  # Code HTTPs 429
        content={"detail": "Rate limit exceeded. Try again later."},  # Message d'erreur
    )

# Dictionnaire des microservices disponibles avec leurs URL de base
MICROSERVICES = {
    # URLs des microservices configurées avec 192.168.4.131
    # Comme nous utilisons le tunnel adb, tout reste sur la même machine
    "cert_info": "https://192.168.4.131:8002/extract-cert-info/",  # URL du microservice de traitement des certificats (form data)
    "cert_info_base64": "https://192.168.4.131:8002/extract-cert-info-base64/",  # URL du microservice de traitement des certificats (base64/JSON)
    "sign": "https://192.168.4.131:8003/sign",  # URL du microservice de signature
    "verify": "https://192.168.4.131:8003/verify",  # URL du microservice de vérification - Maintenant accepte seulement l'ID du document
    "sign/health": "https://192.168.4.131:8003/health"  # URL pour vérifier l'état du microservice de signature
}

# Dictionnaire pour stocker les clés de session par identifiant client
# Note: Ce dictionnaire est seulement défini pour compatibilité, mais n'est plus utilisé
# Utilisation de app.state.client_sessions à la place

# Fonction pour chiffrer un message avec la clé de session
def encrypt_message(message: bytes, session_key: bytes, client_id: str) -> dict:
    """
    Chiffre un message avec la clé de session en utilisant AES-GCM.
    Retourne un dictionnaire contenant l'IV et le texte chiffré.
    """
    try:
        # Générer un vecteur d'initialisation (IV) aléatoire
        iv = os.urandom(12)  # Pour GCM, IV doit être de 12 octets
        
        # Créer le chiffreur avec la clé de session et l'IV
        cipher = Cipher(algorithms.AES(session_key[:32]), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Chiffrer le message
        encrypted_message = encryptor.update(message) + encryptor.finalize()
        
        # Récupérer le tag d'authentification
        tag = encryptor.tag
        
        # Concaténer le message chiffré et le tag
        encrypted_with_tag = encrypted_message + tag
        
        return {
            "iv": base64.b64encode(iv).decode('utf-8'),
            "encrypted_data": base64.b64encode(encrypted_with_tag).decode('utf-8'),
            "client_id": client_id
        }
    except Exception as e:
        logger.error(f"Erreur lors du chiffrement: {e}")
        return None

# Fonction pour déchiffrer un message avec la clé de session
def decrypt_message(encrypted_data: str, iv: str, session_key: bytes) -> bytes:
    """
    Déchiffre un message avec la clé de session en utilisant AES-GCM.
    """
    try:
        # Décoder l'IV et le message chiffré
        iv_bytes = base64.b64decode(iv)
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Les 16 derniers octets sont le tag d'authentification
        encrypted_message = encrypted_bytes[:-16]
        tag = encrypted_bytes[-16:]
        
        # Créer le déchiffreur avec la clé de session, l'IV et le tag
        cipher = Cipher(algorithms.AES(session_key[:32]), modes.GCM(iv_bytes, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Déchiffrer le message
        decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
        
        return decrypted_message
    except Exception as e:
        logger.error(f"Erreur lors du déchiffrement: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur lors du déchiffrement: {str(e)}")

# Endpoint pour l'échange de clés ECDH
@app.post("/dh-exchange/")
async def dh_exchange(request: Request):
    """
    Endpoint pour l'échange de clés ECDH.
    Le client envoie sa clé publique et reçoit la clé publique du serveur.
    """
    # Générer un identifiant de corrélation pour cette requête
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Début de l'échange de clés ECDH")
    try:
        data = await request.json()
        client_id = data.get("client_id")
        # Accepter soit "client_public_key" soit "public_key" pour assurer la compatibilité
        client_public_key_pem = data.get("public_key") or data.get("client_public_key")
        
        if not client_id or not client_public_key_pem:
            raise HTTPException(status_code=400, detail="Client ID et clé publique requis")
        
        # Log pour le debug
        logger.info(f"Échange de clés demandé par le client {client_id}")
        logger.info(f"Clé publique reçue: {client_public_key_pem[:50]}...")
        
        # Charger la clé publique du client (qui doit être de type ECPublicKey)
        client_public_key = load_pem_public_key(client_public_key_pem.encode(), backend=default_backend())
        
        # Générer une paire de clés pour le serveur en ECDH (utilisation de la courbe SECP256R1)
        server_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        server_public_key = server_private_key.public_key()
        
        # Calculer la clé de session partagée via ECDH
        shared_key = server_private_key.exchange(ec.ECDH(), client_public_key)
        
        # Dériver une clé symétrique à partir de la clé partagée
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(shared_key)
        
        # Stocker la clé de session dans l'état global de l'application
        app.state.client_sessions[client_id] = derived_key
        
        # Journaliser l'état des sessions
        logger.info(f"[{correlation_id}] Clé de session créée pour le client {client_id}")
        logger.info(f"[{correlation_id}] Nombre de sessions actives: {len(app.state.client_sessions)}")
        logger.info(f"[{correlation_id}] Clients actifs: {list(app.state.client_sessions.keys())}")
        
        # Sérialiser la clé publique du serveur pour l'envoyer au client
        server_public_key_pem = server_public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        logger.info(f"Échange de clés ECDH réussi pour le client {client_id}")
        
        return {
            "public_key": server_public_key_pem,
            "server_public_key": server_public_key_pem  # Garder les deux noms pour la compatibilité
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de l'échange de clés ECDH: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'échange de clés: {str(e)}")

# Endpoint non chiffré pour l'authentification par certificat (pour déboguer)
@app.post("/unencrypted/auth/certificate/")
@limiter.limit("5/minute")
async def unencrypted_authenticate_with_certificate(request: Request):
    """
    Endpoint non chiffré pour l'authentification par certificat.
    Utilisé uniquement pour le débogage.
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Demande d'authentification non chiffrée par certificat reçue")
    
    try:
        # Récupérer les données directement (sans déchiffrement)
        auth_data = await request.json()
        logger.info(f"[{correlation_id}] Données reçues: {auth_data.keys()}")
        
        # Vérifier que toutes les données nécessaires sont présentes
        if "certificate" not in auth_data or "password" not in auth_data:
            raise HTTPException(status_code=400, detail="Données d'authentification incomplètes")
        
        # Envoyer le certificat au microservice d'extraction
        logger.info(f"[{correlation_id}] Envoi du certificat au microservice d'extraction")
        async with httpx.AsyncClient() as client:
            extract_response = await client.post(
                MICROSERVICES["cert_info_base64"],
                json={
                    "certificate_base64": auth_data["certificate"],
                    "password": auth_data["password"]
                }
            )
            
            if extract_response.status_code != 200:
                logger.error(f"[{correlation_id}] Erreur du microservice d'extraction: {extract_response.text}")
                raise HTTPException(
                    status_code=extract_response.status_code,
                    detail="Erreur lors de l'extraction des informations du certificat"
                )
            
            # Récupérer les informations du certificat
            cert_info = extract_response.json()
            logger.info(f"[{correlation_id}] Informations du certificat extraites avec succès")
            
            # Envoyer les informations du certificat à Django pour vérification/création du compte
            logger.info(f"[{correlation_id}] Envoi des informations à Django pour vérification/création")
            django_data = {
                "certificate_info": cert_info,
                "role": auth_data.get("role", "user"),
                "filename": auth_data.get("filename", "certificate.pfx")
            }
            
            # URL de l'API Django pour la vérification/création d'utilisateur
            django_url = "https://192.168.4.131:8000/api/users/auth-certificate/"
            
            django_response = await client.post(
                django_url,
                json=django_data,
                headers={"Content-Type": "application/json"}
            )
            
            if django_response.status_code not in [200, 201]:
                logger.error(f"[{correlation_id}] Erreur de Django: {django_response.text}")
                raise HTTPException(
                    status_code=django_response.status_code,
                    detail="Erreur lors de la vérification/création du compte"
                )
            
            # Récupérer la réponse de Django
            user_data = django_response.json()
            logger.info(f"[{correlation_id}] Authentification réussie avec statut: {user_data.get('status')}")
            logger.info(f"[{correlation_id}] Contenu complet de la réponse Django: {user_data}")
            
            # Vérifier que le status est présent et correctement formaté
            if 'status' not in user_data:
                logger.error(f"[{correlation_id}] Le statut est manquant dans la réponse Django!")
                user_data['status'] = 'pending'  # Par défaut en cas de problème
            
            # S'assurer que le message est présent
            if 'message' not in user_data and user_data.get('status') == 'pending':
                user_data['message'] = 'Votre compte a été créé et est en attente de validation par un administrateur.'
            
            # Renvoyer les données directement (sans chiffrement)
            logger.info(f"[{correlation_id}] Réponse finale envoyée au frontend: {user_data}")
            return JSONResponse(content=user_data)
    
    except HTTPException as e:
        # Relancer les exceptions HTTP
        raise e
    except Exception as e:
        # Journaliser les erreurs inattendues
        logger.error(f"[{correlation_id}] Erreur inattendue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur du serveur: {str(e)}")

# Endpoint pour vérifier si un utilisateur existe
@app.get("/user-exists/{username}")
async def user_exists(username: str):
    """
    Vérifie si un utilisateur existe déjà dans le système.
    Pour l'instant, cette fonction renvoie simplement un statut fictif.
    Dans une implémentation réelle, vous devriez vérifier dans votre base de données Django.
    """
    try:
        # Simulation d'une vérification dans la base de données
        # Dans une implémentation réelle, vous feriez une requête à votre API Django
        # ou directement à votre base de données
        
        # Pour les besoins de la démonstration, nous supposons que l'utilisateur 'admin' existe
        if username.lower() == 'admin':
            return {"exists": True, "is_admin": True}
        
        # Simulons que certains utilisateurs standard existent déjà
        if username.lower() in ['jean.dupont', 'marie.martin', 'pierre.durand', 'alice.petit']:
            return {"exists": True, "is_admin": False}
            
        # Par défaut, supposons que l'utilisateur n'existe pas encore
        return {"exists": False}
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'existence de l'utilisateur: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

# Route générique modifiée pour prendre en charge le chiffrement
@app.api_route("/gateway/{service_name}/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@limiter.limit("5/minute")  # Limite à 5 requêtes par minute par adresse IP
async def gateway(service_name: str, request: Request):
    # Génération d'un identifiant de corrélation unique pour suivre la requête dans les logs
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Requête {request.method} reçue pour le service: {service_name}")

    # Vérification que le service demandé existe dans la liste des microservices
    if service_name not in MICROSERVICES:
        logger.error(f"[{correlation_id}] Service non trouvé: {service_name}")
        raise HTTPException(status_code=404, detail="Service non trouvé")  # Retourne une erreur 404 si le service n'existe pas

    # Récupération de l'URL du microservice correspondant
    service_url = MICROSERVICES[service_name]
    logger.info(f"[{correlation_id}] Service URL: {service_url}")

    # Pour les méthodes susceptibles d'avoir un corps (POST, PUT, PATCH), on vérifie la taille du corps
    if request.method not in ("GET", "DELETE"):
        body = await request.body()  # Récupère le corps brut de la requête
        body_size = len(body)
        logger.info(f"[{correlation_id}] Taille du corps: {body_size} octets")
        max_body_size = 20 * 1024 * 1024  # Limite maximale augmentée à 20 Mo
        if body_size > max_body_size:
            logger.error(f"[{correlation_id}] Taille du corps trop grande: {body_size} octets")
            raise HTTPException(status_code=413, detail="Request payload too large")  # Erreur 413 si la taille dépasse la limite
    else:
        body = None  # Pour GET et DELETE, aucun corps n'est traité

    # Définition du timeout pour les requêtes vers les microservices
    timeout = 30.0  # Timeout augmenté à 30 secondes

    # Préparation des en-têtes à transmettre (conversion en dictionnaire)
    headers = dict(request.headers)
    logger.info(f"[{correlation_id}] En-têtes: {headers}")

    # Utilisation d'un client HTTP asynchrone pour effectuer la requête vers le microservice
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # Vérifier si la requête est chiffrée (contient un en-tête spécifique)
            content_type = headers.get("content-type", "")
            logger.info(f"[{correlation_id}] Content-Type: {content_type}")
            is_encrypted = "application/encrypted+json" in content_type
            
            if is_encrypted and request.method == "POST":
                logger.info(f"[{correlation_id}] Traitement d'une requête chiffrée")
                try:
                    # Récupérer les données chiffrées
                    encrypted_data = await request.json()
                    logger.info(f"[{correlation_id}] Données chiffrées reçues: {encrypted_data.keys()}")
                    
                    client_id = encrypted_data.get("client_id")
                    iv = encrypted_data.get("iv")
                    encrypted_content = encrypted_data.get("encrypted_data")
                    
                    if not client_id or not iv or not encrypted_content:
                        logger.error(f"[{correlation_id}] Données chiffrées mal formatées")
                        raise HTTPException(status_code=400, detail="Données chiffrées mal formatées")
                    
                    # Récupérer la clé de session depuis l'état global de l'application
                    session_key = app.state.client_sessions.get(client_id)
                    if not session_key:
                        logger.error(f"[{correlation_id}] Session non trouvée pour le client: {client_id}")
                        raise HTTPException(status_code=401, detail="Session non trouvée ou expirée")
                    
                    # Déchiffrer les données
                    logger.info(f"[{correlation_id}] Déchiffrement des données...")
                    decrypted_data = decrypt_message(encrypted_content, iv, session_key)
                    
                    # Vérifier que les données déchiffrées sont valides
                    if not decrypted_data:
                        logger.error(f"[{correlation_id}] Échec du déchiffrement des données")
                        raise HTTPException(status_code=400, detail="Échec du déchiffrement des données")
                    
                    # Log des 100 premiers caractères des données déchiffrées pour debug
                    logger.info(f"[{correlation_id}] Données déchiffrées (début): {decrypted_data[:100] if isinstance(decrypted_data, bytes) else 'Non bytes'}")
                    
                    # Extraire et analyser les données du formulaire
                    try:
                        # S'assurer que decrypted_data est un objet bytes
                        if not isinstance(decrypted_data, bytes):
                            logger.error(f"[{correlation_id}] Les données déchiffrées ne sont pas au format bytes: {type(decrypted_data)}")
                            raise HTTPException(status_code=400, detail="Format des données déchiffrées invalide")
                        
                        # Convertir les bytes en chaîne UTF-8
                        decrypted_str = decrypted_data.decode('utf-8')
                        logger.info(f"[{correlation_id}] Conversion des données déchiffrées en chaîne UTF-8 réussie")
                        
                        # Analyser la chaîne JSON
                        json_data = json.loads(decrypted_str)
                        logger.info(f"[{correlation_id}] Analyse JSON réussie: {list(json_data.keys())}")
                        
                        form_data = json_data.get("formData")
                        file_base64 = json_data.get("fileBase64")
                        
                        if not form_data or not file_base64:
                            logger.error(f"[{correlation_id}] Données de formulaire invalides: formData={bool(form_data)}, fileBase64={bool(file_base64)}")
                            raise HTTPException(status_code=400, detail="Données de formulaire invalides")
                        
                        # Préparer les données pour le microservice
                        form_data_obj = json.loads(form_data)
                        password = form_data_obj.get("password")
                        filename = form_data_obj.get("filename")
                        
                        if not password or not filename:
                            logger.error(f"[{correlation_id}] Mot de passe ou nom de fichier manquant: password={bool(password)}, filename={bool(filename)}")
                            raise HTTPException(status_code=400, detail="Mot de passe ou nom de fichier manquant")
                        
                        logger.info(f"[{correlation_id}] Extraction des données réussie: fichier={filename}, taille_mot_de_passe={len(password)}")
                        
                        # Décodage du fichier base64
                        try:
                            file_bytes = base64.b64decode(file_base64)
                            logger.info(f"[{correlation_id}] Décodage du fichier base64 réussi: taille={len(file_bytes)} octets")
                        except Exception as e:
                            logger.error(f"[{correlation_id}] Erreur lors du décodage base64 du fichier: {e}")
                            raise HTTPException(status_code=400, detail=f"Erreur lors du décodage base64 du fichier: {e}")
                        
                        # Préparer les données à envoyer au microservice
                        import aiohttp
                        form = aiohttp.FormData()
                        form.add_field('file', file_bytes, filename=filename, content_type='application/octet-stream')
                        form.add_field('password', password)
                        
                        # Transmettre les données au microservice
                        logger.info(f"[{correlation_id}] Envoi des données au microservice: {service_url}")
                        
                        # Utiliser aiohttp pour l'envoi de fichiers multipart/form-data
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.post(service_url, data=form, timeout=timeout) as response:
                                    response_data = await response.read()
                                    response_status = response.status
                                    
                                    logger.info(f"[{correlation_id}] Réponse reçue du microservice avec statut: {response_status}")
                                    logger.info(f"[{correlation_id}] Début de la réponse: {response_data[:100] if len(response_data) > 100 else response_data}")
                                    
                                    if response_status != 200:
                                        logger.error(f"[{correlation_id}] Erreur du microservice: {response_status}, {response_data.decode('utf-8', errors='ignore')}")
                                    else:
                                        # Essayer de parser la réponse pour extraire les informations du certificat
                                        try:
                                            cert_info = json.loads(response_data)
                                            # Si le certificat est valide, essayer de créer ou récupérer l'utilisateur
                                            if cert_info.get("status") != "expiré" and cert_info.get("revocation_status_crl") != "révoqué":
                                                # Extraire les informations d'identité du sujet du certificat
                                                subject = cert_info.get("subject", "")
                                                # Typiquement, le sujet contient des valeurs comme CN=Nom Prénom,O=Organisation,C=Pays
                                                cn_match = None
                                                for part in subject.split(','):
                                                    if part.strip().startswith('CN='):
                                                        cn_match = part.strip()[3:]  # Extraire la valeur après "CN="
                                                        break
                                                
                                                if cn_match:
                                                    # Appeler le microservice Django pour créer ou récupérer l'utilisateur
                                                    try:
                                                        # On pourrait appeler un endpoint Django ici, mais pour simplifier, on va inclure
                                                        # les informations d'utilisateur dans la réponse
                                                        user_info = {
                                                            "username": cn_match.lower().replace(' ', '.'),
                                                            "full_name": cn_match,
                                                            "organization": next((part.strip()[2:] for part in subject.split(',') if part.strip().startswith('O=')), ""),
                                                            "country": next((part.strip()[2:] for part in subject.split(',') if part.strip().startswith('C=')), ""),
                                                            "is_valid": True,
                                                            "user_created": True
                                                        }
                                                        # Ajouter ces informations à la réponse du certificat
                                                        cert_info["user_info"] = user_info
                                                        response_data = json.dumps(cert_info).encode('utf-8')
                                                        logger.info(f"[{correlation_id}] Informations d'utilisateur ajoutées à la réponse: {user_info}")
                                                    except Exception as e:
                                                        logger.error(f"[{correlation_id}] Erreur lors du traitement des informations d'utilisateur: {e}")
                                        except json.JSONDecodeError:
                                            logger.error(f"[{correlation_id}] La réponse du microservice n'est pas un JSON valide")
                                        
                                        # Chiffrer la réponse
                                        encrypted_response = encrypt_message(response_data, session_key, client_id)
                                        
                                        if not encrypted_response:
                                            logger.error(f"[{correlation_id}] Échec du chiffrement de la réponse")
                                            raise HTTPException(status_code=500, detail="Échec du chiffrement de la réponse")
                                        
                                        # Renvoyer la réponse chiffrée
                                        return JSONResponse(content=encrypted_response, status_code=response_status)
                        except aiohttp.ClientError as e:
                            logger.error(f"[{correlation_id}] Erreur lors de la communication avec le microservice: {e}")
                            raise HTTPException(status_code=500, detail=f"Erreur lors de la communication avec le microservice: {e}")
                        except Exception as e:
                            logger.error(f"[{correlation_id}] Erreur inattendue lors de la communication avec le microservice: {e}")
                            raise HTTPException(status_code=500, detail=f"Erreur inattendue: {e}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"[{correlation_id}] Erreur lors du décodage JSON: {e}")
                        # Log des données qui ont causé l'erreur
                        if isinstance(decrypted_data, bytes):
                            logger.error(f"[{correlation_id}] Contenu qui a causé l'erreur: {decrypted_data[:200].decode('utf-8', errors='ignore')}")
                        raise HTTPException(status_code=400, detail=f"Erreur lors du décodage JSON: {e}")
                    
                    except Exception as e:
                        logger.error(f"[{correlation_id}] Erreur lors du traitement des données déchiffrées: {e}, type: {type(e)}")
                        import traceback
                        logger.error(f"[{correlation_id}] Traceback: {traceback.format_exc()}")
                        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement des données déchiffrées: {e}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"[{correlation_id}] Erreur lors du décodage JSON de la requête: {e}")
                    raise HTTPException(status_code=400, detail=f"Erreur lors du décodage JSON de la requête: {e}")
                
                except Exception as e:
                    logger.error(f"[{correlation_id}] Erreur lors du traitement de la requête chiffrée: {e}")
                    import traceback
                    logger.error(f"[{correlation_id}] Traceback: {traceback.format_exc()}")
                    raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête chiffrée: {e}")
            
            # Si la requête n'est pas chiffrée, continuer avec le traitement normal
            if request.method == "GET":
                logger.info(f"[{correlation_id}] Transfert d'une requête GET vers {service_url}")
                response = await client.get(
                    service_url,  # URL du microservice cible
                    params=request.query_params,  # Transmission des paramètres de requête
                    headers=headers,  # Transmission des en-têtes d'origine
                    timeout=timeout  # Timeout pour la requête
                )
            elif request.method == "POST":
                logger.info(f"[{correlation_id}] Transfert d'une requête POST vers {service_url}")
                response = await client.post(
                    service_url,
                    data=await request.body(),  # Transmission du corps de la requête en données brutes
                    headers=headers,
                    timeout=timeout
                )
            elif request.method == "PUT":
                logger.info(f"[{correlation_id}] Transfert d'une requête PUT vers {service_url}")
                response = await client.put(
                    service_url,
                    data=await request.body(),
                    headers=headers,
                    timeout=timeout
                )
            elif request.method == "DELETE":
                logger.info(f"[{correlation_id}] Transfert d'une requête DELETE vers {service_url}")
                response = await client.delete(
                    service_url,
                    headers=headers,
                    timeout=timeout
                )
            elif request.method == "PATCH":
                logger.info(f"[{correlation_id}] Transfert d'une requête PATCH vers {service_url}")
                response = await client.patch(
                    service_url,
                    data=await request.body(),
                    headers=headers,
                    timeout=timeout
                )
            else:
                logger.error(f"[{correlation_id}] Méthode HTTP non supportée: {request.method}")
                raise HTTPException(status_code=405, detail="Method Not Allowed")
            
            logger.info(f"[{correlation_id}] Réponse reçue avec le statut {response.status_code} du microservice")
            return Response(content=response.content, status_code=response.status_code)

        except httpx.TimeoutException as exc:
            logger.error(f"[{correlation_id}] Timeout lors de la connexion au microservice {service_name}: {exc}")
            raise HTTPException(status_code=408, detail="Timeout error")
        
        except httpx.RequestError as exc:
            logger.error(f"[{correlation_id}] Erreur de requête pour le microservice {service_name}: {exc}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la communication avec le microservice: {exc}")
        
        except httpx.HTTPStatusError as exc:
            logger.error(f"[{correlation_id}] Erreur HTTP du microservice {service_name}: {exc.response.status_code}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Erreur HTTP : {exc.response.status_code}")
        
        except Exception as exc:
            logger.error(f"[{correlation_id}] Erreur inattendue avec le microservice {service_name}: {exc}")
            raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Endpoint spécial pour la signature de documents (gère les fichiers PDF)
@app.post("/gateway/sign/")
@limiter.limit("5/minute")
async def sign_document(
    request: Request,
    document: UploadFile = File(...),
    certificate: UploadFile = File(...),
    password: str = Form(...),
    metadata: Optional[str] = Form(None),
    owner_id: Optional[str] = Form(None)
):
    """
    Endpoint pour signer un document PDF.
    Transmet la demande au microservice de signature.
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Demande de signature reçue pour le document {document.filename}")
    
    try:
        # Créer une instance du client HTTP avec désactivation de la vérification SSL
        async with httpx.AsyncClient(verify=False) as client:
            # Préparer les fichiers et données à envoyer
            files = {
                "document": (document.filename, await document.read(), document.content_type),
                "certificate": (certificate.filename, await certificate.read(), certificate.content_type)
            }
            
            form_data = {
                "password": password
            }
            
            if metadata:
                form_data["metadata"] = metadata
                
            if owner_id:
                form_data["owner_id"] = owner_id
            
            # URL du microservice de signature
            url = MICROSERVICES["sign"]
            
            # Envoyer la requête au microservice
            response = await client.post(url, files=files, data=form_data)
            
            # Vérifier la réponse
            if response.status_code == 200:
                # Retourner directement la réponse du microservice
                return StreamingResponse(
                    response.iter_bytes(),
                    media_type=response.headers.get("content-type", "application/zip"),
                    headers={"Content-Disposition": response.headers.get("content-disposition", f'attachment; filename="signed_document.zip"')}
                )
            else:
                # En cas d'erreur, retourner le message d'erreur du microservice
                logger.error(f"[{correlation_id}] Erreur de signature: {response.status_code} - {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content=response.json() if response.headers.get("content-type") == "application/json" else {"detail": response.text}
                )
    
    except Exception as e:
        logger.error(f"[{correlation_id}] Erreur lors de la signature: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la signature du document: {str(e)}")

# Endpoint pour l'authentification par certificat
@app.post("/gateway/auth/certificate/")
@limiter.limit("5/minute")
async def authenticate_with_certificate(request: Request):
    """
    Endpoint pour authentifier un utilisateur avec son certificat PFX.
    Récupère les informations du certificat via le microservice d'extraction,
    puis vérifie/crée le compte utilisateur dans Django.
    """
    # Journalisation de la demande d'authentification
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Demande d'authentification par certificat reçue")
    
    try:
        # Récupérer les données chiffrées de la requête
        client_id = request.headers.get("X-Client-ID")
        if not client_id:
            raise HTTPException(status_code=400, detail="En-tête X-Client-ID manquant")
            
        # Journaliser les informations de session
        logger.info(f"[{correlation_id}] Client ID reçu: {client_id}")
        logger.info(f"[{correlation_id}] Sessions actives: {len(app.state.client_sessions)}")
        logger.info(f"[{correlation_id}] Clients actifs: {list(app.state.client_sessions.keys())}")
        
        # Vérifier si une session existe pour ce client
        if client_id not in app.state.client_sessions:
            logger.error(f"[{correlation_id}] Session non trouvée pour le client {client_id}")
            raise HTTPException(status_code=401, detail="Session invalide ou expirée")
        else:
            logger.info(f"[{correlation_id}] Session trouvée pour le client {client_id}")
        
        session_key = app.state.client_sessions[client_id]
        logger.info(f"[{correlation_id}] Clé de session récupérée: {len(session_key)} octets (premiers octets: {session_key[:8].hex()})")
        
        # Récupérer et déchiffrer les données
        encrypted_data = await request.json()
        if not encrypted_data or "data" not in encrypted_data or "iv" not in encrypted_data:
            raise HTTPException(status_code=400, detail="Données de chiffrement incorrectes")
        
        # Déchiffrer le message JSON
        logger.info(f"[{correlation_id}] Tentative de déchiffrement avec la clé de session")
        try:
            decrypted_message = decrypt_message(
                encrypted_data["data"],
                encrypted_data["iv"],
                session_key
            )
            logger.info(f"[{correlation_id}] Déchiffrement réussi")
        except Exception as e:
            logger.error(f"[{correlation_id}] Erreur de déchiffrement: {str(e)}")
            # Ré-lever l'exception pour qu'elle soit gérée par le gestionnaire d'exceptions global
            raise
        
        # Convertir en objet JSON
        auth_data = json.loads(decrypted_message.decode("utf-8"))
        logger.info(f"[{correlation_id}] Données d'authentification déchiffrées avec succès")
        
        # Vérifier que toutes les données nécessaires sont présentes
        if "certificate" not in auth_data or "password" not in auth_data:
            raise HTTPException(status_code=400, detail="Données d'authentification incomplètes")
        
        # Envoyer le certificat au microservice d'extraction
        logger.info(f"[{correlation_id}] Envoi du certificat au microservice d'extraction")
        async with httpx.AsyncClient(verify=False) as client:
            extract_response = await client.post(
                MICROSERVICES["cert_info_base64"],
                json={
                    "certificate_base64": auth_data["certificate"],
                    "password": auth_data["password"]
                }
            )
            
            if extract_response.status_code != 200:
                logger.error(f"[{correlation_id}] Erreur du microservice d'extraction: {extract_response.text}")
                raise HTTPException(
                    status_code=extract_response.status_code,
                    detail="Erreur lors de l'extraction des informations du certificat"
                )
            
            # Récupérer les informations du certificat
            cert_info = extract_response.json()
            logger.info(f"[{correlation_id}] Informations du certificat extraites avec succès")
            
            # Envoyer les informations du certificat à Django pour vérification/création du compte
            logger.info(f"[{correlation_id}] Envoi des informations à Django pour vérification/création")
            django_data = {
                "certificate_info": cert_info,
                "role": auth_data.get("role", "user"),
                "filename": auth_data.get("filename", "certificate.pfx")
            }
            
            # URL de l'API Django pour la vérification/création d'utilisateur
            django_url = "https://192.168.4.131:8000/api/users/auth-certificate/"
            
            django_response = await client.post(
                django_url,
                json=django_data,
                headers={"Content-Type": "application/json"}
            )
            
            if django_response.status_code not in [200, 201]:
                logger.error(f"[{correlation_id}] Erreur de Django: {django_response.text}")
                raise HTTPException(
                    status_code=django_response.status_code,
                    detail="Erreur lors de la vérification/création du compte"
                )
            
            # Récupérer la réponse de Django
            user_data = django_response.json()
            logger.info(f"[{correlation_id}] Authentification réussie avec statut: {user_data.get('status')}")
            
            # Chiffrer la réponse
            response_json = json.dumps(user_data).encode("utf-8")
            encrypted_response = encrypt_message(response_json, session_key, client_id)
            
            return JSONResponse(content=encrypted_response)
            
    except HTTPException as e:
        # Relancer les exceptions HTTP
        raise e
    except Exception as e:
        # Journaliser les erreurs inattendues
        logger.error(f"[{correlation_id}] Erreur inattendue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur du serveur: {str(e)}")

# Endpoint spécial pour la vérification de documents (gère les fichiers PDF)
@app.post("/gateway/verify/")
@limiter.limit("10/minute")
async def verify_document(
    request: Request,
    document: UploadFile = File(...)
):
    """
    Endpoint pour vérifier un document PDF signé.
    Transmet la demande au microservice de vérification.
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Demande de vérification reçue pour le document {document.filename}")
    
    try:
        # Créer une instance du client HTTP
        async with httpx.AsyncClient(verify=False) as client:
            # Préparer le fichier à envoyer
            files = {
                "document": (document.filename, await document.read(), document.content_type)
            }
            
            # URL du microservice de vérification
            url = MICROSERVICES["verify"]
            
            # Envoyer la requête au microservice
            response = await client.post(url, files=files)
            
            # Vérifier la réponse
            if response.status_code == 200:
                # Retourner la réponse du microservice
                return JSONResponse(content=response.json())
            else:
                # En cas d'erreur, retourner le message d'erreur du microservice
                logger.error(f"[{correlation_id}] Erreur de vérification: {response.status_code} - {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content=response.json() if response.headers.get("content-type") == "application/json" else {"detail": response.text}
                )
    
    except Exception as e:
        logger.error(f"[{correlation_id}] Erreur lors de la vérification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification du document: {str(e)}")


# Endpoint pour la vérification de documents par ID (nouvelle version simplifiée)
@app.post("/gateway/verify/")
@limiter.limit("20/minute")
async def verify_document(
    request: Request
):
    """
    Endpoint pour vérifier un document par son ID.
    Transmet la demande au microservice de vérification.
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Demande de vérification par ID reçue")
    
    try:
        # Récupérer le corps de la requête
        body = await request.json()
        document_id = body.get("document_id")
        return_original = body.get("return_original_document", True)  # Par défaut, retourner le document original
        
        if not document_id:
            raise HTTPException(status_code=400, detail="L'ID du document est requis")
            
        logger.info(f"[{correlation_id}] Vérification du document avec ID: {document_id}")
        
        # Créer une instance du client HTTP
        async with httpx.AsyncClient(verify=False) as client:
            # URL du microservice de vérification - utilisation du service 'verify' qui accepte maintenant directement un ID
            url = MICROSERVICES["verify"]
            logger.info(f"[{correlation_id}] Appel du microservice à l'URL: {url}")
            
            # Préparer les données à envoyer
            data = {
                "document_id": document_id,
                "return_original_document": return_original
            }
            
            # Envoyer la requête au microservice
            response = await client.post(url, json=data)
            
            # Vérifier la réponse
            if response.status_code == 200:
                # Retourner la réponse du microservice
                return JSONResponse(content=response.json())
            else:
                # En cas d'erreur, retourner le message d'erreur du microservice
                logger.error(f"[{correlation_id}] Erreur de vérification: {response.status_code} - {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content=response.json() if response.headers.get("content-type") == "application/json" else {"detail": response.text}
                )
    
    except json.JSONDecodeError:
        logger.error(f"[{correlation_id}] Erreur de décodage JSON")
        raise HTTPException(status_code=400, detail="Requête invalide: le corps doit être au format JSON")
    
    except Exception as e:
        logger.error(f"[{correlation_id}] Erreur lors de la vérification par ID: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification du document: {str(e)}")

# Endpoint pour convertir une page PDF en image
@app.post("/gateway/pdf-to-image/")
@limiter.limit("20/minute")
async def pdf_to_image(
    request: Request,
    pdf: UploadFile = File(...),
    page: int = Form(1)
):
    """
    Convertit une page spécifique d'un PDF en image pour l'aperçu.
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Demande de conversion PDF vers image, page {page}")
    
    try:
        # Lire le contenu du PDF
        pdf_content = await pdf.read()
        
        # Convertir la page spécifique en image
        images = convert_from_bytes(
            pdf_content,
            first_page=page,
            last_page=page,
            dpi=150,  # Résolution suffisante pour l'aperçu
            fmt='PNG'
        )
        
        if not images:
            raise HTTPException(status_code=404, detail="Page non trouvée dans le PDF")
        
        # Prendre la première (et seule) image
        image = images[0]
        
        # Redimensionner l'image pour qu'elle corresponde au format A4 dans l'aperçu
        # A4 : 210mm x 297mm, ratio 1:1.414
        max_width = 595  # Largeur A4 en pixels à 72 DPI
        max_height = 842  # Hauteur A4 en pixels à 72 DPI
        
        # Calculer le ratio pour conserver les proportions
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        ratio = min(width_ratio, height_ratio)
        
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)
        
        # Redimensionner l'image (compatibilité avec anciennes versions de Pillow)
        try:
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except AttributeError:
            # Pour les anciennes versions de Pillow
            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Créer un buffer pour l'image
        img_buffer = io.BytesIO()
        resized_image.save(img_buffer, format='PNG', optimize=True)
        img_buffer.seek(0)
        
        # Retourner l'image
        return StreamingResponse(
            img_buffer,
            media_type="image/png",
            headers={
                "Cache-Control": "max-age=3600",  # Cache pendant 1 heure
                "X-Page-Number": str(page)
            }
        )
        
    except Exception as e:
        logger.error(f"[{correlation_id}] Erreur lors de la conversion PDF vers image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la conversion: {str(e)}")

# Endpoint pour obtenir les informations d'un PDF
@app.post("/gateway/pdf-info/")
@limiter.limit("30/minute")
async def pdf_info(
    request: Request,
    pdf: UploadFile = File(...)
):
    """
    Obtient les informations d'un PDF (nombre de pages, dimensions, etc.)
    """
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Demande d'informations sur le PDF {pdf.filename}")
    
    try:
        # Lire le contenu du PDF
        pdf_content = await pdf.read()
        
        # Utiliser PyPDF2 pour obtenir les informations
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        num_pages = len(pdf_reader.pages)
        
        # Obtenir les dimensions de la première page
        first_page = pdf_reader.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)
        
        # Calculer le ratio
        ratio = page_height / page_width
        
        return JSONResponse(content={
            "filename": pdf.filename,
            "num_pages": num_pages,
            "first_page_dimensions": {
                "width": page_width,
                "height": page_height,
                "ratio": ratio
            },
            "is_a4": abs(ratio - 1.414) < 0.1  # Vérifier si c'est approximativement du A4
        })
        
    except Exception as e:
        logger.error(f"[{correlation_id}] Erreur lors de l'obtention des informations PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du PDF: {str(e)}")
