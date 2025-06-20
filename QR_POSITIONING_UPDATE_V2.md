# Mise à jour V2 : Système de Positionnement Avancé du QR Code

## Vue d'ensemble des améliorations

Cette mise à jour majeure transforme complètement l'expérience de positionnement du QR code avec :

1. **Aperçu A4 natif** : Plus d'iframe, utilisation d'images converties du PDF
2. **Positionnement précis** : Le QR sera placé exactement où l'utilisateur le positionne
3. **Sélection des pages** : Choix d'appliquer le QR sur toutes les pages, page actuelle ou pages personnalisées
4. **Aperçu réel** : L'aperçu final montre le vrai document avec le QR intégré

## Architecture technique

### Frontend - Composant QrPositioner.vue

#### Nouvelles fonctionnalités

1. **Conversion PDF → Image**
   - Appel API pour convertir chaque page PDF en image PNG
   - Affichage en format A4 natif (595x842 pixels)
   - Cache des images pour performance optimale

2. **Interface de positionnement**
   - Zone d'aperçu A4 avec dimensions réelles
   - QR code draggable avec feedback visuel
   - Support tactile pour mobile/tablette
   - Indicateur de position en temps réel

3. **Sélection des pages**
   - Option "Toutes les pages"
   - Option "Page actuelle uniquement"
   - Option "Pages personnalisées" avec sélection multiple

4. **Aperçu final amélioré**
   - Modal avec aperçu des pages sélectionnées
   - QR code intégré sur l'image du document
   - Visualisation exacte du résultat final

### Backend - API Gateway

#### Nouveaux endpoints

1. **`/gateway/pdf-to-image/`**
   ```python
   @app.post("/gateway/pdf-to-image/")
   async def pdf_to_image(pdf: UploadFile, page: int)
   ```
   - Convertit une page PDF en image PNG
   - Utilise `pdf2image` et `Pillow`
   - Retourne une image optimisée en format A4

2. **`/gateway/pdf-info/`**
   ```python
   @app.post("/gateway/pdf-info/")
   async def pdf_info(pdf: UploadFile)
   ```
   - Retourne le nombre de pages du PDF
   - Informations sur les dimensions
   - Détection du format (A4, etc.)

### Backend - Microservice de signature

#### Mise à jour de `add_simple_qr_code_to_pdf()`

- Support des pages spécifiques via le paramètre `pages`
- Format accepté : `'all'` ou `[1, 3, 5]` (liste de numéros de pages)
- Application conditionnelle du QR code selon la sélection

## Flux de données complet

### 1. Upload du document
```javascript
// SignDocument.vue
const selectedFile = ref(null);
detectPdfPages(file); // Appel API pour obtenir le nombre de pages
```

### 2. Positionnement du QR
```javascript
// QrPositioner.vue
loadPageImage(pageNumber); // Conversion PDF → Image
handleDragMove(event); // Positionnement interactif
```

### 3. Format des données de position
```json
{
  "x": 50,              // Position X en %
  "y": 20,              // Position Y en %
  "size": "medium",     // Taille : small/medium/large
  "pages": [1, 3, 5]    // Pages sélectionnées ou "all"
}
```

### 4. Traitement backend
```python
# Position transmise via métadonnées
qr_position = {
    'x': 50,
    'y': 20,
    'size': 'medium',
    'pages': [1, 3, 5]
}
```

## Interface utilisateur améliorée

### Zone principale (gauche)
- **Aperçu A4** : Document affiché en taille réelle A4
- **Navigation** : Boutons précédent/suivant entre les pages
- **QR draggable** : Élément interactif avec pattern QR
- **Indicateur** : Position en temps réel (X%, Y%)

### Panneau de contrôle (droite)
- **Sélection des pages** : Radio buttons avec options
- **Pages personnalisées** : Checkboxes pour sélection multiple
- **Taille du QR** : 3 boutons avec aperçu visuel
- **Actions** : Réinitialiser, Aperçu final, Confirmer

### Modal d'aperçu final
- **Grille de pages** : Jusqu'à 3 pages en aperçu
- **QR intégré** : Visualisation sur le document réel
- **Validation** : Boutons Fermer et Confirmer

## Avantages techniques

### Performance
- **Cache d'images** : Les pages converties sont mises en cache
- **Conversion à la demande** : Seules les pages visibles sont converties
- **Optimisation PNG** : Images compressées pour chargement rapide

### Précision
- **Calcul exact** : Conversion pourcentage → coordonnées PDF précises
- **Marges de sécurité** : Protection contre les débordements
- **Format A4 respecté** : Dimensions exactes 210x297mm

### Flexibilité
- **Multi-pages** : Support de sélection complexe
- **Tailles variables** : 3 tailles prédéfinies (0.4", 0.5", 0.6")
- **Position libre** : Placement n'importe où avec limites 5%-95%

## Dépendances requises

### Frontend
```json
{
  "axios": "^1.x",
  "vue": "^3.x"
}
```

### Backend
```txt
pdf2image
pillow
PyPDF2
poppler-utils (système)
```

## Exemples d'utilisation

### Placement sur toutes les pages
```javascript
{
  x: 85,
  y: 10,
  size: 'medium',
  pages: 'all'
}
```

### Placement sur pages spécifiques
```javascript
{
  x: 50,
  y: 50,
  size: 'large',
  pages: [1, 3, 5, 7]
}
```

### Placement page unique
```javascript
{
  x: 20,
  y: 90,
  size: 'small',
  pages: [2]
}
```

## Points d'attention

1. **Poppler** : Nécessite `poppler-utils` installé au niveau système
2. **Mémoire** : Les images en cache peuvent consommer de la mémoire
3. **Performance** : La conversion PDF→Image peut être lente pour gros fichiers
4. **Compatibilité** : Testé avec PDF standard, formats spéciaux à vérifier

Cette mise à jour offre une expérience utilisateur exceptionnelle avec un contrôle total sur le placement du QR code, tout en garantissant une précision maximale et une interface intuitive. 