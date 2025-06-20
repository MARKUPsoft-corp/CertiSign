# CertiSign - Solution de Signature Électronique

CertiSign est une solution complète pour la gestion des certificats numériques et la signature électronique de documents. Le système permet aux utilisateurs de signer des documents PDF, de vérifier des signatures, et offre une interface d'administration pour gérer les utilisateurs et les certificats.

## Architecture

Le projet est organisé en plusieurs composants :

- **Frontend** : Application Vue.js avec une interface utilisateur moderne et réactive
- **Backend** : API REST Django pour la gestion des utilisateurs, des certificats et des documents
- **Microservice de Signature** : Service dédié à la signature et vérification de documents PDF
- **API Gateway** : Point d'entrée unifié pour accéder aux différents services

## Fonctionnalités

### Pour les utilisateurs
- Connexion sécurisée avec certificat électronique
- Tableau de bord personnalisé
- Signature de documents PDF
- Vérification de signatures existantes
- Gestion des certificats personnels

### Pour les administrateurs
- Interface d'administration complète
- Gestion des utilisateurs
- Suivi des activités
- Statistiques d'utilisation
- Paramètres de sécurité configurables

## Installation

### Prérequis
- Python 3.8 ou supérieur
- Node.js 14 ou supérieur
- npm ou yarn

### Installation du Backend

```bash
# Se positionner dans le répertoire backend
cd backend/django

# Exécuter le script d'installation
./setup.sh
```

Le script d'installation va :
- Créer un environnement virtuel Python
- Installer les dépendances
- Créer la base de données
- Appliquer les migrations
- Charger des données de test
- Collecter les fichiers statiques

### Installation du Frontend

```bash
# Se positionner dans le répertoire frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run serve
```

## Utilisation

### Démarrer le backend
```bash
cd backend/django
.venv/bin/python manage.py runserver
```

### Démarrer le frontend
```bash
cd frontend
npm run serve
```

### Accès à l'application
- Frontend: http://localhost:8080
- API Backend: http://localhost:8000/api
- Admin Django: http://localhost:8000/admin

### Comptes de test
- Administrateur : admin / password
- Utilisateur : jean.dupont / password

## Sécurité

Le système a été conçu avec une attention particulière à la sécurité :
- Communications chiffrées entre les services
- Gestion sécurisée des certificats
- Validation complète des signatures
- Journalisation des activités
- Protection contre les attaques courantes

## Développement

### Structure du projet

```
certisign/
├── frontend/                    # Application Vue.js
│   ├── public/
│   └── src/
│       ├── assets/
│       ├── components/
│       ├── router/
│       ├── services/
│       ├── views/
│       └── App.vue
│
├── backend/                     # API Django
│   └── django/
│       ├── certisign/
│       │   ├── management/
│       │   ├── migrations/
│       │   ├── models.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   ├── urls.py
│       │   └── views.py
│       ├── media/
│       ├── static/
│       └── manage.py
│
└── docs/                        # Documentation
```

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Contact

Pour toute question ou support, veuillez contacter l'équipe de développement à support@certisign.fr.
