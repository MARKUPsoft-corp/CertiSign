<template>
  <div class="my-documents-container">
    <div class="section-header">
      <h2 class="section-title">Mes Documents</h2>
      <div class="header-actions">
        <div class="search-container">
          <input 
            type="text" 
            v-model="searchQuery" 
            class="search-input" 
            placeholder="Rechercher un document..."
            @input="filterDocuments"
          >
          <i class="bi bi-search search-icon"></i>
        </div>
        <div class="filter-dropdown">
          <button class="btn btn-outline-secondary dropdown-toggle" @click="toggleFilterMenu">
            <i class="bi bi-funnel"></i> Filtrer
          </button>
          <div class="filter-menu" v-show="showFilterMenu">
            <div class="filter-item">
              <input type="checkbox" id="filter-all" v-model="filters.all" @change="filterDocuments">
              <label for="filter-all">Tous</label>
            </div>
            <div class="filter-item">
              <input type="checkbox" id="filter-draft" v-model="filters.draft" @change="filterDocuments">
              <label for="filter-draft">Brouillons</label>
            </div>
            <div class="filter-item">
              <input type="checkbox" id="filter-pending" v-model="filters.pending" @change="filterDocuments">
              <label for="filter-pending">En attente de signature</label>
            </div>
            <div class="filter-item">
              <input type="checkbox" id="filter-signed" v-model="filters.signed" @change="filterDocuments">
              <label for="filter-signed">Signés</label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- État de chargement -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement de vos documents...</p>
    </div>

    <!-- Message d'erreur -->
    <div v-else-if="error" class="error-state">
      <i class="bi bi-exclamation-triangle-fill"></i>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="fetchDocuments">Réessayer</button>
    </div>

    <!-- Aucun document -->
    <div v-else-if="filteredDocuments.length === 0" class="empty-state">
      <i class="bi bi-file-earmark-x"></i>
      <p v-if="searchQuery">Aucun document ne correspond à votre recherche</p>
      <p v-else>Vous n'avez pas encore de documents</p>
      <div class="debug-info" style="margin-bottom: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px; text-align: left;">
        <p><strong>Informations de débogage:</strong></p>
        <p>Documents chargés: {{ documents.length || 0 }}</p>
        <p>Documents filtrés: {{ filteredDocuments.length || 0 }}</p>
        <p>Documents valides: {{ validFilteredDocuments.length || 0 }}</p>
        <p>Erreur: {{ error || 'Aucune' }}</p>
        <p>Chargement: {{ loading ? 'En cours' : 'Terminé' }}</p>
      </div>
      <button class="btn btn-primary" @click="fetchDocuments">
        <i class="bi bi-arrow-clockwise"></i> Actualiser la liste
      </button>
      <button class="btn btn-primary" style="margin-left: 10px;" @click="openUploadModal">
        <i class="bi bi-upload"></i> Téléverser votre premier document
      </button>
    </div>

    <!-- Liste des documents -->
    <div v-else class="documents-grid">
      <div 
        v-for="document in paginatedDocuments" 
        :key="document.id" 
        class="document-card"
        :class="{
          'document-draft': document.status === 'draft',
          'document-pending': document.status === 'pending_signature',
          'document-signed': document.status === 'signed',
          'document-rejected': document.status === 'rejected',
          'document-expired': document.status === 'expired'
        }"
      >
        <!-- En-tête de carte avec icône et statut -->
        <div class="document-header">
          <div class="document-icon">
            <i class="bi bi-file-earmark-text" v-if="document.status === 'draft'"></i>
            <i class="bi bi-hourglass-split" v-else-if="document.status === 'pending_signature'"></i>
            <i class="bi bi-file-earmark-check" v-else-if="document.status === 'signed'"></i>
            <i class="bi bi-file-earmark-x" v-else-if="document.status === 'rejected'"></i>
            <i class="bi bi-file-earmark-excel" v-else-if="document.status === 'expired'"></i>
          </div>
          <div class="document-status-badge">
            {{ document.status_display || formatStatus(document.status) }}
          </div>
        </div>

        <!-- Contenu principal du document -->
        <div class="document-content">
          <h3 class="document-title" :title="document.title">{{ document.title }}</h3>
          <p class="document-description" v-if="document.description">
            {{ document.description.length > 100 ? document.description.substring(0, 100) + '...' : document.description }}
          </p>
          <p class="document-description empty" v-else>Aucune description</p>
          
          <!-- Métadonnées du document -->
          <div class="document-meta">
            <div class="meta-item">
              <i class="bi bi-calendar-event"></i>
              <span>Créé le: {{ formatDate(document.created_at) }}</span>
            </div>
            <div class="meta-item" v-if="document.signature_date">
              <i class="bi bi-pen-fill"></i>
              <span>Signé le: {{ formatDate(document.signature_date) }}</span>
            </div>
            <div class="meta-item" v-if="document.owner_username">
              <i class="bi bi-person"></i>
              <span>Propriétaire: {{ document.owner_username }}</span>
            </div>
          </div>
        </div>

        <!-- En-tête supplémentaire pour afficher l'original -->
        <div class="document-original-badge" v-if="document.original_file">
          <div class="info-badge" title="Document certifié">
            <i class="bi bi-check-circle"></i> Original disponible
          </div>
        </div>
        
        <!-- Actions principales -->
        <div class="document-main-actions">
          <button class="action-btn primary full-width" @click="viewOriginalDocument(document)">
            Voir l'original
          </button>
          
          <!-- Pour les documents signés, ajouter un bouton pour télécharger la version signée -->
          <button 
            v-if="document.status === 'signed' && document.signed_file" 
            class="action-btn secondary" 
            @click="downloadSignedDocument(document)" 
            title="Télécharger la version signée"
          >
            Télécharger signé
          </button>
          
          <!-- Pour les documents non signés, utiliser le bouton de téléchargement normal -->
          <button 
            v-else 
            class="action-btn secondary" 
            @click="downloadDocument(document)" 
            title="Télécharger le document"
          >
            Télécharger
          </button>
        </div>
        
        <!-- Actions secondaires -->
        <div class="document-secondary-buttons">
          <!-- Pour les documents en mode brouillon, permettre l'édition -->
          <button 
            v-if="document.status === 'draft'" 
            class="action-btn text" 
            @click="editDocument(document)" 
            title="Modifier le document"
          >
            <i class="bi bi-pencil"></i> Modifier
          </button>
        </div>

        <!-- Actions contextuelles selon le statut -->
        <div class="document-status-actions">
          <button 
            v-if="document.status === 'pending_signature'" 
            class="action-btn signature-btn" 
            @click="signDocument(document)"
          >
            <i class="bi bi-pen"></i> Signer maintenant
          </button>
          
          <div v-if="document.status === 'signed'" class="signed-info">
            <i class="bi bi-patch-check-fill"></i>
            <span>Document certifié</span>
          </div>
        </div>


      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination-container">
      <div class="pagination-info">
        <span>Page {{ currentPage }} sur {{ totalPages }}</span>
        <span class="documents-count">({{ validFilteredDocuments.length }} documents au total)</span>
      </div>
      
      <div class="pagination-controls">
        <!-- Bouton Précédent -->
        <button 
          class="pagination-btn prev" 
          :disabled="currentPage === 1"
          @click="previousPage"
          title="Page précédente"
        >
          <i class="bi bi-chevron-left"></i>
          Précédent
        </button>
        
        <!-- Première page si pas visible -->
        <button 
          v-if="visiblePages[0] > 1"
          class="pagination-btn page"
          @click="goToPage(1)"
        >
          1
        </button>
        
        <!-- Points de suspension si nécessaire -->
        <span v-if="visiblePages[0] > 2" class="pagination-dots">...</span>
        
        <!-- Pages visibles -->
        <button 
          v-for="page in visiblePages"
          :key="page"
          class="pagination-btn page"
          :class="{ 'active': page === currentPage }"
          @click="goToPage(page)"
        >
          {{ page }}
        </button>
        
        <!-- Points de suspension si nécessaire -->
        <span v-if="visiblePages[visiblePages.length - 1] < totalPages - 1" class="pagination-dots">...</span>
        
        <!-- Dernière page si pas visible -->
        <button 
          v-if="visiblePages[visiblePages.length - 1] < totalPages"
          class="pagination-btn page"
          @click="goToPage(totalPages)"
        >
          {{ totalPages }}
        </button>
        
        <!-- Bouton Suivant -->
        <button 
          class="pagination-btn next" 
          :disabled="currentPage === totalPages"
          @click="nextPage"
          title="Page suivante"
        >
          Suivant
          <i class="bi bi-chevron-right"></i>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import DocumentService from '@/services/DocumentService';

