<template>
  <!-- Container principal avec style adaptatif -->
  <div class="prepare-document-container integrated-mode">
    <!-- En-tête pour le mode intégré -->
    <div class="section-header">
      <h3 class="section-title">
        <i class="bi bi-file-earmark-plus"></i>
        Préparer un nouveau document
      </h3>
      <button class="btn btn-outline-secondary" @click="closeModal">
        <i class="bi bi-arrow-left"></i> Retour
      </button>
    </div>
      
    <!-- Section card contenant tout le contenu -->
    <div class="section-card">
      <!-- Progression des étapes -->
      <div class="steps-progress">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          :class="['step', { 'active': currentStep >= index, 'completed': currentStep > index }]"
        >
          <div class="step-number">
            <span v-if="currentStep > index"><i class="bi bi-check"></i></span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ step.label }}</div>
        </div>
      </div>

      <!-- Contenu principal qui change selon l'étape courante -->
      <div class="step-content">
        <!-- Étape 1: Sélection du document -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <i class="bi bi-cloud-arrow-up-fill"></i>
            <p>Déposez vos fichiers PDF ici ou cliquez pour sélectionner</p>
            <span class="upload-hint">Formats acceptés: .pdf (max 10MB par fichier) - Sélection multiple supportée</span>
            <input type="file" ref="fileInput" accept=".pdf" multiple @change="handleFileSelection" class="file-input">
          </div>
        </div>

        <!-- Étape 2: Prévisualisation des documents (MODIFICATION: support multi-documents) -->
        <div v-if="currentStep === 1" class="step-body">
          <!-- Onglets des documents -->
          <div class="document-tabs" v-if="selectedFiles.length > 1">
            <div 
              v-for="(file, index) in selectedFiles" 
              :key="index"
              :class="['document-tab', { 'active': activeDocumentIndex === index }]"
              @click="selectDocument(index)"
            >
              <div class="tab-content">
                <i class="bi bi-file-earmark-pdf"></i>
                <span class="tab-name">{{ truncateFileName(file.name) }}</span>
                <button @click.stop="removeDocument(index)" class="remove-document-btn">
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Information du document actuel -->
          <div class="document-info" v-if="selectedFiles[activeDocumentIndex]">
            <div class="document-icon">
              <i class="bi bi-file-earmark-pdf"></i>
            </div>
            <div class="document-details">
              <div class="document-name">{{ selectedFiles[activeDocumentIndex].name }}</div>
              <div class="document-size">{{ formatFileSize(selectedFiles[activeDocumentIndex].size) }}</div>
              <div class="document-pages" v-if="documentPreviews[activeDocumentIndex]?.totalPages">
                {{ documentPreviews[activeDocumentIndex].totalPages }} page(s)
              </div>
            </div>
          </div>

          <!-- Prévisualisation du document actuel -->
          <div class="pdf-preview-container" v-if="documentPreviews[activeDocumentIndex]">
            <div v-if="documentPreviews[activeDocumentIndex].loading" class="pdf-loading">
              <i class="bi bi-arrow-repeat spinning"></i>
              <p>Chargement de la prévisualisation...</p>
            </div>
            <div v-else-if="documentPreviews[activeDocumentIndex].error" class="pdf-error">
              <i class="bi bi-exclamation-triangle"></i>
              <p>Impossible de charger la prévisualisation. {{ documentPreviews[activeDocumentIndex].error }}</p>
            </div>
            <iframe v-else ref="pdfPreview" class="pdf-preview" :src="documentPreviews[activeDocumentIndex].url"></iframe>
          </div>

          <!-- Bouton pour ajouter d'autres documents -->
          <div class="add-more-documents">
            <button @click="triggerFileInput" class="add-document-btn">
              <i class="bi bi-plus-circle"></i> Ajouter d'autres documents
            </button>
          </div>
        </div>

        <!-- Étape 3: Position du QR code (MODIFICATION: support multi-documents) -->
        <div v-if="currentStep === 2" class="step-body">
          <!-- Onglets des documents pour le positionnement -->
          <div class="positioning-tabs" v-if="selectedFiles.length > 1">
            <div 
              v-for="(file, index) in selectedFiles" 
              :key="index"
              :class="['positioning-tab', { 
                'active': activePositioningIndex === index,
                'completed': documentPositions[index]?.completed 
              }]"
              @click="selectPositioningDocument(index)"
            >
              <div class="positioning-tab-content">
                <i class="bi bi-file-earmark-pdf"></i>
                <span class="tab-name">{{ truncateFileName(file.name) }}</span>
                <div class="completion-status">
                  <i v-if="documentPositions[index]?.completed" class="bi bi-check-circle-fill completed-icon"></i>
                  <i v-else class="bi bi-circle pending-icon"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- Information du document en cours de positionnement -->
          <div class="positioning-info" v-if="selectedFiles[activePositioningIndex]">
            <h4>
              <i class="bi bi-crosshair"></i> 
              Positionnement du QR code - {{ selectedFiles[activePositioningIndex].name }}
            </h4>
            <p class="positioning-hint">
              Document {{ activePositioningIndex + 1 }} sur {{ selectedFiles.length }}
              <span v-if="documentPositions[activePositioningIndex]?.completed" class="status-completed">
                ✓ Positionné
              </span>
              <span v-else class="status-pending">
                En attente de positionnement
              </span>
            </p>
          </div>

          <!-- Composant de positionnement -->
          <div class="qr-position-container" v-if="selectedFiles[activePositioningIndex]">
            <qr-positioner
              :pdf-file="selectedFiles[activePositioningIndex]"
              :total-pages="documentPreviews[activePositioningIndex]?.totalPages || 1"
              @position-changed="onQrPositionChanged"
              @position-confirmed="onQrPositionConfirmed"
              @pdf-generated="onPdfGenerated"
            ></qr-positioner>
          </div>
          
          <!-- Statut global et boutons de soumission -->
          <div class="submit-options">
            <div class="global-status">
              <div class="documents-status">
                <span class="completed-count">
                  {{ Object.keys(documentPositions).filter(key => documentPositions[key]?.completed).length }}
                </span>
                /
                <span class="total-count">{{ selectedFiles.length }}</span>
                documents positionnés
              </div>
              
              <div class="status-list">
                <div v-for="(file, index) in selectedFiles" :key="index" class="document-status-item">
                  <i class="bi bi-file-earmark-pdf"></i>
                  <span class="status-file-name">{{ truncateFileName(file.name, 15) }}</span>
                  <span v-if="documentPositions[index]?.completed" class="status-badge completed">
                    <i class="bi bi-check"></i> Positionné
                  </span>
                  <span v-else class="status-badge pending">
                    <i class="bi bi-clock"></i> En attente
                  </span>
                </div>
              </div>
            </div>

            <p class="submit-hint">
              <i class="bi bi-info-circle"></i>
              Une fois que tous les documents ont leurs QR codes positionnés, vous pouvez les soumettre pour signature ou les enregistrer comme brouillons.
            </p>
            
            <div class="submit-buttons">
              <button 
                @click="submitDocument" 
                class="submit-button primary"
                :disabled="!canProceedToNextStep"
              >
                <i class="bi bi-send"></i> Soumettre pour signature
                <span class="button-count">({{ selectedFiles.length }})</span>
              </button>
              <button 
                @click="saveAsDraft" 
                class="submit-button secondary"
                :disabled="!canProceedToNextStep"
              >
                <i class="bi bi-save"></i> Enregistrer comme brouillons
                <span class="button-count">({{ selectedFiles.length }})</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Étape 4: Confirmation -->
        <div v-if="currentStep === 3" class="step-body">
          <div class="submission-status">
            <div v-if="submissionStatus === 'loading'" class="submission-loading">
              <div class="processing-animation">
                <i class="bi bi-file-earmark-check pulsing"></i>
                <div class="spinner-container">
                  <div class="spinner"></div>
                </div>
              </div>
              <p class="processing-text">Préparation des {{ selectedFiles.length }} document(s) en cours...</p>
            </div>
            <div v-else-if="submissionStatus === 'error'" class="submission-error">
              <i class="bi bi-exclamation-circle"></i>
              <h4>Erreur lors de la préparation</h4>
              <p>{{ submissionError }}</p>
            </div>
            <div v-else-if="submissionStatus === 'success'" class="submission-success">
              <div class="success-animation">
                <i class="bi bi-check-circle-fill"></i>
              </div>
              <h3>Documents préparés avec succès !</h3>
              <p>Les {{ selectedFiles.length }} document(s) ont été envoyés au signataire et sont disponibles dans votre tableau de bord.</p>
              
              <div class="documents-list">
                <div v-for="(file, index) in selectedFiles" :key="index" class="document-info">
                <div class="document-icon large">
                  <i class="bi bi-file-earmark-check"></i>
                </div>
                <div class="document-details">
                    <div class="document-name">{{ file.name }}</div>
                  <div class="preparation-date">Préparé le {{ preparationDate }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Boutons de navigation entre les étapes -->
      <div class="step-navigation">
        <button 
          v-if="currentStep > 0 && currentStep < 3" 
          @click="prevStep" 
          class="nav-button secondary"
        >
          <i class="bi bi-arrow-left"></i> Précédent
        </button>
        
        <div class="spacer" v-if="currentStep > 0"></div>
        
        <button 
          v-if="currentStep < 2" 
          @click="nextStep" 
          class="nav-button primary"
          :disabled="!canProceedToNextStep"
        >
          Suivant <i class="bi bi-arrow-right"></i>
        </button>

        <button 
          v-if="currentStep === 3 && submissionStatus === 'success'" 
          @click="closePreparation" 
          class="nav-button primary"
        >
          Terminer <i class="bi bi-check"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineEmits } from 'vue';
