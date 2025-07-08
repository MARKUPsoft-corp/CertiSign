<template>
  <div class="qr-positioner-container">
    <div class="positioner-header">
      <h4>
        <i class="bi bi-qr-code"></i> 
        Positionnement du QR Code et de la signature
      </h4>
      <p>Positionnez le QR code et la signature manuscrite sur le document et choisissez sur quelles pages les appliquer.</p>
    </div>

    <!-- Section d'upload de signature -->
    <div class="signature-upload">
      <h5><i class="bi bi-pen"></i> Signature manuscrite</h5>
      <div v-if="!signatureImage" class="upload-area">
        <input 
          type="file" 
          id="signature-upload" 
          accept="image/png,image/jpeg,image/jpg,image/gif,image/bmp,image/webp,image/svg+xml" 
          @change="handleSignatureUpload" 
          class="file-input"
        >
        <label for="signature-upload" class="upload-label">
          <i class="bi bi-upload"></i>
          <span>Déposer une image de signature ou cliquer pour sélectionner</span>
        </label>
      </div>
      <div v-else class="signature-preview">
        <img :src="signatureImageUrl" alt="Signature" class="signature-image-preview">
        <div class="signature-controls">
          <div class="slider-container">
            <label for="signature-size">Taille: {{ signatureSize }}%</label>
            <input 
              type="range" 
              id="signature-size" 
              v-model="signatureSize" 
              min="10" 
              max="100" 
              step="5"
              @input="updateSignatureSize"
            >
          </div>
          <button @click="removeSignature" class="remove-signature-btn">
            <i class="bi bi-trash"></i> Supprimer
          </button>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- Colonne de gauche : Aperçu du document -->
      <div class="document-preview-section">
        <div class="preview-header">
          <h5>Aperçu du document</h5>
          <div class="page-selector">
            <button @click="previousPage" :disabled="currentPage === 1" class="page-nav-btn">
              <i class="bi bi-chevron-left"></i>
            </button>
            <span class="page-info">Page {{ currentPage }} / {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="page-nav-btn">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>

        <!-- Zone d'aperçu A4 -->
        <div class="a4-preview-container" ref="previewContainer">
          <div class="debug-info" v-if="false">
            Debug: Page {{ currentPage }}/{{ totalPages }}, PDF loaded: {{ pdfLoaded }}
          </div>
          <div class="a4-page" 
               @mousedown="handleDragStart"
               @touchstart="handleTouchStart">
            
            <!-- Affichage du PDF avec vue-pdf-embed -->
            <div class="pdf-page-content">
              <vue-pdf-embed
                v-if="pdfSource"
                :source="pdfSource"
                :page="currentPage"
                :width="595"
                :height="842"
                @loaded="onPdfLoaded"
                @loading-failed="onPdfLoadError"
                @rendered="onPdfRendered"
                class="pdf-embed"
              />
              <div v-else class="pdf-loading">
                <i class="bi bi-file-earmark-pdf"></i>
                <p>Chargement du document...</p>
              </div>
            </div>

            <!-- QR Code draggable -->
            <div 
              v-if="showQrOnCurrentPage && pdfLoaded"
              class="qr-draggable"
              :style="qrStyle"
              :class="{ 'dragging': isDraggingQr }"
              @mousedown.stop="startDragQr"
              @touchstart.stop="startDragQr"
            >
              <div class="qr-content">
                <div class="qr-mock" :class="selectedQrSize">
                  <div class="qr-pattern"></div>
                </div>
                <div class="qr-label">ANTIC</div>
              </div>
            </div>
            
            <!-- Signature draggable -->
            <div 
              v-if="signatureImage && pdfLoaded"
              class="signature-draggable"
              :style="signatureStyle"
              :class="{ 'dragging': isDraggingSignature }"
              @mousedown.stop="startDragSignature($event)"
              @touchstart.stop="startDragSignature($event)"
            >
              <img :src="signatureImageUrl" alt="Signature" class="signature-image">
            </div>
          </div>
        </div>

        <!-- Indicateurs de position -->
        <div class="position-info" v-if="showPositionInfo">
          <span v-if="isDraggingQr">
            Position QR : X: {{ Math.round(getCurrentPagePosition().x) }}% | Y: {{ Math.round(getCurrentPagePosition().y) }}%
          </span>
          <span v-if="isDraggingSignature">
            Position Signature : X: {{ Math.round(getCurrentPageSignaturePosition().x) }}% | Y: {{ Math.round(getCurrentPageSignaturePosition().y) }}%
          </span>
        </div>
      </div>

      <!-- Colonne de droite : Contrôles -->
      <div class="controls-section">
        <!-- Aperçu de toutes les pages -->
        <div class="all-pages-preview" v-if="totalPages > 1">
          <h5>Pages du document ({{ totalPages }} pages)</h5>
          <div class="pages-grid">
            <div 
              v-for="page in Math.min(totalPages, 20)" 
              :key="page"
              :class="['page-thumbnail', { active: currentPage === page }]"
              @click="goToPage(page)"
            >
              <div class="page-thumb-content">
                <vue-pdf-embed
                  v-if="pdfSource"
                  :source="pdfSource"
                  :page="page"
                  :width="80"
                  :height="113"
                  class="page-thumb-pdf"
                />
                <div v-else class="page-thumb-placeholder">
                  <i class="bi bi-file-earmark"></i>
                  <span>{{ page }}</span>
                </div>
              </div>
              <span class="page-number">Page {{ page }}</span>
            </div>
            <div v-if="totalPages > 20" class="more-pages-info">
              <i class="bi bi-three-dots"></i>
              <span>{{ totalPages - 20 }} pages supplémentaires</span>
            </div>
          </div>
        </div>

        <!-- Sélection des pages -->
        <div class="pages-selection">
          <h5>Appliquer les éléments sur :</h5>
          <div class="page-options">
            <label class="radio-option">
              <input type="radio" v-model="pageApplication" value="all" />
              <span>Toutes les pages (même position)</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="pageApplication" value="current" />
              <span>Page actuelle uniquement ({{ currentPage }})</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="pageApplication" value="custom" />
              <span>Pages personnalisées (même position)</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="pageApplication" value="individual" />
              <span>Position individuelle par page</span>
            </label>
          </div>

          <!-- Sélection personnalisée des pages -->
          <div v-if="pageApplication === 'custom'" class="custom-pages">
            <p class="custom-pages-hint">Sélectionnez les pages :</p>
            <div class="page-checkboxes">
              <label v-for="page in totalPages" :key="page" class="page-checkbox">
                <input 
                  type="checkbox" 
                  :value="page" 
                  v-model="selectedPages"
                />
                <span>{{ page }}</span>
              </label>
            </div>
          </div>

          <!-- Pages avec positions individuelles -->
          <div v-if="pageApplication === 'individual'" class="individual-pages">
            <p class="individual-pages-hint">
              <i class="bi bi-info-circle"></i>
              Naviguez entre les pages et positionnez les éléments individuellement sur chaque page.
              <br>
              <small>Glissez-déposez le QR code et la signature pour les ajouter à une page.</small>
            </p>
            <div class="individual-pages-list">
              <div 
                v-for="page in totalPages" 
                :key="page" 
                class="individual-page-item"
                :class="{ 
                  'has-qr': hasIndividualPosition(page), 
                  'current': currentPage === page,
                  'can-position': currentPage === page && !hasIndividualPosition(page)
                }"
                @click="goToPage(page)"
              >
                <span class="page-num">Page {{ page }}</span>
                <span v-if="hasIndividualPosition(page)" class="position-indicator">
                  <i class="bi bi-check-circle-fill"></i>
                  Positionnés
                </span>
                <span v-else-if="currentPage === page" class="position-indicator ready">
                  <i class="bi bi-cursor-fill"></i>
                  Prêt à positionner
                </span>
                <button 
                  v-if="hasIndividualPosition(page)" 
                  @click.stop="removeIndividualPosition(page)"
                  class="remove-btn"
                  title="Supprimer les éléments de cette page"
                >
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Contrôles de taille du QR -->
        <div class="size-controls">
          <h5>Taille du QR Code :</h5>
          <div class="size-options">
            <button 
              v-for="size in qrSizes" 
              :key="size.name"
              :class="['size-btn', { active: selectedQrSize === size.name }]"
              @click="setQrSize(size.name)"
            >
              <div class="size-preview-icon" :class="size.name"></div>
              <span>{{ size.label }}</span>
            </button>
          </div>
        </div>

        <!-- Actions -->
        <div class="actions-section">
          <button @click="resetPosition" class="btn-secondary">
            <i class="bi bi-arrow-clockwise"></i>
            Réinitialiser
          </button>
          
          <button @click="showFinalPreview" class="btn-preview" :disabled="isGeneratingPdf">
            <i class="bi" :class="isGeneratingPdf ? 'bi-hourglass-split spin' : 'bi-eye'"></i>
            {{ isGeneratingPdf ? 'Génération en cours...' : 'Aperçu final' }}
          </button>
          
          <button @click="confirmPosition" class="btn-primary" :disabled="!canConfirm">
            <i class="bi bi-check"></i>
            Confirmer
          </button>
        </div>
      </div>
    </div>

    <!-- Modal d'aperçu final stylisée - Cohérent avec le tableau de bord -->
    <div v-if="showPreviewModal" class="modal-overlay-blur" @click.self="closePreviewModal">
      <div class="stylized-preview-modal">
        <div class="modal-header-stylized">
          <div class="modal-title-section">
            <div class="modal-icon">
              <i class="bi bi-eye"></i>
            </div>
            <div class="modal-title-text">
          <h4>Aperçu final du document</h4>
              <p>Visualisation du document avec QR code et signature</p>
            </div>
          </div>
          <button @click="closePreviewModal" class="modal-close-stylized">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <div class="modal-body-stylized">
          <!-- États de chargement stylisés -->
          <div v-if="isGeneratingPdf" class="pdf-generating-loader-stylized">
            <div class="loading-container">
              <div class="spinner-stylized"></div>
              <div class="loading-text">
                <h5>Génération du PDF en cours...</h5>
                <p>Veuillez patienter pendant que nous préparons votre document</p>
              </div>
            </div>
                    </div>
          
          <!-- États d'erreur stylisés -->
          <div v-else-if="pdfGenerationError" class="pdf-generation-error-stylized">
            <div class="error-container">
              <div class="error-icon">
                <i class="bi bi-exclamation-triangle-fill"></i>
              </div>
              <div class="error-content">
                <h5>Erreur de génération</h5>
            <p>{{ pdfGenerationError }}</p>
            <div class="error-details" v-if="pdfGenerationError.includes('Erreur:')">
                  <details>
                    <summary>Détails techniques</summary>
              <pre>{{ pdfGenerationError.split('Erreur:')[1] }}</pre>
                  </details>
                  </div>
              </div>
              <button @click="showFinalPreview" class="btn-retry-stylized">
                <i class="bi bi-arrow-clockwise"></i>
                Réessayer
              </button>
            </div>
                </div>
          
          <!-- Container PDF stylisé -->
          <div v-else-if="generatedPdfDataUrl" class="pdf-preview-container-stylized">
            <div class="pdf-preview-wrapper">
            <iframe 
              :src="generatedPdfDataUrl" 
                class="pdf-preview-iframe-stylized" 
              title="Aperçu du document"
              frameborder="0"
            ></iframe>
            </div>
              </div>
          
          <!-- Fallback stylisé -->
          <div v-else class="pdf-preview-error-stylized">
            <div class="error-container">
              <div class="error-icon">
            <i class="bi bi-file-earmark-x"></i>
              </div>
              <div class="error-content">
                <h5>Aperçu indisponible</h5>
            <p>Impossible de générer l'aperçu du document.</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer-stylized">
          <div class="footer-actions">
            <button @click="closePreviewModal" class="btn-cancel-stylized">
              <i class="bi bi-x"></i>
              <span>Fermer</span>
            </button>
            <button @click="confirmAndClosePreview" class="btn-confirm-stylized" :disabled="!generatedPdfBlob">
              <i class="bi bi-check-circle"></i>
              <span>Confirmer et continuer</span>
          </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, defineEmits, defineProps } from 'vue';
