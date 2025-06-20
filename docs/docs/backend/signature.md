# Signature Électronique

Le module de signature électronique est au cœur de CertiSign. Il permet de signer numériquement des documents et de vérifier l'authenticité des signatures.

## Types de signatures supportés

CertiSign prend en charge plusieurs types de signatures électroniques :

1. **Signature simple (SES)** - Signature de base garantissant l'intégrité du document
2. **Signature avancée (AdES)** - Signature avec authentification renforcée du signataire
3. **Signature qualifiée (QES)** - Signature équivalente légalement à une signature manuscrite (conformité eIDAS)

Les formats de signature pris en charge incluent :

- **PAdES** (PDF Advanced Electronic Signatures) - Pour les documents PDF
- **XAdES** (XML Advanced Electronic Signatures) - Pour les documents XML
- **CAdES** (CMS Advanced Electronic Signatures) - Pour tout type de document

## Architecture du service de signature

Le service de signature est conçu comme un microservice isolé, construit avec FastAPI pour des performances optimales et une faible latence.

```
                   +-----------------+
                   |   API Django    |
                   +--------+--------+
                            |
                            v
+------------+     +--------+--------+     +-----------------+
| Stockage   |<--->| Service de      |<--->| Service OCSP/   |
| Documents  |     | Signature       |     | CRL             |
+------------+     +--------+--------+     +-----------------+
                            |
                            v
                   +--------+--------+
                   | HSM / Gestionnaire|
                   | de clés          |
                   +-----------------+
```

## Processus de signature

### Préparation du document

1. Le document est téléchargé et préparé pour la signature
2. Les métadonnées du document sont extraites (titre, auteur, nombre de pages, etc.)
3. Un hash SHA-256 du document est calculé pour garantir son intégrité
4. Les zones de signature sont identifiées ou définies par l'utilisateur

### Signature du document

1. L'utilisateur sélectionne le certificat à utiliser pour la signature
2. Le document est haché (hash) à l'aide d'algorithmes sécurisés (SHA-256, SHA-384, SHA-512)
3. Le hash est signé avec la clé privée associée au certificat
4. La signature et les informations du certificat sont intégrées au document
5. Des métadonnées de signature sont ajoutées (date, heure, signataire, raison)
6. Pour les signatures visibles, l'apparence visuelle est générée et ajoutée au document

### Vérification des signatures

1. Le document signé est analysé pour extraire les signatures
2. Chaque signature est vérifiée :
   - Vérification cryptographique (correspondance entre hash et signature)
   - Validation du certificat (chaîne de confiance, période de validité)
   - Vérification du statut de révocation via CRL/OCSP
   - Vérification de l'intégrité du document (détection de modifications)
3. Un rapport détaillé est généré, indiquant la validité de chaque signature

## Composants techniques

### Bibliothèques cryptographiques

CertiSign utilise plusieurs bibliothèques cryptographiques éprouvées :

- **pyca/cryptography** - Opérations cryptographiques de base
- **pyHanko** - Manipulation et signature de PDF
- **python-pkcs11** - Interface avec les HSM via PKCS#11
- **lxml** - Traitement et signature des documents XML
- **asn1crypto** - Manipulation des structures ASN.1 (certificats, CRL)

### Validation des certificats

Le système vérifie la validité des certificats utilisés pour la signature :

- **Vérification de la chaîne de confiance** - Remontée jusqu'à une autorité de certification racine approuvée
- **Validation de la période de validité** - Le certificat ne doit être ni expiré ni pas encore valide
- **Vérification du statut de révocation** :
  - Via les Listes de Révocation de Certificats (CRL)
  - Via le protocole Online Certificate Status Protocol (OCSP)
- **Vérification des extensions** - Utilisation conforme aux extensions du certificat (par ex. KeyUsage pour la signature)

### Horodatage (Timestamp)

Pour renforcer la valeur probante des signatures, CertiSign intègre un service d'horodatage qualifié :

1. Un hash du document signé est envoyé à une Autorité d'Horodatage de Confiance (TSA)
2. La TSA renvoie un jeton d'horodatage signé avec sa propre clé privée
3. Ce jeton est intégré dans la signature électronique
4. Cela permet de prouver qu'un document existait dans un état donné à un moment précis

## Conformité légale

CertiSign est conçu pour se conformer aux réglementations en vigueur concernant la signature électronique :

- **Règlement eIDAS** (UE) N°910/2014 pour l'Union Européenne
- **ESIGN Act** et **UETA** pour les États-Unis
- **UNCITRAL Model Law on Electronic Signatures** pour les standards internationaux

