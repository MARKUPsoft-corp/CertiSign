import typer  # Pour créer des interfaces en ligne de commande (CLI)
import requests  # Pour envoyer des requêtes HTTP à une API
import os  # Pour manipuler le système de fichiers
import getpass  # Pour masquer la saisie du mot de passe
import time  # Pour simuler des temps d'attente (sleep)
from rich.progress import Progress, BarColumn, TextColumn  # Pour afficher une barre de progression stylisée
from rich.console import Console  # Pour afficher du texte stylisé dans le terminal
from rich.panel import Panel  # Pour afficher des panneaux encadrés
from rich.text import Text  # Pour styliser du texte
import shutil  # Pour obtenir la largeur du terminal

# Initialisation de l'application Typer
app = typer.Typer()

# Initialisation du console Rich pour afficher du texte stylisé
console = Console()

# URL de l'API Gateway à utiliser pour envoyer les requêtes 
GATEWAY_URL_cert_info = "http://localhost:8000/gateway/cert_info/"
GATEWAY_URL_sign = "http://localhost:8000/gateway/sign/" 
GATEWAY_URL_verify = "http://localhost:8000/gateway/verify/" 

# Logo ASCII de l'application CertiSign
LOGO_CERTISIGN = """
 ██████╗ ███████╗ ██████╗ ████████╗██╗ ███████╗ ██╗  ██████╗  ███╗   ██╗
██╔════╝ ██╔════╝ ██╔══██╗╚══██╔══╝██║ ██╔════╝ ██║ ██╔════╝  ████╗  ██║               
██║      █████╗   ██████╔╝   ██║   ██║ ███████╗ ██║ ██║ ████  ██╔██╗ ██║
██║      ██╔══╝   ██╔══██╗   ██║   ██║ ╚════██║ ██║ ██║   ██║ ██║╚██╗██║
╚██████╔ ███████╗ ██║  ██║   ██║   ██║ ███████║ ██║ ╚██████╔╝ ██║ ╚████║
 ╚═════╝ ╚══════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚══════╝ ╚═╝  ╚═════╝  ╚═╝  ╚═══╝
"""

# Obtenir la largeur de la console
console_width = shutil.get_terminal_size().columns

# Limiter la largeur du logo à 60% de la largeur de la console
logo_width = int(console_width * 0.6)

# Affichage du logo de CertiSign dans une boîte stylisée
console.print(
    Panel(
        Text(LOGO_CERTISIGN, style="cyan bold"),  # Applique un style de texte cyan et en gras
        title="🔐 CertiSign - Signez en un clic",  # Titre du panneau
        style="blue",  # Style de fond bleu pour le panneau
        width=logo_width  # Limite la largeur du panneau
    )
)

# Fonction pour extraire les informations d'un certificat
def send_cert():
    """
    Extraction des informations d'un certificat PFX.
    """
    # Demande à l'utilisateur d'entrer le chemin du fichier certificat
    cert_path = typer.prompt("📂 Entrez le chemin du fichier certificat PFX")

    # Vérification si le chemin est un répertoire ou un fichier
    if os.path.isdir(cert_path):
        typer.echo("❌ Erreur : Chemin invalide, c'est un répertoire !")
        return
    if not os.path.isfile(cert_path):
        typer.echo("❌ Erreur : Fichier non trouvé !")
        return

    # Demande du mot de passe pour le certificat
    password = getpass.getpass("🔑 Entrez le mot de passe du certificat : ")

    try:
        # Ouverture du fichier certificat en mode binaire
        with open(cert_path, 'rb') as file:
            # Préparation des données pour l'envoi de la requête
            files = {'file': file}
            data = {'password': password}

            # Affichage d'une barre de progression pour montrer que l'extraction est en cours
            with Progress(
                TextColumn("🔄 Extraction en cours..."),  # Colonne de texte
                BarColumn(),  # Colonne de barre de progression
                TextColumn("[green]{task.percentage:>3.0f}%")  # Colonne pour afficher le pourcentage
            ) as progress:
                task = progress.add_task("Extracting", total=100)  # Définition de la tâche de progression
                for _ in range(10):  # Simuler le temps d'attente en avançant la barre
                    time.sleep(0.2)  # Attente de 0.2 secondes
                    progress.update(task, advance=10)  # Mise à jour de la progression

            # Affichage du message de succès après l'extraction
            typer.echo("✅ SUCCÈS : Extraction terminée !\n")

            # Envoi de la requête HTTP à l'API Gateway pour obtenir les informations du certificat
            response = requests.post(GATEWAY_URL_cert_info, files=files, data=data, timeout=10)

        # Si la réponse est positive (code 200), afficher les informations du certificat
        if response.status_code == 200:
            cert_info = "\n".join([f"🔹 {key}: {value}" for key, value in response.json().items()])
            # Affichage des informations du certificat dans un panneau stylisé
            console.print(Panel(cert_info, title="🔍 Informations du certificat", style="green", width=logo_width))
        else:
            # Affichage d'un message d'erreur si le code de réponse n'est pas 200
            typer.echo(f"⚠️ Erreur {response.status_code}: {response.text}")
    except requests.ConnectionError:
        # Gestion de l'erreur si une connexion réseau échoue
        typer.echo("🚨 Erreur : Impossible de se connecter à l'API Gateway.")
    except requests.Timeout:
        # Gestion de l'erreur si la requête expire
        typer.echo("⏳ Erreur : La requête a expiré.")
    except Exception as e:
        # Gestion des erreurs inattendues
        typer.echo(f"❌ Erreur inattendue : {e}")

