<template>
  <div class="edit-document-page">
    <div class="edit-document-container">
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">
            <i class="bi bi-pencil-square"></i> Modifier le brouillon
          </h3>
          <button @click="closeEdit" class="close-button">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <!-- Information du document en cours d'édition -->
        <div v-if="documentData" class="document-info">
          <div class="info-item">
            <i class="bi bi-file-earmark-pdf"></i>
            <span class="document-name">{{ documentData.document_name }}</span>
          </div>
          <div class="info-item">
            <i class="bi bi-calendar"></i>
            <span class="document-date">Créé le {{ formatDate(documentData.created_at) }}</span>
          </div>
          <div class="info-item">
            <i class="bi bi-tag"></i>
            <span class="document-status">Brouillon</span>
          </div>
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
          <!-- Étape 1: Prévisualisation du document -->
          <div v-if="currentStep === 0 && documentData" class="step-body">
            <div class="document-preview-section">
              <h4>Aperçu du document</h4>
              <div class="pdf-preview-container">
                <div v-if="isLoadingPreview" class="loading-state">
                  <div class="loading-spinner"></div>
                  <p>Chargement du document...</p>
                </div>
                <div v-else-if="previewError" class="error-state">
                  <i class="bi bi-exclamation-triangle"></i>
                  <p>{{ previewError }}</p>
                  <button @click="loadDocumentPreview" class="btn-primary">
                    Réessayer
                  </button>
                </div>
                <div v-else class="pdf-preview">
                  <embed :src="documentUrl" type="application/pdf" width="100%" height="400px" />
                </div>
              </div>
            </div>
          </div>

          <!-- Étape 2: Position QR/Signature -->
          <div v-if="currentStep === 1 && documentData" class="step-body">
            <div class="positioning-section">
              <h4>Positionnement QR et Signature</h4>
              <p class="positioning-description">
                Modifiez les positions du QR code et de la signature selon vos besoins.
              </p>
              <QrPositioner 
                :document-url="documentUrl"
                :initial-positions="existingPositions"
                @positionChanged="onPositionChanged"
                @positionsValidated="onPositionsValidated"
              />
            </div>
          </div>

          <!-- Étape 3: Confirmation et actions -->
          <div v-if="currentStep === 2" class="step-body">
            <div class="confirmation-section">
              <div v-if="submissionStatus === 'loading'" class="loading-state">
                <div class="loading-spinner"></div>
                <p>{{ isAssigning ? 'Attribution du document...' : 'Sauvegarde du brouillon...' }}</p>
              </div>
              
              <div v-else-if="submissionStatus === 'error'" class="error-state">
                <i class="bi bi-exclamation-triangle"></i>
                <h4>Erreur</h4>
                <p>{{ submissionError }}</p>
                <button @click="currentStep = 1" class="btn-primary">
                  Revenir
                </button>
              </div>
              
              <div v-else-if="submissionStatus === 'success'" class="success-state">
                <i class="bi bi-check-circle"></i>
                <h4>{{ isAssigning ? 'Document assigné !' : 'Brouillon sauvegardé !' }}</h4>
                <p v-if="isAssigning">
                  Le document a été assigné pour signature le {{ preparationDate }}.
                </p>
                <p v-else>
                  Vos modifications ont été sauvegardées le {{ preparationDate }}.
                </p>
                <div class="success-actions">
                  <button @click="closeEdit" class="btn-primary">
                    Terminer
                  </button>
                  <button @click="resetToEdit" class="btn-secondary">
                    Continuer l'édition
                  </button>
                </div>
              </div>
              
              <div v-else class="confirmation-content">
                <h4>Actions disponibles</h4>
                <p>Que souhaitez-vous faire avec ce document ?</p>
                
                <div class="action-buttons">
                  <button @click="saveDraft" class="btn-secondary" :disabled="!canProceed">
                    <i class="bi bi-save"></i>
                    Sauvegarder le brouillon
                  </button>
                  <button @click="assignForSignature" class="btn-primary" :disabled="!canProceed">
                    <i class="bi bi-send"></i>
                    Assigner pour signature
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div class="step-navigation">
          <button 
            v-if="currentStep > 0 && currentStep < 2" 
            @click="prevStep" 
            class="nav-button secondary"
          >
            <i class="bi bi-arrow-left"></i> Précédent
          </button>
          
          <div class="spacer" v-if="currentStep > 0 && currentStep < 2"></div>
          
          <button 
            v-if="currentStep < 1" 
            @click="nextStep" 
            class="nav-button primary"
          >
            Suivant <i class="bi bi-arrow-right"></i>
          </button>

          <button 
            v-if="currentStep === 1" 
            @click="nextStep" 
            class="nav-button primary"
            :disabled="!hasValidPositions"
          >
            Continuer <i class="bi bi-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import QrPositioner from '@/components/QrPositioner.vue';