import axios from 'axios';
import QrPositioner from '@/components/QrPositioner.vue';

// Définir les émetteurs d'événements
const emit = defineEmits(['close', 'documentPrepared']);

// Étapes du workflow de préparation de document
const steps = [
  { label: 'Sélection' },
  { label: 'Prévisualisation' },
  { label: 'Position QR' },
  { label: 'Confirmation' }
];

// Étape courante
const currentStep = ref(0);

// Références aux éléments DOM
const fileInput = ref(null);
const pdfPreview = ref(null);

// État des documents (MODIFICATION: support multi-documents)
const selectedFiles = ref([]);
const activeDocumentIndex = ref(0);
const activePositioningIndex = ref(0);

// État de la prévisualisation (MODIFICATION: support multi-documents)
const documentPreviews = ref([]);
const documentPositions = ref({});

// État de la soumission
const submissionStatus = ref(null); // 'loading', 'error', 'success'
const submissionError = ref(null);
const preparationDate = ref('');

// État pour le positionnement du QR code (SUPPRIMÉ: remplacé par documentPositions)

// Propriété calculée pour contrôler la progression des étapes (MODIFICATION: multi-documents)
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 0) {
    // Étape 1: Au moins un fichier PDF doit être sélectionné
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 1) {
    // Étape 2: Les prévisualisations doivent être chargées
    return selectedFiles.value.length > 0 && 
           documentPreviews.value.length === selectedFiles.value.length &&
           documentPreviews.value.every(preview => !preview.loading && !preview.error);
  } else if (currentStep.value === 2) {
    // Étape 3: Tous les documents doivent avoir leurs positions définies
    return selectedFiles.value.every((_, index) => 
      documentPositions.value[index]?.hasPositions
    );
  }
  
  return true;
});

