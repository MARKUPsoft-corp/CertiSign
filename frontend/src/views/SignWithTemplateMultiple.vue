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
        <!-- 🆕 ÉTAPE 0: Choix du type de signature (pérenne ou éphémère) -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="signature-type-selection">
            <div class="intro-banner">
              <i class="bi bi-lightning-charge"></i>
              <div>
                <h4>Type de signature</h4>
                <p>Choisissez le type de signature pour vos documents</p>
              </div>
            </div>

            <div class="signature-type-options">
              <!-- Option 1: Signature Pérenne -->
              <div class="signature-type-card" 
                   :class="{ selected: signatureType === 'permanent' }"
                   @click="signatureType = 'permanent'">
                <div class="type-icon permanent">
                  <i class="bi bi-shield-lock-fill"></i>
                </div>
                <div class="type-content">
                  <h4>Signature Pérenne</h4>
                  <p>Signature valide indéfiniment, idéale pour les documents officiels à conserver</p>
                </div>
                <div class="type-badge" v-if="signatureType === 'permanent'">
                  <i class="bi bi-check-circle-fill"></i>
                  Sélectionné
                </div>
              </div>

              <!-- Option 2: Signature Éphémère -->
              <div class="signature-type-card"
                   :class="{ selected: signatureType === 'ephemeral' }"
                   @click="signatureType = 'ephemeral'">
                <div class="type-icon ephemeral">
                  <i class="bi bi-clock-history"></i>
                </div>
                <div class="type-content">
                  <h4>Signature Éphémère</h4>
                  <p>Signature avec date d'expiration, parfaite pour les documents temporaires</p>
                </div>
                <div class="type-badge" v-if="signatureType === 'ephemeral'">
                  <i class="bi bi-check-circle-fill"></i>
                  Sélectionné
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 🆕 ÉTAPE 1: Configuration de la période de validité (si éphémère) -->
        <div v-if="currentStep === 1 && signatureType === 'ephemeral'" class="step-body">
          <div class="expiration-configuration">
            <div class="intro-banner">
              <i class="bi bi-clock-history"></i>
              <div>
                <h4>Période de validité</h4>
                <p>Définissez combien de temps vos signatures resteront valides</p>
              </div>
            </div>

            <!-- Durées pré-définies -->
            <div class="duration-presets">
              <h5>Durées courantes</h5>
              <div class="presets-grid">
                <button v-for="preset in durationPresets" 
                       :key="preset.value"
                       :class="['preset-btn', { active: selectedDuration === preset.value }]"
                       @click="selectDuration(preset.value)">
                  <div class="preset-icon">
                    <i :class="preset.icon"></i>
                  </div>
                  <div class="preset-label">{{ preset.label }}</div>
                  <div class="preset-desc">{{ preset.description }}</div>
                </button>
                
                <!-- Option personnalisée -->
                <button :class="['preset-btn', 'custom', { active: selectedDuration === 'custom' }]"
                       @click="selectDuration('custom')">
                  <div class="preset-icon">
                    <i class="bi bi-calendar-plus"></i>
                  </div>
                  <div class="preset-label">Personnalisé</div>
                  <div class="preset-desc">Choisir une date</div>
                </button>
              </div>
            </div>

            <!-- Sélecteur de date personnalisée -->
            <div v-if="selectedDuration === 'custom'" class="custom-date-selector">
              <h5>Date et heure d'expiration</h5>
              <input type="datetime-local" 
                     v-model="customExpirationDate"
                     :min="minExpirationDate"
                     class="date-input">
              <p class="date-hint">La signature expirera le {{ formatExpirationDisplay }}</p>
            </div>

            <!-- Résumé de l'expiration -->
            <div v-if="expirationDate" class="expiration-summary">
              <i class="bi bi-info-circle"></i>
              <p>La signature expirera <strong>{{ durationDescription }}</strong></p>
            </div>
          </div>
        </div>
        
        <!-- Étape 2: Sélection du template -->
        <div v-if="currentStep === 2" class="step-body">
          <div class="template-selection-banner">
            <i class="bi bi-layout-text-window-reverse"></i>
            <div>
              <h4>Sélectionnez un template de signature</h4>
              <p>Choisissez le template qui sera utilisé pour signer tous vos documents. Le template définit la position du QR code et de la signature.</p>
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
                <p class="template-description">{{ template.description || 'Template de signature personnalisé' }}</p>
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
            <p>Vous devez d'abord créer un template de signature dans votre espace collaborateur.</p>
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
                <span>Signature: {{ templateSettings.signature.positions?.length || 0 }} position(s)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 3: Sélection des documents à signer -->
        <div v-if="currentStep === 3" class="step-body">
          <div class="template-info-banner">
            <i class="bi bi-files"></i>
            <div>
              <h4>Signature multiple avec template: {{ selectedTemplate?.name }}</h4>
              <p>Sélectionnez plusieurs documents PDF qui seront tous signés avec le template "{{ selectedTemplate?.name }}". Le même certificat et les mêmes paramètres seront appliqués à tous les documents.</p>
            </div>
          </div>

          <!-- Résumé du template sélectionné -->
          <div class="template-settings-summary">
            <h4>Paramètres du template sélectionné</h4>
            <div class="settings-grid">
              <div class="setting-item">
                <div class="setting-label">Position QR</div>
                <div class="setting-value">{{ templateSettings.qr_position?.mode === 'all' ? 'Toutes les pages' : 'Pages spécifiques' }}</div>
              </div>
              <div class="setting-item">
                <div class="setting-label">Taille QR</div>
                <div class="setting-value">{{ getQrSizeLabel(templateSettings.qr_position?.size) }}</div>
              </div>
              <div class="setting-item">
                <div class="setting-label">Signature</div>
                <div class="setting-value">{{ templateSettings.signature ? 'Incluse' : 'Non incluse' }}</div>
              </div>
              <div v-if="templateSettings.signature" class="setting-item">
                <div class="setting-label">Positions signature</div>
                <div class="setting-value">{{ templateSettings.signature.positions?.length || 0 }} position(s)</div>
              </div>
            </div>
            
            <div v-if="templateSettings.signature && templateSettings.signature.image" class="signature-preview">
              <h5>Aperçu de la signature</h5>
              <img :src="templateSettings.signature.image" class="signature-image" alt="Signature" />
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

        <!-- Étape 4: Prévisualisation des documents avec onglets -->
        <div v-if="currentStep === 4" class="step-body">
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
                <div v-else class="pdf-error">
                  <i class="bi bi-exclamation-triangle"></i>
                  <p>Aucune prévisualisation disponible pour ce document.</p>
                  <button @click="createDocumentPreviews" class="retry-btn">Réessayer</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 5: Saisie du certificat et du mot de passe -->
        <div v-if="currentStep === 5" class="step-body">
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

        <!-- Étape 6: En cours de signature -->
        <div v-if="currentStep === 6" class="step-body signature-processing">
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

        <!-- Étape 7: Téléchargement des documents signés -->
        <div v-if="currentStep === 7" class="step-body signature-complete">
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
          v-if="currentStep > 0 && currentStep < 7" 
          @click="prevStep" 
          class="nav-button secondary"
        >
          <i class="bi bi-arrow-left"></i> Précédent
        </button>
        
        <div class="spacer" v-if="currentStep > 0"></div>
        
        <button 
          v-if="currentStep < 6" 
          @click="nextStep" 
          class="nav-button primary"
          :disabled="!canProceedToNextStep"
        >
          Suivant <i class="bi bi-arrow-right"></i>
        </button>
        
        <button 
          v-if="currentStep === 7" 
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
import { ref, computed, defineEmits, onMounted } from 'vue';
import TemplateService from '@/services/TemplateService';
import AuthService from '@/services/AuthService';