import VuePdfEmbed from 'vue-pdf-embed';
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import QRCode from 'qrcode';

// Props
const props = defineProps({
  pdfFile: {
    type: Object,
    required: true
  },
  totalPages: {
    type: Number,
    default: 1
  },
  preloadedPositions: {
    type: Object,
    default: null
  }
});

// Emits
const emit = defineEmits(['position-confirmed', 'position-changed', 'signature-uploaded', 'pdf-generated']);

// État du composant
const currentPage = ref(1);
const pdfSource = ref(null);
const pdfLoaded = ref(false);
const isDraggingQr = ref(false);
const isDraggingSignature = ref(false);
const showPreviewModal = ref(false);
const showPositionInfo = ref(false);

// État pour l'aperçu PDF généré
const generatedPdfDataUrl = ref('');
const generatedPdfBlob = ref(null);
const isGeneratingPdf = ref(false);
const pdfGenerationError = ref(null);

// État pour la signature
const signatureImage = ref(null);
const signatureImageUrl = ref('');
const signatureSize = ref(50); // Taille en pourcentage (1-100)

// Position du QR code par défaut (en pourcentage)
const defaultPosition = { x: 85, y: 90 };

// Position unique (pour les modes all et custom)
const qrPosition = reactive({
  x: defaultPosition.x,
  y: defaultPosition.y
});

// Position pour la signature
const signaturePosition = reactive({
  x: 50,
  y: 50
});

// Positions individuelles par page (pour le mode individual)
const qrPositions = ref({});
const signaturePositions = ref({});

// Application des pages
const pageApplication = ref('all');
const selectedPages = ref([]);

// Tailles du QR code
const qrSizes = [
  { name: 'small', label: 'Petit', size: 50 },
  { name: 'medium', label: 'Moyen', size: 70 },
  { name: 'large', label: 'Grand', size: 90 }
];
const selectedQrSize = ref('medium');

// Références DOM
const previewContainer = ref(null);

// Méthodes pour gérer l'upload de signature
function handleSignatureUpload(event) {
  const file = event.target.files[0];
  if (file && file.type.startsWith('image/')) {
    // Vérifier que c'est un format d'image supporté
    const supportedFormats = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml'];
    
    if (supportedFormats.some(format => file.type.includes(format.split('/')[1]))) {
    signatureImage.value = file;
    signatureImageUrl.value = URL.createObjectURL(file);
      
      console.log('Image de signature chargée:', {
        name: file.name,
        type: file.type,
        size: file.size
      });
    
    // Émettre un événement pour informer le composant parent de l'image de signature
    emit('signature-uploaded', file);
  } else {
      alert('Format d\'image non supporté. Formats acceptés: PNG, JPEG, JPG, GIF, BMP, WEBP, SVG.');
      event.target.value = null;
    }
  } else {
    alert('Veuillez sélectionner un fichier image valide.');
    event.target.value = null;
  }
}

function removeSignature() {
  if (signatureImageUrl.value) {
    URL.revokeObjectURL(signatureImageUrl.value);
  }
  signatureImage.value = null;
  signatureImageUrl.value = '';
  signaturePositions.value = {};
}

function updateSignatureSize() {
  // Cette fonction est appelée quand on change la taille avec le slider
  emit('position-changed', getPositionData());
}

// Méthodes pour gérer les positions individuelles
function hasIndividualPosition(page) {
  return qrPositions.value[page] !== undefined || signaturePositions.value[page] !== undefined;
}

function getCurrentPagePosition() {
  if (pageApplication.value === 'individual' && qrPositions.value[currentPage.value]) {
    return qrPositions.value[currentPage.value];
  }
  return qrPosition;
}

function getCurrentPageSignaturePosition() {
  if (pageApplication.value === 'individual' && signaturePositions.value[currentPage.value]) {
    return signaturePositions.value[currentPage.value];
  }
  return signaturePosition;
}

function removeIndividualPosition(page) {
  delete qrPositions.value[page];
  delete signaturePositions.value[page];
  emit('position-changed', getPositionData());
}

// Calculs
const showQrOnCurrentPage = computed(() => {
  if (pageApplication.value === 'all') return true;
  if (pageApplication.value === 'current') return true;
  if (pageApplication.value === 'custom') {
    return selectedPages.value.includes(currentPage.value);
  }
  if (pageApplication.value === 'individual') {
    // En mode individual, toujours afficher le QR pour permettre le positionnement
    return true;
  }
  return false;
});

const canConfirm = computed(() => {
  if (pageApplication.value === 'custom' && selectedPages.value.length === 0) {
    return false;
  }
  if (pageApplication.value === 'individual') {
    // Il faut au moins avoir positionné un élément sur une page
    if (Object.keys(qrPositions.value).length === 0) {
    return false;
    }
  }
  return true;
});

const qrStyle = computed(() => {
  const size = qrSizes.find(s => s.name === selectedQrSize.value);
  const position = getCurrentPagePosition();
  return {
    left: `${position.x}%`,
    top: `${position.y}%`,
    width: `${size.size}px`,
    height: `${size.size}px`,
    transform: 'translate(-50%, -50%)',
    cursor: isDraggingQr.value ? 'grabbing' : 'grab'
  };
});

