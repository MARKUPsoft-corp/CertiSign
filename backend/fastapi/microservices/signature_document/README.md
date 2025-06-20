# Service de Signature Numérique pour Documents PDF

Ce microservice permet de signer numériquement des documents PDF (et autres types de fichiers) en utilisant des certificats PFX. Il offre deux fonctionnalités principales :

1. **Signature numérique de documents**
2. **Vérification de signatures numériques**

## Caractéristiques

- Signature robuste avec hachage SHA-256 et algorithme PSS pour une sécurité maximale
- Compatible avec tous types de fichiers, optimisé pour les PDF
- Détection de toute altération, même minime, des documents signés
- Retour de documents signés avec leur signature dans un package ZIP
- Logs détaillés pour le suivi des opérations
- Interface REST simple et documentée

## Endpoints

### `/sign` - Signer un document

**Méthode:** POST

**Paramètres:**
- `certificate`: Fichier du certificat PFX
- `password`: Mot de passe du certificat
- `document`: Document à signer (PDF recommandé)
- `metadata`: Métadonnées optionnelles pour la signature

**Retourne:**
- Un fichier ZIP contenant :
  - Le document original
  - Le fichier de signature séparé (.sig)
  - Un fichier README avec instructions

### `/verify` - Vérifier une signature

**Méthode:** POST

**Paramètres:**
- `certificate`: Fichier du certificat PFX utilisé pour la signature
- `password`: Mot de passe du certificat
- `document`: Document original dont la signature doit être vérifiée
- `signature`: Fichier de signature (.sig)

**Retourne:**
- Un objet JSON indiquant si la signature est valide

### `/health` - Vérifier l'état du service

**Méthode:** GET

**Retourne:**
- Un objet JSON indiquant l'état du service

## Sécurité de la signature

Le service utilise un processus de signature en deux étapes pour garantir l'intégrité :

1. **Hachage SHA-256** du document complet
2. **Signature du hachage** avec l'algorithme PSS (plus sûr que PKCS#1v15)

Cette approche garantit que toute modification du document, aussi infime soit-elle, sera détectée lors de la vérification.

## Utilisation

### Pour signer un document:

```bash
curl -X POST "http://localhost:8002/sign" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "certificate=@votre_certificat.pfx" \
  -F "password=votre_mot_de_passe" \
  -F "document=@votre_document.pdf" \
  -o document_signe.zip
```

### Pour vérifier une signature:

```bash
curl -X POST "http://localhost:8002/verify" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "certificate=@votre_certificat.pfx" \
  -F "password=votre_mot_de_passe" \
  -F "document=@votre_document.pdf" \
  -F "signature=@votre_document_signature.sig"
```

## Notes techniques

- Le service utilise la bibliothèque `cryptography` pour les opérations cryptographiques
- Les signatures sont encodées en Base64 pour faciliter leur transmission
- Pour les fichiers PDF volumineux, le service optimise la signature en ne signant que le hachage du document, pas son contenu complet 