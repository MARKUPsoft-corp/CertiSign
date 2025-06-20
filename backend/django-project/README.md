# CertiSign - Backend Django

Ce projet est le backend principal de l'application CertiSign, permettant la gestion des utilisateurs, des organisations et des signatures électroniques.

## Fonctionnalités

- Authentification par identifiants ou certificat numérique
- Gestion des utilisateurs avec différents rôles (Super Admin, Admin, Utilisateur)
- Gestion des organisations
- Système d'approbation de comptes
- Journal d'activités complet
- API REST complète

## Prérequis

- Python 3.8 ou supérieur
- PostgreSQL 13 ou supérieur

## Installation

1. Clonez ce dépôt
2. Créez un environnement virtuel Python :
   ```
   python -m venv venv
   ```
3. Activez l'environnement virtuel :
   - Sous Windows : `venv\Scripts\activate`
   - Sous Linux/Mac : `source venv/bin/activate`
4. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```
5. Configurez les variables d'environnement :
   - Copiez le fichier `.env.example` vers `.env`
   - Modifiez les valeurs selon votre environnement
6. Créez la base de données PostgreSQL :
   ```
   createdb certisign
   ```
7. Appliquez les migrations :
   ```
   python manage.py migrate
   ```
8. Créez un superutilisateur :
   ```
   python manage.py createsuperuser
   ```

## Utilisation

Pour démarrer le serveur de développement :
```
python manage.py runserver
```

Le serveur sera accessible à l'adresse : http://127.0.0.1:8000/

L'interface d'administration est disponible à : http://127.0.0.1:8000/admin/

La documentation de l'API est disponible à :
- Format Swagger : http://127.0.0.1:8000/swagger/
- Format ReDoc : http://127.0.0.1:8000/redoc/

## Structure du projet

- `certisign_project/` - Configuration principale du projet Django
- `users/` - Application pour la gestion des utilisateurs, organisations et authentification
- `documents/` - (À venir) Application pour la gestion des documents et signatures

## API Endpoints

### Authentification
- `POST /api/users/auth/login/` - Connexion par identifiants
- `POST /api/users/auth/certificate/` - Connexion par certificat

### Utilisateurs
- `GET /api/users/users/` - Liste des utilisateurs (admin uniquement)
- `POST /api/users/users/` - Créer un utilisateur (admin uniquement)
- `GET /api/users/users/{id}/` - Détails d'un utilisateur
- `PUT/PATCH /api/users/users/{id}/` - Modifier un utilisateur
- `DELETE /api/users/users/{id}/` - Supprimer un utilisateur (admin uniquement)
- `POST /api/users/users/{id}/approve/` - Approuver un utilisateur
- `POST /api/users/users/{id}/reject/` - Rejeter un utilisateur
- `GET /api/users/me/` - Informations sur l'utilisateur actuel

### Organisations
- `GET /api/users/organizations/` - Liste des organisations
- `POST /api/users/organizations/` - Créer une organisation (admin uniquement)
- `GET /api/users/organizations/{id}/` - Détails d'une organisation
- `PUT/PATCH /api/users/organizations/{id}/` - Modifier une organisation (admin uniquement)
- `DELETE /api/users/organizations/{id}/` - Supprimer une organisation (admin uniquement)

### Journal d'activités
- `GET /api/users/activities/` - Liste des activités 