const router = useRouter();

// États du composant
const documents = ref([]);
const filteredDocuments = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const showFilterMenu = ref(false);

// Variables de pagination
const currentPage = ref(1);
const itemsPerPage = 9; // 9 documents par page

// Propriété calculée pour filtrer les documents valides
const validFilteredDocuments = computed(() => {
  // S'assurer que les documents ont une structure valide
  return filteredDocuments.value.filter(doc => doc && typeof doc === 'object' && doc.document_id);
});

// Propriété calculée pour la pagination
const paginatedDocuments = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return validFilteredDocuments.value.slice(start, end);
});

// Propriété calculée pour le nombre total de pages
const totalPages = computed(() => {
  return Math.ceil(validFilteredDocuments.value.length / itemsPerPage);
});

// Propriété calculée pour les numéros de pages à afficher
const visiblePages = computed(() => {
  const pages = [];
  const total = totalPages.value;
  const current = currentPage.value;
  
  // Afficher au maximum 5 pages à la fois
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  
  // Ajuster si on est au début ou à la fin
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});
// Variables précédemment utilisées pour les modales, maintenant désactivées avec eslint-disable
// eslint-disable-next-line no-unused-vars
const currentDocument = ref({});
// eslint-disable-next-line no-unused-vars
const loadingPreview = ref(false);
// eslint-disable-next-line no-unused-vars
const previewUrl = ref('');
// eslint-disable-next-line no-unused-vars
const showViewModal = ref(false);

// Filtres pour les documents
const filters = reactive({
  all: true,
  draft: false,
  pending: false,
  signed: false
});

// État du nouveau document - maintenant désactivé avec eslint-disable car non utilisé
// eslint-disable-next-line no-unused-vars
const newDocument = reactive({
  title: '',
  description: '',
  document_type: 'contract',
  original_file: null
});

// Récupérer les documents de l'utilisateur au chargement du composant
onMounted(async () => {
  await fetchDocuments();
});

