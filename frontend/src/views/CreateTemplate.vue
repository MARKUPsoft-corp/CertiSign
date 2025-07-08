<template>
  <!-- Container principal avec style du collaborateur -->
  <div class="create-template-container">
    <!-- En-tête avec bouton retour -->
    <div class="section-header">
      <h3 class="section-title">
        <i class="bi bi-file-earmark-richtext"></i>
        Créer un nouveau template
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
        <!-- Étape 1: Informations du template -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="template-info-form">
            <div class="form-group">
              <label for="template-name" class="form-label">
                <i class="bi bi-tag"></i>
                Nom du template
              </label>
              <input 
                type="text" 
                id="template-name" 
                v-model="templateData.name" 
                placeholder="Ex: Contrat de partenariat, Rapport mensuel, Facture type..." 
                class="form-input"
                :class="{ 'error': templateNameError }"
                @input="clearTemplateNameError"
              >
              <span v-if="templateNameError" class="error-message">{{ templateNameError }}</span>
            </div>
            
            <div class="form-group">
              <label class="form-label">
                <i class="bi bi-file-earmark-text"></i>
                Description (optionnelle)
              </label>
              <textarea 
                v-model="templateData.description" 
                placeholder="Décrivez brièvement l'usage de ce template..."
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Étape 2: Upload du document PDF -->
        <div v-if="currentStep === 1" class="step-body">
          <div class="upload-section">
            <div class="upload-area" 
                 @click="triggerFileInput" 
                 @dragover.prevent 
                 @drop.prevent="handleFileDrop"
                 :class="{ 'has-file': templateData.file }">
              <input 
                type="file" 
                ref="fileInput" 
                accept=".pdf" 
                @change="handleFileSelection" 
                class="file-input"
              >
              
              <div v-if="!templateData.file" class="upload-placeholder">
                <div class="upload-icon">
                  <i class="bi bi-cloud-upload"></i>
                </div>
                <div class="upload-text">
                  <span class="upload-title">Glissez votre PDF ici</span>
                  <span class="upload-subtitle">ou cliquez pour sélectionner</span>
                  <span class="upload-hint">Format accepté: PDF (max 10MB)</span>
                </div>
              </div>
              
              <div v-else class="file-selected">
                <div class="file-info">
                  <i class="bi bi-file-earmark-pdf text-danger"></i>
                  <div class="file-details">
                    <span class="file-name">{{ templateData.file.name }}</span>
                    <span class="file-size">({{ formatFileSize(templateData.file.size) }})</span>
                    <span v-if="pdfPreview.totalPages" class="file-pages">
                      {{ pdfPreview.totalPages }} page(s)
                    </span>
                  </div>
                </div>
                <button type="button" @click.stop="removeFile" class="remove-file">
                  <i class="bi bi-x-circle"></i>
                </button>
              </div>
            </div>
            
            <span v-if="fileError" class="error-message">{{ fileError }}</span>
          </div>

          <!-- Prévisualisation du PDF -->
          <div class="pdf-preview-section" v-if="templateData.file">
            <h4>
              <i class="bi bi-eye"></i>
              Aperçu du document
            </h4>
            
            <div class="pdf-preview-container">
              <div v-if="pdfPreview.loading" class="pdf-loading">
                <i class="bi bi-arrow-repeat spinning"></i>
                <p>Chargement de la prévisualisation...</p>
              </div>
              <div v-else-if="pdfPreview.error" class="pdf-error">
                <i class="bi bi-exclamation-triangle"></i>
                <p>Impossible de charger la prévisualisation. {{ pdfPreview.error }}</p>
              </div>
              <iframe v-else :src="pdfPreview.url" class="pdf-preview"></iframe>
            </div>
          </div>
        </div>

        <!-- Étape 3: Configuration QR et signature -->
        <div v-if="currentStep === 2" class="step-body">
          <div class="positioning-section">
            <h4>
              <i class="bi bi-crosshair"></i>
              Configuration du QR code et de la signature
            </h4>
            <p class="positioning-hint">
              Configurez la position du QR code et ajoutez une signature manuscrite si nécessaire.
              Cette configuration sera réutilisable pour tous les documents utilisant ce template.
            </p>

            <!-- Composant QrPositioner -->
            <div class="qr-positioner-container" v-if="templateData.file">
              <QrPositioner
                :pdf-file="templateData.file"
                :total-pages="pdfPreview.totalPages || 1"
                :preloaded-positions="templateData.qrPositions"
                @position-changed="onPositionChanged"
                @position-confirmed="onPositionConfirmed"
                @signature-uploaded="onSignatureUploaded"
                @pdf-generated="onPdfGenerated"
              />
            </div>
          </div>
        </div>

        <!-- Étape 4: Confirmation et sauvegarde -->
        <div v-if="currentStep === 3" class="step-body">
          <div class="confirmation-section">
            <div v-if="saveStatus === 'saving'" class="saving-state">
              <div class="saving-icon">
                <i class="bi bi-hourglass-split spinning"></i>
              </div>
              <h4>Enregistrement du template en cours...</h4>
              <p>Veuillez patienter pendant la sauvegarde de votre template.</p>
            </div>
            
            <div v-else-if="saveStatus === 'success'" class="success-state">
              <div class="success-icon">
                <i class="bi bi-check-circle-fill text-success"></i>
              </div>
              <h4>Template créé avec succès !</h4>
              <p>Votre template "<strong>{{ templateData.name }}</strong>" a été enregistré et est maintenant disponible dans votre liste de templates.</p>
              
              <div class="template-summary">
                <div class="summary-item">
                  <i class="bi bi-file-earmark-pdf"></i>
                  <span>Document: {{ templateData.file?.name }}</span>
                </div>
                <div class="summary-item">
                  <i class="bi bi-qr-code"></i>
                  <span>QR configuré: {{ getQrConfigurationSummary() }}</span>
                </div>
                <div class="summary-item" v-if="templateData.hasSignature">
                  <i class="bi bi-vector-pen"></i>
                  <span>Avec signature manuscrite</span>
                </div>
              </div>
            </div>
            
            <div v-else-if="saveStatus === 'error'" class="error-state">
              <div class="error-icon">
                <i class="bi bi-exclamation-triangle-fill text-danger"></i>
              </div>
              <h4>Erreur lors de la sauvegarde</h4>
              <p>{{ saveError }}</p>
              <button class="btn-primary" @click="retrySave">
                <i class="bi bi-arrow-clockwise"></i>
                Réessayer
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation entre les étapes -->
      <div class="step-navigation">
        <div class="nav-left">
          <button 
            v-if="currentStep > 0 && saveStatus !== 'saving'" 
            @click="prevStep" 
            class="btn-secondary"
          >
            <i class="bi bi-chevron-left"></i>
            Précédent
          </button>
        </div>
        
        <div class="nav-right">
          <button 
            v-if="currentStep < 2" 
            @click="nextStep" 
            class="btn-primary"
            :disabled="!canProceedToNextStep"
          >
            Suivant
            <i class="bi bi-chevron-right"></i>
          </button>
          
          <button 
            v-else-if="currentStep === 2" 
            @click="saveTemplate" 
            class="btn-primary"
            :disabled="!canSaveTemplate || saveStatus === 'saving'"
          >
            <span v-if="saveStatus === 'saving'">
              <i class="bi bi-hourglass-split spinning"></i>
              Enregistrement...
            </span>
            <span v-else>
              <i class="bi bi-check-circle"></i>
              Créer le template
            </span>
          </button>
          
          <button 
            v-else-if="currentStep === 3 && saveStatus === 'success'" 
            @click="closeModal" 
            class="btn-primary"
          >
            <i class="bi bi-house"></i>
            Retour au tableau de bord
          </button>
        </div>
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