# Fonction pour signer un document avec un certificat
def sign_document():
    """
    Signature d'un document en utilisant un certificat PFX.
    """

    # Demande du chemin du fichier certificat
    cert_path = typer.prompt("📂 Entrez le chemin du fichier certificat PFX")

    if not os.path.isfile(cert_path):
        # Vérifie si le fichier certificat existe
        typer.echo("❌ Erreur : Le fichier certificat n'existe pas !")
        raise typer.Exit()

    # Demande du mot de passe du certificat
    try:
        cert_password = getpass.getpass("🔑 Entrez le mot de passe du certificat : ")
    except EOFError:
        typer.echo("❌ Erreur : Mot de passe non fourni.")
        raise typer.Exit()

    # Demande du chemin du document à signer
    document_path = typer.prompt("📄 Entrez le chemin du document à signer")

    if not os.path.isfile(document_path):
        # Vérifie si le fichier à signer existe
        typer.echo("❌ Erreur : Le fichier à signer n'existe pas !")
        raise typer.Exit()

    try:
        # Ouverture des fichiers certificat et document en mode binaire
        with open(cert_path, 'rb') as cert_file, open(document_path, 'rb') as doc_file:
            # Préparation des fichiers et des données pour l'envoi
            # IMPORTANT: Les noms des paramètres doivent correspondre exactement à ceux attendus par le microservice:
            # - "certificate": paramètre pour le fichier PFX du certificat
            # - "file": paramètre pour le fichier à signer (NE PAS utiliser "document")
            # - "password": paramètre pour le mot de passe du certificat
            files = {"certificate": cert_file, "file": doc_file}
            data = {"password": cert_password}

            # Envoi de la requête HTTP POST à l'API Gateway pour signer le document
            # L'API Gateway transmettra la requête au microservice de signature (/sign/)
            response = requests.post(GATEWAY_URL_sign, files=files, data=data, timeout=10)

            if response.status_code == 200: 
                # Traiter la réponse en cas de succès
                typer.echo("✅ Document signé avec succès !")
                return response.json()  # Retourner la réponse JSON du microservice 
            else:
                # En cas d'erreur HTTP
                typer.echo(f"❌ Erreur lors de la signature du document : {response.status_code} - {response.text}")
                raise typer.Exit()

    except requests.ConnectionError:
        # Gestion des erreurs de connexion
        typer.echo("🚨 Erreur : Impossible de se connecter à l'API Gateway.")
    except requests.Timeout:
        # Gestion des erreurs de timeout
        typer.echo("⏳ Erreur : La requête a expiré.")
    except Exception as e:
        # Gestion des erreurs inattendues
        typer.echo(f"❌ Erreur inattendue : {e}")
        
        

