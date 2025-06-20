# Introduction au Front-end

Le frontend de CertiSign est une application Vue.js moderne qui offre une interface utilisateur intuitive pour la gestion des certificats et la signature électronique de documents.

## Technologies utilisées

- **Framework** : Vue.js avec Nuxt.js
- **UI Framework** : Bootstrap
- **Gestion d'état** : Vuex
- **Routage** : Vue Router
- **Communication API** : Axios

## Structure du projet

Le code source du frontend est organisé selon les meilleures pratiques Vue.js :

```
frontend/
├── public/               # Fichiers statiques
├── src/                  # Code source
│   ├── assets/           # Images, styles, etc.
│   ├── components/       # Composants réutilisables
│   ├── router/           # Configuration du routage
│   ├── services/         # Services pour les appels API
│   ├── store/            # Gestion de l'état (Vuex)
│   ├── views/            # Pages/vues de l'application
│   ├── App.vue           # Composant racine
│   └── main.js           # Point d'entrée
├── package.json          # Dépendances et scripts
└── vue.config.js         # Configuration de Vue
```

## Fonctionnalités principales

- **Authentification sécurisée** avec support pour les certificats électroniques
- **Tableau de bord** avec statistiques et activités récentes
- **Gestion de documents** pour télécharger, signer et vérifier les documents
- **Gestion des certificats** pour créer, importer et gérer des certificats
- **Interface d'administration** pour les utilisateurs avec droits élevés

## Mise en route

Pour démarrer le frontend en mode développement :

```bash
# Se positionner dans le répertoire frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run serve
```

L'application sera disponible à l'adresse [http://localhost:8080](http://localhost:8080).

## Build de production

Pour construire la version de production :

```bash
npm run build
```

Les fichiers générés seront disponibles dans le répertoire `dist/`. 