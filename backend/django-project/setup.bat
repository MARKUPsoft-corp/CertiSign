@echo off
echo Initialisation du projet CertiSign...

REM Activer l'environnement virtuel
call venv\Scripts\activate

REM Installer les dépendances
echo Installation des dépendances...
pip install -r requirements.txt

REM Créer le projet Django s'il n'existe pas
if not exist "certisign_project" (
    echo Création du projet Django...
    django-admin startproject certisign_project .
)

REM Créer l'application utilisateurs
if not exist "users" (
    echo Création de l'application utilisateurs...
    python manage.py startapp users
)

REM Créer les migrations
echo Création des migrations...
python manage.py makemigrations

REM Appliquer les migrations
echo Application des migrations...
python manage.py migrate

REM Créer un superutilisateur si demandé
set /p create_superuser="Voulez-vous créer un superutilisateur? (o/n): "
if /i "%create_superuser%"=="o" (
    python manage.py createsuperuser
)

echo Configuration terminée!
echo Pour démarrer le serveur: python manage.py runserver 