// Définir les émetteurs d'événements
const emit = defineEmits(['close']);

// Étapes du workflow de signature multiple
const steps = [
  { label: 'Type de signature' },
  { label: 'Configuration expiration' },
  { label: 'Template' },
  { label: 'Sélection' },
  { label: 'Prévisualisation' },
  { label: 'Certificat' },
  { label: 'Signature' },
  { label: 'Téléchargement' }
];

// Étape courante
const currentStep = ref(0);

// 🆕 NOUVELLES VARIABLES POUR SIGNATURES ÉPHÉMÈRES
const signatureType = ref(''); // 'permanent' ou 'ephemeral'
const selectedDuration = ref('1month'); // Durée sélectionnée par défaut
const customExpirationDate = ref(''); // Date personnalisée

// Durées pré-définies
const durationPresets = [
  { 
    value: '1day', 
    label: '1 jour', 
    description: 'Idéal pour documents urgents',
    hours: 24,
    icon: 'bi-hourglass-split'
  },
  { 
    value: '1month', 
    label: '1 mois', 
    description: 'Standard pour la plupart des cas',
    hours: 720,
    icon: 'bi-calendar-month'
  },
  { 
    value: '3months', 
    label: '3 mois', 
    description: 'Pour les documents importants',
    hours: 2160,
    icon: 'bi-calendar-range'
  },
  { 
    value: '6months', 
    label: '6 mois', 
    description: 'Validité prolongée',
    hours: 4320,
    icon: 'bi-calendar-date'
  },
  { 
    value: '1year', 
    label: '1 an', 
    description: 'Validité maximale recommandée',
    hours: 8760,
    icon: 'bi-calendar-check'
  }
];

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

