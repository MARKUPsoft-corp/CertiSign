<template>
  <div class="sign-document-container">
    <div class="section-card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="bi bi-pen"></i> Signer avec un template
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
        
        <!-- Étape 2: Sélection du document à signer avec le template (anciennement étape 0) -->
        <div v-if="currentStep === 2 || (currentStep === 1 && signatureType === 'permanent')" class="step-body">
          <div class="template-info-banner">
            <i class="bi bi-file-earmark-check"></i>
            <div>
              <h4>Template sélectionné: {{ template?.name || 'Template' }}</h4>
              <p>Vous allez utiliser ce template pour signer un document. Sélectionnez le document à signer.</p>
            </div>
          </div>

          <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <i class="bi bi-cloud-arrow-up-fill"></i>
            <p>Déposez votre fichier PDF ici ou cliquez pour sélectionner</p>
            <span class="upload-hint">Formats acceptés: .pdf (max 10MB)</span>
            <input type="file" ref="fileInput" accept=".pdf" @change="handleFileSelection" class="file-input">
          </div>
        </div>

        <!-- Étape 3: Prévisualisation du document (anciennement étape 1) -->
        <div v-if="currentStep === 3 || (currentStep === 2 && signatureType === 'permanent')" class="step-body">
          <div class="document-info">
            <div class="document-icon">
              <i class="bi bi-file-earmark-pdf"></i>
            </div>
            <div class="document-details">
              <div class="document-name">{{ selectedFile.name }}</div>
              <div class="document-size">{{ formatFileSize(selectedFile.size) }}</div>
            </div>
          </div>

          <div class="template-settings-summary">
            <h4>Paramètres du template</h4>
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

        <!-- Étape 4: Saisie du certificat et du mot de passe (anciennement étape 2) -->
        <div v-if="currentStep === 4 || (currentStep === 3 && signatureType === 'permanent')" class="step-body">
          <div class="certificate-info-banner">
            <i class="bi bi-shield-lock-fill"></i>
            <div>
              <h4>Certificat numérique</h4>
              <p>Pour signer le document, vous devez fournir un certificat PFX (.pfx) et son mot de passe.</p>
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

        <!-- Étape 5: En cours de signature (anciennement étape 3) -->
        <div v-if="currentStep === 5 || (currentStep === 4 && signatureType === 'permanent')" class="step-body signature-processing">
          <div v-if="signatureStatus === 'loading'">
            <div class="processing-animation">
              <i class="bi bi-shield-fill-check pulsing"></i>
              <div class="spinner-container">
                <div class="spinner"></div>
              </div>
            </div>
            <p class="processing-text">Signature du document en cours...</p>
            <div class="processing-steps">
              <div :class="['processing-step', {completed: processingStep >= 1}]">
                <i :class="processingStep >= 1 ? 'bi bi-check-circle-fill' : 'bi bi-circle'"></i>
                <span>Préparation du document</span>
              </div>
              <div :class="['processing-step', {completed: processingStep >= 2}]">
                <i :class="processingStep >= 2 ? 'bi bi-check-circle-fill' : 'bi bi-circle'"></i>
                <span>Signature électronique</span>
              </div>
              <div :class="['processing-step', {completed: processingStep >= 3}]">
                <i :class="processingStep >= 3 ? 'bi bi-check-circle-fill' : 'bi bi-circle'"></i>
                <span>Finalisation</span>
              </div>
            </div>
          </div>
          <div v-else-if="signatureStatus === 'error'" class="signature-error">
            <i class="bi bi-exclamation-circle"></i>
            <h4>Erreur lors de la signature</h4>
            <p>{{ signatureError }}</p>
          </div>
        </div>

        <!-- Étape 6: Téléchargement du document signé (anciennement étape 4) -->
        <div v-if="currentStep === 6 || (currentStep === 5 && signatureType === 'permanent')" class="step-body signature-complete">
          <div class="success-animation">
            <i class="bi bi-check-circle-fill"></i>
          </div>
          <h3>Document signé avec succès !</h3>
          <p>Votre document a été signé numériquement avec votre certificat.</p>
          
          <div class="signed-document-info">
            <div class="document-icon large">
              <i class="bi bi-file-earmark-check"></i>
            </div>
            <div class="document-details">
              <div class="document-name">{{ signedDocumentName }}</div>
              <div class="signature-date">Signé le {{ signatureDate }}</div>
            </div>
          </div>

          <div class="download-section">
            <a :href="signedDocumentUrl" :download="signedDocumentName" class="download-button">
              <i class="bi bi-download"></i>
              Télécharger le document signé
            </a>
            <p class="download-note">Le document signé contient une signature numérique et un QR code intégrés qui peuvent être vérifiés. Il a été enregistré dans la base de données et peut être consulté à tout moment dans votre espace personnel.</p>
          </div>
        </div>
      </div>

      <!-- Boutons de navigation entre les étapes -->
      <div class="step-navigation">
        <button 
          v-if="currentStep > 0 && currentStep < 6" 
          @click="prevStep" 
          class="nav-button secondary"
        >
          <i class="bi bi-arrow-left"></i> Précédent
        </button>
        
        <div class="spacer" v-if="currentStep > 0"></div>
        
        <button 
          v-if="currentStep < 5" 
          @click="nextStep" 
          class="nav-button primary"
          :disabled="!canProceedToNextStep"
        >
          Suivant <i class="bi bi-arrow-right"></i>
        </button>
        
        <button 
          v-if="currentStep === 6 || (currentStep === 5 && signatureType === 'permanent')" 
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
import { ref, computed, onMounted, defineEmits, defineProps } from 'vue';

