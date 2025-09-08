<template>
  <div class="create-template-container">
    <!-- En-tête -->
    <div class="section-header">
      <h3 class="section-title">
        <i class="bi bi-file-earmark-richtext"></i>
        Créer un nouveau template
      </h3>
      <button class="btn btn-outline-secondary" @click="$emit('close')">
        <i class="bi bi-arrow-left"></i> Retour
      </button>
    </div>

    <!-- Section card contenant tout le contenu -->
    <div class="section-card">
      <!-- Progression des étapes - Plus étalée -->
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
        <!-- Étape 1: Informations du template -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="form-section">
            <div class="form-group">
              <label for="templateName" class="form-label">
                <i class="bi bi-tag"></i> Nom du template
              </label>
              <input 
                type="text" 
                id="templateName"
                v-model="templateData.name" 
                class="form-control"
                placeholder="Ex: Contrat de partenariat, Rapport mensuel..."
                :class="{ 'is-invalid': templateNameError }"
                @blur="validateTemplateName"
              />
              <div v-if="templateNameError" class="invalid-feedback">
                {{ templateNameError }}
              </div>
            </div>

            <div class="form-group">
              <label for="templateDescription" class="form-label">
                <i class="bi bi-file-text"></i> Description (optionnelle)
              </label>
              <textarea 
                id="templateDescription"
                v-model="templateData.description" 
                class="form-control"
                rows="4"
                placeholder="Décrivez brièvement l'usage de ce template..."
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Étape 2: Document PDF -->
        <div v-if="currentStep === 1" class="step-body">
          <div v-if="!templateData.file" class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <i class="bi bi-cloud-arrow-up-fill"></i>
            <p>Déposez votre fichier PDF ici ou cliquez pour sélectionner</p>
            <span class="upload-hint">Format accepté: .pdf (max 10MB)</span>
            <input type="file" ref="fileInput" accept=".pdf" @change="handleFileSelection" class="file-input">
          </div>

          <div v-else class="document-info">
            <div class="document-icon">
              <i class="bi bi-file-earmark-pdf"></i>
            </div>
            <div class="document-details">
              <div class="document-name">{{ templateData.file.name }}</div>
              <div class="document-size">{{ formatFileSize(templateData.file.size) }}</div>
              <div class="document-pages" v-if="totalPages">
                {{ totalPages }} page(s)
              </div>
            </div>
            <button @click="removeFile" class="remove-file-btn">
              <i class="bi bi-trash"></i>
            </button>
          </div>

          <!-- Prévisualisation PDF -->
          <div v-if="templateData.file" class="pdf-preview-container">
            <div v-if="pdfPreview?.error" class="pdf-error">
              <i class="bi bi-exclamation-triangle"></i>
              <p>Impossible de charger la prévisualisation. {{ pdfPreview?.error }}</p>
            </div>
            <iframe 
              v-else-if="pdfPreview?.url" 
              class="pdf-preview" 
              :src="pdfPreview.url"
              width="100%"
              height="600"
              frameborder="0"
              @load="onIframeLoad"
              @error="onIframeError">
            </iframe>
            <div v-else class="pdf-loading">
              <i class="bi bi-arrow-repeat spinning"></i>
              <p>Préparation de la prévisualisation...</p>
            </div>
          </div>
        </div>

        <!-- Étape 3: Configuration -->
        <div v-if="currentStep === 2" class="step-body">
          <div v-if="templateData.file" class="qr-position-container">
            <qr-positioner
              :pdf-file="templateData.file"
              :total-pages="totalPages"
              @position-changed="onPositionChanged"
              @position-confirmed="onPositionConfirmed"
              @signature-uploaded="onSignatureUploaded"
              @pdf-generated="onPdfGenerated"
            ></qr-positioner>
          </div>
        </div>

        <!-- Étape 4: Confirmation -->
        <div v-if="currentStep === 3" class="step-body">
          <div v-if="saving" class="saving-state">
            <div class="spinner"></div>
            <h4>Création du template en cours...</h4>
            <p>Veuillez patienter pendant que nous sauvegardons votre template.</p>
          </div>

          <div v-else-if="saveError" class="error-state">
            <i class="bi bi-exclamation-triangle"></i>
            <h4>Erreur lors de la création</h4>
            <p>{{ saveError }}</p>
            <button @click="prevStep" class="btn-retry">
              <i class="bi bi-arrow-clockwise"></i> Retenter
            </button>
          </div>

          <div v-else-if="saveSuccess" class="success-state">
            <i class="bi bi-check-circle"></i>
            <h4>Template créé avec succès !</h4>
            <p>Votre template "{{ templateData.name }}" a été créé et est maintenant disponible.</p>
            <button @click="$emit('close')" class="btn-primary">
              <i class="bi bi-check"></i> Terminer
            </button>
          </div>

          <div v-else class="confirmation-state">
            <h4><i class="bi bi-check-circle"></i> Résumé du template</h4>
            
            <div class="template-summary">
              <div class="summary-item">
                <span class="summary-label">Nom:</span>
                <span class="summary-value">{{ templateData.name }}</span>
              </div>
              
              <div class="summary-item" v-if="templateData.description">
                <span class="summary-label">Description:</span>
                <span class="summary-value">{{ templateData.description }}</span>
              </div>
              
              <div class="summary-item">
                <span class="summary-label">Document:</span>
                <span class="summary-value">{{ templateData.file?.name }}</span>
              </div>
              
              <div class="summary-item" v-if="positionData">
                <span class="summary-label">Configuration QR:</span>
                <span class="summary-value">
                  Taille {{ getQrSizeLabel(positionData.qr?.size) }} - 
                  {{ getPageApplicationLabel(positionData.mode) }}
                </span>
              </div>

              <div class="summary-item" v-if="positionData?.signature">
                <span class="summary-label">Signature:</span>
                <span class="summary-value">
                  Incluse (taille {{ positionData.signature.size }}%)
                </span>
              </div>
            </div>

            <div class="confirmation-actions">
              <button @click="saveTemplate" class="btn-primary" :disabled="saving">
                <i class="bi bi-save"></i> Créer le template
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Boutons de navigation entre les étapes - Comme PrepareDocument -->
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
          v-if="currentStep === 2" 
          @click="nextStep" 
          class="nav-button primary"
          :disabled="!canProceedToNextStep"
        >
          Confirmer <i class="bi bi-check"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineEmits } from 'vue';