// Méthodes de navigation entre les étapes
function nextStep() {
  if (currentStep.value < steps.length - 1 && canProceedToNextStep.value) {
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

// Méthodes de manipulation des fichiers
function triggerFileInput() {
  fileInput.value.click();
}

function handleFileSelection(event) {
  const files = Array.from(event.target.files);
  const pdfFiles = files.filter(file => file.type === 'application/pdf');
  
  if (pdfFiles.length > 0) {
    selectedFiles.value = [...selectedFiles.value, ...pdfFiles];
    
    // Si nous sommes à l'étape de sélection, passer automatiquement à la prévisualisation
    if (currentStep.value === 0) {
      nextStep();
      createDocumentPreviews();
    }
  }
}

function handleFileDrop(event) {
  event.preventDefault();
  
  const files = Array.from(event.dataTransfer.files);
  const pdfFiles = files.filter(file => file.type === 'application/pdf');
  
  if (pdfFiles.length > 0) {
    selectedFiles.value = [...selectedFiles.value, ...pdfFiles];
    
    // Si nous sommes à l'étape de sélection, passer automatiquement à la prévisualisation
    if (currentStep.value === 0) {
      nextStep();
      createDocumentPreviews();
    }
  }
}

function formatFileSize(size) {
  if (size < 1024) {
    return size + ' octets';
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' Ko';
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' Mo';
  }
}

// Créer les prévisualisations pour tous les documents (NOUVEAU: multi-documents)
function createDocumentPreviews() {
  console.log('Création des prévisualisations pour', selectedFiles.value.length, 'documents');
  
  documentPreviews.value = selectedFiles.value.map((file, index) => {
    const preview = {
      loading: true,
      error: null,
      url: null,
      totalPages: 1
    };
    
    console.log(`Création prévisualisation pour ${file.name} (index ${index})`);
    
    // Créer l'URL de prévisualisation immédiatement
    try {
  const fileUrl = URL.createObjectURL(file);
      preview.url = fileUrl;
      preview.loading = false;
      
      // Détecter le nombre de pages
      detectPdfPages(file).then(pages => {
        preview.totalPages = pages;
      });
      
      console.log(`URL créée pour ${file.name}:`, fileUrl);
    } catch (error) {
      console.error(`Erreur création URL pour ${file.name}:`, error);
      preview.error = 'Erreur de chargement';
      preview.loading = false;
    }
    
    return preview;
  });
  
  console.log('Prévisualisations créées:', documentPreviews.value);
}

// Fonction pour détecter le nombre de pages du PDF (MODIFICATION: retourne une promesse)
async function detectPdfPages(file) {
  try {
    console.log('Tentative de détection du nombre de pages...');
    
    // Méthode alternative : utiliser PDF.js directement
    const arrayBuffer = await file.arrayBuffer();
    
    // Utiliser PDF.js si disponible
    if (window.pdfjsLib) {
      const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      console.log(`PDF analysé avec PDF.js: ${pdf.numPages} pages détectées`);
      return pdf.numPages;
    }
    
    // Fallback : essayer de deviner depuis la taille du fichier
    const fileSizeKB = file.size / 1024;
    let estimatedPages = Math.max(1, Math.round(fileSizeKB / 50)); // Estimation: ~50KB par page
    estimatedPages = Math.min(estimatedPages, 100); // Max 100 pages estimées
    
    console.log(`Estimation du nombre de pages basée sur la taille: ${estimatedPages} pages (taille: ${fileSizeKB.toFixed(1)}KB)`);
    return estimatedPages;
    
  } catch (error) {
    console.error('Erreur lors de la détection des pages:', error);
    return 1;
  }
}

// Fonctions de navigation entre documents (NOUVEAU: multi-documents)
function selectDocument(index) {
  activeDocumentIndex.value = index;
}

function selectPositioningDocument(index) {
  activePositioningIndex.value = index;
}

function truncateFileName(fileName, maxLength = 20) {
  if (fileName.length <= maxLength) return fileName;
  const extension = fileName.split('.').pop();
  const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
  const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4);
  return `${truncatedName}...${extension}`;
}

function removeDocument(index) {
  selectedFiles.value.splice(index, 1);
  documentPreviews.value.splice(index, 1);
  
  // Supprimer les positions de ce document et réorganiser les indices
  const newPositions = {};
  Object.keys(documentPositions.value).forEach(key => {
    const keyIndex = parseInt(key);
    if (keyIndex < index) {
      newPositions[keyIndex] = documentPositions.value[key];
    } else if (keyIndex > index) {
      newPositions[keyIndex - 1] = documentPositions.value[key];
    }
  });
  documentPositions.value = newPositions;
  
  // Ajuster les indices actifs
  if (activeDocumentIndex.value >= index && activeDocumentIndex.value > 0) {
    activeDocumentIndex.value--;
  }
  if (activePositioningIndex.value >= index && activePositioningIndex.value > 0) {
    activePositioningIndex.value--;
  }
  
  // Si plus de documents, revenir à l'étape de sélection
  if (selectedFiles.value.length === 0) {
    currentStep.value = 0;
  }
}

// Méthodes pour le positionnement du QR code (MODIFICATION: support multi-documents)
function onQrPositionChanged(position) {
  if (!documentPositions.value[activePositioningIndex.value]) {
    documentPositions.value[activePositioningIndex.value] = {};
  }
  documentPositions.value[activePositioningIndex.value].qr_position = position.qr || position; // CORRECTION: gérer les deux structures
}

function onQrPositionConfirmed(position) {
  console.log('Positions confirmées pour le document', activePositioningIndex.value, ':', position);
  console.log('DEBUG - Position storing for index:', activePositioningIndex.value);
  console.log('DEBUG - Position data:', position);
  console.log('DEBUG - position.qr:', position.qr);
  console.log('DEBUG - position.qr keys:', Object.keys(position.qr || {}));
  console.log('DEBUG - position.qr.x:', position.qr?.x);
  console.log('DEBUG - position.qr.y:', position.qr?.y);
  
  // Stocker les positions pour le document actuel
  if (!documentPositions.value[activePositioningIndex.value]) {
    documentPositions.value[activePositioningIndex.value] = {};
  }
  
  // CORRECTION: Extraire les coordonnées de la première page positionée
  const firstPageKey = Object.keys(position.qr?.positions || {})[0];
  const firstPagePosition = position.qr?.positions?.[firstPageKey];
  
  console.log('DEBUG - firstPageKey:', firstPageKey);
  console.log('DEBUG - firstPagePosition:', firstPagePosition);
  console.log('DEBUG - firstPagePosition.x:', firstPagePosition?.x);
  console.log('DEBUG - firstPagePosition.y:', firstPagePosition?.y);
  
  const qrPosition = {
    x: firstPagePosition?.x || 85, // valeur par défaut si pas trouvée
    y: firstPagePosition?.y || 90, // valeur par défaut si pas trouvée
    size: position.qr?.size || 'medium',
    pages: position.qr?.pages || ['all'],
    positions: position.qr?.positions || {},
    mode: position.qr?.mode || 'standard'
  };
  
  console.log('DEBUG - qrPosition créé:', qrPosition);
  
  documentPositions.value[activePositioningIndex.value].qr_position = qrPosition;
  
  // NOUVEAU: Stocker aussi les informations de signature si disponibles
  if (position.signature) {
    console.log('DEBUG - Signature trouvée:', position.signature);
    console.log('DEBUG - position.signature.imageUrl:', position.signature.imageUrl);
    console.log('DEBUG - position.signature.image:', position.signature.image);
    
    const imageToStore = position.signature.imageUrl || position.signature.image || null;
    console.log('DEBUG - imageToStore:', imageToStore);
    
    documentPositions.value[activePositioningIndex.value].signature = {
      image: imageToStore,  // Stocker tel quel, conversion lors de l'envoi
      positions: position.signature.positions || {},
      size: position.signature.size || 50
    };
    console.log('DEBUG - Signature stockée pour le document', activePositioningIndex.value, ':', documentPositions.value[activePositioningIndex.value].signature);
  }
  
  documentPositions.value[activePositioningIndex.value].hasPositions = true;
  documentPositions.value[activePositioningIndex.value].completed = true;
  
  console.log('Document', activePositioningIndex.value, 'marqué comme terminé');
  console.log('DEBUG - After storing, documentPositions keys:', Object.keys(documentPositions.value));
  console.log('DEBUG - Stored QR position for index', activePositioningIndex.value, ':', documentPositions.value[activePositioningIndex.value].qr_position);
  console.log('DEBUG - Stored QR x:', documentPositions.value[activePositioningIndex.value].qr_position?.x);
  console.log('DEBUG - Stored QR y:', documentPositions.value[activePositioningIndex.value].qr_position?.y);
  
  // Passer automatiquement au document suivant s'il y en a un non terminé
  const nextIncomplete = selectedFiles.value.findIndex((_, index) => 
    index > activePositioningIndex.value && !documentPositions.value[index]?.completed
  );
  
  if (nextIncomplete !== -1) {
    console.log('Passage automatique au document suivant non terminé:', nextIncomplete);
    activePositioningIndex.value = nextIncomplete;
  }
}

// Nouvelle fonction pour gérer le PDF généré par QrPositioner
function onPdfGenerated(pdfData) {
  console.log('PDF généré reçu pour le document', activePositioningIndex.value, ':', pdfData);
  console.log('PDF file size:', pdfData.file?.size, 'bytes');
  console.log('PDF file name:', pdfData.file?.name);
  
  // Stocker le PDF généré pour le document actuel
  if (!documentPositions.value[activePositioningIndex.value]) {
    documentPositions.value[activePositioningIndex.value] = {};
  }
  
  documentPositions.value[activePositioningIndex.value].generatedPdf = {
    file: pdfData.file,
    dataUrl: pdfData.dataUrl,
    blob: pdfData.blob
  };
  
  console.log('PDF généré stocké pour le document', activePositioningIndex.value);
  console.log('Toutes les positions:', Object.keys(documentPositions.value));
}

// Soumettre tous les documents pour signature (MODIFICATION: support multi-documents)
async function submitDocument() {
  submissionStatus.value = 'loading';
  currentStep.value = 3; // Passer à l'étape de confirmation
  
  try {
    console.log('Démarrage de la soumission de', selectedFiles.value.length, 'documents');
    
    // Obtenir les informations du collaborateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userInfo.id) {
      console.warn('Utilisateur non connecté ou informations incomplètes');
    }

    // Vérifier qu'on a le nom de l'organisation
    if (!userInfo.organization || !userInfo.organization.name) {
      throw new Error('Informations de l\'organisation manquantes. Veuillez vous reconnecter.');
    }
    
    const processedDocuments = [];
    
    // Traiter chaque document séquentiellement
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i];
      const documentPosition = documentPositions.value[i];
      
      console.log(`Soumission du document ${i + 1}/${selectedFiles.value.length}: ${file.name}`);
      console.log('DEBUG - Index:', i, 'DocumentPosition:', documentPosition);
      console.log('DEBUG - DocumentPosition exists:', !!documentPosition);
      console.log('DEBUG - DocumentPosition.qr_position:', documentPosition?.qr_position);
      console.log('DEBUG - QR position x:', documentPosition?.qr_position?.x);
      console.log('DEBUG - QR position y:', documentPosition?.qr_position?.y);
      console.log('DEBUG - Toutes les positions keys:', Object.keys(documentPositions.value));
      
      // Vérifier que les données de position du QR sont valides pour ce document
      if (!documentPosition?.qr_position || 
          typeof documentPosition.qr_position.x !== 'number' || 
          typeof documentPosition.qr_position.y !== 'number') {
        console.log('DEBUG - Validation failed. documentPosition:', documentPosition);
        console.log('DEBUG - qr_position:', documentPosition?.qr_position);
        console.log('DEBUG - x type:', typeof documentPosition?.qr_position?.x);
        console.log('DEBUG - y type:', typeof documentPosition?.qr_position?.y);
        throw new Error(`Position du QR code invalide pour le document "${file.name}". Veuillez repositionner le QR code.`);
      }
      
      console.log('Position QR à envoyer pour', file.name, ':', documentPosition.qr_position);
      
      // Créer les données pour ce document
    const formData = new FormData();
      formData.append('document_file', file);
      formData.append('document_name', file.name);
    
    // Ajouter les informations de position du QR code avec conversion explicite en string
      formData.append('qr_x_position', documentPosition.qr_position.x.toString());
      formData.append('qr_y_position', documentPosition.qr_position.y.toString());
      formData.append('qr_size', documentPosition.qr_position.size.toString());
    
    // Simplification de qr_pages qui est maintenant un CharField
      formData.append('qr_pages', documentPosition.qr_position.pages || 'all');
      formData.append('qr_positions', JSON.stringify(documentPosition.qr_position.positions || {}));
      formData.append('qr_mode', documentPosition.qr_position.mode || 'standard');
      
      // NOUVEAU: Ajouter les informations de signature si disponibles
      if (documentPosition.signature) {
        console.log('DEBUG - Envoi signature pour document', i, ':', documentPosition.signature);
        
        // Traiter l'image de signature
        if (documentPosition.signature.image) {
          console.log('DEBUG - Image de signature détectée:', documentPosition.signature.image.substring(0, 50) + '...');
          
          let imageBlob;
          const imageData = documentPosition.signature.image;
          
          if (imageData.startsWith('blob:')) {
            // Nouvelle approche pour gérer les URLs blob avec canvas
            console.log('DEBUG - Conversion blob via canvas');
            try {
              // Créer une image et un canvas pour éviter CORS
              const img = new Image();
              const canvas = document.createElement('canvas');
              const ctx = canvas.getContext('2d');
              
              // Attendre que l'image se charge
              await new Promise((resolve, reject) => {
                img.onload = () => {
                  canvas.width = img.width;
                  canvas.height = img.height;
                  ctx.drawImage(img, 0, 0);
                  
                  // Convertir le canvas en blob
                  canvas.toBlob((blob) => {
                    imageBlob = blob;
                    console.log('DEBUG - Conversion canvas réussie:', imageBlob);
                    resolve();
                  }, 'image/png');
                };
                img.onerror = reject;
                img.src = imageData;
              });
            } catch (error) {
              console.error('Erreur conversion canvas:', error);
              // Fallback: essayer fetch quand même
              const response = await fetch(imageData);
              imageBlob = await response.blob();
            }
          } else if (imageData.startsWith('data:image')) {
            // C'est une image base64 complète - conversion directe
            console.log('DEBUG - Conversion base64 en Blob');
            const response = await fetch(imageData);
            imageBlob = await response.blob();
          } else {
            // Fallback : créer un Blob à partir des données base64 pures
            console.log('DEBUG - Conversion base64 pur en Blob');
            const byteCharacters = atob(imageData);
            const byteNumbers = new Array(byteCharacters.length);
            for (let j = 0; j < byteCharacters.length; j++) {
              byteNumbers[j] = byteCharacters.charCodeAt(j);
            }
            const byteArray = new Uint8Array(byteNumbers);
            imageBlob = new Blob([byteArray], { type: 'image/png' });
          }
          
          console.log('DEBUG - Blob créé:', imageBlob);
          formData.append('signature_image', imageBlob, 'signature.png');
        } else {
          console.log('DEBUG - Aucune image de signature à envoyer');
        }
        
        // Ajouter les positions de signature
        formData.append('signature_positions', JSON.stringify(documentPosition.signature.positions || {}));
        formData.append('signature_size', documentPosition.signature.size?.toString() || '50');
      } else {
        console.log('DEBUG - Aucune signature pour le document', i);
      }
    
    // Ajouter le statut
    formData.append('status', 'pending_signature');
    
    // NOUVEAU: Ajouter le PDF généré s'il existe
    if (documentPosition.generatedPdf && documentPosition.generatedPdf.file) {
      console.log('DEBUG - Ajout du PDF généré pour le document', i, ':', documentPosition.generatedPdf.file.name);
      console.log('DEBUG - Taille du PDF généré:', documentPosition.generatedPdf.file.size, 'bytes');
      formData.append('generated_pdf', documentPosition.generatedPdf.file, documentPosition.generatedPdf.file.name);
    } else {
      console.log('DEBUG - Aucun PDF généré disponible pour le document', i);
      console.log('DEBUG - documentPosition.generatedPdf:', !!documentPosition.generatedPdf);
      console.log('DEBUG - documentPosition.generatedPdf.file:', !!documentPosition.generatedPdf?.file);
    }
    
    // Ajouter l'ID de l'organisation
    formData.append('organization_id', userInfo.organization.id);
    
      // Ajouter des métadonnées supplémentaires
    const metadata = {
      prepared_by: {
        user_id: userInfo.id || '',
        username: userInfo.username || '',
        email: userInfo.email || '',
        full_name: userInfo.fullName || '',
      },
      organization: {
        id: userInfo.organization.id,
        name: userInfo.organization.name || '',
        serial_number: userInfo.organization.serial_number || '',
      },
      browser_info: navigator.userAgent,
        batch_info: {
          document_index: i + 1,
          total_documents: selectedFiles.value.length,
          batch_id: Date.now().toString()
        }
    };
    formData.append('metadata', JSON.stringify(metadata));
    
    // Configuration de la requête avec axios
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    };
      
      // Appel direct à l'API Django
      const apiUrl = 'https://ppd.camgovca.cm/api/documents/qr-positions/';
    
    // Appel API avec timeout plus long pour les gros fichiers
    const response = await axios.post(apiUrl, formData, {
      ...config,
      timeout: 30000 // 30 secondes
    });
    
    // Traiter la réponse
    if (response.status === 200 || response.status === 201) {
      const documentId = response.data.id;
        console.log(`Document ${file.name} préparé avec succès, ID:`, documentId);
        
        processedDocuments.push({
          id: documentId,
          name: file.name,
          status: 'pending_signature'
        });
      } else {
        throw new Error(`Erreur lors de la préparation du document "${file.name}"`);
      }
    }
      
      // Formater la date de préparation
      preparationDate.value = new Date().toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      // Passer à l'étape de confirmation
      submissionStatus.value = 'success';
      
    // Émettre l'événement documentPrepared pour tous les documents
      emit('documentPrepared', {
      documents: processedDocuments,
      count: processedDocuments.length,
        status: 'pending_signature'
      });
    
    console.log('Tous les documents ont été préparés avec succès');
    
  } catch (error) {
    console.error('Erreur lors de la préparation des documents:', error);
    console.error('Détails de l\'erreur:', error.response?.data || 'Pas de détails disponibles');
    submissionStatus.value = 'error';
    submissionError.value = error.response?.data?.error || 
                            error.response?.data?.detail || 
                            error.message || 
                            "Une erreur est survenue lors de la préparation des documents.";
  }
}