// Définir les émetteurs d'événements
const emit = defineEmits(['close']);

// Définir les props avec validation détaillée
const props = defineProps({
  templateData: {
    type: Object,
    required: true,
    validator: (value) => {
      // Log des propriétés pour débogage
      console.log('Validation des props templateData:', {
        hasSignatureImage: !!value.signatureImage,
        signatureImageType: typeof value.signatureImage,
        hasSignaturePositions: !!value.signaturePositions,
        signaturePositionsType: typeof value.signaturePositions
      });
      return true;
    }
  }
});

// Accès au template
const template = ref(props.templateData);

// Étapes du workflow de signature (sans l'étape de positionnement QR)
const steps = [
  { label: 'Type de signature' },
  { label: 'Configuration expiration' },
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
const pdfPreview = ref(null);

// État des documents
const selectedFile = ref(null);
const certificateFile = ref(null);
const certificatePassword = ref('');
const showPassword = ref(false);

// État de la prévisualisation
const pdfPreviewUrl = ref('');
const pdfPreviewLoading = ref(false);
const pdfPreviewError = ref(null);
const pdfTotalPages = ref(1);

// État de la signature
const signatureStatus = ref(null); // 'loading', 'error', 'success'
const signatureError = ref(null);
const processingStep = ref(0);

// Informations sur le document signé
const signedDocumentUrl = ref('');
const signedDocumentName = ref('');
const signatureDate = ref('');

// Paramètres du template récupérés
const templateSettings = ref({
  qr_position: null,
  signature: null
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

// Charger les paramètres du template
onMounted(() => {
  // Si nous avons des données de template, les configurer
  if (props.templateData) {
    console.log('Template chargé:', props.templateData);
    
    // Convertir les données du template en structure utilisée par le composant
    console.log('Données brutes du template reçues:', JSON.stringify(props.templateData));
    
    templateSettings.value = {
      qr_position: {
        mode: props.templateData.pageApplication || props.templateData.page_application || 'all',
        size: props.templateData.qrSize || props.templateData.qr_size || 'medium',
        positions: props.templateData.qrPositions?.positions || props.templateData.qr_positions?.positions || props.templateData.qrPositions || props.templateData.qr_positions || [],
        pages: props.templateData.selectedPages || props.templateData.selected_pages || []
      },
      signature: props.templateData.signatureImage || props.templateData.signature_image ? {
        image: props.templateData.signatureImage || props.templateData.signature_image,
        positions: props.templateData.signaturePositions || props.templateData.signature_positions || [],
        size: props.templateData.signatureSize || props.templateData.signature_size || 50  // Ajouter la taille de signature
      } : null
    };
    
    // Déboguer les informations de signature pour vérification
    if (templateSettings.value.signature) {
      console.log('Informations de signature trouvées:', {
        imageUrl: templateSettings.value.signature.image?.substring(0, 30) + '...',
        positions: templateSettings.value.signature.positions
      });
      
      // Télécharger l'image de signature si c'est une URL
      if (templateSettings.value.signature.image && 
          typeof templateSettings.value.signature.image === 'string' && 
          templateSettings.value.signature.image.startsWith('https')) {
        
        console.log('Image de signature est une URL, téléchargement en cours...');
        downloadSignatureImage(templateSettings.value.signature.image);
      }
    } else {
      console.log('Aucune information de signature trouvée dans le template');
    }
    
    console.log('Paramètres du template configurés:', templateSettings.value);
    
    // Vérifier que l'image de signature est correctement formatée
    if (templateSettings.value.signature && templateSettings.value.signature.image) {
      if (typeof templateSettings.value.signature.image === 'string' && 
          templateSettings.value.signature.image.startsWith('data:image')) {
        console.log('Image de signature valide trouvée (base64)');
      } else {
        console.warn('Format d\'image de signature invalide:', 
                     typeof templateSettings.value.signature.image);
      }
    }
    
    // Stocker également dans localStorage pour une utilisation ultérieure
    localStorage.setItem('currentTemplateSettings', JSON.stringify(templateSettings.value));
  } else {
    // Si pas de données passées en props, essayer de récupérer depuis localStorage
    const storedSettings = localStorage.getItem('currentTemplateSettings');
    if (storedSettings) {
      templateSettings.value = JSON.parse(storedSettings);
      console.log('Paramètres du template récupérés du localStorage:', templateSettings.value);
    } else {
      console.warn('Aucun paramètre de template trouvé');
    }
  }
});

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
        
        // Mettre à jour également dans le localStorage
        localStorage.setItem('currentTemplateSettings', JSON.stringify(templateSettings.value));
        localStorage.setItem('signatureImageBase64', base64data);
        
        console.log('Image de signature mise à jour avec les données base64');
      }
    };
    
    // Déclencher la lecture du blob en base64
    reader.readAsDataURL(blob);
  } catch (error) {
    console.error('Erreur lors du téléchargement de l\'image de signature:', error);
  }
}

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
    // Étape sélection: Un fichier PDF doit être sélectionné
    return selectedFile.value !== null;
  } else if (currentStep.value === 3 || (currentStep.value === 2 && signatureType.value === 'permanent')) {
    // Étape prévisualisation: La prévisualisation doit être chargée
    return selectedFile.value !== null && !pdfPreviewLoading.value && !pdfPreviewError.value;
  } else if (currentStep.value === 4 || (currentStep.value === 3 && signatureType.value === 'permanent')) {
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
        // Skip l'étape de configuration et aller directement à la sélection
        currentStep.value = 2;
      } else {
        // Aller à la configuration expiration
        currentStep.value = 1;
      }
    } else if (currentStep.value === 1 && signatureType.value === 'ephemeral') {
      // Depuis la configuration expiration vers sélection documents
      currentStep.value = 2;
    } else if (currentStep.value === 4 || (currentStep.value === 3 && signatureType.value === 'permanent')) {
      // Si nous sommes à l'étape du certificat et passons à la signature, lancer le processus
      startSigningProcess();
      currentStep.value++;
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
      // Si on est à la sélection et type permanent, revenir au choix du type
      currentStep.value = 0;
    } else if (currentStep.value === 2 && signatureType.value === 'ephemeral') {
      // Si on est à la sélection et type éphémère, revenir à la configuration
      currentStep.value = 1;
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
  const file = event.target.files[0];
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file;
    
    // Si nous sommes à l'étape de sélection, passer automatiquement à la prévisualisation
    if (currentStep.value === 2 || (currentStep.value === 1 && signatureType.value === 'permanent')) {
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
    if (currentStep.value === 2 || (currentStep.value === 1 && signatureType.value === 'permanent')) {
      nextStep();
      createPdfPreview(file);
    }
  }
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

// Fonction pour obtenir le libellé de la taille du QR code
function getQrSizeLabel(size) {
  switch(size) {
    case 'small': return 'Petit';
    case 'medium': return 'Moyen';
    case 'large': return 'Grand';
    default: return 'Moyen';
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

// Lancer le processus de signature
async function startSigningProcess() {
  console.log('Début du processus de signature');
  
  // Debug - vérifier l'état du template et ses paramètres
  console.log('Template props lors de la signature:', props.templateData);
  console.log('Paramètres du template lors de la signature:', templateSettings.value);
  
  signatureStatus.value = 'loading';
  processingStep.value = 0;
  
  try {
    // Obtenir les informations de l'utilisateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userInfo.id) {
      console.warn('Utilisateur non connecté ou informations incomplètes');
    }
    
    // Créer les métadonnées utilisateur avec les informations du template
    const userMetadata = {
      user_id: userInfo.id || '',
      username: userInfo.username || '',
      email: userInfo.email || '',
      full_name: userInfo.fullName || '',
      organization: userInfo.organization || '',
      organization_id: userInfo.organizationId || '',
      signer_role: userInfo.position || userInfo.role || '',
      jwt_token: localStorage.getItem('jwtToken') || '',
      // Extraire les positions QR du template
      qr_position: (() => {
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
        
        return {
          x: qrX,
          y: qrY,
          size: templateSettings.value.qr_position?.size || 'medium',
          pages: qrPages,
          positions: qrPositions,
          mode: qrMode
        };
      })(),
      signature_position: null
    };
    
    // Ajouter les informations de signature si disponibles
    if (templateSettings.value.signature) {
      // Récupérer l'image de signature depuis le localStorage si disponible
      let signatureImage = localStorage.getItem('signatureImageBase64') || templateSettings.value.signature.image || null;
      
      // S'assurer que l'image est au bon format
      if (signatureImage) {
        // Vérifier si l'image est déjà au bon format (data:image/...)
        if (!signatureImage.startsWith('data:image')) {
          console.warn('Format d\'image incorrect, tentative de correction');
          // Essayer de déterminer le type d'image
          let imageType = 'png';
          if (signatureImage.startsWith('/9j/')) {
            imageType = 'jpeg';
          }
          // Ajouter le préfixe data:image
          signatureImage = `data:image/${imageType};base64,${signatureImage}`;
        }
        
        console.log('Image de signature formatée:', signatureImage.substring(0, 50) + '...');
      }
      
      // Convertir les positions de signature en format attendu par le microservice
      let signaturePositions = [];
      if (templateSettings.value.signature.positions) {
        // Vérifier si positions est un objet avec des clés numériques ou "default"
        if (typeof templateSettings.value.signature.positions === 'object' && 
            !Array.isArray(templateSettings.value.signature.positions)) {
          
          console.log('Conversion des positions de signature du format objet au format tableau');
          
          // Convertir en tableau d'objets avec page, x, y
          Object.entries(templateSettings.value.signature.positions).forEach(([pageKey, position]) => {
            if (pageKey === 'default') {
              // Pour les positions par défaut (mode "all"), envoyer une seule position avec page: "all"
              console.log('Mode "all" détecté, envoi d\'une position avec page: "all"');
              
              signaturePositions.push({
                page: "all",
                x: position.x,
                y: position.y,
                width: 20,  // Valeurs par défaut pour la largeur et hauteur
                height: 10
              });
              
              console.log('Position avec mode "all" générée');
            } else {
              // Positions individuelles par page
              const pageNumber = parseInt(pageKey);
              
              // Vérifier que pageNumber est valide
              if (!isNaN(pageNumber)) {
                signaturePositions.push({
                  page: pageNumber,
                  x: position.x,
                  y: position.y,
                  width: 20,  // Valeurs par défaut pour la largeur et hauteur
                  height: 10
                });
              }
            }
          });
          
          console.log('Positions de signature converties:', signaturePositions);
        } else if (Array.isArray(templateSettings.value.signature.positions)) {
          // Si c'est déjà un tableau, l'utiliser directement
          signaturePositions = templateSettings.value.signature.positions;
        }
      }
      
      userMetadata.signature_position = {
        positions: signaturePositions,
        signature_image: signatureImage,
        signature_size: templateSettings.value.signature?.size || 50  // Ajouter la taille de signature
      };
    }
    
    // Vérifier et logger les informations de signature
    if (userMetadata.signature_position) {
      console.log('Données de signature préparées pour le microservice:', {
        'positions_count': userMetadata.signature_position.positions?.length || 0,
        'image_disponible': !!userMetadata.signature_position.signature_image,
        'première_position': userMetadata.signature_position.positions?.[0] || 'aucune'
      });
    }
    
    console.log('Données envoyées au microservice de signature:', {
      qr_position: userMetadata.qr_position,
      signature_position: userMetadata.signature_position,
      document: selectedFile.value.name,
      certificate: certificateFile.value.name,
      user: `${userMetadata.user_id} - ${userMetadata.username}`
    });
    
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
    
    // Mise à jour du processus de signature
    processingStep.value = 1; // Préparation
    
    // Créer un FormData pour l'envoi au microservice via l'API gateway
    const formData = new FormData();
    formData.append('document', selectedFile.value);
    formData.append('certificate', certificateFile.value);
    formData.append('password', certificatePassword.value);
    formData.append('metadata', JSON.stringify(signatureMetadata));
    
    // Ajouter l'ID du propriétaire
    if (userInfo.id) {
      formData.append('owner_id', userInfo.id);
    }
    
    // Ajouter l'ID de l'organisation si disponible
    if (userInfo.organizationId) {
      formData.append('organization_id', userInfo.organizationId);
      console.log('Organization ID ajouté au formulaire:', userInfo.organizationId);
    }
    
    // Ajouter le rôle du signataire si disponible
    if (userInfo.position || userInfo.role) {
      formData.append('signer_role', userInfo.position || userInfo.role);
      console.log('Rôle du signataire ajouté au formulaire:', userInfo.position || userInfo.role);
    }
    
    // URL de l'API gateway (port 8001)
    const apiUrl = 'https://ppd.camgovca.cm/sign/sign';
    
    processingStep.value = 2; // Signature en cours
    
    // Appel à l'API gateway
    const response = await fetch(apiUrl, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de la signature du document');
    }
    
    processingStep.value = 3; // Finalisation
    
    // Récupérer le document signé
    const blob = await response.blob();
    const signedDocUrl = URL.createObjectURL(blob);
    
    // Mettre à jour les informations du document signé
    signedDocumentName.value = selectedFile.value.name.replace('.pdf', '_signed.pdf');
    signatureDate.value = new Date().toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    // Stocker l'URL du document signé
    signedDocumentUrl.value = signedDocUrl;
    
    // Passer à l'étape de téléchargement
    currentStep.value = 4;
    signatureStatus.value = 'success';
    
  } catch (error) {
    console.error('Erreur lors de la signature:', error);
    signatureStatus.value = 'error';
    signatureError.value = error.response?.data?.detail || error.message || 'Une erreur est survenue lors de la signature du document.';
  }
}

// Méthode pour fermer le composant
function closeSignature() {
  // Nettoyer les ressources
  if (pdfPreviewUrl.value) {
    URL.revokeObjectURL(pdfPreviewUrl.value);
  }
  if (signedDocumentUrl.value) {
    URL.revokeObjectURL(signedDocumentUrl.value);
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
    if (signedDocumentUrl.value) {
      URL.revokeObjectURL(signedDocumentUrl.value);
    }
    
    // Nettoyer le localStorage à la fermeture du composant
    localStorage.removeItem('currentTemplateSettings');
  };
});
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

.signed-document-info {
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.02);
  padding: 15px;
  border-radius: 8px;
  margin: 20px 0;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.document-icon.large {
  font-size: 2.5rem;
  color: var(--success-color, #28a745);
  margin-right: 15px;
}

.signature-date {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.download-section {
  margin-top: 30px;
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

.download-note {
  margin-top: 15px;
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
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