// Propriétés calculées pour la validation
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 0) {
    // Étape 1: Nom du template requis
    return templateData.value.name.trim().length > 0;
  } else if (currentStep.value === 1) {
    // Étape 2: Fichier PDF requis et prévisualisé
    return templateData.value.file && !pdfPreview.value.loading && !pdfPreview.value.error;
  } else if (currentStep.value === 2) {
    // Étape 3: Positions QR confirmées
    return templateData.value.qrPositions !== null;
  }
  
  return true;
});

const canSaveTemplate = computed(() => {
  return templateData.value.name.trim().length > 0 && 
         templateData.value.file && 
         templateData.value.qrPositions &&
         templateData.value.generatedPdfFile;
});

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
function clearTemplateNameError() {
  templateNameError.value = '';
}

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
  } else {
    fileError.value = 'Veuillez déposer un fichier PDF valide';
  }
}

function removeFile() {
  templateData.value.file = null;
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
  
  console.log('Création de la prévisualisation PDF pour:', templateData.value.file.name);
  
  pdfPreview.value.loading = true;
  pdfPreview.value.error = null;
  
  try {
    const fileUrl = URL.createObjectURL(templateData.value.file);
    pdfPreview.value.url = fileUrl;
    pdfPreview.value.loading = false;
    
    // Détecter le nombre de pages
    detectPdfPages(templateData.value.file).then(pages => {
      pdfPreview.value.totalPages = pages;
      console.log('Nombre de pages détecté:', pages);
    });
    
  } catch (error) {
    console.error('Erreur création URL pour la prévisualisation:', error);
    pdfPreview.value.error = 'Erreur de chargement du PDF';
    pdfPreview.value.loading = false;
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
    emit('template-created', {
      id: response.id,
      name: templateApiData.name,
      description: templateApiData.description,
      createdAt: new Date().toISOString(),
      qrSize: templateApiData.qr_size,
      pageApplication: templateApiData.page_application,
      hasSignature: !!templateApiData.signature_image
    });
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde du template:', error);
    saveStatus.value = 'error';
    saveError.value = error.message || 'Une erreur est survenue lors de la sauvegarde du template.';
  }
}