// Template sélectionné et ses paramètres
const selectedTemplate = ref(null);
const availableTemplates = ref([]);
const templateSettings = ref({
  qr_position: null,
  signature: null
});
const loadingTemplates = ref(false);

// Fonctions pour gérer les templates
async function loadTemplates() {
  loadingTemplates.value = true;
  try {
    // Récupérer l'utilisateur actuel et son organisation
    const user = AuthService.getCurrentUser();
    let organizationName = null;
    
    if (user) {
      if (user.organization && typeof user.organization === 'object') {
        organizationName = user.organization.name;
      } else if (user.organization) {
        organizationName = user.organization;
      }
    }
    
    console.log('Chargement des templates pour l\'organisation:', organizationName);
    
    const response = await TemplateService.getTemplates(organizationName);
    console.log('Réponse des templates:', response);
    
    // Gérer la structure paginée de l'API
    if (response && response.results && Array.isArray(response.results)) {
      availableTemplates.value = response.results;
      console.log('Templates extraits des résultats:', response.results);
    } else if (Array.isArray(response)) {
      // Si c'est déjà un tableau direct
      availableTemplates.value = response;
      console.log('Templates en format tableau direct:', response);
    } else {
      console.warn('Format de réponse inattendu:', response);
      availableTemplates.value = [];
    }
    
    console.log('Templates disponibles pour cette organisation:', availableTemplates.value.length);

    // Vérifier si un template a été sélectionné précédemment depuis le tableau de bord signer
    try {
      const storedTemplateId = localStorage.getItem('selectedTemplateId');
      if (storedTemplateId) {
        const preselected = availableTemplates.value.find(t => String(t.id) === String(storedTemplateId));
        if (preselected) {
          console.log('Template pré-sélectionné trouvé dans le localStorage:', preselected.name);
          selectTemplate(preselected);
        }
        // Nettoyer la sélection du localStorage pour éviter les effets de bords
        localStorage.removeItem('selectedTemplateId');
      }
    } catch (e) {
      console.warn('Impossible d’accéder au localStorage pour la pré-sélection du template', e);
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
        size: templateDetails.signature_size || 50  // Ajouter la taille de signature
      } : null
    };
    
    console.log('Paramètres du template configurés:', templateSettings.value);
    
    // Télécharger l'image de signature si c'est une URL
    if (templateSettings.value.signature && 
        templateSettings.value.signature.image && 
        typeof templateSettings.value.signature.image === 'string' && 
        templateSettings.value.signature.image.startsWith('https')) {
      
      console.log('Image de signature est une URL, téléchargement en cours...');
      await downloadSignatureImage(templateSettings.value.signature.image);
    }
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

// Charger les templates au montage du composant
onMounted(() => {
  loadTemplates();
});

// 🆕 PROPRIÉTÉS CALCULÉES POUR SIGNATURES ÉPHÉMÈRES
// Date minimale pour l'expiration (demain)
const minExpirationDate = computed(() => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().slice(0, 16);
});

// Date d'expiration calculée
const expirationDate = computed(() => {
  if (signatureType.value !== 'ephemeral') return null;
  
  if (selectedDuration.value === 'custom' && customExpirationDate.value) {
    return new Date(customExpirationDate.value);
  }
  
  const preset = durationPresets.find(p => p.value === selectedDuration.value);
  if (preset) {
    const date = new Date();
    date.setHours(date.getHours() + preset.hours);
    return date;
  }
  
  return null;
});

// Formatage de l'affichage de l'expiration
const formatExpirationDisplay = computed(() => {
  if (!expirationDate.value) return 'Non définie';
  
  return expirationDate.value.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
});

// Description de la durée
const durationDescription = computed(() => {
  if (signatureType.value !== 'ephemeral') return '';
  
  if (selectedDuration.value === 'custom') {
    if (!expirationDate.value) return 'Date personnalisée';
    
    const now = new Date();
    const diff = expirationDate.value - now;
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    
    if (days === 1) return 'dans 1 jour';
    if (days < 30) return `dans ${days} jours`;
    if (days < 365) return `dans ${Math.ceil(days / 30)} mois`;
    return `dans ${Math.ceil(days / 365)} an(s)`;
  } else {
    const preset = durationPresets.find(p => p.value === selectedDuration.value);
    return preset ? preset.description : '';
  }
});