const signatureStyle = computed(() => {
  const position = getCurrentPageSignaturePosition();
  // La taille est un pourcentage de la largeur de la page
  const width = `${signatureSize.value * 2}px`;
  
  return {
    left: `${position.x}%`,
    top: `${position.y}%`,
    width: width,
    transform: 'translate(-50%, -50%)',
    cursor: isDraggingSignature.value ? 'grabbing' : 'grab'
  };
});

// Méthodes de navigation
function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}

function nextPage() {
  if (currentPage.value < props.totalPages) {
    currentPage.value++;
  }
}

// Navigation directe vers une page
function goToPage(pageNumber) {
  currentPage.value = pageNumber;
}

// Gestion du PDF
const actualTotalPages = ref(1);
const pdfInitialized = ref(false);

function onPdfLoaded(event) {
  console.log('onPdfLoaded appelé, event:', event);
  pdfLoaded.value = true;
  
  // Extraire le nombre de pages de l'objet PDF
  if (event && event._pdfInfo && event._pdfInfo.numPages) {
    actualTotalPages.value = event._pdfInfo.numPages;
    pdfInitialized.value = true;
    console.log(`Nombre de pages détecté depuis _pdfInfo: ${event._pdfInfo.numPages}`);
  } else if (event && event.numPages) {
    actualTotalPages.value = event.numPages;
    pdfInitialized.value = true;
    console.log(`Nombre de pages détecté depuis numPages: ${event.numPages}`);
  } else if (event && typeof event === 'number' && event > 0) {
    actualTotalPages.value = event;
    pdfInitialized.value = true;
    console.log(`Nombre de pages détecté directement: ${event}`);
  } else {
    console.log('PDF chargé, mais nombre de pages non détecté depuis l\'event');
    // Utiliser la prop comme fallback
    actualTotalPages.value = props.totalPages || 1;
  }
}

function onPdfLoadError(error) {
  console.error('Erreur lors du chargement du PDF:', error);
  pdfLoaded.value = false;
}

function onPdfRendered() {
  console.log(`Page ${currentPage.value} rendue`);
}

// Gestion du drag & drop spécifique
function startDragQr(event) {
  event.stopPropagation();
  event.preventDefault();
  isDraggingQr.value = true;
    showPositionInfo.value = true;
    
    // En mode individual, si la page n'a pas encore de position, la créer maintenant
    if (pageApplication.value === 'individual' && !qrPositions.value[currentPage.value]) {
      const currentPos = getCurrentPagePosition();
      qrPositions.value[currentPage.value] = { x: currentPos.x, y: currentPos.y };
    }
  
  // Ajouter les écouteurs d'événements directement sur le document
  document.addEventListener('mousemove', handleDragMove);
  document.addEventListener('mouseup', handleDragEnd);
  document.addEventListener('touchmove', handleTouchMove, { passive: false });
  document.addEventListener('touchend', handleTouchEnd);
}

function startDragSignature(event) {
  event.stopPropagation();
  event.preventDefault();
  isDraggingSignature.value = true;
  showPositionInfo.value = true;
  
  // En mode individual, si la page n'a pas encore de position, la créer maintenant
  if (pageApplication.value === 'individual' && !signaturePositions.value[currentPage.value]) {
    const currentPos = getCurrentPageSignaturePosition();
    signaturePositions.value[currentPage.value] = { x: currentPos.x, y: currentPos.y };
  }
  
  // Ajouter les écouteurs d'événements directement sur le document
  document.addEventListener('mousemove', handleDragMove);
  document.addEventListener('mouseup', handleDragEnd);
  document.addEventListener('touchmove', handleTouchMove, { passive: false });
  document.addEventListener('touchend', handleTouchEnd);
}

function handleDragMove(event) {
  if (!isDraggingQr.value && !isDraggingSignature.value) return;
  
  // Empêcher le comportement par défaut pour éviter les sélections de texte
  event.preventDefault();
  
  const container = previewContainer.value;
  const a4Page = container.querySelector('.a4-page');
  const pageRect = a4Page.getBoundingClientRect();
  
  const x = ((event.clientX - pageRect.left) / pageRect.width) * 100;
  const y = ((event.clientY - pageRect.top) / pageRect.height) * 100;
  
  // Limiter aux bordures avec marge
  const newX = Math.max(5, Math.min(95, x));
  const newY = Math.max(5, Math.min(95, y));
  
  // Mettre à jour la position appropriée selon l'élément en cours de déplacement
  if (isDraggingQr.value) {
  if (pageApplication.value === 'individual') {
    // Pour les positions individuelles, créer ou mettre à jour la position de la page actuelle
    if (!qrPositions.value[currentPage.value]) {
      qrPositions.value[currentPage.value] = { x: newX, y: newY };
    } else {
      qrPositions.value[currentPage.value].x = newX;
      qrPositions.value[currentPage.value].y = newY;
    }
  } else {
    // Pour les autres modes, utiliser la position unique
    qrPosition.x = newX;
    qrPosition.y = newY;
    }
  } 
  
  if (isDraggingSignature.value) {
    if (pageApplication.value === 'individual') {
      // Pour les positions individuelles, créer ou mettre à jour la position de la page actuelle
      if (!signaturePositions.value[currentPage.value]) {
        signaturePositions.value[currentPage.value] = { x: newX, y: newY };
      } else {
        signaturePositions.value[currentPage.value].x = newX;
        signaturePositions.value[currentPage.value].y = newY;
      }
    } else {
      // Pour les autres modes, utiliser la position unique
      signaturePosition.x = newX;
      signaturePosition.y = newY;
    }
  }
  
  emit('position-changed', getPositionData());
}

function handleDragEnd() {
  if (isDraggingQr.value || isDraggingSignature.value) {
    // Supprimer les écouteurs d'événements
    document.removeEventListener('mousemove', handleDragMove);
    document.removeEventListener('mouseup', handleDragEnd);
    document.removeEventListener('touchmove', handleTouchMove);
    document.removeEventListener('touchend', handleTouchEnd);
    
    isDraggingQr.value = false;
    isDraggingSignature.value = false;
  showPositionInfo.value = false;
  }
}

// Support tactile
function handleTouchStart(event) {
  const touch = event.touches[0];
  const target = document.elementFromPoint(touch.clientX, touch.clientY);
  const qrElement = target && target.closest('.qr-draggable');
  const signatureElement = target && target.closest('.signature-draggable');
  
  if (qrElement) {
    startDragQr(event);
  } else if (signatureElement) {
    startDragSignature(event);
  }
}

function handleTouchMove(event) {
  if (!isDraggingQr.value && !isDraggingSignature.value) return;
  
  // Empêcher le défilement pendant le glisser-déposer
  event.preventDefault();
  
  const touch = event.touches[0];
  const container = previewContainer.value;
  const a4Page = container.querySelector('.a4-page');
  const pageRect = a4Page.getBoundingClientRect();
  
  const x = ((touch.clientX - pageRect.left) / pageRect.width) * 100;
  const y = ((touch.clientY - pageRect.top) / pageRect.height) * 100;
  
  const newX = Math.max(5, Math.min(95, x));
  const newY = Math.max(5, Math.min(95, y));
  
  if (isDraggingQr.value) {
  if (pageApplication.value === 'individual') {
    if (!qrPositions.value[currentPage.value]) {
      qrPositions.value[currentPage.value] = { x: newX, y: newY };
    } else {
      qrPositions.value[currentPage.value].x = newX;
      qrPositions.value[currentPage.value].y = newY;
    }
  } else {
    qrPosition.x = newX;
    qrPosition.y = newY;
    }
  }
  
  if (isDraggingSignature.value) {
    if (pageApplication.value === 'individual') {
      if (!signaturePositions.value[currentPage.value]) {
        signaturePositions.value[currentPage.value] = { x: newX, y: newY };
      } else {
        signaturePositions.value[currentPage.value].x = newX;
        signaturePositions.value[currentPage.value].y = newY;
      }
    } else {
      signaturePosition.x = newX;
      signaturePosition.y = newY;
    }
  }
  
  emit('position-changed', getPositionData());
}

function handleTouchEnd() {
  handleDragEnd();
}

// Contrôles
function setQrSize(size) {
  selectedQrSize.value = size;
  emit('position-changed', getPositionData());
}

function resetPosition() {
  // Réinitialiser les positions et tailles du QR code
  qrPosition.x = defaultPosition.x;
  qrPosition.y = defaultPosition.y;
  qrPositions.value = {};
  selectedQrSize.value = 'medium';
  
  // Réinitialiser les positions et tailles de la signature
  signaturePosition.x = 50;
  signaturePosition.y = 50;
  signaturePositions.value = {};
  signatureSize.value = 50;
  
  pageApplication.value = 'all';
  selectedPages.value = [];
  emit('position-changed', getPositionData());
}

