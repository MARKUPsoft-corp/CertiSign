"""
Storage personnalisé pour forcer l'utilisation du SFTPStorage
"""
from storages.backends.sftpstorage import SFTPStorage
from django.conf import settings

class CertiSignSFTPStorage(SFTPStorage):
    """
    Storage personnalisé pour CertiSign qui utilise SFTP.
    Force l'utilisation du SFTPStorage même si Django utilise un autre storage par défaut.
    """
    
    def __init__(self, *args, **kwargs):
        # Utiliser les paramètres SFTP depuis les settings
        kwargs.update({
            'host': getattr(settings, 'SFTP_STORAGE_HOST', '192.168.2.102'),
            'root_path': getattr(settings, 'SFTP_STORAGE_ROOT', '/mnt/NFS_Storage_Pool2/Disk1/ssatl/media/'),
            'params': getattr(settings, 'SFTP_STORAGE_PARAMS', {}),
        })
        super().__init__(*args, **kwargs)
    
    def get_accessed_time(self, name):
        """Retourne le temps d'accès du fichier"""
        return super().get_accessed_time(name)
    
    def get_created_time(self, name):
        """Retourne le temps de création du fichier"""
        return super().get_created_time(name)
    
    def get_modified_time(self, name):
        """Retourne le temps de modification du fichier"""
        return super().get_modified_time(name)

# Instance globale du storage SFTP
sftp_storage = CertiSignSFTPStorage() 