<template>
  <div class="sign-document-container">
    <div class="section-card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="bi bi-files"></i> Signer plusieurs documents
        </h3>
        <button @click="closeSignature" class="close-button">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
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
        <!-- Étape 1: Sélection des documents à signer -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="template-info-banner">
            <i class="bi bi-files"></i>
            <div>
              <h4>Signature multiple de documents</h4>
              <p>Vous pouvez sélectionner plusieurs documents PDF qui seront tous signés avec le même certificat. Sélectionnez tous les documents à signer.</p>
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

        <!-- Étape 2: Prévisualisation des documents avec onglets -->
        <div v-if="currentStep === 1" class="step-body">
          <div class="documents-summary">
            <h4>{{ selectedFiles.length }} document(s) sélectionné(s) pour la signature</h4>
            <p>Vous pouvez prévisualiser chaque document en cliquant sur les onglets ci-dessous.</p>
          </div>

          <!-- Onglets des documents -->
          <div class="documents-tabs">
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
                <div v-if="documentPreviews[activeDocumentIndex]?.loading" class="pdf-loading">
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
                ></iframe>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 3: Saisie du certificat et du mot de passe -->
        <div v-if="currentStep === 2" class="step-body">
          <div class="certificate-info-banner">
            <i class="bi bi-shield-lock-fill"></i>
            <div>
              <h4>Certificat numérique</h4>
              <p>Pour signer les {{ selectedFiles.length }} documents, vous devez fournir un certificat PFX (.pfx) et son mot de passe. Le même certificat sera utilisé pour tous les documents.</p>
            </div>
          </div>

          <div class="certificate-form">
            <div class="form-group">
              <label>Certificat PFX</label>
              <div class="upload-area small" @click="triggerCertificateInput" @dragover.prevent @drop.prevent="handleCertificateDrop">
                <i class="bi bi-shield-fill"></i>
                <p v-if="!certificateFile">Déposez votre fichier .pfx ou cliquez pour sélectionner</p>
                <p v-else class="certificate-name">{{ certificateFile.name }}</p>
                <input type="file" ref="certificateInput" accept=".pfx" @change="handleCertificateSelection" class="file-input">
              </div>
            </div>

            <div class="form-group">
              <label>Mot de passe du certificat</label>
              <div class="password-input-container">
                <input 
                  :type="showPassword ? 'text' : 'password'"
                  v-model="certificatePassword"
                  class="password-input"
                  placeholder="Entrez le mot de passe du certificat"
                >
                <button @click="showPassword = !showPassword" type="button" class="toggle-password-btn">
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 4: En cours de signature -->
        <div v-if="currentStep === 3" class="step-body signature-processing">
          <div v-if="signatureStatus === 'loading'">
            <div class="processing-animation">
              <i class="bi bi-shield-fill-check pulsing"></i>
              <div class="spinner-container">
                <div class="spinner"></div>
              </div>
            </div>
            <p class="processing-text">Signature des {{ selectedFiles.length }} documents en cours...</p>
            
            <!-- Progression détaillée pour chaque document -->
            <div class="documents-processing">
              <div 
                v-for="(file, index) in selectedFiles" 
                :key="index"
                :class="['document-processing-item', { 
                  'completed': completedDocuments.includes(index),
                  'current': currentProcessingDocument === index,
                  'pending': currentProcessingDocument < index
                }]"
              >
                <div class="processing-icon">
                  <i v-if="completedDocuments.includes(index)" class="bi bi-check-circle-fill"></i>
                  <i v-else-if="currentProcessingDocument === index" class="bi bi-arrow-repeat spinning"></i>
                  <i v-else class="bi bi-circle"></i>
                </div>
                <span class="document-name">{{ file.name }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="signatureStatus === 'error'" class="signature-error">
            <i class="bi bi-exclamation-circle"></i>
            <h4>Erreur lors de la signature</h4>
            <p>{{ signatureError }}</p>
          </div>
        </div>

        <!-- Étape 5: Téléchargement des documents signés -->
        <div v-if="currentStep === 4" class="step-body signature-complete">
          <div class="success-animation">
            <i class="bi bi-check-circle-fill"></i>
          </div>
          <h3>{{ selectedFiles.length }} document(s) signé(s) avec succès !</h3>
          <p>Tous vos documents ont été signés numériquement avec votre certificat.</p>
          
          <!-- Liste des documents signés -->
          <div class="signed-documents-list">
            <h4>Documents signés disponibles pour téléchargement</h4>
            <div class="signed-documents-grid">
              <div v-for="(signedDoc, index) in signedDocuments" :key="index" class="signed-document-card">
                <div class="signed-card-header">
                  <div class="document-icon large">
                    <i class="bi bi-file-earmark-check"></i>
                  </div>
                  <div class="document-status-badge">
                    <i class="bi bi-check-circle-fill"></i>
                    <span>Signé</span>
                  </div>
                </div>
                <div class="signed-card-body">
                  <div class="document-name" :title="signedDoc.name">
                    {{ truncateFileName(signedDoc.name, 35) }}
                  </div>
                  <div class="signature-date">
                    <i class="bi bi-calendar-check"></i>
                    {{ signatureDate }}
                  </div>
                  <div class="document-size-info">
                    <i class="bi bi-file-earmark"></i>
                    Document {{ index + 1 }} de {{ signedDocuments.length }}
                  </div>
                </div>
                <div class="signed-card-footer">
                  <a :href="signedDoc.url" :download="signedDoc.name" class="download-button">
                    <i class="bi bi-download"></i>
                    <span>Télécharger</span>
                  </a>
                </div>
              </div>
            </div>
            
            <!-- Bouton pour télécharger tous les documents -->
            <div class="download-all-section">
              <button @click="downloadAllDocuments" class="download-all-button">
                <i class="bi bi-download"></i>
                Télécharger tous les documents signés
              </button>
              <p class="download-note">Les documents signés contiennent une signature numérique et un QR code intégrés qui peuvent être vérifiés.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Boutons de navigation entre les étapes -->
      <div class="step-navigation">
        <button 
          v-if="currentStep > 0 && currentStep < 4" 
          @click="prevStep" 
          class="nav-button secondary"
        >
          <i class="bi bi-arrow-left"></i> Précédent
        </button>
        
        <div class="spacer" v-if="currentStep > 0"></div>
        
        <button 
          v-if="currentStep < 3" 
          @click="nextStep" 
          class="nav-button primary"
          :disabled="!canProceedToNextStep"
        >
          Suivant <i class="bi bi-arrow-right"></i>
        </button>
        
        <button 
          v-if="currentStep === 4" 
          @click="closeSignature" 
          class="nav-button primary"
        >
          Terminer <i class="bi bi-check"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits } from 'vue';