// Aperçu final
async function showFinalPreview() {
  isGeneratingPdf.value = true;
  pdfGenerationError.value = null;
  
  try {
    // Générer le PDF modifié
    await generateModifiedPdf();
    
    // Afficher la modal
  showPreviewModal.value = true;
  } catch (error) {
    console.error('Erreur lors de la génération du PDF:', error);
    pdfGenerationError.value = `Erreur: ${error.message}`;
  } finally {
    isGeneratingPdf.value = false;
  }
}

// Fonction pour générer le PDF avec modifications
async function generateModifiedPdf() {
  if (!props.pdfFile) {
    throw new Error('Aucun fichier PDF original fourni');
  }
  
  try {
    // Lire le fichier PDF original
    const originalPdfBytes = await props.pdfFile.arrayBuffer();
    
    // Charger le document avec pdf-lib
    const pdfDoc = await PDFDocument.load(originalPdfBytes);
    
    // Pages à traiter
    let pagesToProcess = [];
    
    if (pageApplication.value === 'all') {
      // Ajouter toutes les pages
      pagesToProcess = Array.from({ length: pdfDoc.getPageCount() }, (_, i) => i);
    } else if (pageApplication.value === 'current') {
      // Ajouter uniquement la page actuelle (attention: pdf-lib utilise un index commençant à 0)
      pagesToProcess = [currentPage.value - 1];
    } else if (pageApplication.value === 'custom') {
      // Ajouter les pages sélectionnées (avec conversion d'index)
      pagesToProcess = selectedPages.value.map(p => p - 1);
    } else if (pageApplication.value === 'individual') {
      // Ajouter les pages avec positions individuelles
      const qrPages = Object.keys(qrPositions.value).map(p => parseInt(p) - 1);
      const signaturePages = signatureImage.value ? Object.keys(signaturePositions.value).map(p => parseInt(p) - 1) : [];
      pagesToProcess = [...new Set([...qrPages, ...signaturePages])];
    }
    
    // Pour chaque page à traiter
    for (const pageIndex of pagesToProcess) {
      // Vérifier que l'index de page est valide
      if (pageIndex < 0 || pageIndex >= pdfDoc.getPageCount()) continue;
      
      const page = pdfDoc.getPage(pageIndex);
      const { width, height } = page.getSize();
      
      // Ajouter le QR code si nécessaire pour cette page
      if (shouldShowQrOnPage(pageIndex + 1)) {
        // Obtenir la position du QR pour cette page
        let position;
        if (pageApplication.value === 'individual' && qrPositions.value[pageIndex + 1]) {
          position = qrPositions.value[pageIndex + 1];
        } else {
          position = qrPosition;
        }
        
        // Générer un vrai QR code avec qrcode
        const qrSize = qrSizes.find(s => s.name === selectedQrSize.value).size;
        
        // Convertir la position de pourcentage à coordonnées absolues
        const qrPosX = (position.x / 100) * width;
        const qrPosY = (position.y / 100) * height;
        
        try {
          // Générer le QR code comme une URL de données
          const qrDataUrl = await QRCode.toDataURL('https://antic.cm/verify?id=DEMO-QR-CODE', {
            errorCorrectionLevel: 'H',
            margin: 1,
            width: qrSize * 2, // Plus grande résolution pour meilleure qualité
            color: {
              dark: '#000000',
              light: '#ffffff'
            }
          });
          
          // Convertir l'URL de données en ArrayBuffer
          const qrImageBytes = await fetch(qrDataUrl).then(res => res.arrayBuffer());
          
          // Intégrer l'image QR dans le PDF
          const qrImage = await pdfDoc.embedPng(qrImageBytes);
          
          // D'abord dessiner un rectangle blanc comme fond
          page.drawRectangle({
            x: qrPosX - (qrSize / 2) - 5, // Un peu plus grand que le QR code
            y: height - qrPosY - (qrSize / 2) - 5,
            width: qrSize + 10,
            height: qrSize + 10,
            color: rgb(1, 1, 1), // blanc
            opacity: 1,
            borderWidth: 1,
            borderColor: rgb(0.8, 0.8, 0.8), // gris clair
            borderOpacity: 0.5
          });
          
          // Ensuite dessiner le QR code
          page.drawImage(qrImage, {
            x: qrPosX - (qrSize / 2),
            y: height - qrPosY - (qrSize / 2), // Conversion des coordonnées Y
            width: qrSize,
            height: qrSize
          });
        } catch (qrError) {
          console.error('Erreur lors de la génération du QR code:', qrError);
          
          // Fallback: dessiner un rectangle noir si le QR code échoue
          page.drawRectangle({
            x: qrPosX - (qrSize / 2),
            y: height - qrPosY - (qrSize / 2),
            width: qrSize,
            height: qrSize,
            color: rgb(0, 0, 0),
            opacity: 0.8
          });
        }
        
        // Ajouter le texte "ANTIC" sous le QR code dans un rectangle blanc
        const font = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
        
        // Mesurer la largeur du texte pour centrer
        const textWidth = font.widthOfTextAtSize('ANTIC', 10);
        
        // Dessiner un rectangle blanc comme fond pour le texte
        page.drawRectangle({
          x: qrPosX - (textWidth / 2) - 5,
          y: height - qrPosY - (qrSize / 2) - 25,
          width: textWidth + 10,
          height: 16,
          color: rgb(1, 1, 1), // blanc
          opacity: 1,
          borderWidth: 0
        });
        
        // Dessiner le texte
        page.drawText('ANTIC', {
          x: qrPosX - (textWidth / 2),
          y: height - qrPosY - (qrSize / 2) - 22,
          size: 10,
          font: font,
          color: rgb(0, 0, 0)
        });
      }
      
      // Ajouter la signature si nécessaire pour cette page
      if (shouldShowSignatureOnPage(pageIndex + 1) && signatureImage.value) {
        // Convertir l'image de la signature en format utilisable par pdf-lib
        const signatureImageBytes = await fetch(signatureImageUrl.value).then(res => res.arrayBuffer());
        let signatureEmbed;
        
        // Détecter le type d'image en utilisant le type MIME du fichier original
        const mimeType = signatureImage.value.type || 'image/png';
        console.log('Type MIME de l\'image de signature:', mimeType);
        
        try {
          if (mimeType.includes('jpeg') || mimeType.includes('jpg')) {
          signatureEmbed = await pdfDoc.embedJpg(signatureImageBytes);
          } else if (mimeType.includes('png')) {
          signatureEmbed = await pdfDoc.embedPng(signatureImageBytes);
        } else {
            // Pour les autres formats (GIF, BMP, WEBP, etc.), convertir en PNG via canvas
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            // Charger l'image dans un canvas et la convertir en PNG
            await new Promise((resolve, reject) => {
              img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(async (blob) => {
                  if (blob) {
                    const pngBytes = await blob.arrayBuffer();
                    signatureEmbed = await pdfDoc.embedPng(pngBytes);
                    resolve();
                  } else {
                    reject(new Error('Échec de la conversion en PNG'));
                  }
                }, 'image/png');
              };
              img.onerror = reject;
              img.src = signatureImageUrl.value;
            });
          }
          } catch (e) {
          console.error('Erreur lors de l\'intégration de l\'image de signature:', e);
          console.log('Tentative de fallback avec conversion PNG...');
          
          // Dernier recours : convertir via canvas
          try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            await new Promise((resolve, reject) => {
              img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(async (blob) => {
                  if (blob) {
                    const pngBytes = await blob.arrayBuffer();
                    signatureEmbed = await pdfDoc.embedPng(pngBytes);
                    resolve();
                  } else {
                    reject(new Error('Échec de la conversion en PNG'));
                  }
                }, 'image/png');
              };
              img.onerror = reject;
              img.src = signatureImageUrl.value;
            });
          } catch (fallbackError) {
            console.error('Impossible d\'intégrer l\'image de signature:', fallbackError);
            continue; // Passer à la page suivante
          }
        }
        
        // Obtenir la position de signature pour cette page
        let position;
        if (pageApplication.value === 'individual' && signaturePositions.value[pageIndex + 1]) {
          position = signaturePositions.value[pageIndex + 1];
        } else {
          position = signaturePosition;
        }
        
        // Calculer la taille et position de l'image
        // Utiliser la même échelle que dans l'interface de positionnement
        // La taille dans l'interface est signatureSize.value * 2 (en pixels)
        // On calcule donc un facteur d'échelle proportionnel à la largeur de la page
        const scaleFactor = (signatureSize.value * 2) / 595; // 595 est la largeur standard d'une page A4 en points
        const sigWidth = width * scaleFactor;
        const sigHeight = (signatureEmbed.height / signatureEmbed.width) * sigWidth;
        
        // Convertir la position de pourcentage à coordonnées absolues
        const sigPosX = (position.x / 100) * width - (sigWidth / 2);
        const sigPosY = (position.y / 100) * height - (sigHeight / 2);
        
        // Dessiner l'image
        page.drawImage(signatureEmbed, {
          x: sigPosX,
          y: height - sigPosY - sigHeight, // Conversion des coordonnées Y
          width: sigWidth,
          height: sigHeight,
          opacity: 0.9
        });
      }
    }
    
    // Sérialiser le PDF modifié
    const modifiedPdfBytes = await pdfDoc.save();
    
    // Créer un blob et une URL de données
    const blob = new Blob([modifiedPdfBytes], { type: 'application/pdf' });
    generatedPdfBlob.value = blob;
    generatedPdfDataUrl.value = URL.createObjectURL(blob);
    
    return true;
  } catch (error) {
    console.error('Erreur pendant la génération du PDF:', error);
    throw error;
  }
}