// Fonction pour réessayer la sauvegarde
function retrySave() {
  saveStatus.value = null;
  saveError.value = '';
  currentStep.value = 2; // Retour à l'étape de configuration
}

// Fonction pour fermer la modal
function closeModal() {
  // Nettoyer les URLs créées
  if (pdfPreview.value.url) {
    URL.revokeObjectURL(pdfPreview.value.url);
  }
  if (templateData.value.generatedPdfDataUrl) {
    URL.revokeObjectURL(templateData.value.generatedPdfDataUrl);
  }
  
  emit('close');
}

// Fonction pour obtenir un résumé de la configuration QR
function getQrConfigurationSummary() {
  if (!templateData.value.qrPositions) return 'Non configuré';
  
  const qr = templateData.value.qrPositions.qr;
  const sizeLabels = { small: 'Petit', medium: 'Moyen', large: 'Grand' };
  const modeLabels = { 
    all: 'Toutes les pages',
    current: 'Page actuelle',
    custom: 'Pages spécifiques',
    individual: 'Positions individuelles'
  };
  
  return `${sizeLabels[qr.size] || 'Moyen'} - ${modeLabels[templateData.value.qrPositions.mode] || 'Standard'}`;
}

// Nettoyage au démontage
onMounted(() => {
  console.log('Composant CreateTemplate monté');
});
</script>

<style scoped>
/* Styles cohérents avec CollaboratorDashboard */
.create-template-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
  background: transparent;
}

/* Header section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: var(--card-bg);
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
  position: relative;
}

.section-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 32px;
  right: 32px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  border-radius: 2px;
}

.section-title {
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title i {
  color: var(--primary-color);
  font-size: 1.4rem;
}

/* Section card */
.section-card {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

/* Progression des étapes */
.steps-progress {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 40px;
  padding: 0 20px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 150px;
  position: relative;
}

.step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 20px;
  left: 50%;
  right: -50%;
  height: 2px;
  background: var(--border-color);
  z-index: 1;
}