// Sauvegarder tous les documents comme brouillons (MODIFICATION: support multi-documents)
async function saveAsDraft() {
  submissionStatus.value = 'loading';
  currentStep.value = 3; // Passer à l'étape de confirmation
  
  try {
    console.log('Démarrage de la sauvegarde de', selectedFiles.value.length, 'documents comme brouillons');
    
    // Obtenir les informations du collaborateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userInfo.id) {
      console.warn('Utilisateur non connecté ou informations incomplètes');
    }
    
    // Vérifier qu'on a le nom de l'organisation
    if (!userInfo.organization || !userInfo.organization.name) {
      throw new Error('Informations de l\'organisation manquantes. Veuillez vous reconnecter.');
    }
    
    const savedDocuments = [];
    
    // Traiter chaque document séquentiellement
    for (let i = 0; i < selectedFiles.value.length; i++) {
      const file = selectedFiles.value[i];
      const documentPosition = documentPositions.value[i];
      
      console.log(`Sauvegarde du document ${i + 1}/${selectedFiles.value.length}: ${file.name}`);
      
      // Vérifier que les données de position du QR sont valides pour ce document
      if (!documentPosition?.qr_position || 
          typeof documentPosition.qr_position.x !== 'number' || 
          typeof documentPosition.qr_position.y !== 'number') {
        throw new Error(`Position du QR code invalide pour le document "${file.name}". Veuillez repositionner le QR code.`);
      }
      
      console.log('Position QR à envoyer pour le brouillon', file.name, ':', documentPosition.qr_position);
      
      // Créer les données pour ce document
    const formData = new FormData();
      formData.append('document_file', file);
      formData.append('document_name', file.name);
    
    // Ajouter les informations de position du QR code avec conversion explicite en string
      formData.append('qr_x_position', documentPosition.qr_position.x.toString());
      formData.append('qr_y_position', documentPosition.qr_position.y.toString());
      formData.append('qr_size', documentPosition.qr_position.size.toString());
    
    // Simplification de qr_pages qui est maintenant un CharField
      formData.append('qr_pages', documentPosition.qr_position.pages || 'all');
      formData.append('qr_positions', JSON.stringify(documentPosition.qr_position.positions || {}));
      formData.append('qr_mode', documentPosition.qr_position.mode || 'standard');
      
      // NOUVEAU: Ajouter les informations de signature si disponibles
      if (documentPosition.signature) {
        console.log('DEBUG - Envoi signature pour document', i, ':', documentPosition.signature);
        
        // Traiter l'image de signature
        if (documentPosition.signature.image) {
          console.log('DEBUG - Image de signature détectée:', documentPosition.signature.image.substring(0, 50) + '...');
          
          let imageBlob;
          const imageData = documentPosition.signature.image;
          
          if (imageData.startsWith('blob:')) {
            // Nouvelle approche pour gérer les URLs blob avec canvas
            console.log('DEBUG - Conversion blob via canvas');
            try {
              // Créer une image et un canvas pour éviter CORS
              const img = new Image();
              const canvas = document.createElement('canvas');
              const ctx = canvas.getContext('2d');
              
              // Attendre que l'image se charge
              await new Promise((resolve, reject) => {
                img.onload = () => {
                  canvas.width = img.width;
                  canvas.height = img.height;
                  ctx.drawImage(img, 0, 0);
                  
                  // Convertir le canvas en blob
                  canvas.toBlob((blob) => {
                    imageBlob = blob;
                    console.log('DEBUG - Conversion canvas réussie:', imageBlob);
                    resolve();
                  }, 'image/png');
                };
                img.onerror = reject;
                img.src = imageData;
              });
            } catch (error) {
              console.error('Erreur conversion canvas:', error);
              // Fallback: essayer fetch quand même
              const response = await fetch(imageData);
              imageBlob = await response.blob();
            }
          } else if (imageData.startsWith('data:image')) {
            // C'est une image base64 complète - conversion directe
            console.log('DEBUG - Conversion base64 en Blob');
            const response = await fetch(imageData);
            imageBlob = await response.blob();
          } else {
            // Fallback : créer un Blob à partir des données base64 pures
            console.log('DEBUG - Conversion base64 pur en Blob');
            const byteCharacters = atob(imageData);
            const byteNumbers = new Array(byteCharacters.length);
            for (let j = 0; j < byteCharacters.length; j++) {
              byteNumbers[j] = byteCharacters.charCodeAt(j);
            }
            const byteArray = new Uint8Array(byteNumbers);
            imageBlob = new Blob([byteArray], { type: 'image/png' });
          }
          
          console.log('DEBUG - Blob créé:', imageBlob);
          formData.append('signature_image', imageBlob, 'signature.png');
        } else {
          console.log('DEBUG - Aucune image de signature à envoyer');
        }
        
        // Ajouter les positions de signature
        formData.append('signature_positions', JSON.stringify(documentPosition.signature.positions || {}));
        formData.append('signature_size', documentPosition.signature.size?.toString() || '50');
      } else {
        console.log('DEBUG - Aucune signature pour le document', i);
      }
    
    // Ajouter le statut
    formData.append('status', 'draft');
    
    // NOUVEAU: Ajouter le PDF généré s'il existe
    if (documentPosition.generatedPdf && documentPosition.generatedPdf.file) {
      console.log('DEBUG - Ajout du PDF généré pour le brouillon', i, ':', documentPosition.generatedPdf.file.name);
      formData.append('generated_pdf', documentPosition.generatedPdf.file, documentPosition.generatedPdf.file.name);
    } else {
      console.log('DEBUG - Aucun PDF généré disponible pour le brouillon', i);
    }
    
    // Ajouter l'ID de l'organisation
    formData.append('organization_id', userInfo.organization.id);
    
      // Ajouter des métadonnées supplémentaires
    const metadata = {
      prepared_by: {
        user_id: userInfo.id || '',
        username: userInfo.username || '',
        email: userInfo.email || '',
        full_name: userInfo.fullName || '',
      },
      organization: {
        id: userInfo.organization.id,
        name: userInfo.organization.name || '',
        serial_number: userInfo.organization.serial_number || '',
      },
      browser_info: navigator.userAgent,
        batch_info: {
          document_index: i + 1,
          total_documents: selectedFiles.value.length,
          batch_id: Date.now().toString()
        }
    };
    formData.append('metadata', JSON.stringify(metadata));
    
    // Configuration de la requête avec axios
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    };
      
      // Appel direct à l'API Django
      const apiUrl = 'https://ppd.camgovca.cm/api/documents/qr-positions/';
    
    // Appel API avec timeout plus long pour les gros fichiers
    const response = await axios.post(apiUrl, formData, {
      ...config,
      timeout: 30000 // 30 secondes
    });
    
    // Traiter la réponse
    if (response.status === 200 || response.status === 201) {
      const documentId = response.data.id;
        console.log(`Brouillon ${file.name} sauvegardé avec succès, ID:`, documentId);
        
        savedDocuments.push({
          id: documentId,
          name: file.name,
          status: 'draft'
        });
      } else {
        throw new Error(`Erreur lors de la sauvegarde du brouillon "${file.name}"`);
      }
    }
      
      // Formater la date de préparation
      preparationDate.value = new Date().toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      // Passer à l'étape de confirmation
      submissionStatus.value = 'success';
      
    // Émettre l'événement documentPrepared pour tous les documents
      emit('documentPrepared', {
      documents: savedDocuments,
      count: savedDocuments.length,
        status: 'draft'
      });
    
    console.log('Tous les brouillons ont été sauvegardés avec succès');
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde des brouillons:', error);
    console.error('Détails de l\'erreur:', error.response?.data || 'Pas de détails disponibles');
    submissionStatus.value = 'error';
    submissionError.value = error.response?.data?.error || 
                            error.response?.data?.detail || 
                            error.message || 
                            "Une erreur est survenue lors de la sauvegarde des brouillons.";
  }
}