function closePreviewModal() {
  showPreviewModal.value = false;
  
  // Nettoyer les ressources du PDF généré pour libérer de la mémoire
  if (generatedPdfDataUrl.value) {
    URL.revokeObjectURL(generatedPdfDataUrl.value);
    generatedPdfDataUrl.value = '';
    generatedPdfBlob.value = null;
  }
}

// Cette fonction a été remplacée par confirmDownloadAndClose
// mais est conservée ici pour référence en cas de besoin futur
/* function confirmAndClose() {
  confirmPosition();
  closePreviewModal.value = false;
} */

async function confirmAndClosePreview() {
  if (generatedPdfBlob.value) {
    try {
      // Créer un nom de fichier pour le File object
      let fileName = 'document_modifié.pdf';
      if (props.pdfFile && props.pdfFile.name) {
        const originalName = props.pdfFile.name.replace(/\.pdf$/i, '');
        fileName = `${originalName}_modifié.pdf`;
      }
      
      const pdfFile = new File([generatedPdfBlob.value], fileName, { type: 'application/pdf' });

      // Émettre un événement au composant parent avec les données du PDF généré
      emit('pdf-generated', {
        file: pdfFile,
        dataUrl: generatedPdfDataUrl.value,
        blob: generatedPdfBlob.value
      });
    } catch (error) {
      console.error('Erreur lors de la préparation du PDF généré :', error);
    }
  }

  // Confirmer la position et fermer la modale
  confirmPosition();
  closePreviewModal();
}

// Cette fonction a été intégrée dans confirmDownloadAndClose
// mais est conservée ici pour référence en cas de besoin futur
/* 
// Fonction pour télécharger le PDF généré
function downloadGeneratedPdf() {
  if (!generatedPdfBlob.value) {
    console.error('Aucun PDF généré disponible pour le téléchargement');
    return;
  }
  
  // Obtenir le nom du fichier original
  let fileName = 'document';
  if (props.pdfFile && props.pdfFile.name) {
    // Extraire le nom sans l'extension
    const originalName = props.pdfFile.name.replace(/\.pdf$/i, '');
    fileName = originalName;
  }
  
  // Créer un élément d'ancrage pour le téléchargement
  const a = document.createElement('a');
  a.href = generatedPdfDataUrl.value;
  a.download = `${fileName}_signé_${new Date().toISOString().slice(0,10)}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  }
*/

// Fonctions pour déterminer quelles pages doivent afficher les éléments
function shouldShowQrOnPage(page) {
  if (pageApplication.value === 'all') return true;
  if (pageApplication.value === 'current') return page === currentPage.value;
  if (pageApplication.value === 'custom') return selectedPages.value.includes(page);
  if (pageApplication.value === 'individual') return qrPositions.value[page] !== undefined;
  return false;
}

function shouldShowSignatureOnPage(page) {
  if (!signatureImage.value) return false;
  if (pageApplication.value === 'all') return true;
  if (pageApplication.value === 'current') return page === currentPage.value;
  if (pageApplication.value === 'custom') return selectedPages.value.includes(page);
  if (pageApplication.value === 'individual') return signaturePositions.value[page] !== undefined;
  return false;
}

// Confirmation
function getPositionData() {
  let pages = [];
  let positions = {};
  let signatureData = null;
  
  if (pageApplication.value === 'all') {
    pages = 'all';
    positions = { default: { x: qrPosition.x, y: qrPosition.y } };
  } else if (pageApplication.value === 'current') {
    pages = [currentPage.value];
    positions = { [currentPage.value]: { x: qrPosition.x, y: qrPosition.y } };
  } else if (pageApplication.value === 'custom') {
    pages = selectedPages.value;
    // Toutes les pages sélectionnées ont la même position
    selectedPages.value.forEach(page => {
      positions[page] = { x: qrPosition.x, y: qrPosition.y };
    });
  } else if (pageApplication.value === 'individual') {
    pages = Object.keys(qrPositions.value).map(Number);
    positions = { ...qrPositions.value };
  }
  
  // Ajout des données de signature si disponibles
  if (signatureImage.value) {
    let signaturePages = [];
    let signaturePositionsData = {};
    
    if (pageApplication.value === 'all') {
      signaturePages = 'all';
      signaturePositionsData = { default: { x: signaturePosition.x, y: signaturePosition.y } };
    } else if (pageApplication.value === 'current') {
      signaturePages = [currentPage.value];
      signaturePositionsData = { [currentPage.value]: { x: signaturePosition.x, y: signaturePosition.y } };
    } else if (pageApplication.value === 'custom') {
      signaturePages = selectedPages.value;
      selectedPages.value.forEach(page => {
        signaturePositionsData[page] = { x: signaturePosition.x, y: signaturePosition.y };
      });
    } else if (pageApplication.value === 'individual') {
      signaturePages = Object.keys(signaturePositions.value).map(Number);
      signaturePositionsData = { ...signaturePositions.value };
    }
    
    signatureData = {
      imageUrl: signatureImageUrl.value,
      size: signatureSize.value,
      pages: signaturePages,
      positions: signaturePositionsData
    };
  }
  
  return {
    qr: {
    size: selectedQrSize.value,
    pages: pages,
      positions: positions,
    },
    signature: signatureData,
    mode: pageApplication.value // Pour savoir comment interpréter les données
  };
}

function confirmPosition() {
  emit('position-confirmed', getPositionData());
}

// Initialisation
onMounted(() => {
  console.log('Composant QrPositioner monté');
  console.log('Fichier PDF reçu:', props.pdfFile);
  console.log('Nombre total de pages (prop):', props.totalPages);
  
  if (props.pdfFile) {
    // Créer une URL pour le fichier PDF
    const fileUrl = URL.createObjectURL(props.pdfFile);
    pdfSource.value = fileUrl;
  } else {
    console.error('Aucun fichier PDF fourni au composant');
  }
  
  emit('position-changed', getPositionData());
});

// Watchers
watch(() => props.pdfFile, (newFile) => {
  if (newFile) {
    console.log('Nouveau fichier PDF détecté');
    // Nettoyer l'ancienne URL si elle existe
    if (pdfSource.value) {
      URL.revokeObjectURL(pdfSource.value);
    }
    // Créer une nouvelle URL
    const fileUrl = URL.createObjectURL(newFile);
    pdfSource.value = fileUrl;
    currentPage.value = 1;
  }
});

watch(pageApplication, (newVal) => {
  if (newVal === 'current') {
    selectedPages.value = [currentPage.value];
  } else if (newVal === 'individual') {
    // Lors du passage en mode individuel, ne pas créer automatiquement de position
    // L'utilisateur doit interagir avec le QR pour qu'il soit sauvegardé
  }
  emit('position-changed', getPositionData());
});

// Nettoyage
onUnmounted(() => {
  if (pdfSource.value) {
    URL.revokeObjectURL(pdfSource.value);
  }
  if (signatureImageUrl.value) {
    URL.revokeObjectURL(signatureImageUrl.value);
  }
  if (generatedPdfDataUrl.value) {
    URL.revokeObjectURL(generatedPdfDataUrl.value);
  }
});

// Propriété calculée pour le nombre total de pages (utilise la valeur détectée si disponible)
const totalPages = computed(() => {
  const detectedPages = actualTotalPages.value;
  const propPages = props.totalPages || 1;
  const finalPages = detectedPages > 1 ? detectedPages : propPages;
  console.log(`Total pages calculé: detected=${detectedPages}, prop=${propPages}, final=${finalPages}`);
  return finalPages;
});

// Pas besoin d'initialisation pour pdf-lib

// Gestion du drag & drop pour l'arrière-plan
function handleDragStart(event) {
  // Ne rien faire si on clique déjà sur un élément draggable
  if (event.target.closest('.qr-draggable') || event.target.closest('.signature-draggable')) {
    return;
  }
  
  // Si l'utilisateur clique sur l'arrière-plan, on peut
  // implémenter une fonctionnalité spécifique si nécessaire
  console.log("Clic sur l'arrière-plan de la page");
}