// Fonction pour récupérer les documents signés depuis l'API
async function fetchDocuments() {
  loading.value = true;
  error.value = null;
  console.log('Début de la récupération des documents signés...');
  
  try {
    console.log('Utilisation du service DocumentService pour récupérer les signatures...');
    const response = await DocumentService.getDocuments();
    console.log('Réponse API signatures:', response);
    
    if (response && response.data) {
      documents.value = response.data;
      console.log('Documents signés récupérés:', documents.value);
      
      // Si documents.value est un objet au lieu d'un tableau, vérifier s'il a une propriété résultats
      if (!Array.isArray(documents.value) && documents.value.results) {
        documents.value = documents.value.results;
        console.log('Documents signés extraits du champ results:', documents.value);
      }
      
      // Assurons-nous que documents.value est un tableau
      if (!Array.isArray(documents.value)) {
        console.warn('Les documents signés récupérés ne sont pas un tableau, conversion en tableau vide');
        documents.value = [];
      }
      
      // Mapper les statuts si nécessaire pour la compatibilité avec l'interface
      documents.value = documents.value.map(doc => ({
        ...doc,
        id: doc.document_id, // Pour la compatibilité avec les références existantes
        // S'assurer que le statut est défini, sinon utiliser une valeur par défaut
        status: doc.status || (doc.signed_file ? 'signed' : 'pending_signature'),
        // Format de date pour l'affichage
        created_at_display: doc.created_at_display || doc.created_at,
        // S'assurer que title est défini
        title: doc.title || `Document ${doc.document_id}`,
        // S'assurer que description a une valeur par défaut si absente
        description: doc.description || doc.metadata?.description || '',
        // Handling des fichiers - s'assurer que les chemins sont corrects
        original_file: doc.original_file || null,
        signed_file: doc.signed_file || null
      }));
      
      filteredDocuments.value = documents.value;
      console.log('Documents signés filtrés:', filteredDocuments.value);
    } else {
      console.warn('Aucune donnée dans la réponse API');
      documents.value = [];
      filteredDocuments.value = [];
    }
    
    loading.value = false;
  } catch (err) {
    console.error('Erreur lors de la récupération des documents signés:', err);
    if (err.response) {
      console.error('Détails de l\'erreur API:', err.response.data);
      console.error('Statut:', err.response.status);
    }
    error.value = 'Impossible de charger vos documents signés. Veuillez réessayer plus tard.';
    documents.value = [];
    filteredDocuments.value = [];
    loading.value = false;
  }
}

// Fonction de filtrage des documents
function filterDocuments() {
  // Vérifier si documents.value est un tableau valide
  if (!documents.value || !Array.isArray(documents.value) || documents.value.length === 0) {
    filteredDocuments.value = [];
    return;
  }

  try {
    // Si tous les filtres sont désactivés ou le filtre 'tous' est activé
    if (filters.all || (!filters.draft && !filters.pending && !filters.signed)) {
      filteredDocuments.value = documents.value.filter(doc => {
        // Vérifier que le document est valide et a les propriétés requises
        if (!doc || !doc.title) return false;
        
        return doc.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          (doc.description && doc.description.toLowerCase().includes(searchQuery.value.toLowerCase()));
      });
    } else {
      // Filtrer par statut
      filteredDocuments.value = documents.value.filter(doc => {
        // Vérifier que le document est valide et a les propriétés requises
        if (!doc || !doc.title || !doc.status) return false;
        
        const matchesSearch = doc.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          (doc.description && doc.description.toLowerCase().includes(searchQuery.value.toLowerCase()));
        
        const matchesStatus = 
          (filters.draft && doc.status === 'draft') ||
          (filters.pending && doc.status === 'pending_signature') ||
          (filters.signed && doc.status === 'signed');
        
        return matchesSearch && matchesStatus;
      });
    }
    
    // Réinitialiser à la première page après un filtrage
    currentPage.value = 1;
  } catch (error) {
    console.error('Erreur lors du filtrage des documents:', error);
    filteredDocuments.value = [];
  }
}

// Fonctions de pagination
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
}

function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
}

// Gestion des actions sur les documents
// eslint-disable-next-line no-unused-vars
function viewDocument(document) {
  // Ouvrir le document directement dans un nouvel onglet
  // au lieu d'utiliser la modale qui a été supprimée
  if (document && document.original_file) {
    const url = document.original_file;
    window.open(url, '_blank');
    
    // Enregistrer l'activité de consultation du document
    recordDocumentActivity(document.id, 'viewed');
  } else {
    alert('Document non disponible');
  }
}

async function downloadDocument(doc) {
  try {
    if (!doc || (!doc.document_id && !doc.id)) {
      console.error('ID de document manquant pour le téléchargement');
      alert('Aucun fichier original disponible pour ce document.');
      return;
    }
    
    const documentId = doc.document_id || doc.id;
    console.log('Téléchargement du document original:', documentId);
    
    // Enregistrer l'activité avec des métadonnées détaillées
    await recordDocumentActivity(
      documentId, 
      'downloaded',
      {
        file_type: 'original',
        doc_title: doc.title || `Document ${documentId}`,
        timestamp: new Date().toISOString(),
        file_format: 'pdf'
      }
    );
    
    // Utiliser l'endpoint de téléchargement qui utilise le champ document_id
    const response = await DocumentService.downloadDocument(documentId);
    
    if (response && response.data) {
      // Créer un blob URL pour le téléchargement
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      
      // Créer un lien temporaire pour le téléchargement
      const link = document.createElement('a');
      link.href = url;
      link.download = doc.title || `document-${documentId}.pdf`;
      
      // Ajouter au document, cliquer, puis supprimer
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Libérer l'URL objet
      window.URL.revokeObjectURL(url);
      
      console.log('Téléchargement du document original réussi');
    } else {
      console.error('Données de réponse manquantes');
      alert('Aucun fichier original disponible pour ce document.');
    }
  } catch (error) {
    console.error('Erreur lors du téléchargement:', error);
    alert('Erreur lors du téléchargement du document. Veuillez réessayer.');
  }
}

