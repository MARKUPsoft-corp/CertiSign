from fastapi import FastAPI, HTTPException, Request, Response  # Importation des classes et fonctions nécessaires de FastAPI
import httpx  # Importation de httpx pour effectuer des requêtes HTTP asynchrones
from fastapi.middleware.cors import CORSMiddleware  # Importation du middleware CORS
import logging  # Importation du module logging pour la journalisation
from slowapi import Limiter  # Importation de Limiter pour le rate limiting
from slowapi.errors import RateLimitExceeded  # Importation de l'erreur de dépassement de limite
from fastapi.responses import JSONResponse  # Importation de JSONResponse pour renvoyer des réponses JSON
import uuid  # Importation de uuid pour générer des identifiants de corrélation uniques

# Configuration du logger pour l'API Gateway
logger = logging.getLogger("api_gateway")  # Création d'un logger nommé "api_gateway"
logger.setLevel(logging.INFO)  # Définition du niveau de log à INFO

# Création d'une instance de l'application FastAPI
app = FastAPI()  # Initialisation de l'application FastAPI

# Configuration du middleware CORS pour autoriser les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,  # Middleware pour gérer le Cross-Origin Resource Sharing
    allow_origins=["http://localhost:8080"],  # Autorise uniquement les requêtes provenant de cette URL
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

# Gestionnaire d'exception pour les erreurs de dépassement de rate limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_error(request: Request, exc: RateLimitExceeded):
    # Renvoie une réponse JSON avec le code 429 (Too Many Requests)
    return JSONResponse(
        status_code=429,  # Code HTTP 429
        content={"detail": "Rate limit exceeded. Try again later."},  # Message d'erreur
    )

# Dictionnaire des microservices disponibles avec leurs URL de base
MICROSERVICES = {
    "cert_info": "http://localhost:8001/extract-cert-info/",  # URL du microservice de traitement des certificats
    "sign": "http://localhost:8002/sign",  # URL du microservice de signature
    "verify": "http://localhost:8002/verify"  # URL du microservice de vérification
}

# Route générique pour l'API Gateway acceptant toutes les méthodes HTTP (GET, POST, PUT, DELETE, PATCH)
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

    # Pour les méthodes susceptibles d'avoir un corps (POST, PUT, PATCH), on vérifie la taille du corps
    if request.method not in ("GET", "DELETE"):
        body = await request.body()  # Récupère le corps brut de la requête
        max_body_size = 10 * 1024 * 1024  # Limite maximale fixée à 10 Mo
        if len(body) > max_body_size:
            logger.error(f"[{correlation_id}] Taille du corps trop grande: {len(body)} octets")
            raise HTTPException(status_code=413, detail="Request payload too large")  # Erreur 413 si la taille dépasse la limite
    else:
        body = None  # Pour GET et DELETE, aucun corps n'est traité

    # Définition du timeout pour les requêtes vers les microservices
    timeout = 10.0  # Timeout de 10 secondes

    # Préparation des en-têtes à transmettre (conversion en dictionnaire)
    headers = dict(request.headers)

    # Utilisation d'un client HTTP asynchrone pour effectuer la requête vers le microservice
    async with httpx.AsyncClient() as client:
        try:
            # Sélection de la méthode HTTP et transfert de la requête vers le microservice correspondant
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
                # Si une méthode non prise en charge est utilisée, on renvoie une erreur 405
                logger.error(f"[{correlation_id}] Méthode HTTP non supportée: {request.method}")
                raise HTTPException(status_code=405, detail="Method Not Allowed")
            
            # Journalisation de la réponse reçue du microservice
            logger.info(f"[{correlation_id}] Réponse reçue avec le statut {response.status_code} du microservice")
            
            # Renvoi de la réponse du microservice au client initial
            return Response(content=response.content, status_code=response.status_code)
        
        except httpx.TimeoutException as exc:
            # Gestion spécifique des erreurs de timeout
            logger.error(f"[{correlation_id}] Timeout lors de la connexion au microservice {service_name}: {exc}")
            raise HTTPException(status_code=408, detail="Timeout error")
        
        except httpx.RequestError as exc:
            # Gestion des erreurs de requête (erreurs de connexion, etc.)
            logger.error(f"[{correlation_id}] Erreur de requête pour le microservice {service_name}: {exc}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de la communication avec le microservice: {exc}")
        
        except httpx.HTTPStatusError as exc:
            # Gestion des erreurs HTTP retournées par le microservice
            logger.error(f"[{correlation_id}] Erreur HTTP du microservice {service_name}: {exc.response.status_code}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Erreur HTTP : {exc.response.status_code}")
        
        except Exception as exc:
            # Gestion de toute autre erreur imprévue
            logger.error(f"[{correlation_id}] Erreur inattendue avec le microservice {service_name}: {exc}")
            raise HTTPException(status_code=500, detail="Erreur interne du serveur")