// Initialiser les positions depuis les données préchargées
function initializeFromPreloadedPositions() {
  if (!props.preloadedPositions) return;
  
  console.log('Initialisation des positions préchargées:', props.preloadedPositions);
  
  // Initialiser le mode d'application des pages
  if (props.preloadedPositions.mode) {
    pageApplication.value = props.preloadedPositions.mode;
  }
  
  // Initialiser les positions QR
  if (props.preloadedPositions.qr) {
    // Taille du QR
    if (props.preloadedPositions.qr.size) {
      selectedQrSize.value = props.preloadedPositions.qr.size;
    }
    
    // Pages sélectionnées pour l'application custom
    if (props.preloadedPositions.mode === 'custom' && Array.isArray(props.preloadedPositions.qr.pages)) {
      selectedPages.value = [...props.preloadedPositions.qr.pages];
    }
    
    // Positions du QR
    if (props.preloadedPositions.qr.positions) {
      if (props.preloadedPositions.mode === 'individual') {
        // Pour le mode individual, copier toutes les positions par page
        Object.entries(props.preloadedPositions.qr.positions).forEach(([page, pos]) => {
          qrPositions.value[Number(page)] = { x: pos.x, y: pos.y };
        });
      } else if (props.preloadedPositions.qr.positions.default) {
        // Pour le mode all ou autre, utiliser la position par défaut
        const pos = props.preloadedPositions.qr.positions.default;
        qrPosition.x = pos.x;
        qrPosition.y = pos.y;
      } else if (Object.values(props.preloadedPositions.qr.positions).length > 0) {
        // Fallback: utiliser la première position disponible
        const pos = Object.values(props.preloadedPositions.qr.positions)[0];
        qrPosition.x = pos.x;
        qrPosition.y = pos.y;
      }
    }
  }
  
  // Initialiser les positions de signature si disponibles
  if (props.preloadedPositions.signature) {
    // Taille de la signature
    if (props.preloadedPositions.signature.size) {
      signatureSize.value = props.preloadedPositions.signature.size;
    }
    
    // Positions de la signature
    if (props.preloadedPositions.signature.positions) {
      if (props.preloadedPositions.mode === 'individual') {
        // Pour le mode individual, copier toutes les positions par page
        Object.entries(props.preloadedPositions.signature.positions).forEach(([page, pos]) => {
          signaturePositions.value[Number(page)] = { x: pos.x, y: pos.y };
        });
      } else if (props.preloadedPositions.signature.positions.default) {
        // Pour le mode all ou autre, utiliser la position par défaut
        const pos = props.preloadedPositions.signature.positions.default;
        signaturePosition.x = pos.x;
        signaturePosition.y = pos.y;
      } else if (Object.values(props.preloadedPositions.signature.positions).length > 0) {
        // Fallback: utiliser la première position disponible
        const pos = Object.values(props.preloadedPositions.signature.positions)[0];
        signaturePosition.x = pos.x;
        signaturePosition.y = pos.y;
      }
    }
  }
  
  // Émettre un événement pour informer le composant parent des positions chargées
  emit('position-changed', getPositionData());
}

// Watchers
watch(() => props.preloadedPositions, (newVal) => {
  if (newVal) {
    initializeFromPreloadedPositions();
  }
}, { immediate: true, deep: true });
</script>

<style scoped>
.qr-positioner-container {
  background-color: transparent !important;
  border-radius: 0 !important;
  padding: 0 !important;
  box-shadow: none !important;
  position: relative;
  /* Permettre à la modale de se positionner par rapport à ce conteneur */
  isolation: isolate;
  /* Assurer que le conteneur peut gérer l'overflow pour la modale */
  min-height: 100vh;
  overflow: hidden;
}

.positioner-header {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.positioner-header h4 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.positioner-header h4 i {
  color: var(--primary-color);
}

.positioner-header p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.5;
}

.main-content {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
  display: grid;
  grid-template-columns: 1fr 260px; /* Réduction de 280px à 260px */
  gap: 20px; /* Réduction de 24px à 20px */
  align-items: start;
}

/* Section aperçu du document avec design moderne */
.document-preview-section {
  background: var(--bg-light);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preview-header h5 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-color, #333);
}

.page-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  user-select: none;
}

.page-nav-btn {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-nav-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.page-nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
  min-width: 100px;
  text-align: center;
}

/* Aperçu A4 */
.a4-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
}

.a4-page {
  position: relative;
  width: 595px;
  height: 842px;
  max-width: 100%;
  aspect-ratio: 210 / 297;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: crosshair;
}

.pdf-page-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.pdf-page-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.pdf-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted, #6c757d);
}

.pdf-loading i {
  font-size: 3rem;
  margin-bottom: 16px;
}

/* QR Code draggable */
.qr-draggable {
  position: absolute;
  background: white;
  border: 2px solid var(--primary-color, #3a86ff);
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: box-shadow 0.2s;
  user-select: none;
  z-index: 10;
  cursor: grab;
}

.qr-draggable:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.qr-draggable.dragging {
  opacity: 0.8;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  cursor: grabbing;
}

.qr-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.qr-mock {
  background: white;
  border: 1px solid #333;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.qr-mock.small {
  width: 34px;
  height: 34px;
}

.qr-mock.medium {
  width: 54px;
  height: 54px;
}

.qr-mock.large {
  width: 74px;
  height: 74px;
}

.qr-pattern {
  width: 85%;
  height: 85%;
  background-image: 
    linear-gradient(45deg, #000 25%, transparent 25%),
    linear-gradient(-45deg, #000 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #000 75%),
    linear-gradient(-45deg, transparent 75%, #000 75%);
  background-size: 6px 6px;
  background-position: 0 0, 0 3px, 3px -3px, -3px 0px;
}

.qr-label {
  font-size: 10px;
  font-weight: 600;
  color: #333;
}

.position-info {
  margin-top: 12px;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  font-family: monospace;
}

/* Section contrôles - Design ultra-compact */
.controls-section {
  display: flex;
  flex-direction: column;
  gap: 14px; /* Réduction de 16px à 14px */
}

.pages-selection, .size-controls, .all-pages-preview {
  background: var(--bg-light);
  border-radius: 12px;
  padding: 14px; /* Réduction de 16px à 14px */
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Titres des sections stylisés avec soulignement */
.pages-selection h5, .size-controls h5, .all-pages-preview h5 {
  margin: 0 0 16px 0;
  font-size: 1rem;
  font-weight: 700; /* Plus gras */
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  padding-bottom: 8px;
}

/* Soulignement décoratif pour les titres */
.pages-selection h5::after, 
.size-controls h5::after, 
.all-pages-preview h5::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  border-radius: 2px;
}

/* Titre spécifique pour l'aperçu du document */
.preview-header h5 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-color);
  position: relative;
  padding-bottom: 8px;
}

.preview-header h5::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  border-radius: 2px;
}

/* Contrôles de taille ultra-compacts */
.size-options {
  display: flex;
  gap: 6px; /* Réduction de 8px à 6px */
}

.size-btn {
  flex: 1;
  padding: 10px 6px; /* Réduction de 12px 8px à 10px 6px */
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px; /* Réduction de 6px à 4px */
  position: relative;
  overflow: hidden;
}

.size-btn span {
  font-weight: 600;
  font-size: 0.75rem; /* Réduction de 0.8rem à 0.75rem */
}

/* Actions section avec boutons ultra-compacts */
.actions-section {
  display: flex;
  flex-direction: column;
  gap: 8px; /* Réduction de 10px à 8px */
  margin-top: 14px; /* Réduction de 16px à 14px */
  padding-top: 14px; /* Réduction de 16px à 14px */
  border-top: 1px solid var(--border-color);
}

/* Style des boutons encore plus compacts */
.btn-secondary, .btn-preview, .btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px; /* Réduction de 8px à 6px */
  padding: 10px 12px; /* Réduction de 12px 16px à 10px 12px */
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.85rem; /* Réduction de 0.9rem à 0.85rem */
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  min-height: 40px; /* Réduction de 44px à 40px */
  text-transform: none;
  letter-spacing: 0.2px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06); /* Ombre réduite */
  width: 100%;
}

