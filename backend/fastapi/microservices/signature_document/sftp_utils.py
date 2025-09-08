"""
Utilitaires pour accéder aux fichiers SFTP depuis le microservice
"""
import os
import paramiko
import logging
from typing import Optional, Tuple
from decouple import config

logger = logging.getLogger(__name__)

class SFTPClient:
    """Client SFTP pour accéder aux fichiers"""
    
    def __init__(self):
        self.host = config('SFTP_HOST', default='192.168.2.102')
        self.username = config('SFTP_USERNAME', default='ssatl')
        self.password = config('SFTP_PASSWORD', default='Ssatl.01')
        self.port = config('SFTP_PORT', default=22, cast=int)
        self.root_path = config('SFTP_ROOT_PATH', default='/mnt/NFS_Storage_Pool2/Disk1/ssatl/media/')
        
    def connect(self) -> Tuple[bool, Optional[paramiko.SFTPClient]]:
        """Établit une connexion SFTP"""
        try:
            # Créer le client SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Se connecter
            ssh.connect(
                self.host, 
                port=self.port, 
                username=self.username, 
                password=self.password, 
                timeout=30
            )
            
            # Ouvrir la session SFTP
            sftp = ssh.open_sftp()
            return True, sftp
            
        except Exception as e:
            logger.error(f"Erreur de connexion SFTP: {str(e)}")
            return False, None
    
    def read_file(self, file_path: str) -> Optional[bytes]:
        """Lit un fichier depuis SFTP"""
        success, sftp = self.connect()
        if not success:
            return None
        
        try:
            # Construire le chemin complet
            full_path = os.path.join(self.root_path, file_path)
            
            # Vérifier que le fichier existe
            try:
                sftp.stat(full_path)
            except FileNotFoundError:
                logger.error(f"Fichier SFTP non trouvé: {full_path}")
                return None
            
            # Lire le fichier
            with sftp.file(full_path, 'rb') as f:
                content = f.read()
                logger.info(f"Fichier SFTP lu avec succès: {full_path} ({len(content)} octets)")
                return content
                
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier SFTP {file_path}: {str(e)}")
            return None
        finally:
            try:
                sftp.close()
                sftp.get_channel().close()
            except:
                pass

# Instance globale
sftp_client = SFTPClient()

def get_sftp_file_content(file_path: str) -> Optional[bytes]:
    """Fonction utilitaire pour lire un fichier SFTP"""
    return sftp_client.read_file(file_path) 