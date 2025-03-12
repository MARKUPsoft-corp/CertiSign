import typer  # Bibliothèque pour créer des interfaces en ligne de commande (CLI)
import requests  # Permet d'envoyer des requêtes HTTP à une API
import os  # Utilisé pour vérifier l'existence d'un fichier ou d'un répertoire
import getpass  # Permet de masquer l'entrée du mot de passe
import time  # Utilisé pour la simulation du temps d'extraction
from rich.progress import Progress, BarColumn, TextColumn  # Rich est utilisé pour afficher une barre de progression colorée
from rich.console import Console  # Console pour afficher des éléments stylisés
from rich.panel import Panel  # Permet d'afficher une boîte encadrée
from rich.text import Text  # Permet de styliser du texte

# Création de l'application CLI avec Typer
app = typer.Typer()
console = Console()

# URL de l'API Gateway pour envoyer le certificat
GATEWAY_URL = "http://localhost:8000/gateway/cert_info/"  # Remplace par ton URL d'API

# Logo ASCII pour CertiSign
LOGO_CERTISIGN = """
 ██████╗ ███████╗██████╗ ████████╗██╗███████╗██╗ ██████╗ ███╗   ██╗
██╔════╝ ██╔════╝██╔══██╗╚══██╔══╝██║██╔════╝██║██╔═══██╗████╗  ██║
██║  ███╗█████╗  ██████╔╝   ██║   ██║███████╗██║██║   ██║██╔██╗ ██║
██║   ██║██╔══╝  ██╔══██╗   ██║   ██║╚════██║██║██║   ██║██║╚██╗██║
╚██████╔╝███████╗██║  ██║   ██║   ██║███████║██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""


# Afficher le logo stylisé au démarrage
console.print(Panel.fit(Text(LOGO_CERTISIGN, style="cyan bold"), title="🔐 CertiSign - Signez en un cli", style="blue"))


@app.command()
def send_cert():
    """
    Envoie un certificat PFX à l'API Gateway et affiche les informations du certificat.
    """

    # Demander le chemin du certificat à l'utilisateur
    cert_path = typer.prompt("📂 Entrez le chemin du fichier certificat PFX")

    # Vérification que le chemin donné n'est pas un répertoire
    if os.path.isdir(cert_path):
        typer.echo("❌ Erreur : Chemin invalide, c'est un répertoire !")
        raise typer.Exit()  # Quitte le programme avec une erreur

    # Vérification que le fichier existe bien
    if not os.path.isfile(cert_path):
        typer.echo("❌ Erreur : Fichier non trouvé !")
        raise typer.Exit()  # Quitte le programme avec une erreur

    # Demander le mot de passe de manière sécurisée
    password = getpass.getpass("🔑 Entrez le mot de passe du certificat : ")

    try:
        # Ouverture du fichier en mode lecture binaire
        with open(cert_path, 'rb') as file:
            files = {'file': file}  # Charge le fichier sous forme de données binaires
            data = {'password': password}  # Stocke le mot de passe pour l'envoyer avec la requête

            # Affichage d'une barre de progression pour l'extraction du certificat
            with Progress(
                TextColumn("🔄 Extraction en cours..."),  # Message affiché à l'écran
                BarColumn(),  # Affiche une barre de progression
                TextColumn("[green]{task.percentage:>3.0f}%")  # Affiche le pourcentage de progression en vert
            ) as progress:
                task = progress.add_task("Extracting", total=100)  # Ajoute une tâche avec un total de 100%

                # Simulation d'une extraction en 10 étapes
                for _ in range(10):
                    time.sleep(0.2)  # Pause de 0.2 secondes pour simuler le chargement
                    progress.update(task, advance=10)  # Augmente la progression de 10%

            # Message de succès après extraction
            typer.echo("✅ SUCCÈS : Extraction terminée !\n")

            # Envoi des données à l'API Gateway
            response = requests.post(GATEWAY_URL, files=files, data=data, timeout=10)

        # Vérification de la réponse de l'API
        if response.status_code == 200:
            # Récupération des informations du certificat sous forme de texte formaté
            cert_info = "\n".join([f"🔹 {key}: {value}" for key, value in response.json().items()])
            
            # Affichage des informations encadrées dans une boîte verte
            console.print(Panel(cert_info, title="🔍 Informations du certificat", style="green"))

        else:
            # Affiche l'erreur retournée par l'API si le statut n'est pas 200
            typer.echo(f"⚠️ Erreur {response.status_code}: {response.text}")

    # Gestion des erreurs de connexion
    except requests.ConnectionError:
        typer.echo("🚨 Erreur : Impossible de se connecter à l'API Gateway.")

    # Gestion des erreurs de timeout
    except requests.Timeout:
        typer.echo("⏳ Erreur : La requête a expiré.")

    # Gestion des erreurs générales
    except Exception as e:
        typer.echo(f"❌ Erreur inattendue : {e}")

# Exécution du programme en mode CLI
if __name__ == "__main__":
    app()