import AuthService from '@/services/AuthService';

const route = useRoute();
const router = useRouter();

// Étapes du workflow d'édition
const steps = [
  { label: 'Aperçu' },
  { label: 'Positionnement' },
  { label: 'Confirmation' }
];

// État réactif
const currentStep = ref(0);
const documentData = ref(null);
const documentUrl = ref('');
const isLoadingPreview = ref(false);
const previewError = ref(null);

// État des positions
const existingPositions = ref(null);
const newPositions = ref(null);
const hasValidPositions = ref(false);

// État de soumission
const submissionStatus = ref(null);
const submissionError = ref('');
const preparationDate = ref('');
const isAssigning = ref(false);

// Propriétés calculées
const canProceed = computed(() => {
  return hasValidPositions.value && newPositions.value;
});

// Méthodes de navigation
function nextStep() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

// Méthodes de chargement
async function loadDocumentData() {
  try {
    const documentId = route.params.id;
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('Token d\'authentification manquant');
    }

    const user = AuthService.getCurrentUser();
    const organizationId = user?.organization?.id;
    
    if (!organizationId) {
      throw new Error('ID d\'organisation manquant');
    }

    const config = {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId
      }
    };

    // Charger les données du document
    const response = await axios.get(
      `https://192.168.4.131/api/documents/qr-positions/${documentId}/`,
      config
    );

    if (response.data) {
      documentData.value = response.data;
      
      // Construire l'URL du document
      documentUrl.value = `https://192.168.4.131${response.data.document_file}`;
      
      // Charger les positions existantes
      existingPositions.value = {
        qr: {
          x: response.data.qr_x_position,
          y: response.data.qr_y_position,
          size: response.data.qr_size,
          pages: response.data.qr_pages,
          positions: response.data.qr_positions || {},
          mode: response.data.qr_mode || 'standard'
        },
        signature: response.data.signature_positions ? {
          positions: response.data.signature_positions,
          size: response.data.signature_size || 50,
          image: response.data.signature_image
        } : null
      };
      
      // Initialiser newPositions avec les positions existantes
      newPositions.value = JSON.parse(JSON.stringify(existingPositions.value));
      hasValidPositions.value = true;
      
      console.log('Document chargé:', documentData.value);
      console.log('Positions existantes:', existingPositions.value);
    }
  } catch (error) {
    console.error('Erreur lors du chargement du document:', error);
    previewError.value = error.response?.data?.error || error.message || 'Erreur de chargement';
  }
}

async function loadDocumentPreview() {
  isLoadingPreview.value = true;
  previewError.value = null;
  
  try {
    await loadDocumentData();
  } catch (error) {
    previewError.value = error.message;
  } finally {
    isLoadingPreview.value = false;
  }
}

// Méthodes de positionnement
function onPositionChanged(positions) {
  newPositions.value = positions;
  console.log('Nouvelles positions:', positions);
}

function onPositionsValidated(isValid) {
  hasValidPositions.value = isValid;
  console.log('Positions validées:', isValid);
}