// Définir les émetteurs d'événements
const emit = defineEmits(['close']);

// Étapes du workflow de signature multiple
const steps = [
  { label: 'Sélection' },
  { label: 'Prévisualisation' },
  { label: 'Certificat' },
  { label: 'Signature' },
  { label: 'Téléchargement' }
];

// Étape courante
const currentStep = ref(0);

// Références aux éléments DOM
const fileInput = ref(null);
const certificateInput = ref(null);

// État des documents (changé de selectedFile à selectedFiles pour gérer plusieurs fichiers)
const selectedFiles = ref([]);
const certificateFile = ref(null);
const certificatePassword = ref('');
const showPassword = ref(false);

// Gestion des onglets de prévisualisation
const activeDocumentIndex = ref(0);
const documentPreviews = ref([]);

// État de la signature
const signatureStatus = ref(null); // 'loading', 'error', 'success'
const signatureError = ref(null);
const currentProcessingDocument = ref(-1);
const completedDocuments = ref([]);

// Informations sur les documents signés
const signedDocuments = ref([]);
const signatureDate = ref('');

// Propriété calculée pour contrôler la progression des étapes
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 0) {
    // Étape 1: Au moins un fichier PDF doit être sélectionné
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 1) {
    // Étape 2: Les prévisualisations doivent être chargées
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 2) {
    // Étape 3: Le certificat et le mot de passe doivent être fournis
    return certificateFile.value !== null && certificatePassword.value.trim() !== '';
  }
  
  return true;
});

