# Mise à jour du Workflow de Signature - Positionnement du QR Code

## Vue d'ensemble

Cette mise à jour ajoute une nouvelle étape au processus de signature permettant à l'utilisateur de personnaliser la position du QR code sur le document PDF.

## Nouvelles fonctionnalités

### 1. Étape de positionnement du QR code

Une nouvelle étape a été ajoutée entre la **prévisualisation** et la **saisie du certificat** :

- **Avant** : Sélection → Prévisualisation → Certificat → Signature → Téléchargement
- **Après** : Sélection → Prévisualisation → **Position QR** → Certificat → Signature → Téléchargement

### 2. Interface interactive de positionnement

Le nouveau composant `QrPositioner.vue` offre :

- **QR code draggable** : L'utilisateur peut glisser-déposer le QR code sur l'aperçu du document
- **Choix de taille** : 3 tailles disponibles (Petit, Moyen, Grand)
- **Aperçu en temps réel** : Position affichée en pourcentages
- **Aperçu final** : Visualisation du résultat sur les premières pages
- **Support tactile** : Compatible mobile et tablette

### 3. Personnalisation de la position

L'utilisateur peut :
- Positionner le QR code n'importe où sur le document (avec marges de sécurité)
- Choisir la taille du QR code
- Voir un aperçu en temps réel
- Réinitialiser à la position par défaut
- Confirmer sa sélection

## Modifications techniques

### Frontend (Vue.js)

#### Nouveau composant : `QrPositioner.vue`
- Interface drag & drop pour positionner le QR code
- Contrôles de taille (petit/moyen/grand)
- Aperçu final avec simulation sur plusieurs pages
- Support responsive

#### Mise à jour : `SignDocument.vue`
- Ajout de la nouvelle étape dans le workflow
- Intégration du composant `QrPositioner`
- Transmission des données de position au backend
- Mise à jour de la navigation entre étapes

### Backend (FastAPI)

#### Mise à jour : `main.py` (microservice signature)
- Modification de `add_simple_qr_code_to_pdf()` pour accepter les paramètres de position
- Calcul de position basé sur les pourcentages fournis par le frontend
- Support des différentes tailles de QR code
- Extraction des données de position depuis les métadonnées

#### Nouvelles fonctionnalités :
- **Tailles configurables** : Petit (0.4"), Moyen (0.5"), Grand (0.6")
- **Positionnement précis** : Conversion pourcentage → coordonnées PDF
- **Marges de sécurité** : Évite la troncature du QR code
- **Rétrocompatibilité** : Position par défaut si non spécifiée

## Flux de données

1. **Frontend** : L'utilisateur positionne le QR code
2. **Transmission** : Position (x%, y%, taille) envoyée dans les métadonnées
3. **Backend** : Extraction et conversion en coordonnées PDF
4. **Application** : QR code appliqué à la position spécifiée

## Format des données de position

```json
{
  "qr_position": {
    "x": 85,        // Position X en pourcentage (0-100)
    "y": 90,        // Position Y en pourcentage (0-100)
    "size": "medium" // Taille : "small" | "medium" | "large"
  }
}
```

## Compatibilité

- **Rétrocompatibilité** : Les anciens documents utilisent la position par défaut
- **Fallback** : Position par défaut (85%, 10%, medium) si non spécifiée
- **Validation** : Contrôle des limites pour éviter les débordements

## Interface utilisateur

### Étapes du workflow

1. **Sélection** : Upload du PDF
2. **Prévisualisation** : Vérification du document
3. **🆕 Position QR** : Choix de l'emplacement du QR code
4. **Certificat** : Saisie des informations de signature
5. **Signature** : Traitement automatique
6. **Téléchargement** : Récupération du document signé

### Contrôles disponibles

- **Drag & Drop** : Glisser le QR code sur l'aperçu
- **Boutons de taille** : Petit/Moyen/Grand
- **Aperçu final** : Visualisation du résultat
- **Réinitialiser** : Retour à la position par défaut
- **Confirmer** : Validation et passage à l'étape suivante

## Tests et validation

### Points de test recommandés

1. **Positionnement** : Vérifier que le QR code apparaît à la position choisie
2. **Tailles** : Tester les 3 tailles disponibles
3. **Limites** : S'assurer que le QR code ne dépasse pas des marges
4. **Responsive** : Tester sur différentes tailles d'écran
5. **Rétrocompatibilité** : Vérifier que les anciens documents fonctionnent

### Cas d'usage

- **Position personnalisée** : L'utilisateur choisit l'emplacement exact
- **Taille adaptée** : Sélection de la taille selon le document
- **Multi-pages** : QR code appliqué sur toutes les pages
- **Mobile friendly** : Interface tactile pour appareils mobiles

## Avantages

- **Flexibilité** : Positionnement libre du QR code
- **UX améliorée** : Interface intuitive et visuelle
- **Compatibilité** : Fonctionne avec tous types de documents PDF
- **Performance** : Aucun impact sur la vitesse de signature
- **Accessibilité** : Support mobile et tablette

Cette mise à jour améliore significativement l'expérience utilisateur en donnant le contrôle total sur l'apparence finale du document signé. 