"""
Utilitaires pour gérer les opérations SFTP de manière robuste
"""
import logging
from django.http import FileResponse, HttpResponse
from django.core.files.storage import default_storage
from django.conf import settings
import tempfile
import os

logger = logging.getLogger(__name__)

def get_sftp_preview_response(file_field, content_type='application/pdf'):
    """
    Crée une FileResponse pour afficher un fichier PDF dans l'iframe (pas de téléchargement).
    Gère les erreurs de connexion et les timeouts.
    """
    try:
        # Vérifier que le fichier existe
        if not file_field or not file_field.name:
            return HttpResponse("Fichier non trouvé", status=404)
        
        # Utiliser le storage du champ pour ouvrir le fichier
        storage = file_field.storage
        
        if not storage.exists(file_field.name):
            logger.error(f"Fichier SFTP non trouvé: {file_field.name}")
            return HttpResponse("Fichier non trouvé sur le serveur", status=404)
        
        # Créer un fichier temporaire local
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Copier le contenu du fichier SFTP vers le fichier temporaire
            with storage.open(file_field.name, 'rb') as sftp_file:
                temp_file.write(sftp_file.read())
            
            temp_file_path = temp_file.name
        
        # Créer la réponse avec le fichier temporaire
        response = FileResponse(
            open(temp_file_path, 'rb'),
            content_type=content_type
        )
        
        # Headers pour permettre l'affichage dans iframe
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Content-Security-Policy'] = "frame-ancestors 'self'"
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        # IMPORTANT: Pas de Content-Disposition pour l'affichage dans l'iframe
        # Le navigateur affichera le PDF directement
        
        # Ajouter un callback pour supprimer le fichier temporaire
        response._temp_file_path = temp_file_path
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage SFTP: {str(e)}")
        return HttpResponse(f"Erreur lors de l'affichage: {str(e)}", status=500)

def get_sftp_file_response(file_field, filename=None, content_type='application/octet-stream'):
    """
    Crée une FileResponse pour un fichier stocké sur SFTP.
    Gère les erreurs de connexion et les timeouts.
    """
    try:
        # Vérifier que le fichier existe
        if not file_field or not file_field.name:
            return HttpResponse("Fichier non trouvé", status=404)
        
        # Utiliser le storage du champ pour ouvrir le fichier
        storage = file_field.storage
        
        if not storage.exists(file_field.name):
            logger.error(f"Fichier SFTP non trouvé: {file_field.name}")
            return HttpResponse("Fichier non trouvé sur le serveur", status=404)
        
        # Créer un fichier temporaire local
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Copier le contenu du fichier SFTP vers le fichier temporaire
            with storage.open(file_field.name, 'rb') as sftp_file:
                temp_file.write(sftp_file.read())
            
            temp_file_path = temp_file.name
        
        # Créer la réponse avec le fichier temporaire
        response = FileResponse(
            open(temp_file_path, 'rb'),
            content_type=content_type
        )
        
        # Définir le nom du fichier pour le téléchargement
        if filename:
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_field.name)}"'
        
        # Ajouter un callback pour supprimer le fichier temporaire
        def cleanup_temp_file():
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
        
        # Utiliser une approche plus simple pour la gestion du fichier temporaire
        # Le fichier sera supprimé automatiquement par le système
        response._temp_file_path = temp_file_path
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement SFTP: {str(e)}")
        return HttpResponse(f"Erreur lors du téléchargement: {str(e)}", status=500)

def check_sftp_connection():
    """
    Vérifie la connexion SFTP et retourne un objet SFTP utilisable.
    """
    try:
        import paramiko
        from decouple import config
        
        # Paramètres de connexion SFTP
        host = config('SFTP_HOST', default='192.168.2.102')
        username = config('SFTP_USERNAME', default='ssatl')
        password = config('SFTP_PASSWORD', default='Ssatl.01')
        port = config('SFTP_PORT', default=22, cast=int)
        
        # Créer une connexion SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Se connecter
        ssh_client.connect(host, port, username, password, timeout=30)
        
        # Ouvrir une session SFTP
        sftp_client = ssh_client.open_sftp()
        
        return True, sftp_client
        
    except Exception as e:
        logger.error(f"Erreur de connexion SFTP: {str(e)}")
        return False, str(e)

def get_file_size_sftp(file_field):
    """
    Récupère la taille d'un fichier sur SFTP.
    """
    try:
        if not file_field or not file_field.name:
            return 0
        
        storage = file_field.storage
        if hasattr(storage, 'size'):
            return storage.size(file_field.name)
        else:
            # Fallback: lire le fichier pour obtenir la taille
            with storage.open(file_field.name, 'rb') as f:
                f.seek(0, 2)  # Aller à la fin
                return f.tell()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la taille: {str(e)}")
        return 0

def delete_sftp_file(file_field):
    """
    Supprime un fichier sur SFTP de manière sécurisée.
    """
    try:
        if not file_field or not file_field.name:
            return False
        
        storage = file_field.storage
        if storage.exists(file_field.name):
            storage.delete(file_field.name)
            return True
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression SFTP: {str(e)}")
        return False 