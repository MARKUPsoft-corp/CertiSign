# Importation de FastAPI, le framework permettant de créer des APIs rapidement
from fastapi import FastAPI

# Importation du module requests pour faire des requêtes HTTP vers d'autres services
import requests

# Création d'une instance de l'application FastAPI
app = FastAPI()

# Définition des URLs des microservices pour l'addition et la multiplication
ADDITION_SERVICE_URL = "http://127.0.0.1:8001/add"  # Microservice d'addition
MULTIPLICATION_SERVICE_URL = "http://127.0.0.1:8002/multiply"  # Microservice de multiplication

# Définition d'un endpoint "/add" qui fait appel au microservice d'addition
@app.get("/add")
def add(a: float, b: float):
    """
    Fonction qui prend deux nombres en paramètres et appelle le microservice d'addition.
    - `a` et `b` sont récupérés depuis la requête HTTP (paramètres de l'URL).
    - Une requête est envoyée au microservice d'addition.
    - La réponse est renvoyée telle quelle au client.
    """
    response = requests.get(ADDITION_SERVICE_URL, params={"a": a, "b": b})
    return response.json()  # Retourne le résultat du microservice sous forme de JSON

# Définition d'un endpoint "/multiply" qui fait appel au microservice de multiplication
@app.get("/multiply")
def multiply(a: float, b: float):
    """
    Fonction qui prend deux nombres en paramètres et appelle le microservice de multiplication.
    - `a` et `b` sont récupérés depuis la requête HTTP.
    - Une requête est envoyée au microservice de multiplication.
    - La réponse est renvoyée telle quelle au client.
    """
    response = requests.get(MULTIPLICATION_SERVICE_URL, params={"a": a, "b": b})
    return response.json()  # Retourne le résultat du microservice sous forme de JSON

# Démarrage de l'application FastAPI si ce fichier est exécuté directement
if __name__ == "__main__":
    """
    Vérifie si ce fichier est exécuté en tant que programme principal.
    Si oui, lance le serveur FastAPI avec Uvicorn.
    """
    import uvicorn  # Importation du serveur ASGI Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)  # Lancement du serveur sur le port 8000