import QrPositioner from '@/components/QrPositioner.vue';
import TemplateService from '@/services/TemplateService.js';
import AuthService from '@/services/AuthService.js';

// Définir les émetteurs d'événements
const emit = defineEmits(['close', 'template-created']);

// Étapes du workflow de création de template
const steps = [
  { label: 'Informations' },
  { label: 'Document PDF' },
  { label: 'Configuration' },
  { label: 'Confirmation' }
];

// Étape courante
const currentStep = ref(0);

// Références aux éléments DOM
const fileInput = ref(null);

// Données du template
const templateData = ref({
  name: '',
  description: '',
  file: null,
  qrPositions: null,
  signatureImage: null,
  generatedPdfFile: null,
  generatedPdfBlob: null,
  generatedPdfDataUrl: null,
  hasSignature: false
});

// État de la prévisualisation PDF
const pdfPreview = ref({
  loading: false,
  error: null,
  url: null,
  totalPages: 1
});

// État de sauvegarde
const saveStatus = ref(null); // 'saving', 'success', 'error'
const saveError = ref('');

// Erreurs de validation
const templateNameError = ref('');
const fileError = ref('');

// Propriétés calculées

const canProceedToNextStep = computed(() => {
  switch (currentStep.value) {
    case 0: // Informations
      return templateData.value.name.trim().length > 0;
    case 1: // Document PDF
      return templateData.value.file !== null && 
             pdfPreview.value?.url !== null && 
             !pdfPreview.value?.loading && 
             !pdfPreview.value?.error;
    case 2: // Configuration
      return templateData.value.qrPositions !== null;
    default:
      return false;
  }
});

const canSaveTemplate = computed(() => {
  return templateData.value.name.trim().length > 0 && 
         templateData.value.file !== null && 
         templateData.value.qrPositions !== null;
});

const positionData = computed(() => templateData.value.qrPositions);

const saving = computed(() => saveStatus.value === 'saving');
const saveSuccess = computed(() => saveStatus.value === 'success');

const totalPages = computed(() => pdfPreview.value?.totalPages || 1);

// Méthodes de navigation entre les étapes
function nextStep() {
  if (currentStep.value < steps.length - 1 && canProceedToNextStep.value) {
    // Si on passe à l'étape 2, créer la prévisualisation PDF
    if (currentStep.value === 0) {
      createPdfPreview();
    }
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 0 && saveStatus.value !== 'saving') {
    currentStep.value--;
  }
}

// Méthodes de validation

function clearFileError() {
  fileError.value = '';
}

// Méthodes de manipulation des fichiers
function triggerFileInput() {
  fileInput.value.click();
}

