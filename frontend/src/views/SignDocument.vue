<template>
  <div class="sign-document-container">
    <div class="section-card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="bi bi-pen"></i> Signer un document
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
        
        <!-- Étape suivante: Sélection du document (anciennement étape 0) -->
        <div v-if="currentStep === 2 || (currentStep === 1 && signatureType === 'permanent')" class="step-body">
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

        <!-- Étape 4: Position du QR code (anciennement étape 2) -->
        <div v-if="currentStep === 4 || (currentStep === 3 && signatureType === 'permanent')" class="step-body">
          <div class="qr-position-container">
            <qr-positioner
              :pdf-file="selectedFile"
              :total-pages="pdfTotalPages || 1"
              @position-changed="onQrPositionChanged"
              @position-confirmed="onQrPositionConfirmed"
            ></qr-positioner>
          </div>
        </div>

        <!-- Étape 5: Saisie du certificat et du mot de passe (anciennement étape 3) -->
        <div v-if="currentStep === 5 || (currentStep === 4 && signatureType === 'permanent')" class="step-body">
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

        <!-- Étape 6: En cours de signature (anciennement étape 4) -->
        <div v-if="currentStep === 6 || (currentStep === 5 && signatureType === 'permanent')" class="step-body signature-processing">
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

        <!-- Étape 6: Téléchargement du document signé -->
        <!-- Étape 7: Téléchargement des documents signés (anciennement étape 5) -->
        <div v-if="currentStep === 7 || (currentStep === 6 && signatureType === 'permanent')" class="step-body signature-complete">
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
            <a :href="signedDocumentUrl" download class="download-button">
              <i class="bi bi-download"></i>
              Télécharger le document signé
            </a>
            <p class="download-note">Le document signé contient une signature numérique et un QR code intégrés qui peuvent être vérifiés.</p>
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
          v-if="currentStep === 7 || (currentStep === 6 && signatureType === 'permanent')" 
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
import { ref, computed, onMounted, defineEmits } from 'vue';
import axios from 'axios';
import QrPositioner from '@/components/QrPositioner.vue';

// Définir les émetteurs d'événements
const emit = defineEmits(['close']);

// Étapes du workflow de signature (mise à jour avec la nouvelle étape)
const steps = [
  { label: 'Type de signature' },
  { label: 'Configuration expiration' },
  { label: 'Sélection' },
  { label: 'Prévisualisation' },
  { label: 'Position QR' },
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

// Nouvel état pour le positionnement du QR code
const qrPosition = ref({
  x: 85,
  y: 90,
  size: 'medium'
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

// Propriété calculée pour contrôler la progression des étapes (mise à jour)
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
    // Étape position QR: Position du QR code doit être définie
    return qrPosition.value !== null;
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

// Méthodes de navigation entre les étapes (mise à jour)
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
    } else if (currentStep.value === 5 || (currentStep.value === 4 && signatureType.value === 'permanent')) {
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
  signatureStatus.value = 'loading';
  processingStep.value = 0;
  
  try {
    // Obtenir les informations de l'utilisateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userInfo.id) {
      console.warn('Utilisateur non connecté ou informations incomplètes');
    }
    
    // Créer les métadonnées utilisateur avec les informations de position du QR code
    const userMetadata = {
      user_id: userInfo.id || '',
      username: userInfo.username || '',
      email: userInfo.email || '',
      full_name: userInfo.fullName || '',
      organization: userInfo.organization || '',
      // Ajouter les informations de position du QR code avec les pages
      qr_position: {
        x: qrPosition.value.x,
        y: qrPosition.value.y,
        size: qrPosition.value.size,
        pages: qrPosition.value.pages, // Ajouter les pages sélectionnées
        positions: qrPosition.value.positions, // Ajouter les positions individuelles par page
        mode: qrPosition.value.mode // Ajouter le mode de positionnement
      }
    };
    
    console.log('Métadonnées QR envoyées au microservice:', userMetadata.qr_position);
    
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
    
    // Préparer les données à envoyer
    const formData = new FormData();
    formData.append('document', selectedFile.value);
    formData.append('certificate', certificateFile.value);
    formData.append('password', certificatePassword.value);
    formData.append('metadata', JSON.stringify(signatureMetadata));
    
    // Ajouter l'ID utilisateur séparément pour faciliter le traitement côté backend
    if (userInfo.id) {
      formData.append('owner_id', userInfo.id);
    }
    
    // Montrer les étapes du processus avec des délais raisonnables
    setTimeout(() => { processingStep.value = 1; }, 1000); // Préparation
    
    // Appel au microservice de signature via l'API Gateway
    const apiUrl = 'https://ppd.camgovca.cm/sign/sign';
    setTimeout(() => { processingStep.value = 2; }, 2000); // Signature
    
    // Configuration de la requête avec axios
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      responseType: 'blob' // Important pour recevoir le fichier PDF signé
    };
    
    // Appel API réel au microservice
    setTimeout(() => { processingStep.value = 3; }, 3000); // Finalisation
    const response = await axios.post(apiUrl, formData, config);
    
    // Traiter la réponse (fichier PDF signé)
    if (response.status === 200) {
      // Extraire le nom du fichier du header Content-Disposition
      const contentDisposition = response.headers['content-disposition'];
      let filename = selectedFile.value.name.replace('.pdf', '_signed.pdf');
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*)\2|[^;\n]*/i);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]*/g, '');
        }
      }
      
      // Extraire l'ID du document signé des en-têtes de réponse
      const documentId = response.headers['x-document-id'];
      if (documentId) {
        console.log('Document signé avec succès, ID:', documentId);
      }
      
      // Créer une URL pour le blob de fichier reçu
      const blob = new Blob([response.data], { type: 'application/pdf' });
      signedDocumentUrl.value = URL.createObjectURL(blob);
      signedDocumentName.value = filename;
      
      // Formater la date de signature
      signatureDate.value = new Date().toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      // Passer à l'étape de téléchargement
      currentStep.value = 5;
      signatureStatus.value = 'success';
    } else {
      throw new Error('Erreur lors de la réception du document signé');
    }
    
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
  };
});

