# Composants UI

CertiSign utilise une architecture basée sur des composants pour construire son interface utilisateur. Cette approche favorise la réutilisabilité et la maintenabilité du code.

## Structure des composants

Les composants sont organisés de manière hiérarchique :

- **Composants de base** : Boutons, champs de formulaire, etc.
- **Composants composites** : Formulaires, modales, cartes, etc.
- **Pages/Vues** : Assemblages de composants pour former des pages complètes

## Composants de base

### AppButton

Bouton standardisé avec différentes variantes.

```vue
<AppButton variant="primary" :loading="isLoading" @click="handleClick">
  Valider
</AppButton>
```

**Props disponibles:**
- `variant`: 'primary', 'secondary', 'danger', 'success', 'outlined'
- `size`: 'sm', 'md', 'lg'
- `loading`: boolean
- `disabled`: boolean

### AppInput

Champ de saisie standardisé.

```vue
<AppInput
  v-model="username"
  label="Nom d'utilisateur"
  :error="errors.username"
  placeholder="Entrez votre nom d'utilisateur"
/>
```

**Props disponibles:**
- `modelValue`: la valeur liée (v-model)
- `label`: texte du label
- `type`: 'text', 'password', 'email', 'number', etc.
- `error`: message d'erreur
- `placeholder`: texte indicatif
- `required`: boolean

### AppSelect

Menu déroulant pour sélection d'options.

```vue
<AppSelect
  v-model="selectedOption"
  :options="availableOptions"
  label="Choisissez une option"
/>
```

**Props disponibles:**
- `modelValue`: la valeur sélectionnée (v-model)
- `options`: tableau d'objets `{value, label}`
- `label`: texte du label
- `error`: message d'erreur
- `placeholder`: texte indicatif

## Composants composites

### DocumentCard

Carte affichant les informations d'un document avec actions.

```vue
<DocumentCard
  :document="document"
  @sign="signDocument"
  @download="downloadDocument"
  @delete="confirmDelete"
/>
```

**Props disponibles:**
- `document`: objet document avec propriétés (id, name, status, etc.)

**Événements émis:**
- `sign`: demande de signature du document
- `download`: téléchargement du document
- `delete`: suppression du document

### SignatureModal

Modal pour la signature électronique d'un document.

```vue
<SignatureModal
  v-model="showSignatureModal"
  :document="selectedDocument"
  :certificates="userCertificates"
  @sign="processSignature"
/>
```

**Props disponibles:**
- `modelValue`: contrôle l'affichage de la modale (v-model)
- `document`: document à signer
- `certificates`: certificats disponibles pour la signature

**Événements émis:**
- `sign`: signature avec les paramètres sélectionnés

### CertificateManager

Composant de gestion des certificats de l'utilisateur.

```vue
<CertificateManager
  :certificates="userCertificates"
  @import="importCertificate"
  @create="createCertificate"
  @delete="deleteCertificate"
/>
```

## Pages principales

### Dashboard

Page d'accueil affichant un tableau de bord avec statistiques et activités récentes.

```vue
<template>
  <div class="dashboard">
    <StatisticsCards :stats="statistics" />
    <RecentActivities :activities="recentActivities" />
    <DocumentList :documents="recentDocuments" />
  </div>
</template>
```

### DocumentsView

Page listant tous les documents de l'utilisateur avec options de filtrage et de tri.

```vue
<template>
  <div class="documents-view">
    <SearchFilters v-model="filters" />
    <DocumentTable
      :documents="filteredDocuments"
      :loading="loading"
      @page-change="handlePageChange"
    />
    <Pagination
      :total="totalDocuments"
      :current-page="currentPage"
      :per-page="perPage"
      @change="handlePageChange"
    />
  </div>
</template>
```

### SignDocument

Page dédiée à la signature d'un document spécifique.

```vue
<template>
  <div class="sign-document">
    <DocumentPreview :document="document" />
    <SignatureForm
      :certificates="userCertificates"
      @sign="signDocument"
      @cancel="navigateBack"
    />
  </div>
</template>
```

## Stylisation et thème

CertiSign utilise un système de design cohérent à travers l'application. Les variables CSS sont définies dans des fichiers séparés pour faciliter la personnalisation.

### Variables globales

```scss
// src/assets/scss/_variables.scss

// Couleurs principales
$primary: #2c3e50;
$secondary: #95a5a6;
$success: #27ae60;
$danger: #e74c3c;
$warning: #f39c12;
$info: #3498db;

// Typographie
$font-family-base: 'Roboto', sans-serif;
$font-size-base: 16px;
$line-height-base: 1.5;

// Espacement
$spacing-base: 8px;
$spacing-md: $spacing-base * 2;
$spacing-lg: $spacing-base * 3;

// Bordures
$border-radius: 4px;
$border-color: rgba(0, 0, 0, 0.1);
```

## Accessibilité

Les composants sont conçus en tenant compte de l'accessibilité :

- Utilisation correcte des rôles ARIA
- Contraste de couleurs suffisant
- Support de la navigation au clavier
- Messages d'erreur explicites

## Responsive Design

L'interface s'adapte à différentes tailles d'écran :

- Layout flexible avec Flexbox et Grid
- Media queries pour les ajustements spécifiques
- Approche mobile-first

## Utilisation des composants

Exemple d'intégration de plusieurs composants dans une vue :

```vue
<template>
  <div class="certificate-page">
    <h1>Gestion des certificats</h1>
    
    <AppCard title="Mes certificats">
      <CertificateList
        :certificates="certificates"
        :loading="loading"
        @view="viewCertificate"
        @delete="confirmDeleteCertificate"
      />
      
      <AppButton variant="primary" @click="showImportModal = true">
        Importer un certificat
      </AppButton>
    </AppCard>
    
    <ImportCertificateModal
      v-model="showImportModal"
      @import="importCertificate"
    />
    
    <ConfirmDialog
      v-model="showConfirmDialog"
      title="Supprimer le certificat"
      message="Êtes-vous sûr de vouloir supprimer ce certificat ?"
      @confirm="deleteCertificate"
    />
  </div>
</template>
```

Pour explorer tous les composants disponibles, consultez le code source dans le répertoire `src/components/`. 