function handleFileSelection(event) {
  const file = event.target.files[0];
  if (file && file.type === 'application/pdf') {
    if (file.size > 10 * 1024 * 1024) { // 10MB max
      fileError.value = 'Le fichier ne doit pas dépasser 10MB';
      return;
    }
    templateData.value.file = file;
    clearFileError();
    console.log('Fichier PDF sélectionné:', file.name);
    
    // Créer immédiatement l'aperçu PDF (comme PrepareDocument)
    createPdfPreview();
  } else {
    fileError.value = 'Veuillez sélectionner un fichier PDF valide';
  }
}

function handleFileDrop(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  
  if (file && file.type === 'application/pdf') {
    if (file.size > 10 * 1024 * 1024) {
      fileError.value = 'Le fichier ne doit pas dépasser 10MB';
      return;
    }
    templateData.value.file = file;
    clearFileError();
    console.log('Fichier PDF déposé:', file.name);
    
    // Créer immédiatement l'aperçu PDF (comme PrepareDocument)
    createPdfPreview();
  } else {
    fileError.value = 'Veuillez déposer un fichier PDF valide';
  }
}

function removeFile() {
  templateData.value.file = null;
  
  // Nettoyer l'URL de l'aperçu si elle existe
  if (pdfPreview.value?.url) {
    URL.revokeObjectURL(pdfPreview.value.url);
  }
  
  pdfPreview.value = { loading: false, error: null, url: null, totalPages: 1 };
  clearFileError();
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

// Créer la prévisualisation PDF
function createPdfPreview() {
  if (!templateData.value.file) return;
  
  console.log('🔵 Création de la prévisualisation pour:', templateData.value.file.name);
  
  try {
    // Créer l'URL directement depuis le fichier
    const fileUrl = URL.createObjectURL(templateData.value.file);
    console.log('✅ URL créée:', fileUrl);
    
    // TEST: Essayer avec une URL publique de PDF pour vérifier l'iframe
    // const testUrl = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf';
    // console.log('🧪 TEST avec URL publique:', testUrl);
    
    // Mettre à jour l'état immédiatement
    pdfPreview.value = {
      loading: false,
      error: null,
      url: fileUrl, // ou testUrl pour le test
      totalPages: 1
    };
    
    console.log('📋 État pdfPreview final:', pdfPreview.value);
    console.log('📋 Type de l\'URL:', typeof pdfPreview.value.url);
    console.log('📋 URL commence par blob:', pdfPreview.value.url?.startsWith('blob:'));
    
    // Forcer un refresh de Vue après un court délai
    setTimeout(() => {
      console.log('⏱️ Vérification après 500ms:');
      console.log('- pdfPreview existe toujours?', !!pdfPreview.value);
      console.log('- URL toujours présente?', pdfPreview.value?.url);
      console.log('- templateData.file toujours présent?', !!templateData.value.file);
    }, 500);
    
    // Détecter le nombre de pages
    detectPdfPages(templateData.value.file).then(pages => {
      console.log(`📄 PDF analysé: ${pages} pages détectées`);
      if (pdfPreview.value) {
        pdfPreview.value.totalPages = pages;
      }
    });
    
  } catch (error) {
    console.error('❌ Erreur création URL:', error);
    pdfPreview.value = {
      loading: false,
      error: 'Erreur de chargement: ' + error.message,
      url: null,
      totalPages: 1
    };
  }
}

// Détecter le nombre de pages du PDF
async function detectPdfPages(file) {
  try {
    console.log('Détection du nombre de pages...');
    
    const arrayBuffer = await file.arrayBuffer();
    
    // Utiliser PDF.js si disponible
    if (window.pdfjsLib) {
      const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      console.log(`PDF analysé avec PDF.js: ${pdf.numPages} pages`);
      return pdf.numPages;
    }
    
    // Fallback : estimation basée sur la taille
    const fileSizeKB = file.size / 1024;
    let estimatedPages = Math.max(1, Math.round(fileSizeKB / 50));
    estimatedPages = Math.min(estimatedPages, 100);
    
    console.log(`Estimation: ${estimatedPages} pages (${fileSizeKB.toFixed(1)}KB)`);
    return estimatedPages;
    
  } catch (error) {
    console.error('Erreur détection pages:', error);
    return 1;
  }
}

// Gestionnaires d'événements pour l'iframe
function onIframeLoad() {
  console.log('✅ Iframe chargée avec succès !');
  console.log('URL de l\'iframe:', pdfPreview.value?.url);
}

function onIframeError(event) {
  console.error('❌ Erreur de chargement de l\'iframe:', event);
  console.error('URL de l\'iframe:', pdfPreview.value?.url);
  if (pdfPreview.value) {
    pdfPreview.value.error = 'Erreur de chargement du PDF dans l\'iframe';
  }
}

// Gestionnaires d'événements QrPositioner
function onPositionChanged(position) {
  console.log('Position changée:', position);
  // Optionnel: Sauvegarder les positions en temps réel
}

function onPositionConfirmed(position) {
  console.log('Positions confirmées:', position);
  templateData.value.qrPositions = position;
}

function onSignatureUploaded(file) {
  console.log('Signature uploadée:', file.name);
  templateData.value.signatureImage = file;
  templateData.value.hasSignature = true;
}

function onPdfGenerated(pdfData) {
  console.log('PDF généré:', pdfData.file.name);
  templateData.value.generatedPdfBlob = pdfData.blob;
  templateData.value.generatedPdfFile = pdfData.file;
  templateData.value.generatedPdfDataUrl = pdfData.dataUrl;
}

// Fonction de sauvegarde du template
async function saveTemplate() {
  if (!canSaveTemplate.value) {
    console.error('Template non valide pour la sauvegarde');
    return;
  }
  
  try {
    saveStatus.value = 'saving';
    currentStep.value = 3; // Passer à l'étape de confirmation
    
    console.log('Début de la sauvegarde du template...');
    
    // Obtenir les informations de l'utilisateur connecté
    const userInfo = AuthService.getCurrentUser();
    
    if (!userInfo || !userInfo.organization) {
      throw new Error('Informations d\'organisation manquantes. Veuillez vous reconnecter.');
    }
    
    // Préparer les données pour l'API
    const templateApiData = {
      name: templateData.value.name,
      description: templateData.value.description,
      qr_size: templateData.value.qrPositions.qr.size,
      page_application: templateData.value.qrPositions.mode,
      qr_positions: templateData.value.qrPositions.qr.positions,
      signature_positions: templateData.value.qrPositions.signature ? 
                          templateData.value.qrPositions.signature.positions : null,
      signature_size: templateData.value.qrPositions.signature ? 
                     templateData.value.qrPositions.signature.size : 50,
      selected_pages: templateData.value.qrPositions.qr.pages !== 'all' ? 
                     templateData.value.qrPositions.qr.pages : [],
      original_document: templateData.value.file,
      preview_document: templateData.value.generatedPdfFile,
      signature_image: templateData.value.signatureImage,
      organization_name: userInfo.organization.name,
      user_role: userInfo.role,
      organization_role: userInfo.organization.role
    };
    
    console.log('Données à envoyer à l\'API:', {
      name: templateApiData.name,
      description: templateApiData.description,
      qr_size: templateApiData.qr_size,
      page_application: templateApiData.page_application,
      has_signature: !!templateApiData.signature_image,
      organization: templateApiData.organization_name
    });
    
    // Appel à l'API pour créer le template
    const response = await TemplateService.createTemplate(templateApiData);
    
    console.log('Template créé avec succès:', response);
    
    saveStatus.value = 'success';
    
    // Émettre un événement pour informer le parent
    // Récupérer le template complet depuis l'API pour avoir tous les champs
    const fullTemplate = await TemplateService.getTemplate(response.id);
    
    emit('template-created', {
      id: response.id,
      name: templateApiData.name,
      description: templateApiData.description,
      createdAt: new Date().toISOString(),
      qrSize: templateApiData.qr_size,
      pageApplication: templateApiData.page_application,
      hasSignature: !!templateApiData.signature_image,
      preview_document: fullTemplate.preview_document
    });
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde du template:', error);
    saveStatus.value = 'error';
    saveError.value = error.message || 'Une erreur est survenue lors de la sauvegarde du template.';
  }
}

// Fonctions d'aide pour l'affichage
function getQrSizeLabel(size) {
  const sizeLabels = {
    small: 'Petit',
    medium: 'Moyen',
    large: 'Grand'
  };
  return sizeLabels[size] || 'Moyen';
}

function getPageApplicationLabel(mode) {
  const modeLabels = {
    all: 'Toutes les pages',
    current: 'Page actuelle',
    custom: 'Pages spécifiques',
    individual: 'Positions individuelles'
  };
  return modeLabels[mode] || 'Standard';
}

// Nettoyage au démontage
onMounted(() => {
  console.log('Composant CreateTemplate monté');
  
  // S'assurer que pdfPreview est toujours initialisé
  if (!pdfPreview.value) {
    pdfPreview.value = {
      loading: false,
      error: null,
      url: null,
      totalPages: 1
    };
  }
});
</script>

<style scoped>
.create-template-container {
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
  margin-bottom: 20px;
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

.btn {
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
  cursor: pointer;
}

.btn:hover {
  background: var(--hover-bg);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Progression des étapes - Plus étalée */
.steps-progress {
  display: flex;
  justify-content: space-between;
  margin: 25px 0;
  position: relative;
  padding: 0 20px; /* Réduction des marges latérales */
}

.steps-progress::before {
  content: '';
  position: absolute;
  top: 14px;
  left: 20px;
  right: 20px;
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

/* Contenus des étapes - Marges réduites */
.step-content {
  margin: 20px 0; /* Réduction des marges latérales de 30px à 0 */
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

/* Section formulaire - Plus large */
.form-section {
  max-width: none; /* Suppression de la limitation de largeur */
  width: 100%;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 8px;
  font-size: 1rem;
}

.form-label i {
  color: var(--primary-color);
}

/* Zones de texte étirées */
.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: var(--bg-light);
  color: var(--text-color);
  resize: vertical;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
  background: white;
}

.form-control.is-invalid {
  border-color: var(--danger-color);
}

.invalid-feedback {
  color: var(--danger-color);
  font-size: 0.875rem;
  margin-top: 5px;
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
  width: 100%;
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
  transform: scale(1.1);
}

.upload-area p {
  font-size: 18px;
  color: var(--text-color, #212529);
  margin: 0 0 8px 0;
  font-weight: 500;
}

.upload-hint {
  color: var(--text-muted, #6c757d);
  font-size: 14px;
}

.file-input {
  display: none;
}

/* Info document */
.document-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: var(--bg-light);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.document-icon {
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.document-details {
  flex: 1;
}

.document-name {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 4px;
}

.document-size, .document-pages {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.remove-file-btn {
  background: rgba(220, 53, 69, 0.1);
  border: none;
  border-radius: 8px;
  padding: 10px;
  color: var(--danger-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-file-btn:hover {
  background: rgba(220, 53, 69, 0.2);
  transform: scale(1.1);
}

/* PDF preview styles */
.pdf-preview-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  border: 1px solid var(--border-color);
  height: 600px;
}

.pdf-preview {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-loading, .pdf-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
  font-size: 1.1rem;
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

.pdf-error {
  color: #dc3545;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* QR Positioner container */
.qr-position-container {
  width: 100%;
  margin: 0;
  padding: 0;
}

/* États de sauvegarde */
.saving-state, .error-state, .success-state, .confirmation-state {
  text-align: center;
  padding: 40px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(var(--primary-color-rgb), 0.2);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.error-state i, .success-state i {
  font-size: 4rem;
  margin-bottom: 20px;
}

.error-state i {
  color: var(--danger-color);
}

.success-state i {
  color: var(--success-color);
}

.confirmation-state h4 {
  color: var(--text-color);
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.template-summary {
  background: var(--bg-light);
  border-radius: 12px;
  padding: 25px;
  margin: 20px 0;
  border: 1px solid var(--border-color);
  text-align: left;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(var(--border-color-rgb), 0.5);
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  font-weight: 600;
  color: var(--text-color);
}

.summary-value {
  color: var(--text-secondary);
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

.confirmation-actions {
  margin-top: 30px;
}

/* Navigation entre les étapes - Comme PrepareDocument */
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
  gap: 8px;
  border: none;
}

.nav-button.primary {
  background-color: var(--primary, #4a6cf7);
  color: #fff;
  box-shadow: 0 4px 10px rgba(74, 108, 247, 0.2);
}

.nav-button.primary:hover:not(:disabled) {
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

.spacer {
  flex: 1;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.btn-retry {
  background: var(--danger-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-retry:hover {
  background: var(--danger-dark);
  transform: translateY(-2px);
}

/* Animations */
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

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .step-content {
    margin: 15px 0;
  }
  
  .step-body {
    padding: 20px;
  }
  
  .upload-area {
    padding: 30px 20px;
  }
  
  .form-control {
    padding: 10px 14px;
  }
  
  .steps-progress {
    padding: 0 10px;
  }
  
  .steps-progress::before {
    left: 10px;
    right: 10px;
  }
  
  .step-navigation {
    padding: 15px 20px;
    flex-direction: column;
    gap: 10px;
  }
  
  .nav-button {
    width: 100%;
    justify-content: center;
  }
  
  .spacer {
    display: none;
  }
}
</style> 