// Nouvelles méthodes pour le positionnement du QR code
function onQrPositionChanged(position) {
  qrPosition.value = position;
}

function onQrPositionConfirmed(position) {
  qrPosition.value = position;
  nextStep(); // Passer automatiquement à l'étape suivante
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

.remove-btn {
  background-color: transparent;
  border: none;
  color: var(--text-muted, #6c757d);
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.2s;
}

.remove-btn:hover {
  color: var(--danger, #dc3545);
  background-color: rgba(220, 53, 69, 0.1);
}

.signature-options {
  margin: 25px 0;
}

.option-group {
  margin-bottom: 25px;
}

.option-label {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--text-color, #333);
}

.option-buttons {
  display: flex;
  gap: 10px;
}

.option-button {
  padding: 10px 15px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  font-weight: 500;
}

.option-button.active {
  background-color: var(--primary-color, #3a86ff);
  color: white;
  border-color: var(--primary-dark, #2970cf);
}

.option-button:hover:not(.active) {
  background-color: rgba(0, 0, 0, 0.05);
}

.signature-methods {
  display: flex;
  gap: 15px;
}

.signature-method {
  width: 100px;
  height: 100px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  gap: 10px;
}

.signature-method i {
  font-size: 1.8rem;
  color: var(--primary-color, #3a86ff);
}

.signature-method.active {
  border-color: var(--primary-color, #3a86ff);
  background-color: rgba(58, 134, 255, 0.1);
}

.signature-method:hover:not(.active) {
  background-color: rgba(0, 0, 0, 0.02);
}

.signature-canvas-container {
  margin-top: 20px;
}

.signature-canvas {
  width: 100%;
  height: 150px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background-color: white;
  margin-bottom: 10px;
  cursor: crosshair;
}

.canvas-actions {
  display: flex;
  justify-content: flex-end;
}

.typed-signature-container {
  margin-top: 20px;
}

.signature-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s;
  margin-bottom: 15px;
}

.signature-input:focus {
  outline: none;
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.2);
}

.signature-preview {
  padding: 15px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background-color: white;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.typed-signature {
  font-family: 'Pacifico', cursive;
  font-size: 1.5rem;
  color: #333;
}

.upload-signature-container {
  margin-top: 20px;
}

.signature-image-preview {
  margin-top: 15px;
  padding: 15px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background-color: white;
  position: relative;
  display: flex;
  justify-content: center;
}

.signature-image-preview img {
  max-width: 100%;
  max-height: 100px;
  object-fit: contain;
}

.signature-image-preview .remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
}

.certificate-selection {
  margin-top: 20px;
  background-color: rgba(0, 0, 0, 0.02);
  padding: 15px;
  border-radius: 8px;
}

.certificate-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.certificate-info i {
  font-size: 1.5rem;
  color: var(--primary-color, #3a86ff);
}

.certificate-select, .position-select {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  font-size: 1rem;
  background-color: white;
  transition: all 0.2s;
}

.certificate-select:focus, .position-select:focus {
  outline: none;
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.2);
}

.signature-position {
  margin-top: 20px;
}

.position-options {
  margin-top: 10px;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  gap: 15px;
}

.action-button {
  padding: 12px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  border: none;
}

.action-button.primary {
  background-color: var(--primary-color, #3a86ff);
  color: white;
}

.action-button.primary:hover:not(:disabled) {
  background-color: var(--primary-dark, #2970cf);
}

.action-button.secondary {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--text-color, #333);
}

.action-button.secondary:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
:global(.dark-theme) .certificate-selection {
  background-color: rgba(255, 255, 255, 0.05);
}

:global(.dark-theme) .option-button,
:global(.dark-theme) .signature-method,
:global(.dark-theme) .signature-canvas,
:global(.dark-theme) .signature-preview,
:global(.dark-theme) .signature-image-preview,
:global(.dark-theme) .certificate-select,
:global(.dark-theme) .position-select,
:global(.dark-theme) .signature-input {
  background-color: rgba(30, 41, 59, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-light, #f8f9fa);
}

:global(.dark-theme) .option-button.active {
  background-color: var(--primary-color, #3a86ff);
  color: white;
}

:global(.dark-theme) .typed-signature {
  color: var(--text-light, #f8f9fa);
}

:global(.dark-theme) .action-button.secondary {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-light, #f8f9fa);
}

:global(.dark-theme) .action-button.secondary:hover {
  background-color: rgba(255, 255, 255, 0.15);
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
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 576px) {
  .option-buttons {
    flex-direction: column;
  }
  
  .section-title {
    font-size: 1.1rem;
  }
}

/* Étape de positionnement du QR code */
.qr-position-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0;
}

.qr-position-container .qr-positioner-container {
  background-color: transparent;
  box-shadow: none;
  padding: 0;
}

/* Animations et transitions */
.step-body {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Responsive pour la nouvelle étape */
@media (max-width: 768px) {
  .qr-position-container {
    padding: 8px;
  }
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
