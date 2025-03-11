import argparse  # Importation du module argparse pour traiter les arguments en ligne de commande
import requests  # Importation du module requests pour envoyer des requêtes HTTP
import os  # Importation du module os pour interagir avec le système de fichiers

def main(cert_path):
    # Vérifier si le chemin donné correspond à un répertoire plutôt qu'à un fichier
    if os.path.isdir(cert_path):
        print(f"Erreur : Le chemin '{cert_path}' est un répertoire, pas un fichier.")
        return  # Si c'est un répertoire, on arrête l'exécution de la fonction

    # Demander le mot de passe à l'utilisateur pour le certificat
    password = input("Entrez le mot de passe du certificat : ")

    # Construire les données de la requête
    try:
        # Ouvrir le fichier certificat en mode lecture binaire ('rb')
        files = {'file': open(cert_path, 'rb')}
    except FileNotFoundError:
        # Si le fichier n'est pas trouvé, afficher un message d'erreur
        print(f"Erreur : Le fichier '{cert_path}' n'a pas été trouvé.")
        return  # Arrêter l'exécution de la fonction
    except IsADirectoryError:
        # Si le chemin correspond à un répertoire, afficher un message d'erreur spécifique
        print(f"Erreur : Le chemin '{cert_path}' est un répertoire, pas un fichier.")
        return  # Arrêter l'exécution de la fonction
    except Exception as e:
        # Si une autre erreur inattendue survient lors de l'ouverture du fichier
        print(f"Erreur inattendue lors de l'ouverture du fichier : {e}")
        return  # Arrêter l'exécution de la fonction

    data = {'password': password}  # Créer un dictionnaire avec le mot de passe pour l'envoyer dans la requête

    # URL de l'API Gateway à laquelle la requête sera envoyée
    gateway_url = "http://localhost:8000/gateway/cert_info/"  # Remplacer par l'URL réelle de l'API Gateway

    # Envoyer une requête POST au serveur API Gateway avec les fichiers et les données
    response = requests.post(gateway_url, files=files, data=data)

    # Vérifier si la réponse de l'API est positive (code 200)
    if response.status_code == 200:
        print("Informations du certificat :")
        # Convertir la réponse en format JSON
        response_data = response.json()
        
        # Afficher chaque clé et valeur de la réponse JSON sur une nouvelle ligne
        for key, value in response_data.items():
            print(f"{key}: {value}")
    else:
        # Si le code de statut n'est pas 200, afficher l'erreur
        print(f"Erreur {response.status_code}: {response.text}")
    
    files['file'].close()  # Fermer le fichier après l'envoi de la requête

if __name__ == "__main__":
    # Configuration d'argparse pour accepter un chemin de certificat via la ligne de commande
    parser = argparse.ArgumentParser(description="Envoyer un certificat PFX à l'API Gateway.")
    parser.add_argument('cert_path', type=str, nargs='?', help="Le chemin vers le certificat PFX.")
    
    # Analyser les arguments passés en ligne de commande
    args = parser.parse_args()

    # Si le chemin du certificat est passé en argument, on l'utilise, sinon on demande à l'utilisateur
    if args.cert_path:
        cert_path = args.cert_path
    else:
        cert_path = input("Entrez le chemin du fichier certificat PFX : ")

    # Appeler la fonction principale avec le chemin du certificat
    main(cert_path)
