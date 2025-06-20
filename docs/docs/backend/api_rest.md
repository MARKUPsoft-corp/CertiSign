# API REST

CertiSign expose plusieurs API REST pour interagir avec le système. Cette documentation détaille les endpoints disponibles, les méthodes HTTP supportées, les paramètres requis et les réponses attendues.

## Base URL

```
https://api.certisign.com/api/v1/
```

Pour l'environnement de développement :

```
http://localhost:8000/api/v1/
```

## Format des réponses

Toutes les réponses sont au format JSON et suivent une structure commune :

- Pour les requêtes réussies :

```json
{
  "status": "success",
  "data": { ... },  // Les données demandées
  "meta": { ... }   // Métadonnées (pagination, etc.)
}
```

- Pour les erreurs :

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Description de l'erreur",
    "details": { ... }  // Détails supplémentaires (facultatif)
  }
}
```

## Authentification

La plupart des endpoints nécessitent une authentification. CertiSign utilise l'authentification par token JWT.

Pour vous authentifier, ajoutez un header HTTP `Authorization` à vos requêtes :

```
Authorization: Bearer <votre_token_jwt>
```

## Endpoints

### Authentification

#### POST /auth/login

Connecte un utilisateur et renvoie des tokens d'accès et de rafraîchissement.

**Corps de la requête :**

```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

#### POST /auth/refresh

Rafraîchit un token d'accès expiré.

**Corps de la requête :**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

#### POST /auth/logout

Déconnecte l'utilisateur en révoquant son token.

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "message": "Successfully logged out"
  }
}
```

### Utilisateurs

#### GET /users/me

Récupère les informations de l'utilisateur connecté.

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "john.doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "created_at": "2023-01-15T10:30:15Z",
    "last_login": "2023-03-10T14:20:30Z"
  }
}
```

#### PUT /users/me

Met à jour les informations de l'utilisateur connecté.

**Corps de la requête :**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "new.email@example.com"
}
```

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "john.doe",
    "email": "new.email@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "created_at": "2023-01-15T10:30:15Z",
    "updated_at": "2023-03-15T09:45:22Z"
  }
}
```

### Documents

#### GET /documents

Liste les documents de l'utilisateur connecté.

**Paramètres de requête :**

- `page` (optionnel) : Numéro de page (défaut: 1)
- `per_page` (optionnel) : Nombre d'éléments par page (défaut: 20)
- `status` (optionnel) : Filtrer par statut ('draft', 'pending', 'signed', 'expired')
- `sort` (optionnel) : Champ de tri ('created_at', 'updated_at', 'name')
- `order` (optionnel) : Ordre de tri ('asc', 'desc')

**Réponse :**

```json
{
  "status": "success",
  "data": [
    {
      "id": "doc-123",
      "name": "Contract-2023.pdf",
      "status": "signed",
      "size": 2543678,
      "created_at": "2023-02-15T10:30:15Z",
      "updated_at": "2023-02-16T14:20:30Z",
      "signed_at": "2023-02-16T14:20:30Z",
      "signatures_count": 2,
      "thumbnail_url": "https://api.certisign.com/thumbnails/doc-123.jpg"
    },
    // ... autres documents
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_items": 98
  }
}
```

#### POST /documents/upload

Télécharge un nouveau document.

**Corps de la requête :**

Requête multipart/form-data avec les champs suivants :
- `file` : Le fichier à télécharger
- `name` (optionnel) : Nom personnalisé du document
- `description` (optionnel) : Description du document
- `expiration_date` (optionnel) : Date d'expiration au format ISO 8601

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "id": "doc-456",
    "name": "Agreement-2023.pdf",
    "status": "draft",
    "size": 1245678,
    "created_at": "2023-03-15T10:30:15Z",
    "updated_at": "2023-03-15T10:30:15Z",
    "download_url": "https://api.certisign.com/documents/doc-456/download",
    "thumbnail_url": "https://api.certisign.com/thumbnails/doc-456.jpg"
  }
}
```

#### GET /documents/{id}

Récupère les détails d'un document spécifique.

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "id": "doc-123",
    "name": "Contract-2023.pdf",
    "description": "Service agreement for 2023",
    "status": "signed",
    "size": 2543678,
    "created_at": "2023-02-15T10:30:15Z",
    "updated_at": "2023-02-16T14:20:30Z",
    "signed_at": "2023-02-16T14:20:30Z",
    "expiration_date": "2024-02-15T10:30:15Z",
    "owner": {
      "id": 1,
      "username": "john.doe"
    },
    "signatures": [
      {
        "signer": {
          "id": 1,
          "name": "John Doe",
          "email": "john.doe@example.com"
        },
        "signed_at": "2023-02-16T14:20:30Z",
        "certificate_info": {
          "issuer": "CertiSign CA",
          "valid_until": "2024-05-10T00:00:00Z"
        }
      }
    ],
    "download_url": "https://api.certisign.com/documents/doc-123/download",
    "thumbnail_url": "https://api.certisign.com/thumbnails/doc-123.jpg"
  }
}
```

