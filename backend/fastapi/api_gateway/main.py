from fastapi import FastAPI, HTTPException, Request, Response
import httpx
from fastapi.middleware.cors import CORSMiddleware


# Crée une instance de l'application FastAPI
app = FastAPI()

# 🔥 Configuration de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Mets ici l'URL de ton frontend
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)

# Liste des microservices disponibles avec leurs URL de base
MICROSERVICES = {
    "cert_info": "http://localhost:8001/extract-cert-info/",  # L'URL du microservice de traitement des certificats
    "sign": "http://localhost:8002/sign",  # L'URL du microservice de signature
    "verify": "http://localhost:8002/verify"
}

# Route POST pour le point d'entrée de l'API Gateway
@app.post("/gateway/{service_name}/")
async def gateway(service_name: str, request: Request):
    # Vérifier si le service demandé existe dans la liste des microservices disponibles
    if service_name not in MICROSERVICES:
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Récupérer l'URL du microservice correspondant au nom du service passé dans l'URL
    service_url = MICROSERVICES[service_name]

    # Transférer la requête vers le microservice en utilisant httpx
    async with httpx.AsyncClient() as client:
        try:
            # Effectuer la requête POST vers le microservice, en transmettant les données de la requête initiale
            response = await client.post(
                service_url,  # URL du microservice cible
                data=await request.body(),  # Récupérer le corps de la requête et le transmettre au microservice
                headers=request.headers  # Copier les en-têtes de la requête d'origine
            )

            # Retourner la réponse du microservice
            return Response(content=response.content, status_code=response.status_code)

        except httpx.RequestError as exc:
            # Si une erreur se produit, renvoyer une erreur HTTP 500
            raise HTTPException(status_code=500, detail=f"Erreur lors de la communication avec le microservice: {exc}")
