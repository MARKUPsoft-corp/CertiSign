<template>
  <div class="prepare-document-container">
    <div class="section-card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="bi bi-file-earmark-text"></i> Préparer un document
        </h3>
        <button @click="closePreparation" class="close-button">
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
        <!-- Étape 1: Sélection du document -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <i class="bi bi-cloud-arrow-up-fill"></i>
            <p>Déposez votre fichier PDF ici ou cliquez pour sélectionner</p>
            <span class="upload-hint">Formats acceptés: .pdf (max 10MB)</span>
            <input type="file" ref="fileInput" accept=".pdf" @change="handleFileSelection" class="file-input">
          </div>
        </div>

        <!-- Étape 2: Prévisualisation du document -->
        <div v-if="currentStep === 1" class="step-body">
          <div class="document-info">
            <div class="document-icon">
              <i class="bi bi-file-earmark-pdf"></i>
            </div>
            <div class="document-details">
              <div class="document-name">{{ selectedFile.name }}</div>
              <div class="document-size">{{ formatFileSize(selectedFile.size) }}</div>
            </div>
          </div>

          <div class="pdf-preview-container">
            <div v-if="pdfPreviewLoading" class="pdf-loading">
              <i class="bi bi-arrow-repeat spinning"></i>
              <p>Chargement de la prévisualisation...</p>
            </div>
            <div v-else-if="pdfPreviewError" class="pdf-error">
              <i class="bi bi-exclamation-triangle"></i>
              <p>Impossible de charger la prévisualisation. {{ pdfPreviewError }}</p>
            </div>
            <iframe v-else ref="pdfPreview" class="pdf-preview" :src="pdfPreviewUrl"></iframe>
          </div>
        </div>

        <!-- Étape 3: Position du QR code -->
        <div v-if="currentStep === 2" class="step-body">
          <div class="qr-position-container">
            <qr-positioner
              :pdf-file="selectedFile"
              :total-pages="pdfTotalPages || 1"
              @position-changed="onQrPositionChanged"
              @position-confirmed="onQrPositionConfirmed"
            ></qr-positioner>
          </div>
          
          <div class="submit-options">
            <p class="submit-hint">
              <i class="bi bi-info-circle"></i>
              Une fois que vous êtes satisfait du positionnement du QR code, vous pouvez soumettre le document pour signature ou l'enregistrer comme brouillon.
            </p>
            <div class="submit-buttons">
              <button 
                @click="submitDocument" 
                class="submit-button primary"
              >
                <i class="bi bi-send"></i> Soumettre pour signature
              </button>
              <button 
                @click="saveAsDraft" 
                class="submit-button secondary"
              >
                <i class="bi bi-save"></i> Enregistrer comme brouillon
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
              <p class="processing-text">Préparation du document en cours...</p>
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
              <h3>Document préparé avec succès !</h3>
              <p>Le document a été envoyé au signataire et est disponible dans votre tableau de bord.</p>
              
              <div class="document-info">
                <div class="document-icon large">
                  <i class="bi bi-file-earmark-check"></i>
                </div>
                <div class="document-details">
                  <div class="document-name">{{ selectedFile.name }}</div>
                  <div class="preparation-date">Préparé le {{ preparationDate }}</div>
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

// État des documents
const selectedFile = ref(null);

// État de la prévisualisation
const pdfPreviewUrl = ref('');
const pdfPreviewLoading = ref(false);
const pdfPreviewError = ref(null);
const pdfTotalPages = ref(1);

// État de la soumission
const submissionStatus = ref(null); // 'loading', 'error', 'success'
const submissionError = ref(null);
const preparationDate = ref('');

// État pour le positionnement du QR code
const qrPosition = ref({
  x: 85,
  y: 90,
  size: 'medium'
});

// Propriété calculée pour contrôler la progression des étapes
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 0) {
    // Étape 1: Un fichier PDF doit être sélectionné
    return selectedFile.value !== null;
  } else if (currentStep.value === 1) {
    // Étape 2: La prévisualisation doit être chargée
    return selectedFile.value !== null && !pdfPreviewLoading.value && !pdfPreviewError.value;
  } else if (currentStep.value === 2) {
    // Étape 3: Position du QR code doit être définie
    return qrPosition.value !== null;
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
  const file = event.target.files[0];
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file;
    
    // Si nous sommes à l'étape de sélection, passer automatiquement à la prévisualisation
    if (currentStep.value === 0) {
      nextStep();
      createPdfPreview(file);
    }
  }
}