// Propriété calculée pour contrôler la progression des étapes
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 0) {
    // Étape type de signature: Un type doit être sélectionné
    return signatureType.value !== '';
  } else if (currentStep.value === 1 && signatureType.value === 'ephemeral') {
    // Étape configuration expiration: Une durée doit être sélectionnée
    if (selectedDuration.value === 'custom') {
      return customExpirationDate.value !== '';
    }
    return selectedDuration.value !== '';
  } else if (currentStep.value === 2 || (currentStep.value === 1 && signatureType.value === 'permanent')) {
    // Étape template: Un template doit être sélectionné
    return selectedTemplate.value !== null;
  } else if (currentStep.value === 3 || (currentStep.value === 2 && signatureType.value === 'permanent')) {
    // Étape sélection: Au moins un fichier PDF doit être sélectionné
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 4 || (currentStep.value === 3 && signatureType.value === 'permanent')) {
    // Étape prévisualisation: Les prévisualisations doivent être chargées
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 5 || (currentStep.value === 4 && signatureType.value === 'permanent')) {
    // Étape certificat: Le certificat et le mot de passe doivent être fournis
    return certificateFile.value !== null && certificatePassword.value.trim() !== '';
  }
  
  return true;
});

// 🆕 MÉTHODE POUR LA SÉLECTION DE DURÉE
function selectDuration(duration) {
  selectedDuration.value = duration;
  if (duration !== 'custom') {
    customExpirationDate.value = '';
  }
}