#### DELETE /documents/{id}

Supprime un document.

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "message": "Document successfully deleted"
  }
}
```

#### POST /documents/{id}/sign

Signe un document.

**Corps de la requête :**

```json
{
  "certificate_id": "cert-789",
  "signature_position": {
    "page": 2,
    "x": 100,
    "y": 200,
    "width": 200,
    "height": 50
  },
  "signature_type": "visible",
  "password": "certificate_password"
}
```

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "id": "doc-123",
    "status": "signed",
    "signed_at": "2023-03-15T14:30:45Z",
    "signature_id": "sig-456",
    "download_url": "https://api.certisign.com/documents/doc-123/download"
  }
}
```

#### GET /documents/{id}/verify

Vérifie les signatures d'un document.

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "document_id": "doc-123",
    "document_name": "Contract-2023.pdf",
    "verification_time": "2023-03-16T09:45:30Z",
    "signatures": [
      {
        "signer": "John Doe",
        "valid": true,
        "signed_at": "2023-02-16T14:20:30Z",
        "certificate": {
          "issuer": "CertiSign CA",
          "serial_number": "123456789ABCDEF",
          "valid_from": "2022-05-10T00:00:00Z",
          "valid_until": "2024-05-10T00:00:00Z"
        },
        "validation": {
          "integrity": true,
          "certificate_validity": true,
          "certificate_revocation": false
        }
      }
    ],
    "document_integrity": true,
    "overall_validity": true
  }
}
```

### Certificats

#### GET /certificates

Liste les certificats de l'utilisateur.

**Réponse :**

```json
{
  "status": "success",
  "data": [
    {
      "id": "cert-123",
      "name": "John Doe Signature Certificate",
      "issuer": "CertiSign CA",
      "serial_number": "123456789ABCDEF",
      "valid_from": "2022-05-10T00:00:00Z",
      "valid_until": "2024-05-10T00:00:00Z",
      "status": "valid"
    },
    // ... autres certificats
  ]
}
```

#### POST /certificates/import

Importe un certificat existant.

**Corps de la requête :**

Requête multipart/form-data avec les champs suivants :
- `certificate_file` : Fichier de certificat (format PFX/P12)
- `password` : Mot de passe du certificat
- `name` (optionnel) : Nom personnalisé du certificat

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "id": "cert-456",
    "name": "John Doe Signature Certificate",
    "issuer": "CertiSign CA",
    "serial_number": "123456789ABCDEF",
    "valid_from": "2022-05-10T00:00:00Z",
    "valid_until": "2024-05-10T00:00:00Z",
    "status": "valid",
    "created_at": "2023-03-16T10:15:30Z"
  }
}
```

#### DELETE /certificates/{id}

Supprime un certificat.

**Réponse :**

```json
{
  "status": "success",
  "data": {
    "message": "Certificate successfully deleted"
  }
}
```

## Codes d'erreur

| Code                  | Description                                  |
|-----------------------|----------------------------------------------|
| `AUTHENTICATION_ERROR`| Problème d'authentification                  |
| `AUTHORIZATION_ERROR` | Permissions insuffisantes                    |
| `VALIDATION_ERROR`    | Données invalides dans la requête            |
| `RESOURCE_NOT_FOUND`  | Ressource demandée non trouvée               |
| `DOCUMENT_ERROR`      | Erreur liée au document                      |
| `CERTIFICATE_ERROR`   | Erreur liée au certificat                    |
| `SIGNATURE_ERROR`     | Erreur lors du processus de signature        |
| `SERVER_ERROR`        | Erreur interne du serveur                    |

## Limites de requêtes

Pour éviter les abus, l'API CertiSign implémente des limites de taux de requêtes :

- API publique : 60 requêtes par minute
- API authentifiée : 300 requêtes par minute

Lorsque vous dépassez ces limites, l'API renvoie une réponse avec le code d'état 429 (Too Many Requests).

## Versionnement de l'API

L'API CertiSign suit le versionnement sémantique. La version actuelle est v1.

Les modifications incompatibles sont introduites uniquement dans de nouvelles versions majeures de l'API.

## Documentation Swagger

Une documentation interactive de l'API est disponible à l'adresse :

```
https://api.certisign.com/docs/
```

Pour l'environnement de développement :

```
http://localhost:8000/docs/
``` 