.btn-secondary {
  background-color: var(--bg-light);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.btn-secondary:hover {
  background-color: var(--hover-bg);
  border-color: var(--text-secondary);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.btn-preview {
  background-color: #17a2b8;
  color: white;
  border: 1px solid #17a2b8;
}

.btn-preview:hover:not(:disabled) {
  background-color: #138496;
  border-color: #117a8b;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(23, 162, 184, 0.3);
}

.btn-preview:disabled {
  background-color: #6c757d;
  border-color: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  opacity: 0.6;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border: 1px solid var(--primary-color);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-dark);
  border-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.btn-primary:disabled {
  background-color: #6c757d;
  border-color: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  opacity: 0.6;
}

/* Icônes des boutons */
.btn-secondary i, .btn-preview i, .btn-primary i {
  font-size: 1rem;
}

/* Animation pour les icônes de chargement */
.spin {
  animation: buttonSpin 1s linear infinite;
}

@keyframes buttonSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Modal d'aperçu final stylisée - Centrée dans le composant QrPositioner */
.modal-overlay-blur {
  position: absolute !important;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
  animation: modalOverlayIn 0.3s ease-out;
}

.stylized-preview-modal {
  background: var(--card-bg);
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 1200px;
  max-height: 85%;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.modal-header-stylized {
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.modal-title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.modal-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.modal-title-text h4 {
  margin: 0 0 5px 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.modal-title-text p {
  margin: 0;
  opacity: 0.9;
  font-size: 0.9rem;
}

.modal-close-stylized {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 12px;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close-stylized:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.modal-body-stylized {
  padding: 30px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background: var(--bg-light);
}

/* États de chargement stylisés */
.pdf-generating-loader-stylized {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-container {
  text-align: center;
  padding: 40px;
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.spinner-stylized {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(var(--primary-color-rgb), 0.2);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spinnerRotate 1s linear infinite;
  margin: 0 auto 20px;
}

.loading-text h5 {
  margin: 0 0 10px 0;
  color: var(--text-color);
  font-size: 1.2rem;
}

.loading-text p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* États d'erreur stylisés */
.pdf-generation-error-stylized,
.pdf-preview-error-stylized {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.error-container {
  text-align: center;
  padding: 40px;
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #dc3545;
}

.error-icon {
  width: 70px;
  height: 70px;
  background: rgba(220, 53, 69, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 2rem;
  color: #dc3545;
}

.error-content h5 {
  margin: 0 0 15px 0;
  color: var(--text-color);
  font-size: 1.2rem;
}

.error-content p {
  margin: 0 0 20px 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
}

.error-details {
  margin-top: 15px;
  text-align: left;
}

.error-details summary {
  cursor: pointer;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.error-details pre {
  background: var(--bg-dark);
  padding: 15px;
  border-radius: 8px;
  font-size: 0.8rem;
  overflow-x: auto;
  white-space: pre-wrap;
}

.btn-retry-stylized {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 auto;
}

.btn-retry-stylized:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(var(--primary-color-rgb), 0.3);
}

/* Container PDF stylisé */
.pdf-preview-container-stylized {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.pdf-preview-wrapper {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.pdf-preview-iframe-stylized {
  width: 100%;
  height: 100%;
  min-height: 600px;
  border: none;
  display: block;
}

/* Footer stylisé */
.modal-footer-stylized {
  background: var(--bg-dark);
  padding: 20px 30px;
  border-top: 1px solid var(--border-color);
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-cancel-stylized,
.btn-confirm-stylized {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 140px;
  justify-content: center;
}

.btn-cancel-stylized {
  background: var(--bg-light);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-cancel-stylized:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn-confirm-stylized {
  background: var(--primary-color);
  color: white;
}

.btn-confirm-stylized:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(var(--primary-color-rgb), 0.3);
}

.btn-confirm-stylized:disabled {
  background: var(--neutral-color);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Animations */
@keyframes modalOverlayIn {
  from {
    opacity: 0;
    backdrop-filter: blur(0px);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(8px);
  }
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes spinnerRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .modal-overlay-blur {
    padding: 10px;
  }
  
  .stylized-preview-modal {
    width: 95%;
    max-height: 80%;
  }
  
  .modal-header-stylized {
    padding: 20px;
    flex-direction: column;
    gap: 15px;
  text-align: center;
}

  .modal-title-section {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-body-stylized {
    padding: 20px;
  }
  
  .footer-actions {
    flex-direction: column;
  }
  
  .btn-cancel-stylized,
  .btn-confirm-stylized {
    width: 100%;
  }
  
  .pdf-preview-iframe-stylized {
    min-height: 400px;
  }
}

/* Dark mode */
:global(.dark-theme) .stylized-preview-modal {
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .loading-container,
:global(.dark-theme) .error-container {
  background: rgba(15, 23, 42, 0.9);
}

:global(.dark-theme) .pdf-preview-wrapper {
  background: rgba(255, 255, 255, 0.98);
}

/* Styles pour vue-pdf-embed */
.pdf-embed {
  width: 100%;
  height: 100%;
}

.page-thumb-pdf {
  width: 100%;
  height: 100%;
}

.page-preview-pdf {
  width: 100%;
  height: 100%;
}

/* Navigation améliorée */
.page-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  user-select: none;
}

.page-info {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
  min-width: 100px;
  text-align: center;
}

/* Debug du positionnement */
.a4-page {
  position: relative;
  width: 595px;
  height: 842px;
  max-width: 100%;
  aspect-ratio: 210 / 297;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: crosshair;
}

.pdf-page-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.qr-draggable {
  position: absolute;
  background: white;
  border: 2px solid var(--primary-color, #3a86ff);
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: box-shadow 0.2s;
  user-select: none;
  z-index: 10;
  cursor: grab;
}

/* Aperçu de toutes les pages */
.all-pages-preview {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.all-pages-preview h5 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: var(--text-color, #333);
}

.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.page-thumbnail {
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}

.page-thumbnail:hover {
  transform: scale(1.05);
}

.page-thumbnail.active {
  outline: 3px solid var(--primary-color, #3a86ff);
  border-radius: 4px;
}

.page-thumb-content {
  width: 100%;
  aspect-ratio: 210 / 297;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.page-thumb-content img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.page-thumb-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #999;
}

.page-thumb-placeholder i {
  font-size: 20px;
}

.page-thumb-placeholder span {
  font-size: 12px;
}

.page-number {
  font-size: 11px;
  color: var(--text-muted, #6c757d);
  margin-top: 4px;
}

.more-pages-info {
  grid-column: 1 / -1;
  text-align: center;
  color: var(--text-muted, #6c757d);
  font-size: 12px;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

/* Scrollbar personnalisée pour la grille de pages */
.pages-grid::-webkit-scrollbar {
  width: 6px;
}

.pages-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.pages-grid::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.pages-grid::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Restauration des styles manquants */
.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
}

.footer-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .controls-section {
    order: -1;
  }
  
  .a4-page {
    max-height: 600px;
  }
}

@media (max-width: 768px) {
  .qr-positioner-container {
    padding: 16px;
  }
  
  .final-preview-pages {
    grid-template-columns: 1fr;
  }
  
  .signature-preview {
    flex-direction: column;
    align-items: stretch;
  }
  
  .signature-image-preview {
    max-width: 100%;
    margin: 0 auto;
  }
}

/* Debug info */
.debug-info {
  position: absolute;
  top: -25px;
  left: 0;
  font-size: 11px;
  color: #666;
  background: #ffe;
  padding: 2px 5px;
  border: 1px solid #ddd;
  z-index: 100;
}

/* Amélioration des styles pour l'aperçu final */
.qr-overlay-final.debug {
  background: rgba(255, 0, 0, 0.3) !important;
  border: 2px solid red !important;
}

/* Styles pour les positions individuelles */
.individual-pages {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ddd;
}

.individual-pages-hint {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.individual-pages-hint i {
  color: var(--info-color, #17a2b8);
}

.individual-pages-hint small {
  font-size: 0.75rem;
  color: var(--text-muted, #6c757d);
  opacity: 0.8;
}

.individual-pages-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 8px;
}

.individual-page-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  border: 1px solid transparent;
}

.individual-page-item:hover {
  background: #f8f9fa;
  border-color: #ddd;
}

.individual-page-item.has-qr {
  background: #e8f5e9;
  border-color: #4caf50;
}

.individual-page-item.current {
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.1);
}

.individual-page-item.can-position {
  background: #fff3cd;
  border-color: #ffc107;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 1;
  }
}

.page-num {
  font-weight: 500;
  color: var(--text-color, #333);
}

.position-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #4caf50;
}

.position-indicator i {
  font-size: 1rem;
}

.position-indicator.ready {
  color: #856404;
  font-style: italic;
}

.remove-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: rgba(220, 53, 69, 0.1);
}

/* Scrollbar personnalisée pour la liste des pages individuelles */
.individual-pages-list::-webkit-scrollbar {
  width: 6px;
}

.individual-pages-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.individual-pages-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.individual-pages-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Ajustement de la radio option pour le nouveau mode */
.radio-option {
  padding: 8px 0;
}

.radio-option:hover {
  color: var(--primary-color, #3a86ff);
}

/* Styles pour les onglets */
.positioning-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.tab-btn {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.tab-btn.active {
  color: var(--primary-color, #3a86ff);
  border-bottom-color: var(--primary-color, #3a86ff);
}

.tab-btn:hover:not(.active) {
  background-color: #f8f9fa;
}

/* Styles pour l'upload de signature */
.signature-upload {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.signature-upload h5 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.signature-upload h5 i {
  color: var(--accent-color);
}

/* Upload area améliorée */
.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
  background: var(--bg-light);
  position: relative;
  overflow: hidden;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: rgba(var(--primary-color-rgb), 0.05);
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.upload-label i {
  font-size: 2.5rem;
  color: var(--primary-color);
  transition: transform 0.3s ease;
}

.upload-area:hover .upload-label i {
  transform: scale(1.1);
}

.upload-label span {
  font-weight: 500;
}

/* Prévisualisation de signature */
.signature-preview {
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: var(--bg-light);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.signature-image-preview {
  max-width: 200px;
  max-height: 100px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: white;
  align-self: center;
}

.signature-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.slider-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.slider-container label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
}

.slider-container input[type="range"] {
  width: 100%;
  cursor: pointer;
  height: 8px;
  border-radius: 4px;
  background: var(--bg-light);
  outline: none;
}

.remove-signature-btn {
  background: linear-gradient(135deg, #dc3545, #e74c3c);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.remove-signature-btn:hover {
  background: linear-gradient(135deg, #c82333, #dc3545);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

/* Styles pour les deux éléments draggables */
.qr-draggable, .signature-draggable {
  z-index: 10;
  position: absolute;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: box-shadow 0.2s;
  user-select: none;
  cursor: grab;
}

.qr-draggable {
  background: white;
  border: 2px solid var(--primary-color, #3a86ff);
  border-radius: 8px;
  padding: 8px;
}

.signature-draggable {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid var(--accent-color, #4cb58e);
  border-radius: 4px;
  padding: 2px;
}

.qr-draggable:hover, .signature-draggable:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.qr-draggable.dragging, .signature-draggable.dragging {
  opacity: 0.8;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  cursor: grabbing;
}

.signature-image {
  max-width: 100%;
  max-height: 100%;
  display: block;
}

.slider-container input[type="range"] {
  width: 100%;
  cursor: pointer;
}

/* Modification de l'aperçu final pour inclure la signature */
.signature-overlay-final {
  position: absolute;
  z-index: 10;
  border: 1px solid #6c757d;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 2px;
}

.signature-image-final {
  max-width: 100%;
  max-height: 100%;
  display: block;
}

/* Nouveaux styles pour l'aperçu PDF */
.pdf-preview-iframe-container {
  width: 100%;
  height: 75vh;
  min-height: 550px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.pdf-preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-generating-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--primary-color, #3a86ff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.pdf-generation-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 15px;
  color: #dc3545;
  text-align: center;
  padding: 20px;
}

.pdf-generation-error i {
  font-size: 3rem;
}

.error-details {
  width: 100%;
  max-width: 500px;
  margin-top: 10px;
  text-align: left;
}

.error-details small {
  display: block;
  margin-bottom: 5px;
  color: #856404;
}

.error-details pre {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  color: #721c24;
  max-height: 150px;
  border: 1px solid #f5c6cb;
}

.btn-retry {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.pdf-preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 15px;
  color: #6c757d;
  text-align: center;
}

.pdf-preview-error i {
  font-size: 3rem;
}

.btn-download {
  background-color: #28a745;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  padding: 10px 15px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
}

.btn-download:hover {
  background-color: #218838;
}

.btn-download:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Animation pour l'icône de chargement */
.spin {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Options radio améliorées */
.page-options {
  display: flex;
  flex-direction: column;
  gap: 10px; /* Réduction */
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 10px; /* Réduction */
  cursor: pointer;
  padding: 8px 10px; /* Réduction */
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.radio-option:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
}

.radio-option input[type="radio"] {
  cursor: pointer;
  accent-color: var(--primary-color);
  transform: scale(1.1);
}

.radio-option label {
  cursor: pointer;
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.9rem; /* Légèrement plus petit */
}

/* Styles manquants pour les boutons de taille */
.size-btn:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.size-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.size-preview-icon {
  border: 2px solid currentColor;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.size-preview-icon.small {
  width: 18px; /* Réduction */
  height: 18px;
}

.size-preview-icon.medium {
  width: 26px; /* Réduction */
  height: 26px;
}

.size-preview-icon.large {
  width: 34px; /* Réduction */
  height: 34px;
}

/* Custom pages compact */
.custom-pages {
  margin-top: 12px; /* Réduction */
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.custom-pages-hint {
  font-size: 0.85rem; /* Réduction */
  color: var(--text-secondary);
  margin-bottom: 10px; /* Réduction */
  padding: 10px; /* Réduction */
  background: rgba(var(--primary-color-rgb), 0.05);
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.page-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); /* Réduction */
  gap: 6px; /* Réduction */
  max-height: 100px; /* Réduction */
  overflow-y: auto;
  padding: 6px; /* Réduction */
  background: white;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.page-checkbox {
  display: flex;
  align-items: center;
  gap: 4px; /* Réduction */
  cursor: pointer;
  padding: 4px 6px; /* Réduction */
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 0.8rem; /* Réduction */
}

.page-checkbox:hover {
  background: var(--hover-bg);
}

.page-checkbox input[type="checkbox"] {
  cursor: pointer;
  accent-color: var(--primary-color);
  transform: scale(0.9); /* Réduction */
}

/* Responsive design amélioré */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr 240px; /* Encore plus compact */
    gap: 16px;
  }
  
  .controls-section {
    gap: 12px;
  }
  
  .pages-selection, .size-controls, .all-pages-preview {
    padding: 12px;
  }
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr; /* Une seule colonne */
    gap: 20px;
  }
  
  .controls-section {
    order: -1; /* Contrôles en haut sur mobile */
  }
  
  .size-options {
    gap: 6px;
  }
  
  .size-btn {
    padding: 10px 6px;
  }
  
  .btn-secondary, .btn-preview, .btn-primary {
    padding: 10px 14px;
    min-height: 40px;
    font-size: 0.85rem;
  }
}

/* Ajout des styles manquants - Options radio compactes */
.page-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  font-size: 0.9rem;
}

.radio-option:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
}

.radio-option input[type="radio"] {
  cursor: pointer;
  accent-color: var(--primary-color);
  transform: scale(1.1);
}

.radio-option label {
  cursor: pointer;
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.9rem;
}

/* Styles manquants pour les boutons de taille */
.size-btn:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.size-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.size-preview-icon {
  border: 2px solid currentColor;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.size-preview-icon.small {
  width: 18px; /* Réduction */
  height: 18px;
}

.size-preview-icon.medium {
  width: 26px; /* Réduction */
  height: 26px;
}

.size-preview-icon.large {
  width: 34px; /* Réduction */
  height: 34px;
}

/* Custom pages compact */
.custom-pages {
  margin-top: 12px; /* Réduction */
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.custom-pages-hint {
  font-size: 0.85rem; /* Réduction */
  color: var(--text-secondary);
  margin-bottom: 10px; /* Réduction */
  padding: 10px; /* Réduction */
  background: rgba(var(--primary-color-rgb), 0.05);
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.page-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); /* Réduction */
  gap: 6px; /* Réduction */
  max-height: 100px; /* Réduction */
  overflow-y: auto;
  padding: 6px; /* Réduction */
  background: white;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.page-checkbox {
  display: flex;
  align-items: center;
  gap: 4px; /* Réduction */
  cursor: pointer;
  padding: 4px 6px; /* Réduction */
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 0.8rem; /* Réduction */
}

.page-checkbox:hover {
  background: var(--hover-bg);
}

.page-checkbox input[type="checkbox"] {
  cursor: pointer;
  accent-color: var(--primary-color);
  transform: scale(0.9); /* Réduction */
}

/* Responsive design amélioré */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr 240px; /* Encore plus compact */
    gap: 16px;
  }
  
  .controls-section {
    gap: 12px;
  }
  
  .pages-selection, .size-controls, .all-pages-preview {
    padding: 12px;
  }
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr; /* Une seule colonne */
    gap: 20px;
  }
  
  .controls-section {
    order: -1; /* Contrôles en haut sur mobile */
  }
  
  .size-options {
    gap: 6px;
  }
  
  .size-btn {
    padding: 10px 6px;
  }
  
  .btn-secondary, .btn-preview, .btn-primary {
    padding: 10px 14px;
    min-height: 40px;
    font-size: 0.85rem;
  }
}

/* Ajout des styles manquants - Options radio compactes */
.page-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  font-size: 0.9rem;
}

.radio-option:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
}

.radio-option input[type="radio"] {
  cursor: pointer;
  accent-color: var(--primary-color);
  transform: scale(1.1);
}

.radio-option label {
  cursor: pointer;
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.9rem;
}

/* Styles manquants pour les boutons de taille */
.size-btn:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.size-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.size-preview-icon {
  border: 2px solid currentColor;
  border-radius: 6px;
  transition: all 0.3s ease;
}

</style>
