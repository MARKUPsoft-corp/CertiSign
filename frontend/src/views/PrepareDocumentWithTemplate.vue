<template>
  <div class="prepare-document-container integrated-mode">
    <!-- En-tête -->
    <div class="section-header">
      <h3 class="section-title">
        <i class="bi bi-layout-text-window-reverse"></i>
        Préparer des documents avec un template
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
        <!-- Étape 1: Sélection du template -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="template-selection-banner">
            <i class="bi bi-layout-text-window-reverse"></i>
            <div>
              <h4>Sélectionnez un template pour vos documents</h4>
              <p>Choisissez le template qui sera utilisé pour préparer vos documents. Le template définit automatiquement la position du QR code et de la signature.</p>
            </div>
          </div>

          <!-- Chargement des templates -->
          <div v-if="loadingTemplates" class="templates-loading">
            <i class="bi bi-arrow-repeat spinning"></i>
            <p>Chargement des templates...</p>
          </div>

          <!-- Liste des templates disponibles -->
          <div v-else-if="availableTemplates.length > 0" class="templates-grid">
            <div 
              v-for="template in availableTemplates" 
              :key="template.id"
              @click="selectTemplate(template)"
              :class="['template-card', { 'selected': selectedTemplate?.id === template.id }]"
            >
              <div class="template-header">
                <i class="bi bi-layout-text-window-reverse"></i>
                <div class="template-status" v-if="selectedTemplate?.id === template.id">
                  <i class="bi bi-check-circle-fill"></i>
                </div>
              </div>
              <div class="template-body">
                <h5 class="template-name">{{ template.name }}</h5>
                <p class="template-description">{{ template.description || 'Template de préparation personnalisé' }}</p>
                <div class="template-details">
                  <div class="template-detail">
                    <i class="bi bi-qr-code"></i>
                    <span>QR: {{ getQrSizeLabel(template.qr_size) }}</span>
                  </div>
                  <div class="template-detail" v-if="template.signature_image">
                    <i class="bi bi-vector-pen"></i>
                    <span>Avec signature</span>
                  </div>
                  <div class="template-detail">
                    <i class="bi bi-file-earmark"></i>
                    <span>{{ template.page_application === 'all' ? 'Toutes pages' : 'Pages spécifiques' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Aucun template disponible -->
          <div v-else class="no-templates">
            <i class="bi bi-exclamation-triangle"></i>
            <h4>Aucun template disponible</h4>
            <p>Vous devez d'abord créer un template dans votre espace collaborateur.</p>
            <button @click="$emit('create-template')" class="btn btn-primary">
              <i class="bi bi-plus"></i> Créer un template
            </button>
          </div>

          <!-- Résumé du template sélectionné -->
          <div v-if="selectedTemplate" class="selected-template-summary">
            <h4>Template sélectionné: {{ selectedTemplate.name }}</h4>
            <div class="template-settings-preview">
              <div class="setting-preview">
                <i class="bi bi-qr-code"></i>
                <span>QR Code: {{ getQrSizeLabel(templateSettings.qr_position?.size) }}</span>
              </div>
              <div class="setting-preview">
                <i class="bi bi-file-earmark"></i>
                <span>Application: {{ templateSettings.qr_position?.mode === 'all' ? 'Toutes les pages' : 'Pages spécifiques' }}</span>
              </div>
              <div class="setting-preview" v-if="templateSettings.signature">
                <i class="bi bi-vector-pen"></i>
                <span>Signature incluse</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 2: Sélection des documents -->
        <div v-if="currentStep === 1" class="step-body">
          <div class="template-info-banner">
            <i class="bi bi-files"></i>
            <div>
              <h4>Documents avec template: {{ selectedTemplate?.name }}</h4>
              <p>Sélectionnez les documents PDF qui seront préparés avec le template "{{ selectedTemplate?.name }}". Les positions QR et signature sont automatiquement appliquées.</p>
            </div>
          </div>

          <!-- Zone d'upload multiple -->
          <div class="upload-area multiple" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <i class="bi bi-cloud-arrow-up-fill"></i>
            <p>Déposez vos fichiers PDF ici ou cliquez pour sélectionner</p>
            <span class="upload-hint">Formats acceptés: .pdf (max 10MB par fichier) - Sélection multiple autorisée</span>
            <input type="file" ref="fileInput" accept=".pdf" multiple @change="handleFileSelection" class="file-input">
          </div>

          <!-- Liste des documents sélectionnés -->
          <div v-if="selectedFiles.length > 0" class="selected-documents-list">
            <h4>Documents sélectionnés ({{ selectedFiles.length }})</h4>
            <div class="documents-grid">
              <div v-for="(file, index) in selectedFiles" :key="index" class="document-card">
                <div class="document-header">
                  <div class="document-icon">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </div>
                  <button @click="removeDocument(index)" class="remove-btn" title="Supprimer ce document">
                    <i class="bi bi-x-circle-fill"></i>
                  </button>
                </div>
                <div class="document-info">
                  <div class="document-name" :title="file.name">{{ file.name }}</div>
                  <div class="document-size">{{ formatFileSize(file.size) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 3: Prévisualisation des documents avec template appliqué -->
        <div v-if="currentStep === 2" class="step-body">
          <div class="documents-summary">
            <h4>{{ selectedFiles.length }} document(s) sélectionné(s) avec template {{ selectedTemplate?.name }}</h4>
            <p>Prévisualisez vos documents avec le template appliqué. Les positions QR et signature sont automatiquement configurées.</p>
          </div>

          <!-- Onglets des documents -->
          <div class="documents-tabs" v-if="selectedFiles.length > 1">
            <div class="tabs-header">
              <button 
                v-for="(file, index) in selectedFiles" 
                :key="index"
                @click="setActiveDocument(index)"
                :class="['tab-button', { 'active': activeDocumentIndex === index }]"
              >
                <i class="bi bi-file-earmark-pdf"></i>
                <span class="tab-title">{{ truncateFileName(file.name, 20) }}</span>
                <button @click.stop="removeDocument(index)" class="tab-remove-btn" title="Supprimer">
                  <i class="bi bi-x"></i>
                </button>
              </button>
            </div>
          </div>
            
          <!-- Contenu de l'onglet actif -->
          <div class="tab-content" v-if="selectedFiles[activeDocumentIndex]">
            <div class="document-info-header">
              <div class="document-icon">
                <i class="bi bi-file-earmark-pdf"></i>
              </div>
              <div class="document-details">
                <div class="document-name">{{ selectedFiles[activeDocumentIndex].name }}</div>
                <div class="document-size">{{ formatFileSize(selectedFiles[activeDocumentIndex].size) }}</div>
              </div>
            </div>

            <!-- Prévisualisation PDF -->
            <div class="pdf-preview-container">
              <div v-if="!documentPreviews || !documentPreviews[activeDocumentIndex]" class="pdf-loading">
                <i class="bi bi-arrow-repeat spinning"></i>
                <p>Initialisation de la prévisualisation...</p>
              </div>
              <div v-else-if="documentPreviews[activeDocumentIndex]?.loading" class="pdf-loading">
                <i class="bi bi-arrow-repeat spinning"></i>
                <p>Chargement de la prévisualisation...</p>
              </div>
              <div v-else-if="documentPreviews[activeDocumentIndex]?.error" class="pdf-error">
                <i class="bi bi-exclamation-triangle"></i>
                <p>Impossible de charger la prévisualisation. {{ documentPreviews[activeDocumentIndex].error }}</p>
              </div>
              <iframe 
                v-else-if="documentPreviews[activeDocumentIndex]?.url" 
                class="pdf-preview" 
                :src="documentPreviews[activeDocumentIndex].url"
                width="100%"
                height="600"
                frameborder="0"
              ></iframe>
            </div>
          </div>
        </div>

        <!-- Étape 4: Confirmation et soumission -->
        <div v-if="currentStep === 3" class="step-body">
          <div class="submission-status">
            <div v-if="submissionStatus === 'loading'" class="submission-loading">
              <div class="processing-animation">
                <i class="bi bi-file-earmark-check pulsing"></i>
                <div class="spinner-container">
                  <div class="spinner"></div>
                </div>
              </div>
              <p class="processing-text">Préparation des {{ selectedFiles.length }} document(s) avec template...</p>
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
              <p>Les {{ selectedFiles.length }} document(s) ont été préparés avec le template "{{ selectedTemplate?.name }}" et sont prêts pour signature.</p>
              
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
            <div v-else class="ready-to-submit">
              <div class="submit-summary">
                <h4>Prêt à soumettre</h4>
                <p>{{ selectedFiles.length }} document(s) avec template "{{ selectedTemplate?.name }}"</p>
                
                <div class="template-applied-info">
                  <h5>Template appliqué :</h5>
                  <div class="applied-settings">
                    <div class="applied-setting">
                      <i class="bi bi-qr-code"></i>
                      <span>QR Code {{ getQrSizeLabel(templateSettings.qr_position?.size) }} - {{ templateSettings.qr_position?.mode === 'all' ? 'Toutes pages' : 'Pages spécifiques' }}</span>
                    </div>
                    <div class="applied-setting" v-if="templateSettings.signature">
                      <i class="bi bi-vector-pen"></i>
                      <span>Signature manuscrite incluse</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="submit-actions">
                <button @click="submitDocuments" class="submit-button primary">
                  <i class="bi bi-send"></i> Soumettre pour signature
                  <span class="button-count">({{ selectedFiles.length }})</span>
                </button>
                <button @click="saveAsDrafts" class="submit-button secondary">
                  <i class="bi bi-save"></i> Enregistrer comme brouillons
                  <span class="button-count">({{ selectedFiles.length }})</span>
                </button>
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
          v-if="currentStep === 2" 
          @click="proceedToSubmission" 
          class="nav-button primary"
          :disabled="!canProceedToNextStep"
        >
          Préparer la soumission <i class="bi bi-arrow-right"></i>
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
import { ref, computed, onMounted, defineEmits, defineProps } from 'vue';
import TemplateService from '@/services/TemplateService';
import DocumentService from '@/services/DocumentService';

// Définir les props
const props = defineProps({
  preselectedTemplate: {
    type: Object,
    default: null
  }
});

// Définir les émetteurs d'événements
const emit = defineEmits(['close', 'documentPrepared', 'create-template']);

// Étapes du workflow
const steps = [
  { label: 'Template' },
  { label: 'Documents' },
  { label: 'Prévisualisation' },
  { label: 'Confirmation' }
];

// État principal
const currentStep = ref(0);

// Références DOM
const fileInput = ref(null);

// État des templates
const selectedTemplate = ref(null);
const availableTemplates = ref([]);
const templateSettings = ref({
  qr_position: null,
  signature: null
});
const loadingTemplates = ref(false);

// État des documents
const selectedFiles = ref([]);
const activeDocumentIndex = ref(0);
const documentPreviews = ref([]);

// État de soumission
const submissionStatus = ref(null); // 'loading', 'error', 'success'
const submissionError = ref('');
const preparationDate = ref('');

// Propriété calculée pour contrôler la progression
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 0) {
    // Étape 1: Un template doit être sélectionné
    return selectedTemplate.value !== null;
  } else if (currentStep.value === 1) {
    // Étape 2: Au moins un fichier PDF doit être sélectionné
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 2) {
    // Étape 3: Les prévisualisations doivent être chargées
    return selectedFiles.value.length > 0 && 
           documentPreviews.value.length === selectedFiles.value.length &&
           documentPreviews.value.every(preview => !preview.loading && !preview.error);
  }
  
  return true;
});

// Navigation entre étapes
function nextStep() {
  if (currentStep.value < steps.length - 1 && canProceedToNextStep.value) {
    currentStep.value++;
    
    // Actions selon l'étape
    if (currentStep.value === 2) {
      // Arrivée à l'étape de prévisualisation
      createDocumentPreviews();
    }
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

function proceedToSubmission() {
  if (canProceedToNextStep.value) {
    currentStep.value = 3;
  }
}

// Gestion des templates
async function loadTemplates() {
  loadingTemplates.value = true;
  try {
    const response = await TemplateService.getTemplates();
    console.log('Templates récupérés:', response);
    
    if (response && response.results && Array.isArray(response.results)) {
      availableTemplates.value = response.results;
    } else if (Array.isArray(response)) {
      availableTemplates.value = response;
    } else {
      console.warn('Format de réponse inattendu:', response);
      availableTemplates.value = [];
    }
  } catch (error) {
    console.error('Erreur lors du chargement des templates:', error);
    availableTemplates.value = [];
  } finally {
    loadingTemplates.value = false;
  }
}

function selectTemplate(template) {
  selectedTemplate.value = template;
  console.log('Template sélectionné:', template);
  
  // Charger les détails complets du template
  loadTemplateDetails(template.id);
}

async function loadTemplateDetails(templateId) {
  try {
    const templateDetails = await TemplateService.getTemplate(templateId);
    console.log('Détails du template chargés:', templateDetails);
    
    // Configurer les paramètres du template
    templateSettings.value = {
      qr_position: {
        mode: templateDetails.page_application || 'all',
        size: templateDetails.qr_size || 'medium',
        positions: templateDetails.qr_positions?.positions || templateDetails.qr_positions || [],
        pages: templateDetails.selected_pages || []
      },
      signature: templateDetails.signature_image ? {
        image: templateDetails.signature_image,
        positions: templateDetails.signature_positions || [],
        size: templateDetails.signature_size || 50
      } : null
    };
    
    console.log('Paramètres du template configurés:', templateSettings.value);
  } catch (error) {
    console.error('Erreur lors du chargement des détails du template:', error);
  }
}

function getQrSizeLabel(size) {
  switch(size) {
    case 'small': return 'Petit';
    case 'medium': return 'Moyen';
    case 'large': return 'Grand';
    default: return 'Moyen';
  }
}

// Gestion des fichiers
function triggerFileInput() {
  fileInput.value.click();
}

function handleFileSelection(event) {
  const files = Array.from(event.target.files);
  addFiles(files);
}

function handleFileDrop(event) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer.files);
  addFiles(files);
}

function addFiles(files) {
  const pdfFiles = files.filter(file => file.type === 'application/pdf');
  
  if (pdfFiles.length > 0) {
    selectedFiles.value = [...selectedFiles.value, ...pdfFiles];
    console.log('Fichiers ajoutés:', pdfFiles.length);
  }
}

function removeDocument(index) {
  selectedFiles.value.splice(index, 1);
  documentPreviews.value.splice(index, 1);
  
  // Ajuster l'index actif si nécessaire
  if (activeDocumentIndex.value >= selectedFiles.value.length) {
    activeDocumentIndex.value = Math.max(0, selectedFiles.value.length - 1);
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

function truncateFileName(fileName, maxLength = 25) {
  if (fileName.length <= maxLength) return fileName;
  const extension = fileName.split('.').pop();
  const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
  const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4);
  return `${truncatedName}...${extension}`;
}

// Gestion des prévisualisations
function createDocumentPreviews() {
  console.log('Création des prévisualisations pour', selectedFiles.value.length, 'documents');
  
  documentPreviews.value = selectedFiles.value.map((file, index) => {
    const preview = {
      loading: true,
      error: null,
      url: null
    };
    
    try {
      const fileUrl = URL.createObjectURL(file);
      preview.url = fileUrl;
      preview.loading = false;
      console.log(`URL créée pour ${file.name}:`, fileUrl);
    } catch (error) {
      console.error(`Erreur création URL pour ${file.name}:`, error);
      preview.error = 'Erreur de chargement';
      preview.loading = false;
    }
    
    return preview;
  });
}

function setActiveDocument(index) {
  activeDocumentIndex.value = index;
}

// Soumission des documents
async function submitDocuments() {
  submissionStatus.value = 'loading';
  preparationDate.value = new Date().toLocaleDateString('fr-FR');
  
  try {
    // Ici on implémenterait l'API call pour soumettre les documents avec le template
    console.log('Soumission des documents avec template:', {
      template: selectedTemplate.value,
      documents: selectedFiles.value,
      settings: templateSettings.value
    });

    // Simuler un délai d'API
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Préparer les métadonnées avec le template
    const documentsToSubmit = selectedFiles.value.map(file => ({
      file: file,
      templateId: selectedTemplate.value.id,
      templateSettings: templateSettings.value
    }));

    // Appel à l'API de préparation des documents
    for (const docData of documentsToSubmit) {
      await DocumentService.prepareDocumentWithTemplate(docData);
    }
    
    submissionStatus.value = 'success';
    emit('documentPrepared', {
      count: selectedFiles.value.length,
      template: selectedTemplate.value.name
    });
    
  } catch (error) {
    console.error('Erreur lors de la soumission:', error);
    submissionStatus.value = 'error';
    submissionError.value = error.message || 'Une erreur est survenue lors de la préparation des documents.';
  }
}

async function saveAsDrafts() {
  submissionStatus.value = 'loading';
  preparationDate.value = new Date().toLocaleDateString('fr-FR');
  
  try {
    console.log('Sauvegarde en brouillons avec template:', {
      template: selectedTemplate.value,
      documents: selectedFiles.value
    });

    // Simuler un délai d'API
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Préparer les métadonnées avec le template
    const documentsToSave = selectedFiles.value.map(file => ({
      file: file,
      templateId: selectedTemplate.value.id,
      templateSettings: templateSettings.value,
      status: 'draft'
    }));

    // Appel à l'API de sauvegarde en brouillon
    for (const docData of documentsToSave) {
      await DocumentService.saveDocumentDraftWithTemplate(docData);
    }
    
    submissionStatus.value = 'success';
    emit('documentPrepared', {
      count: selectedFiles.value.length,
      template: selectedTemplate.value.name,
      type: 'draft'
    });
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error);
    submissionStatus.value = 'error';
    submissionError.value = error.message || 'Une erreur est survenue lors de la sauvegarde des brouillons.';
  }
}

// Fermeture et nettoyage
function closeModal() {
  emit('close');
}

function closePreparation() {
  // Nettoyer les ressources
  documentPreviews.value.forEach(preview => {
    if (preview.url) {
      URL.revokeObjectURL(preview.url);
    }
  });
  
  emit('close');
}

// Initialisation
onMounted(() => {
  loadTemplates();
  
  // Si un template est pré-sélectionné, l'utiliser automatiquement
  if (props.preselectedTemplate) {
    selectedTemplate.value = props.preselectedTemplate;
    console.log('Template pré-sélectionné:', props.preselectedTemplate);
    
    // Charger les détails du template
    loadTemplateDetails(props.preselectedTemplate.id);
    
    // Passer automatiquement à l'étape de sélection des documents
    currentStep.value = 1;
  }
});
</script> 

<style scoped>
/* Container principal */
.prepare-document-container {
  background-color: var(--bg-color, #f8f9fa);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 100%;
  animation: fade-in 0.3s ease-in-out;
}

.integrated-mode {
  border-radius: 0;
  box-shadow: none;
  background: transparent;
}

/* En-tête */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.section-title i {
  color: var(--primary-color);
}

/* Card principale */
.section-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

/* Progression des étapes */
.steps-progress {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 40px;
  gap: 40px;
  position: relative;
}

.steps-progress::before {
  content: '';
  position: absolute;
  top: 25px;
  left: 15%;
  right: 15%;
  height: 2px;
  background: linear-gradient(90deg, var(--border-color) 0%, var(--border-color) 100%);
  z-index: 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  z-index: 1;
  transition: all 0.3s ease;
}

.step-number {
  width: 50px;
  height: 50px;
  background: var(--bg-light);
  border: 3px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.step.active .step-number {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
  transform: scale(1.1);
}

.step.completed .step-number {
  background: var(--success-color);
  border-color: var(--success-color);
  color: white;
}

.step-label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.step.active .step-label {
  color: var(--primary-color);
}

.step.completed .step-label {
  color: var(--success-color);
}

/* Contenu des étapes */
.step-content {
  min-height: 500px;
}

.step-body {
  animation: slide-in 0.4s ease-out;
}

/* Bannières d'information */
.template-selection-banner,
.template-info-banner {
  background: linear-gradient(135deg, rgba(var(--primary-color-rgb), 0.1), rgba(var(--accent-color-rgb), 0.1));
  border: 1px solid rgba(var(--primary-color-rgb), 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.template-selection-banner i,
.template-info-banner i {
  font-size: 2rem;
  color: var(--primary-color);
}

.template-selection-banner h4,
.template-info-banner h4 {
  margin: 0 0 8px 0;
  color: var(--text-color);
  font-size: 1.2rem;
}

.template-selection-banner p,
.template-info-banner p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Chargement des templates */
.templates-loading {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.templates-loading i {
  font-size: 3rem;
  margin-bottom: 16px;
  animation: spin 1s linear infinite;
}

.templates-loading p {
  font-size: 1.1rem;
  margin: 0;
}

/* Grille des templates */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.template-card {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.template-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.template-card.selected {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(var(--primary-color-rgb), 0.05), rgba(var(--accent-color-rgb), 0.05));
  box-shadow: 0 8px 25px rgba(var(--primary-color-rgb), 0.2);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.template-header i {
  font-size: 2rem;
  color: var(--primary-color);
}

.template-status i {
  font-size: 1.5rem;
  color: var(--success-color);
}

.template-body h5 {
  margin: 0 0 8px 0;
  color: var(--text-color);
  font-size: 1.1rem;
  font-weight: 600;
}

.template-body p {
  margin: 0 0 16px 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
}

.template-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.template-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.template-detail i {
  font-size: 1rem;
  color: var(--accent-color);
}

/* Aucun template */
.no-templates {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.no-templates i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: var(--warning-color);
}

.no-templates h4 {
  margin: 0 0 12px 0;
  color: var(--text-color);
}

.no-templates p {
  margin: 0 0 20px 0;
  line-height: 1.5;
}

/* Résumé du template sélectionné */
.selected-template-summary {
  background: var(--bg-light);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.selected-template-summary h4 {
  margin: 0 0 16px 0;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.template-settings-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.setting-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.setting-preview i {
  color: var(--accent-color);
}

/* Zone d'upload */
.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-light);
  position: relative;
  overflow: hidden;
}

.upload-area:hover,
.upload-area.dragover {
  border-color: var(--primary-color);
  background: rgba(var(--primary-color-rgb), 0.05);
}

.upload-area i {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

.upload-area:hover i {
  transform: scale(1.1);
}

.upload-area p {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px 0;
}

.upload-hint {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

/* Liste des documents sélectionnés */
.selected-documents-list {
  margin-top: 24px;
}

.selected-documents-list h4 {
  margin: 0 0 16px 0;
  color: var(--text-color);
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.document-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.document-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.document-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: rgba(var(--danger-color-rgb), 0.1);
}

.document-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.document-name {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.document-size {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* Onglets des documents */
.documents-tabs {
  margin-bottom: 24px;
}

.tabs-header {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  position: relative;
}

.tab-button:hover {
  border-color: var(--primary-color);
  background: rgba(var(--primary-color-rgb), 0.05);
}

.tab-button.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.tab-remove-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 8px;
}

.tab-remove-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Résumé des documents */
.documents-summary {
  text-align: center;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-light);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.documents-summary h4 {
  margin: 0 0 8px 0;
  color: var(--text-color);
}

.documents-summary p {
  margin: 0;
  color: var(--text-secondary);
}

/* Info du document */
.document-info-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: var(--bg-light);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.document-details {
  flex: 1;
}

.document-name {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 4px;
}

.document-size {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Prévisualisation PDF */
.pdf-preview-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.pdf-preview {
  width: 100%;
  height: 600px;
  border: none;
  display: block;
}

.pdf-loading,
.pdf-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 16px;
  color: var(--text-secondary);
  text-align: center;
  padding: 40px;
}

.pdf-loading i {
  font-size: 3rem;
  color: var(--primary-color);
  animation: spin 1s linear infinite;
}

.pdf-error i {
  font-size: 3rem;
  color: var(--danger-color);
}

/* Statut de soumission */
.submission-status {
  text-align: center;
  padding: 40px;
}

.submission-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.processing-animation {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.processing-animation i {
  font-size: 4rem;
  color: var(--primary-color);
  z-index: 2;
}

.spinner-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.spinner {
  width: 80px;
  height: 80px;
  border: 4px solid rgba(var(--primary-color-rgb), 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.processing-text {
  font-size: 1.2rem;
  color: var(--text-color);
  margin: 0;
}

.submission-error {
  color: var(--danger-color);
}

.submission-error i {
  font-size: 4rem;
  margin-bottom: 16px;
}

.submission-error h4 {
  margin: 0 0 12px 0;
}

.submission-error p {
  margin: 0;
  font-size: 1rem;
}

.submission-success {
  color: var(--success-color);
}

.success-animation i {
  font-size: 5rem;
  margin-bottom: 20px;
  animation: pulse 2s ease-in-out;
}

.submission-success h3 {
  margin: 0 0 16px 0;
  color: var(--text-color);
}

.submission-success p {
  margin: 0 0 24px 0;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

/* Documents list dans le succès */
.documents-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
}

.document-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-light);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.document-icon.large {
  width: 50px;
  height: 50px;
  font-size: 1.5rem;
}

.preparation-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* Ready to submit */
.ready-to-submit {
  padding: 20px;
}

.submit-summary {
  margin-bottom: 24px;
  text-align: left;
}

.submit-summary h4 {
  margin: 0 0 8px 0;
  color: var(--text-color);
}

.submit-summary p {
  margin: 0 0 20px 0;
  color: var(--text-secondary);
}

.template-applied-info {
  background: var(--bg-light);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.template-applied-info h5 {
  margin: 0 0 12px 0;
  color: var(--text-color);
}

.applied-settings {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.applied-setting {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.applied-setting i {
  color: var(--accent-color);
}

.submit-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.submit-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-size: 1rem;
}

.submit-button.primary {
  background: var(--primary-color);
  color: white;
}

.submit-button.primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.submit-button.secondary {
  background: var(--bg-light);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.submit-button.secondary:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
}

.button-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  margin-left: 4px;
}

/* Navigation des étapes */
.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.spacer {
  flex: 1;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-size: 1rem;
}

.nav-button.primary {
  background: var(--primary-color);
  color: white;
}

.nav-button.primary:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-color-rgb), 0.3);
}

.nav-button.secondary {
  background: var(--bg-light);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.nav-button.secondary:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Animations */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulsing {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* Responsive */
@media (max-width: 768px) {
  .section-card {
    padding: 20px;
  }
  
  .steps-progress {
    gap: 20px;
  }
  
  .step-number {
    width: 40px;
    height: 40px;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .documents-grid {
    grid-template-columns: 1fr;
  }
  
  .tabs-header {
    flex-direction: column;
  }
  
  .submit-actions {
    flex-direction: column;
  }
  
  .step-navigation {
    flex-direction: column;
    gap: 12px;
  }
  
  .nav-button {
    width: 100%;
    justify-content: center;
  }
}

/* Utilities pour l'animation de rotation */
.spinning {
  animation: spin 1s linear infinite;
}
</style> 