# Importation des modules nécessaires
from fastapi import FastAPI, HTTPException, Request, Response  # FastAPI pour la création d'API, HTTPException pour gérer les erreurs, Request et Response pour gérer les requêtes et réponses HTTP
import httpx  # httpx pour effectuer des requêtes HTTP asynchrones vers les microservices

# Crée une instance de l'application FastAPI
app = FastAPI()

# Liste des microservices disponibles avec leurs URL de base
MICROSERVICES = {
    "cert_info": "http://localhost:8001/extract-cert-info/",  # L'URL de base du microservice de traitement des certificats
    # Ajouter ici d'autres microservices avec leur URL respective si nécessaire
}

# Route POST pour le point d'entrée de l'API Gateway
@app.post("/gateway/{service_name}/")
async def gateway(service_name: str, request: Request):
    # Vérifier si le service demandé existe dans la liste des microservices disponibles
    if service_name not in MICROSERVICES:
        # Si le service n'existe pas, renvoyer une erreur 404 (service non trouvé)
        raise HTTPException(status_code=404, detail="Service non trouvé")

    # Récupérer l'URL du microservice correspondant au nom du service passé dans l'URL
    service_url = MICROSERVICES[service_name]

    # Transférer la requête vers le microservice en utilisant httpx
    async with httpx.AsyncClient() as client:  # Créer un client asynchrone pour faire la requête HTTP
        try:
            # Effectuer la requête POST vers le microservice, en transmettant les données de la requête initiale
            response = await client.post(
                service_url,  # URL du microservice cible
                data=await request.body(),  # Récupérer le corps de la requête et le transmettre au microservice
                headers=request.headers  # Copier les en-têtes de la requête d'origine (comme les informations d'authentification, etc.)
            )

            # Retourner la réponse du microservice, en conservant le contenu et le code de statut
            return Response(content=response.content, status_code=response.status_code)

        except httpx.RequestError as exc:
            # Si une erreur se produit lors de la requête vers le microservice, renvoyer une erreur HTTP 500
            raise HTTPException(status_code=500, detail=f"Erreur lors de la communication avec le microservice: {exc}")