function handleFileDrop(event) {
  event.preventDefault();
  
  const file = event.dataTransfer.files[0];
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file;
    
    // Si nous sommes à l'étape de sélection, passer automatiquement à la prévisualisation
    if (currentStep.value === 0) {
      nextStep();
      createPdfPreview(file);
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

// Générer une prévisualisation du PDF
function createPdfPreview(file) {
  if (!file) return;
  
  pdfPreviewLoading.value = true;
  pdfPreviewError.value = null;
  
  // Créer une URL d'objet pour le fichier
  const fileUrl = URL.createObjectURL(file);
  pdfPreviewUrl.value = fileUrl;
  
  // Essayer de déterminer le nombre de pages du PDF
  detectPdfPages(file);
  
  // Vérifier que le fichier charge correctement
  setTimeout(() => {
    pdfPreviewLoading.value = false;
  }, 1500);
}

// Fonction pour détecter le nombre de pages du PDF
async function detectPdfPages(file) {
  try {
    console.log('Tentative de détection du nombre de pages...');
    
    // Méthode alternative : utiliser PDF.js directement
    const arrayBuffer = await file.arrayBuffer();
    
    // Utiliser PDF.js si disponible
    if (window.pdfjsLib) {
      const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      pdfTotalPages.value = pdf.numPages;
      console.log(`PDF analysé avec PDF.js: ${pdf.numPages} pages détectées`);
      return;
    }
    
    // Fallback : essayer de deviner depuis la taille du fichier
    const fileSizeKB = file.size / 1024;
    let estimatedPages = Math.max(1, Math.round(fileSizeKB / 50)); // Estimation: ~50KB par page
    estimatedPages = Math.min(estimatedPages, 100); // Max 100 pages estimées
    
    pdfTotalPages.value = estimatedPages;
    console.log(`Estimation du nombre de pages basée sur la taille: ${estimatedPages} pages (taille: ${fileSizeKB.toFixed(1)}KB)`);
    
  } catch (error) {
    console.error('Erreur lors de la détection des pages:', error);
    pdfTotalPages.value = 1;
  }
}

// Méthodes pour le positionnement du QR code
function onQrPositionChanged(position) {
  qrPosition.value = position;
}

function onQrPositionConfirmed(position) {
  qrPosition.value = position;
}

// Soumettre le document pour signature
async function submitDocument() {
  submissionStatus.value = 'loading';
  currentStep.value = 3; // Passer à l'étape de confirmation
  
  try {
    // Obtenir les informations du collaborateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userInfo.id) {
      console.warn('Utilisateur non connecté ou informations incomplètes');
    }

    // Vérifier qu'on a le nom de l'organisation
    if (!userInfo.organization || !userInfo.organization.name) {
      throw new Error('Informations de l\'organisation manquantes. Veuillez vous reconnecter.');
    }
    
    // Vérifier que les données de position du QR sont valides
    if (!qrPosition.value || typeof qrPosition.value.x !== 'number' || typeof qrPosition.value.y !== 'number') {
      throw new Error('Position du QR code invalide. Veuillez repositionner le QR code.');
    }
    
    console.log('Position QR à envoyer:', qrPosition.value);
    
    // Créer les données de position du QR code
    const formData = new FormData();
    formData.append('document_file', selectedFile.value);
    formData.append('document_name', selectedFile.value.name);
    
    // Ajouter les informations de position du QR code avec conversion explicite en string
    formData.append('qr_x_position', qrPosition.value.x.toString());
    formData.append('qr_y_position', qrPosition.value.y.toString());
    formData.append('qr_size', qrPosition.value.size.toString());
    
    // Simplification de qr_pages qui est maintenant un CharField
    formData.append('qr_pages', qrPosition.value.pages || 'all');
    formData.append('qr_positions', JSON.stringify(qrPosition.value.positions || {}));
    formData.append('qr_mode', qrPosition.value.mode || 'standard');
    
    // Ajouter le statut
    formData.append('status', 'pending_signature');
    
    // Ajouter le nom de l'organisation
    formData.append('organization_name', userInfo.organization.name);
    
    // Ajouter des métadonnées supplémentaires si nécessaire
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
    };
    formData.append('metadata', JSON.stringify(metadata));
    
    console.log('Envoi du document au backend...');
    
    // Vérifier le contenu du formData (debug)
    for (let [key, value] of formData.entries()) {
      console.log(`${key}: ${value instanceof File ? value.name : value}`);
    }
    
    // Appel direct à l'API Django
    const apiUrl = 'https://192.168.4.131:8000/api/documents/qr-positions/';
    
    // Configuration de la requête avec axios
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('token')}` // Utiliser le token d'authentification
      }
    };
    
    // Appel API avec timeout plus long pour les gros fichiers
    const response = await axios.post(apiUrl, formData, {
      ...config,
      timeout: 30000 // 30 secondes
    });
    
    // Traiter la réponse
    if (response.status === 200 || response.status === 201) {
      // Extraire l'ID du document préparé des données de réponse
      const documentId = response.data.id;
      console.log('Document préparé avec succès, ID:', documentId);
      
      // Formater la date de préparation
      preparationDate.value = new Date().toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      // Passer à l'étape de confirmation
      currentStep.value = 3;
      submissionStatus.value = 'success';
      
      // Émettre l'événement documentPrepared
      emit('documentPrepared', {
        id: documentId,
        name: selectedFile.value.name,
        status: 'pending_signature'
      });
    } else {
      throw new Error('Erreur lors de la préparation du document');
    }
    
  } catch (error) {
    console.error('Erreur lors de la préparation du document:', error);
    console.error('Détails de l\'erreur:', error.response?.data || 'Pas de détails disponibles');
    submissionStatus.value = 'error';
    submissionError.value = error.response?.data?.error || 
                            error.response?.data?.detail || 
                            error.message || 
                            "Une erreur est survenue lors de la préparation du document.";
  }
}

// Sauvegarder le document comme brouillon
async function saveAsDraft() {
  submissionStatus.value = 'loading';
  currentStep.value = 3; // Passer à l'étape de confirmation
  
  try {
    // Obtenir les informations du collaborateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userInfo.id) {
      console.warn('Utilisateur non connecté ou informations incomplètes');
    }
    
    // Vérifier qu'on a le nom de l'organisation
    if (!userInfo.organization || !userInfo.organization.name) {
      throw new Error('Informations de l\'organisation manquantes. Veuillez vous reconnecter.');
    }
    
    // Vérifier que les données de position du QR sont valides
    if (!qrPosition.value || typeof qrPosition.value.x !== 'number' || typeof qrPosition.value.y !== 'number') {
      throw new Error('Position du QR code invalide. Veuillez repositionner le QR code.');
    }
    
    console.log('Position QR à envoyer (brouillon):', qrPosition.value);
    
    // Créer les données de position du QR code
    const formData = new FormData();
    formData.append('document_file', selectedFile.value);
    formData.append('document_name', selectedFile.value.name);
    
    // Ajouter les informations de position du QR code avec conversion explicite en string
    formData.append('qr_x_position', qrPosition.value.x.toString());
    formData.append('qr_y_position', qrPosition.value.y.toString());
    formData.append('qr_size', qrPosition.value.size.toString());
    
    // Simplification de qr_pages qui est maintenant un CharField
    formData.append('qr_pages', qrPosition.value.pages || 'all');
    formData.append('qr_positions', JSON.stringify(qrPosition.value.positions || {}));
    formData.append('qr_mode', qrPosition.value.mode || 'standard');
    
    // Ajouter le statut
    formData.append('status', 'draft');
    
    // Ajouter le nom de l'organisation
    formData.append('organization_name', userInfo.organization.name);
    
    // Ajouter des métadonnées supplémentaires si nécessaire
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
    };
    formData.append('metadata', JSON.stringify(metadata));
    
    console.log('Envoi du brouillon au backend...');
    
    // Vérifier le contenu du formData (debug)
    for (let [key, value] of formData.entries()) {
      console.log(`${key}: ${value instanceof File ? value.name : value}`);
    }
    
    // Appel direct à l'API Django
    const apiUrl = 'http://192.168.4.131:8000/api/documents/qr-positions/';
    
    // Configuration de la requête avec axios
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('token')}` // Utiliser le token d'authentification
      }
    };
    
    // Appel API avec timeout plus long pour les gros fichiers
    const response = await axios.post(apiUrl, formData, {
      ...config,
      timeout: 30000 // 30 secondes
    });
    
    // Traiter la réponse
    if (response.status === 200 || response.status === 201) {
      // Extraire l'ID du document préparé des données de réponse
      const documentId = response.data.id;
      console.log('Brouillon sauvegardé avec succès, ID:', documentId);
      
      // Formater la date de préparation
      preparationDate.value = new Date().toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      // Passer à l'étape de confirmation
      currentStep.value = 3;
      submissionStatus.value = 'success';
      
      // Émettre l'événement documentPrepared
      emit('documentPrepared', {
        id: documentId,
        name: selectedFile.value.name,
        status: 'draft'
      });
    } else {
      throw new Error('Erreur lors de la sauvegarde du brouillon');
    }
    
  } catch (error) {
    console.error('Erreur lors de la sauvegarde du brouillon:', error);
    console.error('Détails de l\'erreur:', error.response?.data || 'Pas de détails disponibles');
    submissionStatus.value = 'error';
    submissionError.value = error.response?.data?.error || 
                            error.response?.data?.detail || 
                            error.message || 
                            "Une erreur est survenue lors de la sauvegarde du brouillon.";
  }
}

// Méthode pour fermer le composant
function closePreparation() {
  // Nettoyer les ressources
  if (pdfPreviewUrl.value) {
    URL.revokeObjectURL(pdfPreviewUrl.value);
  }
  
  // Émettre l'événement pour fermer le composant
  emit('close');
}

// Nettoyer les ressources lors du démontage du composant
onMounted(() => {
  return () => {
    if (pdfPreviewUrl.value) {
      URL.revokeObjectURL(pdfPreviewUrl.value);
    }
  };
});
</script>

<style scoped>
.prepare-document-container {
  background-color: var(--bg-color, #f8f9fa);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 100%;
  animation: slide-up 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow-y: auto;
  max-height: 90vh;
  margin: 0 auto;
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
</style> 