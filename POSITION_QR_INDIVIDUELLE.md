# Documentation : Positionnement individuel des QR codes par page

## Vue d'ensemble

Cette nouvelle fonctionnalité permet de définir des positions différentes pour le QR code sur chaque page d'un document PDF. Auparavant, la même position était appliquée à toutes les pages sélectionnées. Désormais, vous pouvez personnaliser la position du QR code page par page.

## Utilisation dans l'interface

### 1. Nouvelle option de positionnement

Dans l'étape "Position QR" du workflow de signature, vous avez maintenant 4 options :

- **Toutes les pages (même position)** : Applique le QR code à la même position sur toutes les pages
- **Page actuelle uniquement** : Applique le QR code uniquement sur la page affichée
- **Pages personnalisées (même position)** : Sélectionnez des pages spécifiques, toutes avec la même position
- **Position individuelle par page** ✨ (NOUVEAU) : Définissez une position différente pour chaque page

### 2. Mode "Position individuelle par page"

Lorsque vous sélectionnez cette option :

1. **Navigation** : Naviguez entre les pages du document avec les boutons < et >
2. **Positionnement** : Sur chaque page où vous souhaitez un QR code, glissez-déposez le QR à la position désirée
3. **Indicateur visuel** : Les pages avec un QR code positionné apparaissent en vert dans la liste
4. **Modification** : Cliquez sur une page dans la liste pour y retourner et ajuster la position
5. **Suppression** : Utilisez le bouton × pour retirer le QR code d'une page spécifique

### 3. Aperçu final

L'aperçu final affiche maintenant correctement les QR codes avec leurs positions individuelles sur chaque page.

## Structure des données

### Frontend (QrPositioner.vue)

Le composant envoie maintenant une structure enrichie :

```javascript
{
  x: 85,              // Position X par défaut (compatibilité)
  y: 90,              // Position Y par défaut (compatibilité)
  size: 'medium',     // Taille du QR code
  pages: [1, 3, 5],   // Pages où appliquer le QR
  positions: {        // NOUVEAU : Positions par page
    "1": { x: 85, y: 90 },
    "3": { x: 20, y: 20 },
    "5": { x: 50, y: 50 }
  },
  mode: 'individual'  // Mode de positionnement
}
```

### Backend (main.py)

La fonction `add_simple_qr_code_to_pdf` gère maintenant les positions individuelles :

```python
# Si mode individual et position spécifique pour cette page
if position_mode == 'individual' and str(page_number) in individual_positions:
    page_position = individual_positions[str(page_number)]
    x_percent = page_position.get('x', x_percent)
    y_percent = page_position.get('y', y_percent)
```

## Exemples d'utilisation

### Cas d'usage 1 : Document avec en-tête variable

- Page 1 : QR en haut à droite (car l'en-tête est à gauche)
- Pages 2-5 : QR en bas à droite (car l'en-tête occupe tout le haut)
- Dernière page : QR au centre (page de signature)

### Cas d'usage 2 : Document avec graphiques

- Pages avec texte : QR en position standard (85%, 90%)
- Pages avec graphiques : QR repositionné pour ne pas masquer les données importantes

## Compatibilité

La fonctionnalité est rétrocompatible :
- Les anciens modes continuent de fonctionner normalement
- Les données sont structurées pour permettre l'évolution future
- Le backend accepte les deux formats (ancien et nouveau)

## Notes techniques

1. **Performance** : Les positions sont calculées uniquement pour les pages modifiées
2. **Stockage** : Les positions individuelles sont stockées dans un objet JavaScript pour un accès rapide
3. **Validation** : Chaque position est validée pour rester dans les limites de la page
4. **Responsive** : L'interface s'adapte aux petits écrans avec une liste scrollable

## Améliorations futures possibles

1. **Templates de position** : Sauvegarder des modèles de positionnement réutilisables
2. **Copier/Coller** : Copier la position d'une page vers d'autres pages
3. **Alignement automatique** : Détecter les zones libres sur chaque page
4. **Prévisualisation en temps réel** : Afficher toutes les pages avec leurs QR codes simultanément

## Support

Pour toute question ou problème, consultez les logs du microservice qui affichent maintenant :
- Le mode de positionnement utilisé
- Les positions individuelles définies
- Les pages traitées avec leurs positions respectives 