async function downloadSignedDocument(doc) {
  try {
    // Vérifier si le document signé existe
    if (!doc.signed_file) {
      alert('Ce document n\'a pas de version signée.');
      return;
    }
    
    if (!doc || (!doc.document_id && !doc.id)) {
      console.error('ID de document manquant pour le téléchargement de la version signée');
      alert('Impossible d\'identifier le document signé à télécharger.');
      return;
    }
    
    const documentId = doc.document_id || doc.id;
    console.log('Téléchargement du document signé:', documentId);
    
    // Construire le nom du fichier
    const filename = doc.title ? `${doc.title.replace(/\.[^/.]+$/, '')}_signed.pdf` : `document-${documentId}_signed.pdf`;
    
    // Enregistrer l'activité avec des métadonnées détaillées avant le téléchargement
    await recordDocumentActivity(
      documentId, 
      'downloaded',
      {
        file_type: 'signed',
        doc_title: doc.title || `Document ${documentId}`,
        timestamp: new Date().toISOString(),
        file_format: 'pdf',
        signature_date: doc.signature_date || doc.created_at,
        filename: filename
      }
    );
    
    // Utiliser l'endpoint de téléchargement qui utilise le champ document_id
    const response = await DocumentService.downloadDocument(documentId);
    
    if (response && response.data) {
      // Créer un blob URL pour le téléchargement
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      
      // Créer un lien temporaire pour le téléchargement
      const link = document.createElement('a');
      
      link.href = url;
      link.download = filename;
      
      // Ajouter au document, cliquer, puis supprimer
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Libérer l'URL objet
      window.URL.revokeObjectURL(url);
      
      console.log('Téléchargement du document signé réussi');
    } else {
      console.error('Données de réponse manquantes');
      alert('Impossible de télécharger le document signé.');
    }
  } catch (error) {
    console.error('Erreur lors du téléchargement du document signé:', error);
    alert('Erreur lors du téléchargement du document signé. Veuillez réessayer.');
  }
}

function editDocument() {
  alert('Fonctionnalité d\'édition à venir');
}

function signDocument(document) {
  const documentId = document.document_id || document.id;
  console.log('Redirection vers la page de signature pour le document:', documentId);
  
  // Enregistrer l'activité avant la redirection
  recordDocumentActivity(
    documentId,
    'signed',
    {
      action: 'initiate_signature_process',
      doc_title: document.title || `Document ${documentId}`,
      timestamp: new Date().toISOString(),
      document_status: document.status
    }
  ).then(() => {
    // Rediriger vers la page de signature après l'enregistrement de l'activité
    router.push({ 
      name: 'sign-document', 
      params: { documentId: documentId }
    });
  }).catch((error) => {
    console.error('Erreur lors de l\'enregistrement de l\'activité de signature:', error);
    // Rediriger malgré l'erreur d'enregistrement
    router.push({ 
      name: 'sign-document', 
      params: { documentId: documentId }
    });
  });
}

/* Ces fonctions sont temporairement désactivées mais conservées pour une utilisation future */

// eslint-disable-next-line no-unused-vars
function shareDocument() {
  alert('Fonctionnalité de partage à venir');
}