// Méthode pour fermer le composant (MODIFICATION: nettoyage multi-documents)
function closePreparation() {
  // Nettoyer les ressources pour tous les documents
  documentPreviews.value.forEach(preview => {
    if (preview.url) {
      URL.revokeObjectURL(preview.url);
    }
  });
  
  // Émettre l'événement pour fermer le composant
  emit('close');
}

// Alias pour closeModal (compatibilité)
function closeModal() {
  closePreparation();
}

// Nettoyer les ressources lors du démontage du composant (MODIFICATION: nettoyage multi-documents)
onMounted(() => {
  return () => {
    documentPreviews.value.forEach(preview => {
      if (preview.url) {
        URL.revokeObjectURL(preview.url);
    }
    });
  };
});
</script>

<style scoped>
.prepare-document-container {
  background-color: transparent;
  border-radius: 16px;
  box-shadow: none;
  width: 100%;
  max-width: 100%;
  animation: slide-up 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow-y: auto;
  max-height: 85vh;
  margin: 0;
  padding: 0;
}

.section-card {
  background-color: var(--card-bg, #ffffff);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  padding: 24px;
  position: relative;
  border: 1px solid var(--border-color, #eaeaea);
}

/* Effet de fond stylisé */
.prepare-document-container::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(6, 255, 165, 0.1) 0%, rgba(255, 255, 255, 0) 70%);
  border-radius: 50%;
  z-index: 0;
  pointer-events: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid rgba(6, 255, 165, 0.2);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 5;
}

