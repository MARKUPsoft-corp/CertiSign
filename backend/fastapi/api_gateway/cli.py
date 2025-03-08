import requests

# URL du serveur FastAPI qui gère les opérations
API_URL = "http://127.0.0.1:8000"

def get_user_input():
    """ Demande à l'utilisateur d'entrer deux nombres. """
    while True:
        try:
            a = float(input("Entrez le premier nombre : "))
            b = float(input("Entrez le deuxième nombre : "))
            return a, b
        except ValueError:
            print("Entrée invalide. Veuillez entrer des nombres valides.")

def send_request(operation, a, b):
    """ Envoie une requête HTTP à l'API FastAPI. """
    response = requests.get(f"{API_URL}/{operation}", params={"a": a, "b": b})
    return response.json()

def main():
    """ Fonction principale de l'application CLI. """
    print("Bienvenue dans l'application CLI de calcul.")
    print("Choisissez une opération :")
    print("1. Addition")
    print("2. Multiplication")
    
    choice = input("Votre choix (1 ou 2) : ")

    if choice not in ["1", "2"]:
        print("Choix invalide. Veuillez sélectionner 1 ou 2.")
        return
    
    a, b = get_user_input()  # Demande des nombres à l'utilisateur

    operation = "add" if choice == "1" else "multiply"
    
    result = send_request(operation, a, b)  # Envoie la requête

    print(f"Résultat de l'opération {operation} : {result}")

if __name__ == "__main__":
    main()
