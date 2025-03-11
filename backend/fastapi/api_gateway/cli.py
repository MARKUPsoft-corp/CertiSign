import argparse
import requests
import os  # Importation pour vérifier si le chemin est un fichier ou un répertoire

def main(cert_path):
    # Vérifier si le chemin est un répertoire au lieu d'un fichier
    if os.path.isdir(cert_path):
        print(f"Erreur : Le chemin '{cert_path}' est un répertoire, pas un fichier.")
        return

    # Demander le mot de passe pour le certificat
    password = input("Entrez le mot de passe du certificat : ")

    # Construire les données de la requête
    try:
        # Tenter d'ouvrir le certificat en mode lecture binaire
        files = {'file': open(cert_path, 'rb')}
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{cert_path}' n'a pas été trouvé.")
        return
    except IsADirectoryError:
        print(f"Erreur : Le chemin '{cert_path}' est un répertoire, pas un fichier.")
        return
    except Exception as e:
        print(f"Erreur inattendue lors de l'ouverture du fichier : {e}")
        return

    data = {'password': password}

    # URL de l'API Gateway
    gateway_url = "http://localhost:8000/gateway/cert_info/"  # Remplacez par l'URL de votre API Gateway

    # Envoyer la requête POST à l'API Gateway
    response = requests.post(gateway_url, files=files, data=data)

    # Afficher la réponse de l'API Gateway
    if response.status_code == 200:
        print("Informations du certificat :")
        # Récupérer la réponse au format JSON
        response_data = response.json()
        
        # Affichage de chaque information sur une nouvelle ligne
        for key, value in response_data.items():
            print(f"{key}: {value}")
    else:
        print(f"Erreur {response.status_code}: {response.text}")
    
    files['file'].close()  # Fermer le fichier après envoi

if __name__ == "__main__":
    # Configuration de argparse pour accepter un chemin de certificat
    parser = argparse.ArgumentParser(description="Envoyer un certificat PFX à l'API Gateway.")
    parser.add_argument('cert_path', type=str, nargs='?', help="Le chemin vers le certificat PFX.")
    
    # Obtenir le chemin du certificat depuis l'argument ou via input()
    args = parser.parse_args()

    if args.cert_path:
        cert_path = args.cert_path
    else:
        cert_path = input("Entrez le chemin du fichier certificat PFX : ")

    # Appeler la fonction principale avec le chemin du certificat
    main(cert_path)