// eslint-disable-next-line no-unused-vars
async function deleteDocument(document) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le document "${document.title}" ?`)) {
    try {
      await DocumentService.deleteDocument(document.id);
      
      // Retirer le document de la liste
      documents.value = documents.value.filter(doc => doc.id !== document.id);
      filterDocuments();
      
      alert('Document supprimé avec succès');
    } catch (err) {
      console.error('Erreur lors de la suppression:', err);
      alert('Impossible de supprimer le document. Veuillez réessayer plus tard.');
    }
  }
}

// Fonction pour voir le document original
async function viewOriginalDocument(document) {
  if (!document.original_file) {
    alert('Aucun fichier original disponible pour ce document.');
    return;
  }
  
  const documentId = document.document_id || document.id;
  const documentTitle = document.title || `Document ${documentId}`;
  
  try {
    // Enregistrer l'activité de consultation avec métadonnées détaillées
    await recordDocumentActivity(
      documentId, 
      'viewed',
      {
        file_type: 'original',
        doc_title: documentTitle,
        timestamp: new Date().toISOString(),
        view_method: 'browser_preview',
        user_agent: navigator.userAgent
      }
    );
    
    console.log('Document original à visualiser :', document);
    
    // Au lieu d'utiliser l'URL directement, utilisons l'API spécifique pour le document original
    try {
      // Télécharger EXPLICITEMENT le document original via l'API dédiée
      const response = await DocumentService.downloadOriginalDocument(documentId);
      console.log('Document original téléchargé pour prévisualisation:', response);
      
      if (response && response.data) {
        // Créer un blob URL pour la visualisation
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const blobUrl = window.URL.createObjectURL(blob);
        
        // Ouvrir le PDF dans un nouvel onglet avec une interface améliorée
        const pdfViewer = window.open('', '_blank');
        pdfViewer.document.write(`
          <html>
            <head>
              <title>Document Original: ${documentTitle}</title>
              <style>
                body { margin:0; padding:0; overflow:hidden; background-color: #f5f5f5; }
                .toolbar { 
                  background-color: #333; color: white; padding: 10px; 
                  display: flex; justify-content: space-between; align-items: center;
                  font-family: Arial, sans-serif;
                }
                .toolbar h3 { margin: 0; }
                .info { font-size: 12px; margin-top: 5px; }
              </style>
            </head>
            <body>
              <div class="toolbar">
                <h3>Document Original: ${documentTitle}</h3>
                <div class="info">ID: ${documentId}</div>
              </div>
              <embed
                src="${blobUrl}"
                type="application/pdf"
                style="width:100%;height:calc(100vh - 50px);"
              />
            </body>
          </html>
        `);
        
        // Libérer l'URL objet lorsque l'utilisateur ferme l'onglet
        pdfViewer.onunload = () => {
          window.URL.revokeObjectURL(blobUrl);
        };
      } else {
        throw new Error('Aucune donnée reçue pour ce document');
      }
    } catch (viewError) {
      console.error('Erreur lors de la prévisualisation:', viewError);
      alert('Impossible de visualiser ce document. Essayez de le télécharger à la place.');
    }
    
    console.log('Visualisation du document original réussie');
  } catch (err) {
    console.error('Erreur lors de l\'affichage du document original:', err);
    alert('Impossible d\'afficher le document original.');
  }
}

// Fonction pour voir un document signé
// eslint-disable-next-line no-unused-vars
async function viewSignedDocument(document) {
  if (!document.signed_file) {
    alert('Ce document ne possède pas de version signée');
    return;
  }
  
  const documentId = document.document_id || document.id;
  const documentTitle = document.title || `Document ${documentId}`;
  
  try {
    // Enregistrer l'activité de consultation du document signé avec métadonnées détaillées
    await recordDocumentActivity(
      documentId, 
      'viewed',
      {
        file_type: 'signed',
        doc_title: documentTitle,
        timestamp: new Date().toISOString(),
        view_method: 'browser_preview',
        user_agent: navigator.userAgent,
        signature_info: {
          signature_date: document.signature_date || document.created_at,
          status: 'signed'
        }
      }
    );
    
    console.log('Document signé à visualiser :', document);
    
    // Au lieu d'utiliser l'URL directement, utilisons l'API pour obtenir le contenu du fichier
    try {
      // Télécharger le document signé via l'API
      const response = await DocumentService.downloadDocument(documentId);
      console.log('Document signé téléchargé pour prévisualisation:', response);
      
      if (response && response.data) {
        // Créer un blob URL pour la visualisation
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const blobUrl = window.URL.createObjectURL(blob);
        
        // Ouvrir le PDF dans un nouvel onglet avec une interface améliorée
        const pdfViewer = window.open('', '_blank');
        pdfViewer.document.write(`
          <html>
            <head>
              <title>Document Signé: ${documentTitle}</title>
              <style>
                body { margin:0; padding:0; overflow:hidden; background-color: #f5f5f5; }
                .toolbar { 
                  background-color: #226933; color: white; padding: 10px; 
                  display: flex; justify-content: space-between; align-items: center;
                  font-family: Arial, sans-serif;
                }
                .toolbar h3 { margin: 0; }
                .signature-badge {
                  background-color: #dff5e2;
                  color: #226933;
                  padding: 3px 8px;
                  border-radius: 4px;
                  font-size: 12px;
                  display: inline-flex;
                  align-items: center;
                  margin-left: 10px;
                }
                .signature-badge:before {
                  content: '\\2713';
                  margin-right: 4px;
                  font-weight: bold;
                }
                .info { font-size: 12px; margin-top: 5px; }
              </style>
            </head>
            <body>
              <div class="toolbar">
                <div>
                  <h3>Document Signé: ${documentTitle}</h3>
                  <span class="signature-badge">Certifié</span>
                </div>
                <div class="info">ID: ${documentId}</div>
              </div>
              <embed
                src="${blobUrl}"
                type="application/pdf"
                style="width:100%;height:calc(100vh - 50px);"
              />
            </body>
          </html>
        `);
        
        // Libérer l'URL objet lorsque l'utilisateur ferme l'onglet
        pdfViewer.onunload = () => {
          window.URL.revokeObjectURL(blobUrl);
        };
      } else {
        throw new Error('Aucune donnée reçue pour ce document signé');
      }
    } catch (viewError) {
      console.error('Erreur lors de la prévisualisation du document signé:', viewError);
      alert('Impossible de visualiser ce document signé. Essayez de le télécharger à la place.');
    }
    
    console.log('Visualisation du document signé réussie');
  } catch (err) {
    console.error('Erreur lors de l\'affichage du document signé:', err);
    alert('Impossible d\'afficher le document signé.');
  }
}

// eslint-disable-next-line no-unused-vars
function closeUploadModal() {
  console.warn('Cette fonction a été désactivée car la modale a été supprimée');
}

// eslint-disable-next-line no-unused-vars
function resetUploadForm() {
  console.warn('Cette fonction a été désactivée car la modale a été supprimée');
}

// eslint-disable-next-line no-unused-vars
function onFileChange() {
  console.warn('Cette fonction a été désactivée car la modale a été supprimée');
}

// eslint-disable-next-line no-unused-vars
function onFileDrop() {
  console.warn('Cette fonction a été désactivée car la modale a été supprimée');
}

// eslint-disable-next-line no-unused-vars
function clearSelectedFile() {
  console.warn('Cette fonction a été désactivée car la modale a été supprimée');
}

// eslint-disable-next-line no-unused-vars
async function uploadDocument() {
  console.warn('Cette fonction a été désactivée car la modale a été supprimée');
}

// eslint-disable-next-line no-unused-vars
function closeViewModal() {
  console.warn('Cette fonction a été désactivée car la modale a été supprimée');
}

// Gestion des menus déroulants
function toggleFilterMenu() {
  showFilterMenu.value = !showFilterMenu.value;
}

// Utilitaires
function formatDate(dateString) {
  if (!dateString) return 'Non disponible';
  
  const options = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  
  try {
    return new Date(dateString).toLocaleDateString('fr-FR', options);
  } catch (error) {
    console.error('Erreur de formatage de date:', error);
    return dateString;
  }
}

/**
 * Convertit les codes de statut en libellés lisibles
 */
function formatStatus(status) {
  if (!status) return 'Inconnu';
  
  const statusMap = {
    'draft': 'Brouillon',
    'pending_signature': 'En attente de signature',
    'signed': 'Signé',
    'rejected': 'Rejeté',
    'expired': 'Expiré'
  };
  
  return statusMap[status] || status;
}

// Enregistre l'activité de l'utilisateur sur un document
async function recordDocumentActivity(documentId, activityType, metadata = {}) {
  try {
    if (!documentId) {
      console.error('ID de document manquant pour l\'enregistrement de l\'activité');
      return;
    }
    
    console.log('Enregistrement de l\'activité:', activityType, 'pour le document', documentId);
    
    // Obtenir la description en fonction du type d'activité
    const description = getActivityDescription(activityType);
    
    // Enregistrer l'activité via le service document
    const response = await DocumentService.recordActivity(
      documentId,
      activityType,
      description,
      metadata
    );
    
    if (response) {
      console.log('Activité enregistrée avec succès:', response);
    }
    
    return response;
  } catch (error) {
    console.error('Erreur lors de l\'enregistrement de l\'activité:', error);
    return null;
  }
}

function getActivityDescription(activityType) {
  const descriptions = {
    'created': 'Création du document',
    'viewed': 'Consultation du document',
    'modified': 'Modification du document',
    'signed': 'Signature du document',
    'downloaded': 'Téléchargement du document'
  };
  
  return descriptions[activityType] || `Activité: ${activityType}`;
}
</script>

<style scoped>
.my-documents-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  color: var(--text-color);
  animation: fade-in 0.3s ease;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-title {
  font-size: 28px;
  margin: 0;
  position: relative;
  color: var(--text-color);
  font-weight: 600;
  display: inline-block;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 60px;
  height: 3px;
  background: var(--primary-color);
  border-radius: 3px;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.search-container {
  position: relative;
}

.search-input {
  padding: 10px 15px 10px 40px;
  border-radius: 25px;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg);
  color: var(--text-color);
  min-width: 250px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.2);
}

.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.filter-dropdown {
  position: relative;
}

.filter-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 10px;
  z-index: 10;
  min-width: 200px;
}

.filter-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-radius: 4px;
}

.filter-item:hover {
  background-color: var(--hover-bg);
}

.filter-item label {
  margin-left: 10px;
  cursor: pointer;
}

/* États du composant */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: var(--text-secondary);
}

.loading-state .spinner,
.loading-preview .spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(var(--primary-color-rgb), 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.error-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 10px;
  color: var(--text-secondary);
}

.error-state p,
.empty-state p {
  margin-bottom: 20px;
  font-size: 1.1rem;
}

/* Grille de documents */
.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

/* Card design moderne et élégant */
.document-card {
  background-color: var(--card-bg, #ffffff);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.07);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color, #eaeaea);
  height: 100%;
  transform-origin: center bottom;
}

.document-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.15);
  border-color: rgba(0, 0, 0, 0.08);
}

/* En-tête avec icône et statut */
.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.document-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: var(--light-bg, #f8f9fa);
}

.document-status-badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background-color: var(--light-bg, #f0f0f0);
  color: var(--text-secondary, #6c757d);
}

/* Couleurs par statut */
.document-draft {
  --status-color: #6c757d;
}

.document-draft .document-icon {
  color: #6c757d;
  background-color: #f0f0f0;
}

.document-draft .document-status-badge {
  background-color: #f0f0f0;
  color: #6c757d;
}

.document-pending {
  --status-color: #ffc107;
}

.document-pending .document-icon {
  color: #ffc107;
  background-color: #fff8e1;
}

.document-pending .document-status-badge {
  background-color: #fff8e1;
  color: #ff9800;
}

.document-signed {
  --status-color: #28a745;
}

.document-signed .document-icon {
  color: #28a745;
  background-color: #e8f5e9;
}

.document-signed .document-status-badge {
  background-color: #e8f5e9;
  color: #28a745;
}

.document-rejected {
  --status-color: #dc3545;
}

.document-rejected .document-icon {
  color: #dc3545;
  background-color: #fdf0f2;
}

.document-rejected .document-status-badge {
  background-color: #fdf0f2;
  color: #dc3545;
}

.document-expired {
  --status-color: #6c757d;
}

.document-expired .document-icon {
  color: #6c757d;
  background-color: #f0f0f0;
}

.document-expired .document-status-badge {
  background-color: #f0f0f0;
  color: #6c757d;
}

/* Contenu du document */
.document-content {
  padding: 20px 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.document-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #333);
  line-height: 1.4;
  /* Ellipsis pour les titres longs */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.document-description {
  margin: 0 0 15px 0;
  color: var(--text-secondary, #666);
  font-size: 14px;
  line-height: 1.5;
  /* Limiter à 3 lignes */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.document-description.empty {
  color: var(--text-muted, #aaa);
  font-style: italic;
}

/* Document meta styles */
.document-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: auto;
  padding-top: 15px;
  font-size: 13px;
  color: var(--text-secondary, #6c757d);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-item i {
  width: 16px;
  text-align: center;
  color: var(--text-secondary, #6c757d);
  opacity: 0.7;
}

/* Badge Document original */
.document-original-badge {
  padding: 8px 15px;
  text-align: center;
  margin-top: 5px;
}

/* Style pour le badge informatif (pas cliquable) */
.info-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background-color: rgba(40, 167, 69, 0.08);
  color: var(--success-color, #28a745);
  border: 1px solid rgba(40, 167, 69, 0.15);
  border-radius: 20px;
  font-size: 13px;
}

.info-badge i {
  font-size: 14px;
}

/* Pour référence - ancien style de badge-btn */
.badge-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background-color: rgba(13, 110, 253, 0.08);
  color: var(--primary-color, #007bff);
  border: 1px solid rgba(13, 110, 253, 0.15);
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.badge-btn:hover {
  background-color: rgba(13, 110, 253, 0.15);
}

.badge-btn i {
  font-size: 14px;
}

/* Document main actions */
.document-main-actions {
  display: flex;
  gap: 10px;
  padding: 12px 15px;
  border-top: 1px solid var(--border-color, #f0f0f0);
}

.action-btn {
  padding: 8px 15px;
  font-size: 14px;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border: none;
  flex: 1;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1.275);
  letter-spacing: 0.2px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  text-transform: uppercase;
}

.action-btn.full-width {
  flex: 2;
}

.action-btn.primary {
  background-color: var(--primary-color, #007bff);
  color: white;
}

.action-btn.primary:hover {
  background-color: var(--primary-dark, #0069d9);
  box-shadow: 0 5px 15px rgba(0, 123, 255, 0.3);
  transform: translateY(-2px);
}

.action-btn.secondary {
  background-color: var(--light-bg, #f8f9fa);
  color: var(--text-color, #495057);
  border: 1px solid var(--border-color, #ddd);
}

.action-btn.secondary:hover {
  background-color: var(--hover-bg, #e9ecef);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Status actions (signer, etc.) */
.document-status-actions {
  display: flex;
  justify-content: center;
  padding: 0 15px 8px 15px;
  margin-top: -5px;
}

.action-btn.signature-btn {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
  padding: 10px 20px;
  width: 100%;
  font-weight: 600;
  border-radius: 30px;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  border: none;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.action-btn.signature-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
}

.action-btn.signature-btn i {
  margin-right: 8px;
}

/* Signed info badge */
.signed-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 15px;
  background-color: #e8f5e9;
  color: #28a745;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  width: 100%;
}

.signed-info i {
  color: #28a745;
  font-size: 16px;
}

/* Actions secondaires */
.document-secondary-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  padding: 5px 15px 15px;
  border-top: 1px solid rgba(0, 0, 0, 0.03);
}

.action-btn.text {
  background: transparent;
  color: var(--text-secondary, #6c757d);
  border: none;
  box-shadow: none;
  padding: 8px 12px;
  text-transform: none;
  font-weight: 500;
  font-size: 14px;
  letter-spacing: normal;
}

.action-btn.text:hover {
  background-color: rgba(0, 0, 0, 0.03);
  color: var(--primary-color, #007bff);
  box-shadow: none;
  transform: none;
}

.action-btn.text.accent {
  color: var(--primary-color, #007bff);
  font-weight: 600;
}

.action-btn.text.accent:hover {
  background-color: rgba(0, 123, 255, 0.08);
}

.document-actions {
  position: absolute;
  top: 15px;
  right: 15px;
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: var(--text-secondary);
}

.btn-icon:hover {
  background-color: var(--hover-bg);
  color: var(--primary-color);
}

.action-menu {
  position: absolute;
  top: 40px;
  right: 0;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 100;
  width: 220px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(10px);
  animation: fadeInDown 0.2s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.action-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-color, #333);
  font-size: 14px;
  position: relative;
  overflow: hidden;
}

.action-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background-color: transparent;
  transition: all 0.2s ease;
}

.action-item:hover {
  background-color: var(--hover-bg, #f8f9fa);
}

.action-item:hover::before {
  background-color: var(--primary-color, #007bff);
}

.action-item i {
  font-size: 16px;
  color: var(--text-secondary, #6c757d);
  transition: all 0.2s ease;
}

.action-item:hover i {
  color: var(--primary-color, #007bff);
}

.action-separator {
  margin: 6px 0;
  border: none;
  height: 1px;
  background-color: var(--border-color, #eaeaea);
}

.action-item.danger {
  color: #dc3545;
}

.action-item.danger:hover {
  background-color: #fff5f5;
}

.action-item.danger:hover::before {
  background-color: #dc3545;
}

.action-item.danger i {
  color: #dc3545;
}

.action-item.danger i {
  color: #dc3545;
}

/* Les styles des modales ont été supprimés car les modales ne sont plus utilisées */

.file-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.file-size {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

/* Document viewer */
.document-viewer {
  margin-bottom: 20px;
}

.document-preview {
  width: 100%;
  height: 400px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.loading-preview {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--input-bg);
}

.preview-error {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--input-bg);
  color: var(--text-secondary);
}

.preview-error i {
  font-size: 3rem;
  margin-bottom: 15px;
}

.document-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  background-color: var(--input-bg);
  padding: 10px 15px;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 25px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
}

.btn-secondary {
  background-color: var(--secondary-bg);
  color: var(--text-color);
}

.btn-secondary:hover {
  background-color: var(--hover-bg);
}

.btn-outline-secondary {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.btn-outline-secondary:hover {
  background-color: var(--hover-bg);
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.btn i {
  font-size: 1rem;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.85rem;
}

/* Animations */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .search-input {
    min-width: 0;
    width: 150px;
  }
  
  .documents-grid {
    grid-template-columns: 1fr;
  }
  
  .document-preview {
    height: 300px;
  }
  
  .document-details {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .header-actions {
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .search-container {
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
  
  .document-viewer {
    height: 250px;
  }
  
  .document-preview {
    height: 250px;
  }
  
  .modal-content {
    width: 95%;
  }
}

/* Dark Mode Optimization */
:global(.dark-theme) .document-card {
  background-color: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .search-input,
:global(.dark-theme) .form-control,
:global(.dark-theme) .detail-item {
  background-color: rgba(30, 41, 59, 0.5);
}

:global(.dark-theme) .modal-content {
  background-color: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .filter-menu,
:global(.dark-theme) .action-menu {
  background-color: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .btn-secondary {
  background-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme) .btn-outline-secondary {
  border-color: rgba(255, 255, 255, 0.2);
}

:global(.dark-theme) .upload-zone {
  border-color: rgba(255, 255, 255, 0.2);
}

/* Animations et effets visuels */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* Fond animé avec particules */
.my-documents-container {
  position: relative;
  min-height: 100vh;
  padding: 30px 20px;
  background-color: var(--bg-color);
  overflow: hidden;
}

.particles-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  z-index: 1;
  filter: blur(2px);
  animation: float infinite linear;
  transition: all 0.3s ease;
}

.particle-primary {
  background-color: var(--primary-color, #007bff);
}

.particle-accent {
  background-color: var(--accent-color, #17a2b8);
}

.particle-light {
  background-color: var(--text-color, #495057);
  opacity: 0.1;
}

.content-wrapper {
  position: relative;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
}

/* Améliorations des cards */
.document-card {
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  animation: fadeIn 0.5s ease-out;
  animation-fill-mode: both;
  transform-origin: center bottom;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

.document-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.12);
}

/* Animation d'entrée pour les cards */
@media (prefers-reduced-motion: no-preference) {
  .document-card {
    opacity: 0;
    animation: slideInUp 0.5s forwards;
  }
  
  .document-card:nth-child(1) { animation-delay: 0.1s; }
  .document-card:nth-child(2) { animation-delay: 0.2s; }
  .document-card:nth-child(3) { animation-delay: 0.3s; }
  .document-card:nth-child(4) { animation-delay: 0.4s; }
  .document-card:nth-child(5) { animation-delay: 0.5s; }
  .document-card:nth-child(n+6) { animation-delay: 0.6s; }
}

/* États d'affichage améliorés */
.loading-container, .error-message, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background-color: var(--card-bg, white);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.5s ease-out;
  margin: 20px 0;
  min-height: 300px;
}

.loading-container .spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(var(--primary-color-rgb, 0, 123, 255), 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color, #007bff);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 25px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message i, .empty-state i {
  font-size: 70px;
  color: var(--danger-color, #dc3545);
  margin-bottom: 25px;
  animation: bounceIn 0.8s;
}

@keyframes bounceIn {
  0% { 
    transform: scale(0); 
    opacity: 0;
  }
  60% { 
    transform: scale(1.1); 
    opacity: 1;
  }
  100% { 
    transform: scale(1); 
  }
}

.empty-state i {
  color: var(--text-secondary, #6c757d);
}

/* Améliorations des boutons et contrôles */
.controls-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.search-box {
  position: relative;
  flex-grow: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 20px 12px 40px;
  border-radius: 30px;
  border: 1px solid var(--border-color, #ddd);
  background-color: var(--input-bg, white);
  color: var(--text-color, #495057);
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.search-input:focus {
  border-color: var(--primary-color, #007bff);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb, 0, 123, 255), 0.25);
  outline: none;
}

.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary, #6c757d);
  transition: color 0.3s ease;
}

.filter-btn {
  padding: 8px 16px;
  background-color: var(--light-bg, #f8f9fa);
  border: 1px solid var(--border-color, #ddd);
  border-radius: 20px;
  color: var(--text-secondary, #6c757d);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-right: 8px;
}

.filter-btn.active {
  background-color: var(--primary-color, #007bff);
  color: white;
  border-color: var(--primary-color, #007bff);
}

.filter-btn:hover:not(.active) {
  background-color: var(--hover-bg, #e9ecef);
}

.add-document {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 30px;
  color: var(--text-color, #495057);
  position: relative;
  display: inline-block;
}

.page-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 0;
  width: 60px;
  height: 4px;
  background-color: var(--primary-color, #007bff);
  border-radius: 2px;
}

/* Styles pour la pagination */
.pagination-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
  padding: 30px;
  background-color: var(--card-bg, white);
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.pagination-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  text-align: center;
  color: var(--text-color, #495057);
}

.pagination-info span:first-child {
  font-weight: 600;
  font-size: 16px;
}

.documents-count {
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 15px;
  border: 1px solid var(--border-color, #ddd);
  background-color: var(--card-bg, white);
  color: var(--text-color, #495057);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  min-width: 44px;
  min-height: 44px;
  text-decoration: none;
  gap: 6px;
}

.pagination-btn:hover:not(:disabled) {
  background-color: var(--primary-color, #007bff);
  color: white;
  border-color: var(--primary-color, #007bff);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

.pagination-btn.active {
  background-color: var(--primary-color, #007bff);
  color: white;
  border-color: var(--primary-color, #007bff);
  font-weight: 600;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--light-bg, #f8f9fa);
  color: var(--text-secondary, #6c757d);
}

.pagination-btn:disabled:hover {
  transform: none;
  box-shadow: none;
  background-color: var(--light-bg, #f8f9fa);
  color: var(--text-secondary, #6c757d);
  border-color: var(--border-color, #ddd);
}

.pagination-btn.prev,
.pagination-btn.next {
  padding: 10px 20px;
  font-weight: 600;
}

.pagination-btn.page {
  width: 44px;
  height: 44px;
  padding: 0;
  border-radius: 50%;
}

.pagination-dots {
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: var(--text-secondary, #6c757d);
  font-weight: bold;
  font-size: 16px;
}

/* Responsive pour la pagination */
@media (max-width: 768px) {
  .pagination-container {
    margin-top: 30px;
    padding: 20px;
  }
  
  .pagination-controls {
    gap: 4px;
  }
  
  .pagination-btn {
    min-width: 40px;
    min-height: 40px;
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .pagination-btn.page {
    width: 40px;
    height: 40px;
  }
  
  .pagination-btn.prev,
  .pagination-btn.next {
    padding: 8px 16px;
  }
  
  /* Masquer le texte sur mobile, garder seulement les icônes */
  .pagination-btn.prev span,
  .pagination-btn.next span {
    display: none;
  }
}

@media (max-width: 480px) {
  .pagination-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
  }
}
</style>
