# CertiSign - Solution de Signature Électronique

> 🔐 **Sécuriser et signer vos transactions facilement !**

## Présentation

CertiSign est une solution complète pour la gestion des certificats numériques et la signature électronique de documents. Le système permet aux utilisateurs de signer des documents PDF, de vérifier des signatures, et offre une interface d'administration pour gérer les utilisateurs et les certificats.

## Fonctionnalités principales

- 📜 **Signature électronique** (PDF, XML, TXT)
- 🔑 **Chiffrement & déchiffrement sécurisé**
- ✅ **Validation des certificats PKI (CRL, OCSP, OID)**
- 🛡️ **Sécurité contre les attaques (replay, injection, DDoS)**
- 📊 **Tableau de bord personnalisé**
- 👥 **Gestion des utilisateurs**
- 📈 **Statistiques d'utilisation**

## Architecture du système

CertiSign est architecturé autour de plusieurs composants qui travaillent ensemble pour offrir une solution complète et sécurisée:

=== "Front-end"
    - 📌 **Technologie** : Vue.js + Nuxt.js  
    - 🎨 **UI Framework** : Bootstrap  
    - 🔗 **Consommation API** : `fetch()` & `axios`  

    ```javascript
    fetch('/api/auth', { method: 'POST', body: JSON.stringify({ user }) })
    ```

=== "Back-end"
    - ⚙️ **Technologie** : Django + FastAPI  
    - 🔐 **Sécurité** : JWT, OAuth2  
    - 📡 **API Endpoints** : `/auth/login`, `/users/`  

    ```python
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/api/auth")
    async def authenticate():
        return {"message": "Authentifié"}
    ```

## Pour commencer

Consultez les sections suivantes pour plonger dans la documentation détaillée:

- **[Front-end](frontend/index.md)** - Découvrez l'interface utilisateur et ses composants
- **[Back-end](backend/index.md)** - Explorez l'API REST et les services
- **[Déploiement](deploy.md)** - Instructions pour déployer CertiSign
- **[À propos](about.md)** - Informations sur le projet et les contributeurs

![Logo CertiSign]("/home/markup/Images/Captures d'écran/test.png")