// Méthodes de navigation entre les étapes
function nextStep() {
  if (currentStep.value < steps.length - 1 && canProceedToNextStep.value) {
    if (currentStep.value === 0) {
      // Lors du passage à l'étape de prévisualisation, créer les prévisualisations
      createDocumentPreviews();
    } else if (currentStep.value === 2) {
      // Si nous sommes à l'étape du certificat et passons à la signature, lancer le processus
      startSigningProcess();
    }
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

function triggerCertificateInput() {
  certificateInput.value.click();
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
  const pdfFiles = files.filter(file => file.type === 'application/pdf' && file.size <= 10 * 1024 * 1024);
  
  pdfFiles.forEach(file => {
    // Vérifier si le fichier n'est pas déjà dans la liste
    const exists = selectedFiles.value.some(existingFile => 
      existingFile.name === file.name && existingFile.size === file.size
    );
    
    if (!exists) {
      selectedFiles.value.push(file);
    }
  });
  
  // Si c'est le premier fichier ajouté, le définir comme onglet actif
  if (activeDocumentIndex.value >= selectedFiles.value.length) {
    activeDocumentIndex.value = selectedFiles.value.length - 1;
  }
}

function removeDocument(index) {
  selectedFiles.value.splice(index, 1);
  documentPreviews.value.splice(index, 1);
  
  // Ajuster l'index de l'onglet actif
  if (activeDocumentIndex.value >= selectedFiles.value.length) {
    activeDocumentIndex.value = Math.max(0, selectedFiles.value.length - 1);
  }
}

function setActiveDocument(index) {
  activeDocumentIndex.value = index;
}

function truncateFileName(fileName, maxLength) {
  if (fileName.length <= maxLength) return fileName;
  const extension = fileName.split('.').pop();
  const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
  const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4);
  return `${truncatedName}...${extension}`;
}

function handleCertificateSelection(event) {
  const file = event.target.files[0];
  if (file && file.name.toLowerCase().endsWith('.pfx')) {
    certificateFile.value = file;
  }
}

function handleCertificateDrop(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file && file.name.toLowerCase().endsWith('.pfx')) {
    certificateFile.value = file;
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

// Créer les prévisualisations pour tous les documents
function createDocumentPreviews() {
  documentPreviews.value = selectedFiles.value.map((file, index) => {
    const preview = {
      loading: true,
      error: null,
      url: null
    };
    
    // Créer l'URL de prévisualisation
    setTimeout(() => {
      try {
        const fileUrl = URL.createObjectURL(file);
        preview.url = fileUrl;
        preview.loading = false;
      } catch (error) {
        preview.error = 'Erreur de chargement';
        preview.loading = false;
      }
    }, 500 * index); // Décaler le chargement pour éviter les conflits
    
    return preview;
  });
}

// Lancer le processus de signature pour tous les documents
async function startSigningProcess() {
  signatureStatus.value = 'loading';
  currentProcessingDocument.value = 0;
  completedDocuments.value = [];
  signedDocuments.value = [];
  
  try {
    // Obtenir les informations de l'utilisateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Signer chaque document séquentiellement
    for (let i = 0; i < selectedFiles.value.length; i++) {
      currentProcessingDocument.value = i;
      
      const file = selectedFiles.value[i];
      
      // Créer les métadonnées utilisateur
      const userMetadata = {
        user_id: userInfo.id || '',
        username: userInfo.username || '',
        email: userInfo.email || '',
        full_name: userInfo.fullName || '',
        organization: userInfo.organization || '',
        organization_id: userInfo.organizationId || '',
        signer_role: userInfo.position || userInfo.role || '',
        qr_position: {
          x: 85,
          y: 90,
          size: 'medium',
          pages: 'all',
          mode: 'all'
        }
      };
      
      // Créer un FormData pour l'envoi au microservice
      const formData = new FormData();
      formData.append('document', file);
      formData.append('certificate', certificateFile.value);
      formData.append('password', certificatePassword.value);
      formData.append('metadata', JSON.stringify(userMetadata));
      
      if (userInfo.id) {
        formData.append('owner_id', userInfo.id);
      }
      if (userInfo.organizationId) {
        formData.append('organization_id', userInfo.organizationId);
      }
      
      // URL de l'API gateway
      const apiUrl = 'https://192.168.4.131:8001/gateway/sign/';
      
      // Appel à l'API gateway
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Erreur lors de la signature de ${file.name}: ${errorData.detail}`);
      }
      
      // Récupérer le document signé
      const blob = await response.blob();
      const signedDocUrl = URL.createObjectURL(blob);
      
      // Ajouter le document signé à la liste
      signedDocuments.value.push({
        name: file.name.replace('.pdf', '_signed.pdf'),
        url: signedDocUrl,
        originalIndex: i
      });
      
      // Marquer ce document comme terminé
      completedDocuments.value.push(i);
    }
    
    // Tous les documents sont signés
    signatureDate.value = new Date().toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    // Passer à l'étape de téléchargement
    currentStep.value = 4;
    signatureStatus.value = 'success';
    
  } catch (error) {
    console.error('Erreur lors de la signature:', error);
    signatureStatus.value = 'error';
    signatureError.value = error.message || 'Une erreur est survenue lors de la signature des documents.';
  }
}

// Télécharger tous les documents signés
function downloadAllDocuments() {
  signedDocuments.value.forEach(doc => {
    const link = document.createElement('a');
    link.href = doc.url;
    link.download = doc.name;
    link.click();
  });
}

// Méthode pour fermer le composant
function closeSignature() {
  // Nettoyer les ressources
  documentPreviews.value.forEach(preview => {
    if (preview.url) {
      URL.revokeObjectURL(preview.url);
    }
  });
  
  signedDocuments.value.forEach(doc => {
    if (doc.url) {
      URL.revokeObjectURL(doc.url);
    }
  });
  
  emit('close');
}


</script>

<style scoped>
.sign-document-container {
  background-color: var(--bg-color, #f8f9fa);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 100%;
  animation: fade-in 0.3s ease-in-out;
}

/* Progression des étapes */
.steps-progress {
  display: flex;
  justify-content: space-between;
  margin: 25px 0;
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
  background-color: white;
  border: 2px solid var(--border-color, rgba(0, 0, 0, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 8px;
  transition: all 0.3s ease;
  color: var(--text-muted, #6c757d);
}

.step.active .step-number {
  background-color: var(--primary-color, #3a86ff);
  border-color: var(--primary-color, #3a86ff);
  color: white;
}

.step.completed .step-number {
  background-color: var(--success-color, #28a745);
  border-color: var(--success-color, #28a745);
  color: white;
}

.step-label {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  text-align: center;
  transition: all 0.3s ease;
}

.step.active .step-label,
.step.completed .step-label {
  color: var(--text-color, #333);
  font-weight: 500;
}

.section-card {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-button {
  background-color: transparent;
  border: none;
  color: var(--text-muted, #6c757d);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--danger, #dc3545);
}

/* Contenu des étapes */
.step-content {
  padding: 15px 0;
  min-height: 300px;
}

.step-body {
  animation: fade-in 0.3s ease;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

/* Template info */
.template-info-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: rgba(58, 134, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.template-info-banner i {
  font-size: 2rem;
  color: var(--primary-color, #3a86ff);
}

.template-info-banner h4 {
  margin: 0 0 5px;
  font-size: 1.1rem;
}

.template-info-banner p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.template-settings-summary {
  padding: 15px;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  margin-bottom: 20px;
}

.template-settings-summary h4 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1rem;
  color: var(--text-color, #333);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.setting-item {
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  padding: 10px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.setting-label {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  margin-bottom: 5px;
}

.setting-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-color, #333);
}

.upload-area {
  border: 2px dashed var(--primary-color, #3a86ff);
  border-radius: 10px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: rgba(58, 134, 255, 0.05);
}

.upload-area.small {
  padding: 20px;
}

.upload-area:hover {
  background-color: rgba(58, 134, 255, 0.1);
  border-color: var(--primary-dark, #2970cf);
}

.upload-area i {
  font-size: 48px;
  color: var(--primary-color, #3a86ff);
  margin-bottom: 15px;
  display: block;
}

.upload-area p {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-color, #333);
}

.upload-hint {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.file-input {
  display: none;
}

/* Prévisualisation du PDF */
.pdf-preview-container {
  margin: 20px 0;
  height: 400px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.pdf-preview {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-loading, .pdf-error {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted, #6c757d);
}

.pdf-loading i, .pdf-error i {
  font-size: 3rem;
  margin-bottom: 15px;
}

.pdf-error i {
  color: var(--danger, #dc3545);
}

.spinning {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Formulaire de certificat */
.certificate-info-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  background-color: rgba(58, 134, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.certificate-info-banner i {
  font-size: 2rem;
  color: var(--primary-color, #3a86ff);
}

.certificate-info-banner h4 {
  margin: 0 0 5px;
  font-size: 1.1rem;
}

.certificate-info-banner p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.certificate-form {
  margin: 25px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
}

.certificate-name {
  font-weight: 500;
  color: var(--primary-color, #3a86ff);
}

.password-input-container {
  position: relative;
}

.password-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s;
}

.password-input:focus {
  outline: none;
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.2);
}

.toggle-password-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted, #6c757d);
  cursor: pointer;
}

/* Étape de traitement de la signature */
.signature-processing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
}

.processing-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 20px;
}

.processing-animation i {
  font-size: 4rem;
  color: var(--primary-color, #3a86ff);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.pulsing {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; transform: translate(-50%, -50%) scale(0.9); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  100% { opacity: 0.6; transform: translate(-50%, -50%) scale(0.9); }
}

.spinner-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.spinner {
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top: 3px solid var(--primary-color, #3a86ff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.processing-text {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 25px;
}

.processing-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
  max-width: 300px;
  margin: 0 auto;
}

.processing-step {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted, #6c757d);
  transition: all 0.3s ease;
}

.processing-step.completed {
  color: var(--success-color, #28a745);
}

.signature-error {
  text-align: center;
  color: var(--danger, #dc3545);
}

.signature-error i {
  font-size: 3rem;
  margin-bottom: 15px;
}

/* Étape de téléchargement du document signé */
.signature-complete {
  text-align: center;
  padding: 30px 0;
}

.success-animation {
  margin-bottom: 20px;
}

.success-animation i {
  font-size: 5rem;
  color: var(--success-color, #28a745);
  animation: scale-in 0.5s ease-out;
}

@keyframes scale-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.signed-documents-list {
  margin-top: 30px;
}

.signed-documents-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.signed-document-card {
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.02);
  padding: 15px;
  border-radius: 8px;
  width: calc(50% - 7.5px);
}

.document-icon.large {
  font-size: 2.5rem;
  color: var(--success-color, #28a745);
  margin-right: 15px;
}

.document-details {
  flex: 1;
}

.document-name {
  font-weight: 600;
  margin-bottom: 3px;
  word-break: break-word;
}

.signature-date {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.download-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: var(--primary-color, #3a86ff);
  color: white;
  text-decoration: none;
  padding: 12px 25px;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.2s;
}

.download-button:hover {
  background-color: var(--primary-dark, #2970cf);
  transform: translateY(-2px);
}

.download-all-section {
  margin-top: 30px;
}

.download-all-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: var(--primary-color, #3a86ff);
  color: white;
  text-decoration: none;
  padding: 12px 25px;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.2s;
}

.download-all-button:hover {
  background-color: var(--primary-dark, #2970cf);
  transform: translateY(-2px);
}

.download-note {
  margin-top: 15px;
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}

.document-preview-section {
  padding: 10px 0;
}

.document-info {
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.02);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.document-icon {
  font-size: 1.8rem;
  color: #e74c3c;
  margin-right: 15px;
}

.document-details {
  flex: 1;
}

.document-name {
  font-weight: 600;
  margin-bottom: 3px;
  word-break: break-word;
}

.document-size {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

/* Navigation entre les étapes */
.step-navigation {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding-top: 20px;
}

.nav-button {
  padding: 12px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  border: none;
  min-width: 120px;
  justify-content: center;
}

.nav-button.primary {
  background-color: var(--primary-color, #3a86ff);
  color: white;
}

.nav-button.primary:hover:not(:disabled) {
  background-color: var(--primary-dark, #2970cf);
}

.nav-button.secondary {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--text-color, #333);
}

.nav-button.secondary:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.nav-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spacer {
  flex: 1;
}

/* Animations */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Dark mode */
:global(.dark-theme) .section-card {
  background-color: rgba(30, 41, 59, 0.7);
  border-color: rgba(255, 255, 255, 0.05);
}

:global(.dark-theme) .upload-area {
  background-color: rgba(58, 134, 255, 0.1);
  border-color: rgba(58, 134, 255, 0.5);
}

:global(.dark-theme) .document-info,
:global(.dark-theme) .certificate-selection,
:global(.dark-theme) .template-settings-summary {
  background-color: rgba(255, 255, 255, 0.05);
}

:global(.dark-theme) .setting-item {
  background-color: rgba(50, 61, 79, 0.7);
}

:global(.dark-theme) .certificate-select,
:global(.dark-theme) .position-select,
:global(.dark-theme) .password-input {
  background-color: rgba(30, 41, 59, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-light, #f8f9fa);
}

/* Styles pour la sélection multiple de documents */
.upload-area.multiple {
  border: 2px dashed #6c757d;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area.multiple:hover {
  border-color: var(--primary-color, #3a86ff);
  background-color: rgba(58, 134, 255, 0.05);
}

.selected-documents-list {
  margin-top: 20px;
}

.selected-documents-list h4 {
  margin-bottom: 15px;
  color: var(--text-color, #333);
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.document-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.document-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.remove-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.remove-btn:hover {
  background-color: rgba(220, 53, 69, 0.1);
  transform: scale(1.1);
}

.document-info {
  flex: 1;
}

.document-name {
  font-weight: 600;
  margin-bottom: 5px;
  font-size: 0.9rem;
  color: var(--text-color, #333);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-size {
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
}

/* Styles pour les onglets des documents */
.documents-summary {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color, #3a86ff);
}

.documents-summary h4 {
  margin: 0 0 8px 0;
  color: var(--text-color, #333);
}

.documents-summary p {
  margin: 0;
  color: var(--text-muted, #6c757d);
  font-size: 0.9rem;
}

.documents-tabs {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.tabs-header {
  display: flex;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  overflow-x: auto;
  min-height: 50px;
}

.tab-button {
  background: none;
  border: none;
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
  min-width: 200px;
  position: relative;
}

.tab-button:hover {
  background-color: rgba(58, 134, 255, 0.1);
}

.tab-button.active {
  background-color: white;
  border-bottom-color: var(--primary-color, #3a86ff);
  color: var(--primary-color, #3a86ff);
}

.tab-title {
  flex: 1;
  text-align: left;
  font-size: 0.9rem;
}

.tab-remove-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  margin-left: 8px;
  opacity: 0.7;
  transition: all 0.2s;
}

.tab-remove-btn:hover {
  opacity: 1;
  background-color: rgba(220, 53, 69, 0.1);
}

.tab-content {
  padding: 20px;
}

.document-info-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.document-info-header .document-icon {
  font-size: 2rem;
  color: #e74c3c;
  margin-right: 15px;
}

.document-info-header .document-details {
  flex: 1;
}

.document-info-header .document-name {
  font-weight: 600;
  margin-bottom: 5px;
  font-size: 1.1rem;
}

/* Styles pour le processus de signature multiple */
.documents-processing {
  margin-top: 20px;
}

.document-processing-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 6px;
  transition: all 0.3s;
}

.document-processing-item.pending {
  background-color: #f8f9fa;
  color: var(--text-muted, #6c757d);
}

.document-processing-item.current {
  background-color: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
  border-left: 4px solid var(--primary-color, #3a86ff);
}

.document-processing-item.completed {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
  border-left: 4px solid #28a745;
}

.processing-icon {
  margin-right: 12px;
  font-size: 1.2rem;
}

.document-name {
  font-weight: 500;
}

/* Styles pour les documents signés */
.signed-documents-list h4 {
  margin-bottom: 20px;
  color: var(--text-color, #333);
}

.signed-documents-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 35px;
  margin-bottom: 30px;
}

.signed-document-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 400px;
  width: 100%;
}

.signed-document-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
  border-color: var(--primary-color, #3a86ff);
}

.signed-card-header {
  background: linear-gradient(135deg, #28a745, #20c997);
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  position: relative;
}

.signed-card-header::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-top: 10px solid #20c997;
}

.signed-document-card .document-icon.large {
  font-size: 3rem;
  color: white;
  margin: 0;
}

.document-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.signed-card-body {
  padding: 30px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.signed-document-card .document-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-color, #333);
  line-height: 1.4;
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.signature-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  margin: 0;
}

.document-size-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
  font-style: italic;
}

.signed-card-footer {
  padding: 0 30px 30px 30px;
  margin-top: auto;
}

.download-button {
  background: linear-gradient(135deg, var(--primary-color, #3a86ff), #007bff);
  color: white;
  text-decoration: none;
  padding: 18px 30px;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(58, 134, 255, 0.3);
  width: 100%;
}

.download-button:hover {
  background: linear-gradient(135deg, var(--primary-dark, #2970cf), #0056b3);
  color: white;
  text-decoration: none;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 134, 255, 0.4);
}

.download-button i {
  font-size: 1.1rem;
}

/* Responsive pour la grille des documents signés */
@media (max-width: 1200px) {
  .signed-documents-grid {
    grid-template-columns: 1fr;
    gap: 25px;
  }
}

@media (max-width: 768px) {
  .signed-documents-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .signed-card-header {
    padding: 20px;
  }
  
  .signed-card-header::after {
    bottom: -8px;
    border-left-width: 12px;
    border-right-width: 12px;
    border-top-width: 8px;
  }
  
  .signed-card-body {
    padding: 20px;
  }
  
  .signed-card-footer {
    padding: 0 20px 20px 20px;
  }
}

@media (max-width: 480px) {
  .signed-document-card {
    min-height: 280px;
  }
  
  .signed-card-header .document-icon.large {
    font-size: 2.2rem;
  }
  
  .document-status-badge {
    font-size: 0.75rem;
    padding: 4px 8px;
  }
}

.download-all-section {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
}

.download-all-button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 10px;
}

.download-all-button:hover {
  background-color: #218838;
  transform: translateY(-1px);
}



/* Responsive styles */
@media (max-width: 768px) {
  .steps-progress {
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .steps-progress::before {
    display: none;
  }
  
  .step {
    width: 30%;
    margin-bottom: 10px;
  }
  
  .step-navigation {
    flex-direction: column;
    gap: 10px;
  }
  
  .nav-button {
    width: 100%;
  }
  
  .spacer {
    display: none;
  }
  
  .pdf-preview-container {
    height: 300px;
  }
  
  .template-settings-summary {
    padding: 10px;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  /* Responsive pour les nouvelles fonctionnalités */
  .documents-grid {
    grid-template-columns: 1fr;
  }
  
  .tabs-header {
    flex-direction: column;
  }
  
  .tab-button {
    min-width: auto;
    width: 100%;
    justify-content: space-between;
  }
  
  .signed-documents-grid {
    grid-template-columns: 1fr;
  }
  
  .signed-document-card {
    flex-direction: column;
    text-align: center;
  }
  
  .document-processing-item {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
}

@media (max-width: 576px) {
  .template-info-banner {
    flex-direction: column;
    text-align: center;
  }
  
  .certificate-info-banner {
    flex-direction: column;
    text-align: center;
  }
  
  .section-title {
    font-size: 1.1rem;
  }
}

.signature-preview {
  margin-top: 15px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  border: 1px dashed rgba(0, 0, 0, 0.1);
}

.signature-preview h5 {
  font-size: 0.9rem;
  margin-top: 0;
  margin-bottom: 10px;
  color: var(--text-muted, #6c757d);
}

.signature-image {
  max-width: 200px;
  max-height: 80px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
  border-radius: 4px;
}
</style> 