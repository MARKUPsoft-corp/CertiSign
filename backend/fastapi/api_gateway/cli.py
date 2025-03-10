import requests  # Importation du module 'requests' pour envoyer des requêtes HTTP

def main():
    # Demande à l'utilisateur le chemin du certificat et le mot de passe
    cert_path = input("Veuillez entrer le chemin du certificat (.pfx, .pem, .p12) : ")  # Demande à l'utilisateur de saisir le chemin du fichier certificat
    password = input("Veuillez entrer le mot de passe du certificat : ")  # Demande à l'utilisateur de saisir le mot de passe du certificat

    # Affiche les informations saisies pour le débogage
    print(f"Chemin du certificat : {cert_path}")  # Affiche le chemin du certificat saisi
    print(f"Mot de passe : {password}")  # Affiche le mot de passe saisi

    # Prépare la requête pour l'API Gateway
    api_url = "http://localhost:8000/extract_cert_info"  # L'URL de l'API Gateway qui va traiter la requête

    # Ouvre le certificat en mode binaire pour l'envoyer dans la requête
    try:
        print("Ouverture du certificat...")  # Affiche un message pour indiquer que l'ouverture du certificat commence
        with open(cert_path, 'rb') as cert_file:  # Ouvre le fichier du certificat en mode binaire ('rb')
            files = {'cert': cert_file}  # Prépare les données à envoyer : le fichier du certificat
            data = {'password': password}  # Prépare les données supplémentaires à envoyer : le mot de passe du certificat
            
            print(f"Envoi de la requête POST à {api_url}...")  # Affiche un message pour indiquer que la requête va être envoyée
            # Envoie la requête POST au microservice via l'API Gateway
            response = requests.post(api_url, files=files, data=data)  # Envoie la requête HTTP POST à l'API avec les fichiers et les données
            
            # Vérifie la réponse de l'API
            if response.status_code == 200:  # Si le code de statut de la réponse est 200, cela signifie que la requête a réussi
                print("Réponse reçue avec succès.")  # Affiche un message indiquant que la réponse a été reçue avec succès
                print("Informations extraites :")  # Affiche un titre pour les données extraites
                print(response.json())  # Affiche les données extraites du certificat sous forme de JSON
            else:  # Si le code de statut n'est pas 200, une erreur est survenue
                print(f"Erreur lors de l'extraction du certificat : {response.status_code}")  # Affiche l'erreur basée sur le code de statut
                print(response.text)  # Affiche le texte d'erreur renvoyé par l'API pour plus de détails
    except FileNotFoundError:  # Si le fichier certificat n'est pas trouvé, une exception est levée
        print("Le fichier certificat n'a pas été trouvé. Vérifiez le chemin.")  # Affiche un message d'erreur pour indiquer que le fichier n'existe pas
    except Exception as e:  # Si une autre erreur se produit (par exemple, problème de connexion ou autre erreur)
        print(f"Erreur lors de la connexion ou du traitement : {e}")  # Affiche un message d'erreur générique avec la description de l'exception

if __name__ == "__main__":  # Vérifie si ce fichier est exécuté directement (et non importé en tant que module)
    main()  # Appelle la fonction principale pour lancer le programme