.step.active:not(:last-child)::after,
.step.completed:not(:last-child)::after {
  background: var(--primary-color);
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-light);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
  transition: all 0.3s ease;
}

.step.active .step-number,
.step.completed .step-number {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.step-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-align: center;
}

.step.active .step-label,
.step.completed .step-label {
  color: var(--primary-color);
  font-weight: 600;
}

/* Contenu des étapes */
.step-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.step-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Formulaire d'informations */
.template-info-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
}

.form-label i {
  color: var(--primary-color);
}

.form-input, .form-textarea {
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-light);
  color: var(--text-color);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
}

.form-input.error {
  border-color: var(--danger-color);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.error-message {
  color: var(--danger-color);
  font-size: 0.85rem;
  font-weight: 500;
}

/* Section upload */
.upload-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-light);
  position: relative;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: rgba(var(--primary-color-rgb), 0.02);
}

.upload-area.has-file {
  border-style: solid;
  border-color: var(--success-color);
  background: rgba(var(--success-color-rgb), 0.05);
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  font-size: 3rem;
  color: var(--primary-color);
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.upload-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color);
}

.upload-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
}

.upload-hint {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.file-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.file-info i {
  font-size: 2rem;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-weight: 600;
  color: var(--text-color);
  font-size: 1rem;
}

.file-size, .file-pages {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.remove-file {
  background: none;
  border: none;
  color: var(--danger-color);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.remove-file:hover {
  background: rgba(var(--danger-color-rgb), 0.1);
}

/* Section prévisualisation PDF */
.pdf-preview-section h4 {
  color: var(--text-color);
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pdf-preview-container {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  height: 400px;
  background: white;
}

.pdf-loading, .pdf-error {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-secondary);
}

.pdf-loading .spinning {
  animation: spin 1s linear infinite;
}

.pdf-preview {
  width: 100%;
  height: 100%;
  border: none;
}

/* Section positionnement */
.positioning-section h4 {
  color: var(--text-color);
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.positioning-hint {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 24px;
  line-height: 1.5;
}

.qr-positioner-container {
  background: var(--bg-light);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

/* Section confirmation */
.confirmation-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 24px;
  padding: 40px 20px;
}

.saving-state, .success-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  max-width: 500px;
}

.saving-icon, .success-icon, .error-icon {
  font-size: 4rem;
}

.saving-icon .spinning {
  animation: spin 1s linear infinite;
  color: var(--primary-color);
}

.success-icon {
  color: var(--success-color);
}

.error-icon {
  color: var(--danger-color);
}

.confirmation-section h4 {
  color: var(--text-color);
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
}

.confirmation-section p {
  color: var(--text-secondary);
  font-size: 1rem;
  margin: 0;
  line-height: 1.5;
}

.template-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--bg-light);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 400px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-color);
  font-size: 0.9rem;
}

.summary-item i {
  color: var(--primary-color);
  width: 20px;
  text-align: center;
}

/* Navigation */
.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.nav-left, .nav-right {
  display: flex;
  gap: 12px;
}

/* Boutons */
.btn {
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.btn-secondary {
  background: var(--bg-light);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--hover-bg);
  border-color: var(--text-secondary);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: 1px solid var(--primary-color);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(var(--primary-color-rgb), 0.3);
}

.btn-primary:disabled {
  background: var(--neutral-color);
  border-color: var(--neutral-color);
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.btn .spinning {
  animation: spin 1s linear infinite;
}

/* Animations */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .create-template-container {
    padding: 16px;
  }
  
  .section-header {
    padding: 20px;
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .section-card {
    padding: 24px 20px;
  }
  
  .steps-progress {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .template-info-form {
    max-width: 100%;
  }
  
  .step-navigation {
    flex-direction: column-reverse;
    gap: 16px;
  }
  
  .nav-left, .nav-right {
    width: 100%;
    justify-content: center;
  }
}
</style> 