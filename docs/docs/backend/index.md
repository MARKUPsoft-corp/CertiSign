# Introduction au Back-end

Le backend de CertiSign est composé de plusieurs services travaillant ensemble pour fournir une solution complète de signature électronique. Il est principalement construit avec Django et FastAPI.

## Technologies utilisées

- **Framework principal** : Django
- **API REST** : Django REST Framework
- **Microservices** : FastAPI
- **Authentification** : JWT, OAuth2
- **Base de données** : PostgreSQL
- **Cache** : Redis
- **File d'attente** : Celery
- **Conteneurisation** : Docker

## Architecture

L'architecture backend est composée des éléments suivants :

1. **API REST Django** : Gestionnaire principal pour les utilisateurs, documents et certificats
2. **Microservice FastAPI** : Service dédié à la signature et validation cryptographique
3. **Base de données PostgreSQL** : Stockage persistant des données
4. **Redis** : Gestion du cache et des sessions
5. **Celery** : Traitement asynchrone des tâches lourdes

```
        +-------------+
        |  Front-end  |
        +------+------+
               |
               v
        +------+------+
        | API Gateway  +--------+
        +------+------+        |
               |                |
     +---------+---------+     |
     |                   |     |
+----v-----+       +-----v----+
| Django   |       | FastAPI  |
| REST API |       | Micro-   |
+----+-----+       | service  |
     |              +-----+----+
     |                    |
+----v----+               |
|Postgres |               |
+---------+               |
     ^                    |
     |                    |
     +--------------------+
```

## Structure du projet Django

```
backend/django/
├── manage.py
├── config/                  # Configuration globale
├── apps/
│   ├── users/               # Gestion des utilisateurs
│   ├── documents/           # Gestion des documents
│   ├── certificates/        # Gestion des certificats
│   └── audit/               # Journal d'audit
├── utils/                   # Fonctions utilitaires
│   ├── crypto/              # Utilitaires cryptographiques
│   └── validators/          # Validateurs
├── templates/               # Templates Django
└── static/                  # Fichiers statiques
```

## Structure du microservice FastAPI

```
backend/fastapi/
├── main.py                  # Point d'entrée
├── app/
│   ├── api/                 # Définition des endpoints
│   ├── core/                # Configuration centrale
│   ├── models/              # Modèles de données
│   ├── services/            # Logique métier
│   │   ├── signature/       # Service de signature
│   │   ├── validation/      # Service de validation
│   │   └── crypto/          # Services cryptographiques
│   └── utils/               # Fonctions utilitaires
└── tests/                   # Tests unitaires et d'intégration
```

## Mise en route

Pour démarrer le backend en mode développement :

### Django

```bash
# Se positionner dans le répertoire backend/django
cd backend/django

# Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sous Linux/Mac
# ou
.venv\Scripts\activate     # Sous Windows

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

### FastAPI

```bash
# Se positionner dans le répertoire backend/fastapi
cd backend/fastapi

# Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sous Linux/Mac
# ou
.venv\Scripts\activate     # Sous Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
uvicorn app.main:app --reload
```

## Sécurité

Le backend implémente plusieurs couches de sécurité :

- **Authentification JWT** avec tokens d'accès et de rafraîchissement
- **Validation des certificats** via CRL et OCSP
- **Protection contre les injections** par validation des entrées
- **Throttling** pour limiter les tentatives d'attaque par force brute
- **Journalisation des événements** pour l'audit et la détection des anomalies
- **Chiffrement des données sensibles** au repos et en transit

Pour plus de détails sur les différents aspects du backend, consultez les sections suivantes :

- [API REST](api_rest.md) - Détails sur les endpoints disponibles
- [Authentification](auth.md) - Mécanismes d'authentification et d'autorisation
- [Signature Électronique](signature.md) - Processus de signature et validation 