// Méthodes de sauvegarde et assignation
async function saveDraft() {
  submissionStatus.value = 'loading';
  isAssigning.value = false;
  currentStep.value = 2;

  try {
    await updateDocument('draft');
    submissionStatus.value = 'success';
    preparationDate.value = new Date().toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    submissionStatus.value = 'error';
    submissionError.value = error.message;
  }
}

async function assignForSignature() {
  submissionStatus.value = 'loading';
  isAssigning.value = true;
  currentStep.value = 2;

  try {
    await updateDocument('pending_signature');
    submissionStatus.value = 'success';
    preparationDate.value = new Date().toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    submissionStatus.value = 'error';
    submissionError.value = error.message;
  }
}

async function updateDocument(status) {
  try {
    const documentId = route.params.id;
    const token = localStorage.getItem('token');
    const user = AuthService.getCurrentUser();
    const organizationId = user?.organization?.id;

    if (!token || !organizationId) {
      throw new Error('Informations d\'authentification manquantes');
    }

    const formData = new FormData();
    
    // Ajouter les nouvelles positions
    if (newPositions.value?.qr) {
      formData.append('qr_x_position', newPositions.value.qr.x.toString());
      formData.append('qr_y_position', newPositions.value.qr.y.toString());
      formData.append('qr_size', newPositions.value.qr.size.toString());
      formData.append('qr_pages', newPositions.value.qr.pages || 'all');
      formData.append('qr_positions', JSON.stringify(newPositions.value.qr.positions || {}));
      formData.append('qr_mode', newPositions.value.qr.mode || 'standard');
    }

    // Ajouter les positions de signature si disponibles
    if (newPositions.value?.signature) {
      formData.append('signature_positions', JSON.stringify(newPositions.value.signature.positions || {}));
      formData.append('signature_size', newPositions.value.signature.size?.toString() || '50');
      
      // Si une nouvelle image de signature a été fournie
      if (newPositions.value.signature.image && newPositions.value.signature.image !== existingPositions.value?.signature?.image) {
        // Traiter l'image de signature
        if (newPositions.value.signature.image.startsWith('data:image')) {
          const response = await fetch(newPositions.value.signature.image);
          const imageBlob = await response.blob();
          formData.append('signature_image', imageBlob, 'signature.png');
        }
      }
    }

    // Ajouter le nouveau statut
    formData.append('status', status);

    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      },
      params: {
        organization_id: organizationId
      }
    };

    // Mettre à jour le document
    const response = await axios.patch(
      `https://192.168.4.131/api/documents/qr-positions/${documentId}/`,
      formData,
      config
    );

    if (response.status === 200) {
      console.log('Document mis à jour avec succès:', response.data);
    } else {
      throw new Error('Erreur lors de la mise à jour du document');
    }
  } catch (error) {
    console.error('Erreur lors de la mise à jour:', error);
    throw new Error(error.response?.data?.error || error.message || 'Erreur lors de la mise à jour');
  }
}

// Méthodes utilitaires
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
}

function resetToEdit() {
  submissionStatus.value = null;
  currentStep.value = 1;
}

function closeEdit() {
  router.push({ name: 'collaborator-dashboard' });
}

// Initialisation
onMounted(() => {
  document.title = 'Édition de brouillon - CertiSign';
  loadDocumentPreview();
});
</script>

