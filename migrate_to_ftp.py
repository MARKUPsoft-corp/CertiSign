import os
import ftplib
import getpass

# --- Configuration ---

FTP_HOST = '192.168.2.102'
FTP_USER = 'votre_nom_utilisateur_ici'  
FTP_PASS = 'votre_mot_de_passe_ici'      
REMOTE_BASE_PATH = '/mtn/NFS_Storage_Pool2/Disk1/ssatl/media/'

# Chemin vers votre dossier media local (ne pas modifier)
LOCAL_MEDIA_ROOT = os.path.join(os.getcwd(), 'media')

# --- Fonctions ---
def ensure_ftp_dir(ftp, path):
    """S'assure qu'un répertoire existe sur le serveur FTP, le crée sinon."""
    parts = path.strip('/').split('/')
    current_path = ''
    for part in parts:
        if not part:
            continue
        # Pour les chemins absolus, le premier "part" commence par une barre oblique
        if not current_path:
            current_path = '/' + part
        else:
            current_path += '/' + part
        
        try:
            ftp.cwd(current_path)
        except ftplib.error_perm:
            print(f"Création du répertoire : {current_path}")
            ftp.mkd(current_path)
            ftp.cwd(current_path)

# --- Script principal ---
def main():
    """Fonction principale pour la migration des fichiers."""
    if not os.path.isdir(LOCAL_MEDIA_ROOT):
        print(f"Erreur : Le dossier local '{LOCAL_MEDIA_ROOT}' n'a pas été trouvé.")
        return

    # Utiliser les identifiants fournis ou demander le mot de passe de manière sécurisée
    ftp_user = FTP_USER
    ftp_password = FTP_PASS
    if ftp_user == 'votre_nom_utilisateur_ici':
        ftp_user = input("Entrez votre nom d'utilisateur FTP : ")
    if ftp_password == 'votre_mot_de_passe_ici':
        ftp_password = getpass.getpass(f"Entrez le mot de passe pour l'utilisateur '{ftp_user}': ")

    print(f"Connexion au serveur FTP : {FTP_HOST}...")
    try:
        with ftplib.FTP(FTP_HOST, ftp_user, ftp_password) as ftp:
            print("Connexion réussie.")

            # Se positionner dans le répertoire de base sur le serveur FTP
            print(f"Vérification du répertoire de destination : {REMOTE_BASE_PATH}")
            ensure_ftp_dir(ftp, REMOTE_BASE_PATH)
            ftp.cwd(REMOTE_BASE_PATH)
            print(f"Répertoire de destination sur le FTP : {ftp.pwd()}")

            # Parcourir le dossier media local
            for root, dirs, files in os.walk(LOCAL_MEDIA_ROOT):
                relative_path = os.path.relpath(root, LOCAL_MEDIA_ROOT)
                current_remote_dir = REMOTE_BASE_PATH
                if relative_path != '.':
                    current_remote_dir = os.path.join(REMOTE_BASE_PATH, relative_path).replace('\\', '/')
                
                # Créer les sous-dossiers sur le FTP si nécessaire
                ensure_ftp_dir(ftp, current_remote_dir)
                ftp.cwd(current_remote_dir)

                # Transférer les fichiers
                for filename in files:
                    local_file_path = os.path.join(root, filename)
                    print(f"  -> Transfert de '{filename}' vers '{ftp.pwd()}'...")
                    with open(local_file_path, 'rb') as f:
                        ftp.storbinary(f'STOR {filename}', f)

            print("\nMigration terminée avec succès !")

    except ftplib.all_errors as e:
        print(f"\nErreur FTP : {e}")
        print("Veuillez vérifier vos identifiants et le chemin de destination.")

if __name__ == "__main__":
    main()