// Méthodes de navigation entre les étapes
function nextStep() {
  if (currentStep.value < steps.length - 1 && canProceedToNextStep.value) {
    // Logique spéciale pour le workflow éphémère vs permanent
    if (currentStep.value === 0) {
      // Depuis l'étape de choix du type
      if (signatureType.value === 'permanent') {
        // Skip l'étape de configuration et aller directement au template
        currentStep.value = 2;
      } else {
        // Aller à la configuration expiration
        currentStep.value = 1;
      }
    } else if (currentStep.value === 1 && signatureType.value === 'ephemeral') {
      // Depuis la configuration expiration vers sélection template
      currentStep.value = 2;
    } else if (currentStep.value === 2) {
      // Depuis l'étape template vers sélection documents
      currentStep.value = 3;
    } else if (currentStep.value === 3) {
      // Arrivée à l'étape de prévisualisation, créer les prévisualisations
      console.log('Création des prévisualisations pour', selectedFiles.value.length, 'documents');
      createDocumentPreviews();
      currentStep.value = 4;
    } else if (currentStep.value === 4) {
      // Depuis prévisualisation vers certificat
      currentStep.value = 5;
    } else if (currentStep.value === 5) {
      // Depuis certificat vers signature
      console.log('Passage à l\'étape de signature');
      currentStep.value = 6;
      // Lancer le processus de signature après un court délai pour laisser l'interface se mettre à jour
      setTimeout(() => {
        startSigningProcess();
      }, 100);
    } else {
      // Navigation normale pour les autres étapes
      currentStep.value++;
    }
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    // Logique spéciale pour revenir en arrière avec les signatures éphémères
    if (currentStep.value === 2 && signatureType.value === 'permanent') {
      // Si on est au template et type permanent, revenir au choix du type
      currentStep.value = 0;
    } else if (currentStep.value === 2 && signatureType.value === 'ephemeral') {
      // Si on est au template et type éphémère, revenir à la configuration
      currentStep.value = 1;
    } else if (currentStep.value === 3) {
      // Depuis sélection documents vers template
      currentStep.value = 2;
    } else if (currentStep.value === 4) {
      // Depuis prévisualisation vers sélection documents
      currentStep.value = 3;
    } else if (currentStep.value === 5) {
      // Depuis certificat vers prévisualisation
      currentStep.value = 4;
    } else {
      currentStep.value--;
    }
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
  console.log('Création des prévisualisations pour', selectedFiles.value.length, 'documents');
  
  documentPreviews.value = selectedFiles.value.map((file, index) => {
    const preview = {
      loading: true,
      error: null,
      url: null
    };
    
    console.log(`Création prévisualisation pour ${file.name} (index ${index})`);
    
    // Créer l'URL de prévisualisation immédiatement
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
  
  console.log('Prévisualisations créées:', documentPreviews.value);
}

// Lancer le processus de signature pour tous les documents
async function startSigningProcess() {
  console.log('Démarrage du processus de signature');
  console.log('Démarrage du processus de signature pour', selectedFiles.value.length, 'documents');
  
  signatureStatus.value = 'loading';
  currentProcessingDocument.value = 0;
  completedDocuments.value = [];
  signedDocuments.value = [];
  signatureError.value = '';
  
  try {
    // Obtenir les informations de l'utilisateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    console.log('Informations utilisateur:', userInfo);
    
    // Signer chaque document séquentiellement
    for (let i = 0; i < selectedFiles.value.length; i++) {
      currentProcessingDocument.value = i;
      console.log(`Signature du document ${i + 1}/${selectedFiles.value.length}: ${selectedFiles.value[i].name}`);
      
      const file = selectedFiles.value[i];
      
      // Debug - vérifier l'état du template sélectionné et ses paramètres
      console.log('Template sélectionné lors de la signature:', selectedTemplate.value);
      console.log('Paramètres du template lors de la signature:', templateSettings.value);
      
      // Extraire les positions QR du template
      let qrX = 85; // valeur par défaut
      let qrY = 90; // valeur par défaut
      let qrPages = 'all'; // valeur par défaut
      let qrPositions = {};
      let qrMode = templateSettings.value.qr_position?.mode || 'all';
      
      if (templateSettings.value.qr_position?.positions) {
        // Vérifier si positions est un objet avec des clés numériques (format {1: {x, y}, 2: {x, y}})
        if (typeof templateSettings.value.qr_position.positions === 'object' && 
            !Array.isArray(templateSettings.value.qr_position.positions)) {
          
          console.log('Positions QR sous format objet, extraction des positions');
          
          // Si la clé est "default", c'est pour le mode "all"
          if (templateSettings.value.qr_position.positions.default) {
            const defaultPosition = templateSettings.value.qr_position.positions.default;
            qrX = defaultPosition.x || 85;
            qrY = defaultPosition.y || 90;
            qrPages = 'all';
            qrPositions = templateSettings.value.qr_position.positions;
            console.log(`Position QR par défaut extraite: x=${qrX}, y=${qrY}`);
          } else {
            // Sinon, c'est des positions individuelles par page
            const firstPageKey = Object.keys(templateSettings.value.qr_position.positions)[0];
            if (firstPageKey && templateSettings.value.qr_position.positions[firstPageKey]) {
              const firstPosition = templateSettings.value.qr_position.positions[firstPageKey];
              qrX = firstPosition.x || 85;
              qrY = firstPosition.y || 90;
              console.log(`Position QR extraite de la page ${firstPageKey}: x=${qrX}, y=${qrY}`);
            }
            // Convertir les clés en entiers, en excluant les clés non numériques
            qrPages = Object.keys(templateSettings.value.qr_position.positions)
              .filter(k => !isNaN(parseInt(k)))
              .map(k => parseInt(k));
            qrPositions = templateSettings.value.qr_position.positions;
          }
        } else if (Array.isArray(templateSettings.value.qr_position.positions) && 
                   templateSettings.value.qr_position.positions.length > 0) {
          
          console.log('Positions QR sous format tableau, extraction de la première position');
          const firstPosition = templateSettings.value.qr_position.positions[0];
          qrX = firstPosition.x || 85;
          qrY = firstPosition.y || 90;
          console.log(`Position QR extraite du tableau: x=${qrX}, y=${qrY}`);
          qrPositions = templateSettings.value.qr_position.positions;
        }
      }
      
      // Créer les métadonnées utilisateur avec les paramètres du template
      const userMetadata = {
        user_id: userInfo.id || '',
        username: userInfo.username || '',
        email: userInfo.email || '',
        full_name: userInfo.fullName || '',
        organization: userInfo.organization || '',
        organization_id: userInfo.organizationId || '',
        signer_role: userInfo.position || userInfo.role || '',
        jwt_token: localStorage.getItem('jwtToken') || '',
        qr_position: {
          x: qrX,
          y: qrY,
          size: templateSettings.value.qr_position?.size || 'medium',
          pages: qrPages,
          positions: qrPositions,
          mode: qrMode
        },
        signature_position: null
      };
      
      console.log('Métadonnées QR position préparées:', {
        template_qr_position: templateSettings.value.qr_position,
        metadata_qr_position: userMetadata.qr_position
      });
      
      // DEBUG - Inspection détaillée des positions QR
      console.log('DEBUGAGE POSITIONS QR:', {
        'qr_position_exists': !!templateSettings.value.qr_position,
        'positions_exists': !!templateSettings.value.qr_position?.positions,
        'positions_type': typeof templateSettings.value.qr_position?.positions,
        'positions_is_array': Array.isArray(templateSettings.value.qr_position?.positions),
        'positions_content': templateSettings.value.qr_position?.positions,
        'first_position_x': templateSettings.value.qr_position?.positions?.[0]?.x,
        'first_position_y': templateSettings.value.qr_position?.positions?.[0]?.y
      });
      
      // Ajouter les informations de signature si disponibles dans le template
      if (templateSettings.value.signature) {
        let signatureImage = templateSettings.value.signature.image;
        
        console.log('DEBUG SIGNATURE IMAGE - État initial:', {
          'image_exists': !!signatureImage,
          'image_type': typeof signatureImage,
          'image_length': signatureImage?.length || 0,
          'image_starts_with_data': signatureImage?.startsWith('data:image'),
          'image_preview': signatureImage?.substring(0, 100) + '...'
        });
        
        // S'assurer que l'image est au bon format
        if (signatureImage && !signatureImage.startsWith('data:image')) {
          console.warn('Format d\'image incorrect, tentative de correction');
          let imageType = 'png';
          if (signatureImage.startsWith('/9j/')) {
            imageType = 'jpeg';
          }
          signatureImage = `data:image/${imageType};base64,${signatureImage}`;
          console.log('Image corrigée:', signatureImage.substring(0, 100) + '...');
        }
        
        // Convertir les positions de signature en format attendu par le microservice
        let signaturePositions = [];
        console.log('DEBUG SIGNATURE POSITIONS - Positions brutes:', templateSettings.value.signature.positions);
        
        if (templateSettings.value.signature.positions) {
          if (typeof templateSettings.value.signature.positions === 'object' && 
              !Array.isArray(templateSettings.value.signature.positions)) {
            
            console.log('Conversion des positions de signature du format objet au format tableau');
            Object.entries(templateSettings.value.signature.positions).forEach(([pageKey, position]) => {
              if (pageKey === 'default') {
                // Pour les positions par défaut (mode "all"), envoyer une seule position avec page: "all"
                console.log('Mode "all" détecté, envoi d\'une position avec page: "all"');
                
                signaturePositions.push({
                  page: "all",
                  x: position.x,
                  y: position.y,
                  width: 20,
                  height: 10
                });
                
                console.log('Position avec mode "all" générée');
              } else {
                // Positions individuelles par page
                const pageNumber = parseInt(pageKey);
                
                // Vérifier que pageNumber est valide
                if (!isNaN(pageNumber)) {
                  const convertedPosition = {
                    page: pageNumber,
                    x: position.x,
                    y: position.y,
                    width: 20,
                    height: 10
                  };
                  signaturePositions.push(convertedPosition);
                  console.log(`Position signature page ${pageNumber}:`, convertedPosition);
                }
              }
            });
          } else if (Array.isArray(templateSettings.value.signature.positions)) {
            signaturePositions = templateSettings.value.signature.positions;
            console.log('Positions signature déjà en format tableau:', signaturePositions);
          }
        }
        
        userMetadata.signature_position = {
          positions: signaturePositions,
          signature_image: signatureImage,
          signature_size: templateSettings.value.signature?.size || 50  // Ajouter la taille de signature
        };
        
        console.log('DEBUG SIGNATURE FINAL - Données finales:', {
          'positions_count': userMetadata.signature_position.positions?.length || 0,
          'image_disponible': !!userMetadata.signature_position.signature_image,
          'image_final_format': userMetadata.signature_position.signature_image?.startsWith('data:image'),
          'positions_detail': userMetadata.signature_position.positions
        });
        
              console.log('Données de signature préparées pour le document:', file.name, {
        'positions_count': userMetadata.signature_position.positions?.length || 0,
        'image_disponible': !!userMetadata.signature_position.signature_image
      });
    } else {
      console.warn('Aucune signature trouvée dans templateSettings:', templateSettings.value);
    }
    
    // 🆕 AJOUTER LES DONNÉES D'EXPIRATION POUR SIGNATURES ÉPHÉMÈRES DANS LES MÉTADONNÉES
    const signatureMetadata = {
      ...userMetadata,
      signature_type: signatureType.value === 'ephemeral' ? 'ephemeral' : 'permanent'
    };
    
    if (signatureType.value === 'ephemeral' && expirationDate.value) {
      signatureMetadata.expiration_date = expirationDate.value.toISOString();
      console.log('🕐 Signature éphémère configurée, expiration:', expirationDate.value.toISOString());
    } else {
      console.log('🔒 Signature pérenne configurée (pas d\'expiration)');
    }
    
    // Créer un FormData pour l'envoi au microservice
    const formData = new FormData();
    formData.append('document', file);
    formData.append('certificate', certificateFile.value);
    formData.append('password', certificatePassword.value);
    formData.append('metadata', JSON.stringify(signatureMetadata));
      
      if (userInfo.id) {
        formData.append('owner_id', userInfo.id);
      }
      
      // Gestion complète des informations d'organisation (comme dans SignSimple)
      const orgId = userInfo.organizationId || (userInfo.organization && userInfo.organization.id);
      const orgName = userInfo.organizationName || (userInfo.organization && userInfo.organization.name);
      
      if (orgId) {
        formData.append('organization_id', orgId);
        console.log('Organization ID ajouté:', orgId);
      }
      if (orgName) {
        formData.append('organization_name', orgName);
        console.log('Organization name ajouté:', orgName);
      }
      
      // Ajouter le rôle du signataire si disponible
      const signerRole = userInfo.position || userInfo.role || 'Signataire';
      formData.append('signer_role', signerRole);
      console.log('Signer role ajouté:', signerRole);
      
      // Ajouter le nom du signataire si disponible
      const signerName = userInfo.first_name && userInfo.last_name ? 
        `${userInfo.first_name} ${userInfo.last_name}` : 
        userInfo.username || 'Signataire';
      formData.append('signer_name', signerName);
      console.log('Signer name ajouté:', signerName);
      
      console.log('Envoi de la requête de signature pour:', file.name);
      
      // URL de l'API gateway
      const apiUrl = 'https://ppd.camgovca.cm/sign/sign';
      
      // Appel à l'API gateway
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage;
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || 'Erreur inconnue';
        } catch {
          errorMessage = errorText || 'Erreur de communication avec le serveur';
        }
        throw new Error(`Erreur lors de la signature de ${file.name}: ${errorMessage}`);
      }
      
      // Récupérer le document signé
      const blob = await response.blob();
      console.log('Document signé reçu pour:', file.name, 'Taille:', blob.size);
      
      const signedDocUrl = URL.createObjectURL(blob);
      
      // Ajouter le document signé à la liste
      signedDocuments.value.push({
        name: file.name.replace('.pdf', '_signed.pdf'),
        url: signedDocUrl,
        originalIndex: i
      });
      
      // Marquer ce document comme terminé
      completedDocuments.value.push(i);
      console.log(`Document ${i + 1} signé avec succès`);
    }
    
    // Tous les documents sont signés
    signatureDate.value = new Date().toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    console.log('Tous les documents ont été signés avec succès');
    
    // Passer à l'étape de téléchargement
    currentStep.value = 7;
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

// Fonction pour télécharger l'image de signature et la convertir en base64
async function downloadSignatureImage(imageUrl) {
  try {
    console.log('Téléchargement de l\'image depuis:', imageUrl);
    
    // Récupérer l'image
    const response = await fetch(imageUrl);
    if (!response.ok) {
      throw new Error(`Erreur lors du téléchargement de l'image: ${response.status}`);
    }
    
    // Convertir en blob
    const blob = await response.blob();
    
    // Créer un FileReader pour convertir le blob en base64
    const reader = new FileReader();
    reader.onloadend = function() {
      // Le résultat est une chaîne base64
      const base64data = reader.result;
      console.log('Image convertie en base64:', base64data.substring(0, 50) + '...');
      
      // Mettre à jour l'image de signature dans les paramètres du template
      if (templateSettings.value.signature) {
        templateSettings.value.signature.image = base64data;
        console.log('Image de signature mise à jour avec les données base64');
      }
    };
    
    // Déclencher la lecture du blob en base64
    reader.readAsDataURL(blob);
  } catch (error) {
    console.error('Erreur lors du téléchargement de l\'image de signature:', error);
  }
}

// Fonction pour obtenir le libellé de la taille du QR code
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
  margin-bottom: 5px;
  font-size: 0.9rem;
  color: var(--text-color, #333);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

/* Styles pour la sélection de template */
.template-selection-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  background: linear-gradient(135deg, rgba(58, 134, 255, 0.1), rgba(0, 123, 255, 0.05));
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  border: 1px solid rgba(58, 134, 255, 0.2);
}

.template-selection-banner i {
  font-size: 2.5rem;
  color: var(--primary-color, #3a86ff);
}

.template-selection-banner h4 {
  margin: 0 0 5px;
  color: var(--text-color, #333);
  font-size: 1.2rem;
}

.template-selection-banner p {
  margin: 0;
  color: var(--text-muted, #6c757d);
  line-height: 1.4;
}

.templates-loading {
  text-align: center;
  padding: 40px;
  color: var(--text-muted, #6c757d);
}

.templates-loading i {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.template-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.template-card:hover {
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 4px 12px rgba(58, 134, 255, 0.15);
  transform: translateY(-2px);
}

.template-card.selected {
  border-color: var(--primary-color, #3a86ff);
  background: linear-gradient(135deg, rgba(58, 134, 255, 0.05), rgba(0, 123, 255, 0.02));
  box-shadow: 0 6px 20px rgba(58, 134, 255, 0.2);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.template-header i {
  font-size: 2rem;
  color: var(--primary-color, #3a86ff);
}

.template-status {
  color: var(--success-color, #28a745);
  font-size: 1.5rem;
}

.template-body h5 {
  margin: 0 0 8px;
  color: var(--text-color, #333);
  font-size: 1.1rem;
  font-weight: 600;
}

.template-description {
  color: var(--text-muted, #6c757d);
  font-size: 0.9rem;
  margin-bottom: 15px;
  line-height: 1.4;
}

.template-details {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.template-detail {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0, 0, 0, 0.05);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
}

.template-detail i {
  font-size: 0.9rem;
  color: var(--primary-color, #3a86ff);
}

.no-templates {
  text-align: center;
  padding: 40px;
  color: var(--text-muted, #6c757d);
}

.no-templates i {
  font-size: 3rem;
  color: var(--warning-color, #ffc107);
  margin-bottom: 15px;
  display: block;
}

.no-templates h4 {
  margin: 0 0 10px;
  color: var(--text-color, #333);
}

.selected-template-summary {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(32, 201, 151, 0.05));
  border: 1px solid rgba(40, 167, 69, 0.2);
  border-radius: 10px;
  padding: 20px;
  margin-top: 25px;
}

.selected-template-summary h4 {
  margin: 0 0 15px;
  color: var(--success-color, #28a745);
  font-size: 1.1rem;
}

.template-settings-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.setting-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.7);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-color, #333);
}

.setting-preview i {
  color: var(--success-color, #28a745);
  font-size: 1rem;
}

/* Responsive pour les templates */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .template-details {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .template-settings-preview {
    flex-direction: column;
  }
}

.pdf-error i {
  color: var(--danger, #dc3545);
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: var(--primary-color, #3a86ff);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.retry-btn:hover {
  background-color: var(--primary-hover, #2969d6);
  transform: translateY(-1px);
}

.spinning {
  animation: spin 1.5s linear infinite;
}

/* 🆕 STYLES POUR SIGNATURES ÉPHÉMÈRES */

/* Sélection du type de signature */
.signature-type-selection {
  padding: 20px 0;
}

.intro-banner {
  background: rgba(34, 197, 94, 0.1);
  border-radius: 12px;
  padding: 20px;
  color: #333;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.intro-banner i {
  font-size: 2.5rem;
  opacity: 0.9;
}

.intro-banner h4 {
  margin: 0 0 5px 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.intro-banner p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
}

.signature-type-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.signature-type-card {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(229, 231, 235, 0.6);
  border-radius: 16px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.signature-type-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.6);
}

.signature-type-card.selected {
  border-color: rgba(34, 197, 94, 0.8);
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(255, 255, 255, 0.9) 100%);
  box-shadow: 0 10px 25px rgba(34, 197, 94, 0.2);
}

.type-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.type-icon.permanent {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.type-icon.ephemeral {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.signature-type-card:hover .type-icon {
  transform: scale(1.1) rotate(5deg);
}

.type-content h4 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: var(--text-color);
}

.type-content p {
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
  font-size: 0.95rem;
}

.type-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Configuration de l'expiration */
.expiration-configuration {
  padding: 20px 0;
}

.duration-presets {
  margin-bottom: 30px;
}

.duration-presets h5 {
  font-size: 1.1rem;
  margin-bottom: 15px;
  color: var(--text-secondary);
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.preset-btn {
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-height: 120px;
}

.preset-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.preset-btn.active {
  background: rgba(58, 134, 255, 0.1);
  border-color: var(--primary-color);
}

.preset-btn.custom {
  border-style: dashed;
}

.preset-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.preset-btn.custom .preset-icon {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.preset-label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.95rem;
}

.preset-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.3;
}

/* Sélecteur de date personnalisée */
.custom-date-selector {
  background: var(--bg-light);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.custom-date-selector h5 {
  margin: 0 0 15px 0;
  color: var(--text-secondary);
}

.date-input {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.date-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(58, 134, 255, 0.1);
}

.date-hint {
  margin: 10px 0 0 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* Résumé de l'expiration */
.expiration-summary {
  background: rgba(58, 134, 255, 0.1);
  border: 1px solid rgba(58, 134, 255, 0.3);
  border-radius: 12px;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}

.expiration-summary i {
  color: var(--primary-color);
  font-size: 1.3rem;
}

.expiration-summary p {
  margin: 0;
  color: var(--text-color);
}

.expiration-summary strong {
  color: var(--primary-color);
  font-weight: 600;
}

</style> 