<style scoped>
.edit-document-page {
  min-height: 100vh;
  background: linear-gradient(135deg, 
    var(--bg-color, #f8f9fa) 0%, 
    rgba(6, 255, 165, 0.05) 50%, 
    var(--bg-color, #f8f9fa) 100%);
  padding: 2rem 1rem;
}

.edit-document-container {
  max-width: 1200px;
  margin: 0 auto;
  animation: slide-up 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.section-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid rgba(6, 255, 165, 0.2);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
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

.document-info {
  display: flex;
  gap: 2rem;
  padding: 20px 25px;
  background: rgba(6, 255, 165, 0.05);
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-color, #212529);
}

.info-item i {
  color: var(--accent-color, #06ffa5);
  font-size: 1.1em;
}

.document-name {
  font-weight: 600;
}

.document-status {
  padding: 0.25rem 0.75rem;
  background: rgba(255, 193, 7, 0.2);
  color: #856404;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* Progression des étapes */
.steps-progress {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  gap: 2rem;
  background: rgba(255, 255, 255, 0.8);
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  opacity: 0.4;
  transition: all 0.3s ease;
}

.step.active {
  opacity: 1;
}

.step.completed {
  opacity: 1;
}

.step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 20px;
  left: 100%;
  width: 2rem;
  height: 2px;
  background: rgba(6, 255, 165, 0.2);
  transition: all 0.3s ease;
}

.step.completed:not(:last-child)::after {
  background: var(--accent-color, #06ffa5);
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(6, 255, 165, 0.1);
  border: 2px solid rgba(6, 255, 165, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
  transition: all 0.3s ease;
}

.step.active .step-number {
  background: var(--accent-color, #06ffa5);
  border-color: var(--accent-color, #06ffa5);
  color: white;
}

.step.completed .step-number {
  background: var(--accent-color, #06ffa5);
  border-color: var(--accent-color, #06ffa5);
  color: white;
}

.step-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-muted, #6c757d);
  text-align: center;
}

.step.active .step-label {
  color: var(--text-color, #212529);
  font-weight: 600;
}

/* Contenu des étapes */
.step-content {
  padding: 2rem;
  min-height: 400px;
}

.step-body h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color, #212529);
  font-size: 1.2rem;
  font-weight: 600;
}

/* Aperçu du document */
.document-preview-section {
  max-width: 800px;
  margin: 0 auto;
}

.pdf-preview-container {
  border: 2px dashed rgba(6, 255, 165, 0.3);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(6, 255, 165, 0.02);
}

.pdf-preview {
  width: 100%;
  min-height: 400px;
}

/* Positionnement */
.positioning-section {
  max-width: 1000px;
  margin: 0 auto;
}

.positioning-description {
  color: var(--text-muted, #6c757d);
  margin-bottom: 1.5rem;
  text-align: center;
}

/* États de chargement et d'erreur */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(6, 255, 165, 0.1);
  border-left: 3px solid var(--accent-color, #06ffa5);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state i {
  font-size: 3rem;
  color: var(--danger, #dc3545);
  margin-bottom: 1rem;
}

/* Confirmation */
.confirmation-section {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.success-state {
  padding: 2rem;
}

.success-state i {
  font-size: 4rem;
  color: var(--success, #28a745);
  margin-bottom: 1rem;
}

.success-state h4 {
  color: var(--success, #28a745);
  margin-bottom: 1rem;
}

.success-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

/* Navigation */
.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-top: 1px solid rgba(6, 255, 165, 0.1);
  background: rgba(255, 255, 255, 0.8);
}

.spacer {
  flex: 1;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.nav-button.primary {
  background: var(--accent-color, #06ffa5);
  color: white;
}

.nav-button.primary:hover:not(:disabled) {
  background: #05e094;
  transform: translateY(-1px);
}

.nav-button.secondary {
  background: rgba(108, 117, 125, 0.1);
  color: var(--text-color, #212529);
  border: 1px solid rgba(108, 117, 125, 0.2);
}

.nav-button.secondary:hover {
  background: rgba(108, 117, 125, 0.15);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Boutons d'action */
.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background: var(--accent-color, #06ffa5);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #05e094;
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(108, 117, 125, 0.1);
  color: var(--text-color, #212529);
  border: 1px solid rgba(108, 117, 125, 0.2);
}

.btn-secondary:hover {
  background: rgba(108, 117, 125, 0.15);
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animation d'entrée */
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
  .edit-document-page {
    padding: 1rem 0.5rem;
  }
  
  .steps-progress {
    gap: 1rem;
    padding: 1rem;
  }
  
  .step-content {
    padding: 1rem;
  }
  
  .document-info {
    flex-direction: column;
    gap: 1rem;
  }
  
  .action-buttons,
  .success-actions {
    flex-direction: column;
  }
}
</style> 