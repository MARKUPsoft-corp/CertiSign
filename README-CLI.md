# Interface en Ligne de Commande (CLI) pour CertiSign

Ce document décrit comment installer et utiliser l'interface en ligne de commande (CLI) pour interagir avec le service de signature numérique CertiSign.

## Aperçu

La CLI de CertiSign est un outil qui permet aux utilisateurs de :

- Signer numériquement des documents via l'API Gateway
- Vérifier l'authenticité des signatures numériques
- Vérifier l'état de santé du service de signature

Cette approche est particulièrement utile pour intégrer la signature numérique dans des workflows automatisés ou pour les utilisateurs qui préfèrent travailler en ligne de commande.

## Architecture

La CLI s'intègre avec le reste du système CertiSign comme suit :

```
+---------------+           +-------------+           +---------------+
|  CLI          | --------> |  API        | --------> |  Microservice |
|  (signature-  |           |  Gateway    |           |  Signature    |
|   cli)        |           |             |           |               |
+---------------+           +-------------+           +---------------+
```

## Prérequis

- Python 3.6 ou plus récent
- Un environnement virtuel Python (recommandé)
- L'API Gateway et le microservice de signature en fonctionnement
- Un certificat PFX valide

## Installation

1. Clonez le dépôt CertiSign si vous ne l'avez pas déjà fait :
   ```
   git clone <URL_REPO> CertiSign
   cd CertiSign
   ```

2. Créez et activez un environnement virtuel (recommandé) :
   ```
   python3 -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installez la CLI en mode développement :
   ```
   cd backend/fastapi/cli
   pip install -e .
   ```

## Configuration

Par défaut, la CLI est configurée pour se connecter à l'API Gateway sur `http://localhost:8000/gateway`. Si votre API Gateway est déployée à une autre adresse, vous devez modifier la variable `API_GATEWAY_URL` dans le fichier `signature_cli.py`.

## Démarrage des services

Avant d'utiliser la CLI, assurez-vous que les services suivants sont en cours d'exécution :

1. L'API Gateway :
   ```
   cd backend/fastapi/api_gateway
   uvicorn main:app --reload --port 8000
   ```

2. Le microservice de signature :
   ```
   cd backend/fastapi/microservices/signature_document
   uvicorn main:app --reload --port 8002
   ```

## Commandes disponibles

### Vérifier l'état du service

```
signature-cli health
```

### Signer un document

```
signature-cli sign --certificate CHEMIN_CERTIFICAT.pfx --password MOT_DE_PASSE --document CHEMIN_DOCUMENT.pdf [--output DOSSIER_SORTIE]
```

### Vérifier une signature

```
signature-cli verify --certificate CHEMIN_CERTIFICAT.pfx --password MOT_DE_PASSE --document CHEMIN_DOCUMENT.pdf --signature CHEMIN_SIGNATURE.sig
```

### Obtenir de l'aide

```
signature-cli --help
```

## Exemples d'utilisation

### Exemple 1 : Signer un document PDF

```bash
signature-cli sign --certificate mon_cert.pfx --password MonMotDePasse --document rapport.pdf --output documents_signes
```

### Exemple 2 : Vérifier une signature

```bash
signature-cli verify --certificate mon_cert.pfx --password MonMotDePasse --document rapport.pdf --signature rapport.sig
```

## Intégration avec d'autres outils

### Script bash pour signer plusieurs documents

```bash
#!/bin/bash
# Script pour signer tous les PDFs d'un répertoire

CERT_PATH="chemin/vers/certificat.pfx"
CERT_PASSWORD="MotDePasse"
OUTPUT_DIR="documents_signes"

# Créer le répertoire de sortie
mkdir -p $OUTPUT_DIR

# Signer tous les PDFs du répertoire courant
for pdf in *.pdf; do
  echo "Signature de $pdf..."
  signature-cli sign --certificate $CERT_PATH --password $CERT_PASSWORD --document "$pdf" --output $OUTPUT_DIR
done

echo "Tous les documents ont été signés!"
```

## Dépannage

### Problèmes de connexion

Si vous rencontrez des problèmes de connexion à l'API Gateway :

1. Vérifiez que l'API Gateway est en cours d'exécution avec `signature-cli health`
2. Vérifiez que la configuration de l'URL dans la CLI est correcte
3. Assurez-vous que les ports nécessaires sont ouverts (8000 pour l'API Gateway, 8002 pour le microservice)

### Erreurs de signature

Si vous rencontrez des erreurs lors de la signature :

1. Vérifiez que le certificat PFX est valide
2. Assurez-vous que le mot de passe du certificat est correct
3. Vérifiez que le document est accessible et n'est pas corrompu

## Avancé : Configuration de l'environnement de développement

Pour les développeurs qui souhaitent modifier ou améliorer la CLI :

1. Installez les dépendances en mode développement :
   ```
   cd backend/fastapi/cli
   pip install -e ".[dev]"
   ```

2. Exécutez les tests :
   ```
   pytest
   ```

3. Vérifiez le style du code :
   ```
   flake8 signature_cli.py
   ```

## Documentation complémentaire

- Pour plus de détails sur le microservice de signature, consultez la documentation dans `backend/fastapi/microservices/signature_document/README.md`
- Pour plus d'informations sur la CLI, consultez la documentation spécifique dans `backend/fastapi/cli/README.md` 