.section-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color, #212529);
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-title i {
  color: var(--accent-color, #06ffa5);
  font-size: 1.3em;
}

.close-button {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  color: var(--text-muted, #6c757d);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--danger, #dc3545);
}

/* Progression des étapes */
.steps-progress {
  display: flex;
  justify-content: space-between;
  margin: 25px 30px;
  position: relative;
}

.steps-progress::before {
  content: '';
  position: absolute;
  top: 14px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--border-color, rgba(0, 0, 0, 0.1));
  z-index: 1;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
  flex: 1;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: var(--bg-color, #fff);
  border: 2px solid var(--border-color, rgba(0, 0, 0, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-muted, #6c757d);
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background-color: var(--primary, #4a6cf7);
  border-color: var(--primary, #4a6cf7);
  color: #fff;
  transform: scale(1.1);
  box-shadow: 0 0 15px rgba(74, 108, 247, 0.3);
}

.step.completed .step-number {
  background-color: var(--accent-color, #06ffa5);
  border-color: var(--accent-color, #06ffa5);
  color: #fff;
}

.step-label {
  font-size: 14px;
  color: var(--text-muted, #6c757d);
  text-align: center;
  transition: all 0.3s ease;
}

.step.active .step-label,
.step.completed .step-label {
  color: var(--text-color, #212529);
  font-weight: 500;
}

/* Contenus des étapes */
.step-content {
  margin: 30px;
  min-height: auto;
  position: relative;
  z-index: 1;
}

.step-body {
  animation: fade-in 0.3s ease-in-out;
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.03);
}

/* Zone de dépôt de fichier */
.upload-area {
  border: 2px dashed var(--border-color, #dee2e6);
  border-radius: 12px;
  padding: 50px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: rgba(6, 255, 165, 0.02);
}

.upload-area:hover {
  border-color: var(--accent-color, #06ffa5);
  background-color: rgba(6, 255, 165, 0.05);
  transform: translateY(-2px);
}

.upload-area i {
  font-size: 54px;
  color: var(--primary, #4a6cf7);
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.upload-area:hover i {
  color: var(--accent-color, #06ffa5);
  transform: scale(1.05);
}

.upload-area p {
  font-size: 18px;
  margin-bottom: 10px;
  font-weight: 500;
}

.upload-hint {
  font-size: 14px;
  color: var(--text-muted, #6c757d);
}

.file-input {
  display: none;
}

/* Informations du document */
.document-info {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 12px;
  background-color: rgba(6, 255, 165, 0.05);
  border: 1px solid rgba(6, 255, 165, 0.1);
}

.document-icon {
  font-size: 24px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background-color: rgba(74, 108, 247, 0.1);
  color: var(--primary, #4a6cf7);
  margin-right: 15px;
}

.document-icon.large {
  font-size: 32px;
  width: 70px;
  height: 70px;
}

.document-name {
  font-weight: 600;
  margin-bottom: 5px;
  word-break: break-all;
}

.document-size,
.preparation-date {
  font-size: 14px;
  color: var(--text-muted, #6c757d);
}

/* Prévisualisation du PDF */
.pdf-preview-container {
  height: 500px;
  border: 1px solid var(--border-color, #dee2e6);
  border-radius: 12px;
  overflow: hidden;
  background-color: #fff;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.03);
}

.pdf-preview {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-loading,
.pdf-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 20px;
}

.pdf-loading i {
  font-size: 48px;
  margin-bottom: 15px;
  color: var(--primary, #4a6cf7);
}

.pdf-error i {
  font-size: 48px;
  margin-bottom: 15px;
  color: var(--danger, #dc3545);
}

/* Formulaire du signataire */
.signatory-info-banner {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  background-color: rgba(74, 108, 247, 0.1);
  margin-bottom: 25px;
  border-left: 4px solid var(--primary, #4a6cf7);
}

.signatory-info-banner i {
  font-size: 24px;
  color: var(--primary, #4a6cf7);
  margin-right: 15px;
}

.signatory-info-banner h4 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.signatory-info-banner p {
  margin: 0;
  color: var(--text-muted, #6c757d);
}

.signatory-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid var(--border-color, #dee2e6);
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  border-color: var(--accent-color, #06ffa5);
  outline: none;
  box-shadow: 0 0 0 3px rgba(6, 255, 165, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

/* Statut de soumission */
.submission-status {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.submission-loading,
.submission-error,
.submission-success {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: fade-in 0.3s ease-in-out;
  max-width: 500px;
  margin: 0 auto;
}

.processing-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
}

.processing-animation i {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  color: var(--accent-color, #06ffa5);
}

.spinner-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.spinner {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 4px solid rgba(6, 255, 165, 0.1);
  border-top: 4px solid var(--accent-color, #06ffa5);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.processing-text {
  font-size: 18px;
  margin-bottom: 20px;
  font-weight: 500;
}

.submission-error i {
  font-size: 48px;
  color: var(--danger, #dc3545);
  margin-bottom: 15px;
}

.success-animation {
  margin-bottom: 20px;
}

.success-animation i {
  font-size: 64px;
  color: var(--accent-color, #06ffa5);
  animation: pop-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Navigation entre les étapes */
.step-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  border-top: 1px solid var(--border-color, rgba(0, 0, 0, 0.1));
  padding: 20px 25px;
  background: rgba(255, 255, 255, 0.9);
}

.nav-button {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-button.primary {
  background-color: var(--primary, #4a6cf7);
  color: #fff;
  border: none;
  box-shadow: 0 4px 10px rgba(74, 108, 247, 0.2);
}

.nav-button.primary:hover {
  background-color: #3955c8;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(74, 108, 247, 0.3);
}

.nav-button.secondary {
  background-color: transparent;
  color: var(--text-color, #212529);
  border: 1px solid var(--border-color, #dee2e6);
}

.nav-button.secondary:hover {
  background-color: rgba(0, 0, 0, 0.05);
  border-color: var(--text-muted, #6c757d);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.nav-button i {
  margin-left: 8px;
  margin-right: 8px;
}

.spacer {
  flex: 1;
}

/* Animations */
.pulsing {
  animation: pulse 1.5s infinite;
}

.spinning {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pop-in {
  0% { transform: scale(0); opacity: 0; }
  80% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes slide-up {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

/* Styles pour les onglets de documents */
.document-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color, #dee2e6);
  padding-bottom: 15px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.document-tabs::-webkit-scrollbar {
  display: none;
}

.document-tab {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #dee2e6);
  background: #fff;
  min-width: 180px;
  flex-shrink: 0;
}

.document-tab:hover {
  border-color: var(--primary, #4a6cf7);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(74, 108, 247, 0.15);
}

.document-tab.active {
  border-color: var(--accent-color, #06ffa5);
  background: linear-gradient(135deg, rgba(6, 255, 165, 0.1), rgba(6, 255, 165, 0.05));
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.2);
}

.tab-content {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.tab-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-color, #212529);
  flex: 1;
}

.remove-document-btn {
  background: rgba(220, 53, 69, 0.1);
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--danger, #dc3545);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
}

.remove-document-btn:hover {
  background: rgba(220, 53, 69, 0.2);
  transform: scale(1.1);
}

/* Styles pour le positionnement multi-documents */
.positioning-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color, #dee2e6);
  padding-bottom: 15px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.positioning-tabs::-webkit-scrollbar {
  display: none;
}

.positioning-tab {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  padding: 10px 15px;
  border: 1px solid var(--border-color, #dee2e6);
  background: #fff;
  min-width: 200px;
  flex-shrink: 0;
}

.positioning-tab:hover {
  border-color: var(--primary, #4a6cf7);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(74, 108, 247, 0.15);
}

.positioning-tab.active {
  border-color: var(--accent-color, #06ffa5);
  background: linear-gradient(135deg, rgba(6, 255, 165, 0.1), rgba(6, 255, 165, 0.05));
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.2);
}

.positioning-tab.completed {
  border-color: var(--success, #28a745);
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(40, 167, 69, 0.05));
}

.positioning-tab-content {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.completion-status {
  margin-left: auto;
}

.completed-icon {
  color: var(--success, #28a745);
  font-size: 16px;
}

.pending-icon {
  color: var(--text-muted, #6c757d);
  font-size: 16px;
}

/* Styles pour les informations de positionnement */
.positioning-info {
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(6, 255, 165, 0.05);
  border-radius: 8px;
  border-left: 4px solid var(--accent-color, #06ffa5);
}

.positioning-info h4 {
  margin: 0 0 5px 0;
  color: var(--text-color, #212529);
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.positioning-hint {
  margin: 0;
  color: var(--text-muted, #6c757d);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-completed {
  color: var(--success, #28a745);
  font-weight: 500;
}

.status-pending {
  color: var(--warning, #ffc107);
  font-weight: 500;
}

/* Styles pour le statut global */
.global-status {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid var(--border-color, #dee2e6);
}

.documents-status {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color, #212529);
  margin-bottom: 15px;
  text-align: center;
}

.completed-count {
  color: var(--success, #28a745);
}

.total-count {
  color: var(--text-muted, #6c757d);
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.document-status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid var(--border-color, #dee2e6);
}

.status-file-name {
  flex: 1;
  font-size: 14px;
  color: var(--text-color, #212529);
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-badge.completed {
  background: rgba(40, 167, 69, 0.1);
  color: var(--success, #28a745);
}

.status-badge.pending {
  background: rgba(255, 193, 7, 0.1);
  color: var(--warning, #ffc107);
}

/* Styles pour le bouton d'ajout de documents */
.add-more-documents {
  margin-top: 20px;
  text-align: center;
  padding: 15px;
  border: 2px dashed var(--border-color, #dee2e6);
  border-radius: 8px;
  background: rgba(6, 255, 165, 0.02);
}

.add-document-btn {
  background: transparent;
  border: 1px solid var(--accent-color, #06ffa5);
  color: var(--accent-color, #06ffa5);
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 auto;
}

.add-document-btn:hover {
  background: var(--accent-color, #06ffa5);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.3);
}

/* Styles pour la liste des documents dans la confirmation */
.documents-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.documents-list .document-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(6, 255, 165, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(6, 255, 165, 0.1);
}

/* Styles pour les compteurs dans les boutons */
.button-count {
  font-size: 11px;
  opacity: 0.8;
  margin-left: 4px;
}

/* Responsive */
@media (max-width: 768px) {
  .step-label {
    font-size: 12px;
  }
  
  .upload-area {
    padding: 30px 20px;
  }
  
  .pdf-preview-container {
    height: 400px;
  }
  
  .step-content {
    margin: 20px 15px;
  }
  
  .step-body {
    padding: 15px;
  }
   
  .submit-buttons {
    flex-direction: column;
  }
   
  .submit-button {
    width: 100%;
  }
  
  /* Responsive pour les onglets */
  .document-tabs, .positioning-tabs {
    gap: 6px;
  }
  
  .document-tab, .positioning-tab {
    min-width: 140px;
    padding: 6px 10px;
  }
  
  .tab-name {
    font-size: 12px;
  }
  
  .positioning-info h4 {
    font-size: 14px;
  }
  
  .positioning-hint {
    font-size: 13px;
  }
  
  .status-list {
    gap: 6px;
  }
  
  .document-status-item {
    padding: 6px 10px;
  }
  
  .status-file-name {
    font-size: 13px;
  }
  
  .global-status {
    padding: 12px;
  }
  
  .documents-status {
    font-size: 14px;
  }
}

/* Styles pour les options de soumission */
.submit-options {
  margin-top: 30px;
  padding: 20px;
  background-color: rgba(6, 255, 165, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(6, 255, 165, 0.1);
}

.submit-hint {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 20px;
  color: var(--text-muted, #6c757d);
  font-size: 15px;
  line-height: 1.5;
}

.submit-hint i {
  color: var(--primary, #4a6cf7);
  margin-top: 2px;
}

.submit-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.submit-button {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.submit-button.primary {
  background-color: var(--primary, #4a6cf7);
  color: #fff;
  border: none;
  box-shadow: 0 4px 10px rgba(74, 108, 247, 0.2);
  flex: 1;
}

.submit-button.primary:hover {
  background-color: #3955c8;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(74, 108, 247, 0.3);
}

.submit-button.secondary {
  background-color: white;
  color: var(--text-color, #212529);
  border: 1px solid var(--border-color, #dee2e6);
}

.submit-button.secondary:hover {
  background-color: rgba(0, 0, 0, 0.05);
  border-color: var(--text-muted, #6c757d);
}

/* Styles spécifiques pour le mode intégré */
.prepare-document-container.integrated-mode {
  background: transparent !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  max-height: none !important;
  overflow-y: visible !important;
  padding: 0 !important;
  margin: 0 !important;
}

.prepare-document-container.integrated-mode .section-card {
  background: var(--card-bg) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
  padding: 24px !important;
  margin-bottom: 20px !important;
  border: 1px solid var(--border-color) !important;
}

.prepare-document-container.integrated-mode .section-header {
  background: transparent !important;
  border-bottom: 1px solid var(--border-color) !important;
  backdrop-filter: none !important;
  margin-bottom: 20px !important;
}

.prepare-document-container.integrated-mode .section-title {
  color: var(--text-color) !important;
  font-size: 1.5rem !important;
}

/* Styles pour les boutons dans le mode intégré */
.prepare-document-container.integrated-mode .btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  background: var(--bg-light);
  color: var(--text-color);
}

.prepare-document-container.integrated-mode .btn:hover {
  background: var(--hover-bg);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style> 