def verify_signature():
    """
    Vérifie la signature d'un document en utilisant un certificat PFX.
    """
    # Demande du chemin du fichier certificat
    cert_path = typer.prompt("📂 Entrez le chemin du fichier certificat PFX")

    if not os.path.isfile(cert_path):
        # Vérifie si le fichier certificat existe
        typer.echo("❌ Erreur : Le fichier certificat n'existe pas !")
        raise typer.Exit()

    # Demande du mot de passe du certificat
    try:
        cert_password = getpass.getpass("🔑 Entrez le mot de passe du certificat : ")
    except EOFError:
        typer.echo("❌ Erreur : Mot de passe non fourni.")
        raise typer.Exit()

    # Demande du chemin du document à vérifier
    document_path = typer.prompt("📄 Entrez le chemin du document à vérifier")

    if not os.path.isfile(document_path):
        # Vérifie si le fichier à vérifier existe
        typer.echo("❌ Erreur : Le fichier à vérifier n'existe pas !")
        raise typer.Exit()

    # Demande du chemin du fichier de signature
    signature_path = typer.prompt("📜 Entrez le chemin du fichier de signature")

    if not os.path.isfile(signature_path):
        # Vérifie si le fichier de signature existe
        typer.echo("❌ Erreur : Le fichier de signature n'existe pas !")
        raise typer.Exit()

    try:
        # Ouverture des fichiers certificat, document et signature en mode binaire
        with open(cert_path, 'rb') as cert_file, open(document_path, 'rb') as doc_file, open(signature_path, 'rb') as sig_file:
            # Préparation des fichiers et des données pour l'envoi
            files = {
                "certificate": ("certificat.pfx", cert_file, "application/x-pkcs12"),
                "document": ("document.pfx", doc_file, "text/plain"),
                "signature_file": ("signature.txt", sig_file, "text/plain"),
            }
            data = {"password": cert_password}
            headers = {"accept": "application/json"}

            # Envoi de la requête HTTP POST à l'API Gateway pour vérifier la signature
            response = requests.post(GATEWAY_URL_verify, files=files, data=data, headers=headers, timeout=10)

            if response.status_code == 200:
                # Traiter la réponse en cas de succès
                result = response.json()
                if result.get("valid"):
                    typer.echo("✅ La signature est valide.")
                else:
                    typer.echo("❌ La signature est invalide.")
                return result  # Retourner la réponse JSON du microservice
            else:
                # En cas d'erreur HTTP
                typer.echo(f"❌ Erreur lors de la vérification de la signature : {response.status_code} - {response.text}")
                raise typer.Exit()

    except requests.ConnectionError:
        # Gestion des erreurs de connexion
        typer.echo("🚨 Erreur : Impossible de se connecter à l'API Gateway.")
    except requests.Timeout:
        # Gestion des erreurs de timeout
        typer.echo("⏳ Erreur : La requête a expiré.")
    except Exception as e:
        # Gestion des erreurs inattendues
        typer.echo(f"❌ Erreur inattendue : {e}")
        
        


# Fonction pour afficher le menu principal
def show_menu():
    """
    Affiche le menu principal dans une box avec le texte en blanc et un logo devant chaque option.
    """
    # Définition du contenu du menu
    menu_lines = [
        "[yellow]🔍 1. Extraire les informations d'un certificat[/yellow]",
        "[green]📝 2. Signer un document[/green]",
        "[blue]🔏 3. Vérifier la signature d'un document[/blue]",
        "[red]🚪 4. Quitter[/red]"
    ]
    menu = "\n".join(menu_lines)  # Fusionner les lignes du menu en une seule chaîne
    # Affichage du menu dans un panneau stylisé avec une largeur réduite
    console.print(Panel(menu, title="[bold cyan]Menu Principal[/bold cyan]", style="blue", width=logo_width))

# Fonction principale qui lance le menu interactif
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Menu interactif principal.
    """
    while True:
        # Affichage du menu principal
        show_menu()

        # Demande à l'utilisateur de faire un choix
        choice = typer.prompt("Entrez le numéro de l'option que vous souhaitez")
        # Affiche deux sauts de ligne avant de lancer la fonction choisie
        console.print("\n\n")

        # Traitement du choix de l'utilisateur
        if choice == "1":
            send_cert()  # Appel de la fonction pour extraire les informations du certificat
        elif choice == "2":
            sign_document()  # Appel de la fonction pour signer un document
        elif choice == "3":
            verify_signature()  # Appel de la fonction pour vérifier la signature
        elif choice == "4":
            typer.echo("Au revoir! 👋")  # Message de départ
            raise typer.Exit()  # Quitte l'application
        else:
            typer.echo("❌ Option invalide, veuillez réessayer.")  # Message d'erreur si l'option est invalide

        # Pause pour laisser le temps à l'utilisateur de consulter le résultat avant de revenir au menu
        typer.prompt("Appuyez sur une touche puis sur Entrée pour revenir au menu")

# Si ce fichier est exécuté directement, l'application Typer est lancée
if __name__ == "__main__":
    app()
