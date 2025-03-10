# Importation de requests pour envoyer des requêtes HTTP
import requests

def upload_certificate():
    """
    Cette fonction demande à l'utilisateur un fichier de certificat,
    puis l'envoie au microservice via l'API Gateway.
    """
    # Demander à l'utilisateur de saisir le chemin du certificat
    cert_path = input("Entrez le chemin du certificat : ")

    try:
        # Ouvrir le fichier certificat en mode binaire (lecture)
        with open(cert_path, "rb") as cert_file:
            # Préparer les données pour l'envoi via requête POST
            files = {"cert_file": (cert_path, cert_file, "application/x-pem-file")}
            
            # Envoyer le certificat à l'API Gateway
            response = requests.post("http://127.0.0.1:8000/upload-cert", files=files)

            # Vérifier si la requête a réussi
            if response.status_code == 200:
                print("\nInformations du certificat :")
                print(response.json())  # Afficher la réponse JSON contenant les infos du certificat
            else:
                print("\nErreur :", response.text)  # Afficher l'erreur HTTP

    except FileNotFoundError:
        # Gérer le cas où le fichier n'existe pas
        print("Fichier introuvable, vérifiez le chemin.")
    except Exception as e:
        # Gérer d'autres erreurs éventuelles
        print(f"Erreur : {e}")

# Vérifier si le script est exécuté directement
if __name__ == "__main__":
    upload_certificate()