### Niveaux de conformité eIDAS

La solution implémente les trois niveaux définis par le règlement eIDAS :

1. **Signature électronique simple (SES)** - Niveau de base
2. **Signature électronique avancée (AdES)** - Niveau intermédiaire avec identification renforcée du signataire
3. **Signature électronique qualifiée (QES)** - Niveau le plus élevé, équivalent juridique de la signature manuscrite

## Protection des clés privées

La sécurité des clés privées est primordiale pour garantir l'intégrité du processus de signature :

### Options de stockage des clés

1. **Module de Sécurité Matériel (HSM)** - Recommandé pour les environnements professionnels
2. **Tokens PKCS#11** - Comme les cartes à puce ou tokens USB
3. **Certificats stockés dans le navigateur** - Pour une utilisation personnelle
4. **Stockage logiciel sécurisé** - Avec chiffrement et protection par mot de passe

### Interface avec les HSM

Pour les déploiements d'entreprise, CertiSign peut s'interfacer avec des HSM via le standard PKCS#11 :

```python
import pkcs11
from pkcs11 import Mechanism

# Connexion au HSM
lib = pkcs11.lib(settings.PKCS11_LIBRARY_PATH)
token = lib.get_token(token_label=settings.HSM_TOKEN_LABEL)
session = token.open(user_pin=hsm_pin)

# Signature avec une clé privée stockée dans le HSM
private_key = session.get_key(label=certificate_label, cls=pkcs11.PrivateKey)
signature = private_key.sign(document_hash, mechanism=Mechanism.RSA_PKCS)
```

## Personnalisation visuelle des signatures

Pour les signatures visibles dans les documents PDF, CertiSign permet de personnaliser leur apparence :

- **Informations affichées** - Nom du signataire, date/heure, raison, emplacement, etc.
- **Aspect visuel** - Logo, couleurs, polices, etc.
- **Position** - Page, coordonnées X/Y, taille
- **Champs de signature** - Prédéfinis ou créés dynamiquement

## Exemple d'utilisation FastAPI

```python
@router.post("/documents/{document_id}/sign", response_model=SignatureResponse)
async def sign_document(
    document_id: str,
    signature_data: SignatureRequest,
    current_user: User = Depends(get_current_user),
    signature_service: SignatureService = Depends(get_signature_service)
):
    """
    Signe un document avec le certificat spécifié.
    """
    # Récupérer le document
    document = await document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Vérifier les permissions
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to sign this document")
    
    # Récupérer le certificat
    certificate = await certificate_service.get_certificate(
        signature_data.certificate_id, 
        current_user.id
    )
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    try:
        # Signer le document
        signed_document = await signature_service.sign_document(
            document=document,
            certificate=certificate,
            password=signature_data.password,
            signature_position=signature_data.signature_position,
            signature_type=signature_data.signature_type,
            reason=signature_data.reason
        )
        
        # Mettre à jour le statut du document
        await document_service.update_document_status(document_id, "signed")
        
        # Enregistrer l'activité de signature
        await audit_service.log_signature_activity(
            user_id=current_user.id,
            document_id=document_id,
            certificate_id=certificate.id,
            activity_type="document_signed",
            ip_address=request.client.host
        )
        
        return {
            "status": "success",
            "data": {
                "id": document_id,
                "status": "signed",
                "signed_at": datetime.utcnow(),
                "signature_id": signed_document.signature_id,
                "download_url": f"/api/v1/documents/{document_id}/download"
            }
        }
    except CertificatePasswordError:
        raise HTTPException(status_code=400, detail="Invalid certificate password")
    except CertificateRevokedError:
        raise HTTPException(status_code=400, detail="Certificate has been revoked")
    except SignatureError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Archivage à long terme

CertiSign implémente des mécanismes pour assurer la validité des signatures sur le long terme :

- **PAdES-LTV** (Long Term Validation) - Intégration des informations de validation
- **Conservation des CRL/réponses OCSP** - Pour vérification ultérieure
- **Renouvellement des timestamps** - Avant l'expiration des algorithmes cryptographiques
- **Format d'archivage** - Conformité avec les standards d'archivage électronique

## Audit et traçabilité

Toutes les opérations de signature sont journalisées pour garantir la traçabilité :

- Qui a signé le document (identité du signataire)
- Quand le document a été signé (horodatage)
- Quel certificat a été utilisé (empreinte du certificat)
- Depuis quelle adresse IP la signature a été réalisée
- Quel dispositif a été utilisé (informations sur le navigateur/appareil)

Ces journaux sont sécurisés et peuvent être utilisés comme preuves en cas de litige. 