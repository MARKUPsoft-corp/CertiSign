<template>
  <div class="signer-dashboard">
    <!-- Fond animé avec particules -->
    <div class="particles-container">
      <div v-for="i in 10" :key="i" class="particle" 
        :style="{
          top: particlePositions[(i-1) % particlePositions.length].top,
          left: particlePositions[(i-1) % particlePositions.length].left,
          width: particlePositions[(i-1) % particlePositions.length].size + 'px',
          height: particlePositions[(i-1) % particlePositions.length].size + 'px',
          animationDuration: particlePositions[(i-1) % particlePositions.length].duration + 's',
          animationDelay: particlePositions[(i-1) % particlePositions.length].delay + 's'
        }">
      </div>
    </div>

    <!-- En-tête -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="logo-container">
          <div class="logo-icon-text">
            <img src="@/assets/doc.png" alt="Logo" class="header-logo-img">
            <h1 class="logo-text">
              <span class="text-green">Doc</span>
              <span class="text-red">@uth</span>
              <span class="text-yellow">ANTIC</span>
            </h1>
          </div>
          <span class="role-badge signer top-right-of-logo">Signataire</span>
        </div>
        
        <div class="user-info">
          <div class="organization-info">
            <div class="org-name-wrapper">
              <span class="org-name">{{ organizationName }}</span>
              <span v-if="organizationStatus" 
                    class="status-badge org-status top-right-of-org-name" 
                    :class="`org-status-${organizationStatus.toLowerCase()}`">
                {{ organizationStatus }}
              </span>
            </div>
          </div>
          <div class="user-profile">
            <span class="user-name">{{ userName }}</span>
            <button class="logout-btn" @click="logout">
              <i class="bi bi-box-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- Section de bienvenue -->
      <section class="welcome-section">
        <div class="welcome-content">
          <h2 class="welcome-title">
            <span class="underlined-text">Espace de <span class="highlight-text">signature</span></span>
          </h2>
          <p class="welcome-description">
            Signez vos documents assignés de manière sécurisée
          </p>
        </div>
      </section>

      <!-- Statistiques -->
      <section class="stats-section">
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.thisWeek }}</div>
              <div class="stat-label">Signés cette semaine</div>
            </div>
            <div class="stat-icon success">
              <i class="bi bi-calendar-week"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">Total signé</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-file-earmark-check"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.avgTime }}</div>
              <div class="stat-label">Temps moyen de signature</div>
            </div>
            <div class="stat-icon warning">
              <i class="bi bi-stopwatch"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Actions rapides -->
      <section class="quick-actions">
        <div class="actions-grid">
          <div class="action-card urgent" v-if="urgentDocuments.length > 0">
            <div class="action-icon">
              <i class="bi bi-exclamation-triangle-fill"></i>
            </div>
            <span class="action-title">Urgent</span>
            <span class="action-description">{{ urgentDocuments.length }} documents urgents</span>
            <div class="notification-badge">{{ urgentDocuments.length }}</div>
          </div>
          <button class="action-card" @click="activeSection = 'pending'" :class="{ 'active': activeSection === 'pending' }">
            <div class="action-icon warning">
              <i class="bi bi-file-earmark-plus"></i>
            </div>
            <span class="action-title">À signer</span>
            <span class="action-description">{{ pendingDocuments.length }} documents en attente</span>
          </button>
          <button class="action-card" @click="activeSection = 'signed'" :class="{ 'active': activeSection === 'signed' }">
            <div class="action-icon success">
              <i class="bi bi-file-earmark-check"></i>
            </div>
            <span class="action-title">Signés</span>
            <span class="action-description">{{ signedDocuments.length }} documents signés</span>
          </button>
          <button class="action-card" @click="activeSection = 'history'" :class="{ 'active': activeSection === 'history' }">
            <div class="action-icon primary">
              <i class="bi bi-clock-history"></i>
            </div>
            <span class="action-title">Historique</span>
            <span class="action-description">Voir toutes les signatures</span>
          </button>
        </div>
      </section>

      <!-- Contenu dynamique selon la section active -->
      <section class="content-section" v-if="activeSection">
        <!-- Documents à signer -->
        <div v-if="activeSection === 'pending'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-file-earmark-plus"></i>
            Documents à signer
          </h3>
          
          <div class="documents-list">
            <div v-for="doc in sortedPendingDocuments" :key="doc.id" class="document-item" :class="{ 'urgent': doc.is_urgent }">
              <div class="doc-info">
                <i class="bi" :class="doc.is_urgent ? 'bi-exclamation-triangle-fill' : 'bi-file-earmark'"></i>
                <div class="doc-details">
                  <div class="doc-header">
                    <span class="doc-name">{{ doc.document_name || 'Document sans nom' }}</span>
                    <span v-if="doc.is_urgent" class="urgent-tag">URGENT</span>
                  </div>
                  <span class="doc-meta">
                    Préparé par {{ doc.preparedBy || doc.collaborator_username || 'Collaborateur' }} • 
                    {{ formatDate(doc.assignedAt || doc.created_at) }}
                  </span>
                  <div class="doc-priority">
                    <span class="time-elapsed" :class="{ 'urgent': doc.is_urgent }">
                      {{ getTimeElapsed(doc.assignedAt || doc.created_at) }} d'attente
                    </span>
                  </div>
                </div>
              </div>
              <div class="doc-actions">
                <button class="btn-primary" @click="signDocument(doc)">
                  <i class="bi bi-pen"></i>
                  Signer maintenant
                </button>
                <button class="btn-icon" title="Prévisualiser" @click="previewDocument(doc)">
                  <i class="bi bi-eye"></i>
                </button>
              </div>
            </div>
            <div v-if="pendingDocuments.length === 0" class="empty-state">
              <i class="bi bi-file-earmark-check"></i>
              <p>Aucun document à signer</p>
              <span class="empty-subtitle">Parfait ! Tous vos documents sont à jour.</span>
            </div>
          </div>
        </div>

        <!-- Documents signés -->
        <div v-if="activeSection === 'signed'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-file-earmark-check"></i>
            Documents récemment signés
          </h3>
          
          <div class="documents-list">
            <div v-for="doc in signedDocuments" :key="doc.id" class="document-item">
              <div class="doc-info">
                <i class="bi bi-file-earmark-check"></i>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.document_name || doc.name || 'Document sans nom' }}</span>
                  <span class="doc-meta">Signé le {{ formatDate(doc.signedAt || doc.updated_at) }}</span>
                  <div class="signer-info" v-if="doc.organization_name || doc.signer_role">
                    <i class="bi bi-building"></i>
                    <span>{{ doc.organization_name }}{{ doc.signer_role ? ` - ${doc.signer_role}` : '' }}</span>
                  </div>
                </div>
              </div>
              <div class="doc-status">
                <span class="status-badge signed">Signé</span>
                <div class="doc-actions">
                  <button class="btn-icon" title="Télécharger" @click="downloadSignedDocument(doc)">
                    <i class="bi bi-download"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="signedDocuments.length === 0" class="empty-state">
              <i class="bi bi-file-earmark"></i>
              <p>Aucun document signé récemment</p>
            </div>
          </div>
        </div>

        <!-- Historique -->
        <div v-if="activeSection === 'history'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-clock-history"></i>
            Historique des signatures
          </h3>
          
          <div class="history-timeline">
            <div v-for="entry in signatureHistory" :key="entry.id" class="timeline-item">
              <div class="timeline-marker" :class="entry.status">
                <i class="bi" :class="getStatusIcon(entry.status)"></i>
              </div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-title">{{ entry.action }}</span>
                  <span class="timeline-date">{{ formatDateTime(entry.timestamp) }}</span>
                </div>
                <div class="timeline-details">
                  <span class="document-name">{{ entry.documentName }}</span>
                  <span class="timeline-description">{{ entry.description }}</span>
                </div>
              </div>
            </div>
            <div v-if="signatureHistory.length === 0" class="empty-state">
              <i class="bi bi-clock"></i>
              <p>Aucun historique disponible</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Section par défaut si aucune section active -->
      <section v-if="!activeSection" class="default-content">
        <div class="welcome-card">
          <div class="welcome-icon">
            <i class="bi bi-pen-fill"></i>
          </div>
          <h3>Prêt à signer ?</h3>
          <p>Consultez vos documents en attente de signature</p>
          <button class="btn-primary" @click="activeSection = 'pending'">
            <i class="bi bi-file-earmark-plus"></i>
            Voir les documents
          </button>
        </div>
      </section>
    </main>

    <!-- Popup de signature -->
    <div class="signature-modal" v-if="showSignatureModal">
      <div class="signature-modal-overlay" @click="closeSignatureModal"></div>
      <div class="signature-modal-content">
        <div class="signature-modal-header">
          <h3>
            <i class="bi bi-pen-fill"></i>
            Signature de document
          </h3>
          <button class="close-btn" @click="closeSignatureModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <div class="signature-modal-body">
          <div class="document-preview">
            <div class="document-name">{{ currentDocument?.document_name || 'Document' }}</div>
            <div class="document-info">
              <i class="bi bi-file-earmark-pdf"></i>
              <span>{{ currentDocument?.document_name || 'Document sans nom' }}</span>
            </div>
          </div>
          
          <div class="form-section">
            <div class="form-title">Votre certificat de signature</div>
            <div class="form-group">
              <label for="certificate">Certificat PFX</label>
              <div 
                class="dropzone"
                :class="{ 'active': isDragging, 'has-file': certificateFile }"
                @dragenter.prevent="isDragging = true"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleDrop"
                @click="$refs.certificateInput.click()"
              >
                <input 
                  type="file" 
                  id="certificate" 
                  ref="certificateInput" 
                  @change="handleCertificateChange" 
                  accept=".pfx,.p12" 
                  class="hidden-input" 
                />
                
                <div v-if="!certificateFile" class="dropzone-placeholder">
                  <i class="bi bi-file-earmark-lock2"></i>
                  <div class="dropzone-text">
                    <span class="main-text">Glissez votre certificat ici</span>
                    <span class="sub-text">ou cliquez pour parcourir</span>
                  </div>
                </div>
                
                <div v-else class="dropzone-file">
                  <i class="bi bi-file-earmark-check"></i>
                  <div class="file-info">
                    <span class="file-name">{{ certificateFile.name }}</span>
                    <span class="file-size">{{ formatFileSize(certificateFile.size) }}</span>
                  </div>
                  <button class="remove-file" @click.stop="removeCertificate">
                    <i class="bi bi-x-circle"></i>
                  </button>
                </div>
              </div>
              <small>Sélectionnez votre certificat de signature (.pfx ou .p12)</small>
            </div>
            
            <div class="form-group">
              <label for="password">Mot de passe du certificat</label>
              <div class="password-input-container">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  id="password" 
                  v-model="certificatePassword"
                  placeholder="Entrez le mot de passe"
                />
                <button class="toggle-password" @click="togglePasswordVisibility">
                  <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="signature-modal-footer">
          <div class="signature-status" v-if="signatureStatus">
            <i :class="signatureStatus.icon"></i>
            <span :class="signatureStatus.class">{{ signatureStatus.message }}</span>
          </div>
          <div class="button-group">
            <button class="btn-cancel" @click="closeSignatureModal">Annuler</button>
            <button 
              class="btn-sign" 
              @click="submitSignature" 
              :disabled="isSigningInProgress || !certificateFile || !certificatePassword"
            >
              <i class="bi" :class="isSigningInProgress ? 'bi-hourglass-split' : 'bi-pen-fill'"></i>
              {{ isSigningInProgress ? 'Signature en cours...' : 'Signer le document' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/AuthService';
import axios from 'axios';

const router = useRouter();

// État réactif
const activeSection = ref('');
const userName = ref('');
const organizationName = ref('');
const organizationStatus = ref('');

// État pour la popup de signature
const showSignatureModal = ref(false);
const currentDocument = ref(null);
const certificateFile = ref(null);
const certificatePassword = ref('');
const showPassword = ref(false);
const isSigningInProgress = ref(false);
const signatureStatus = ref(null);
const isDragging = ref(false);

// Statistiques
const stats = ref({
  thisWeek: 0,
  total: 0,
  avgTime: '0j'
});

// Documents à signer
const pendingDocuments = ref([]);

// Documents signés
const signedDocuments = ref([]);

// Historique des signatures
const signatureHistory = ref([
  {
    id: 1,
    action: 'Document signé',
    documentName: 'Convention collective 2024.pdf',
    description: 'Signature électronique appliquée avec succès',
    timestamp: new Date('2024-01-11T14:30:00'),
    status: 'signed'
  },
  {
    id: 2,
    action: 'Document reçu',
    documentName: 'Rapport annuel 2023.pdf',
    description: 'Assigné pour signature par Jean Dupont',
    timestamp: new Date('2024-01-12T09:15:00'),
    status: 'received'
  },
  {
    id: 3,
    action: 'Document signé',
    documentName: 'Accord de partenariat.pdf',
    description: 'Signature électronique appliquée avec succès',
    timestamp: new Date('2024-01-10T16:45:00'),
    status: 'signed'
  }
]);

// Watcher pour rafraîchir les données quand la section active change
watch(activeSection, (newSection) => {
  console.log('Section active changée vers:', newSection);
  
  if (newSection === 'pending') {
    fetchPendingDocuments();
  } else if (newSection === 'signed') {
    fetchSignedDocuments();
  } else if (newSection === 'history') {
    // L'historique est statique pour l'instant
    console.log('Section historique activée');
  }
});

// Computed
const urgentDocuments = computed(() => {
  return pendingDocuments.value.filter(doc => doc.is_urgent);
});

const sortedPendingDocuments = computed(() => {
  return [...pendingDocuments.value].sort((a, b) => {
    if (a.is_urgent && !b.is_urgent) return -1;
    if (!a.is_urgent && b.is_urgent) return 1;
    return new Date(b.assignedAt) - new Date(a.assignedAt);
  });
});

// Positionnement des particules
const particlePositions = Array.from({ length: 10 }, () => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 5 + 2,
  duration: Math.random() * 30 + 25,
  delay: Math.random() * 10
}));

// Méthodes
function formatDate(dateStr) {
  if (!dateStr) return 'Date inconnue';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return 'Date invalide';
    }
    
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(date);
  } catch (error) {
    console.error('Erreur de formatage de date:', error);
    return 'Date invalide';
  }
}

function formatDateTime(dateStr) {
  if (!dateStr) return 'Date inconnue';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return 'Date invalide';
    }
    
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  } catch (error) {
    console.error('Erreur de formatage de date:', error);
    return 'Date invalide';
  }
}

function getTimeElapsed(dateStr) {
  if (!dateStr) return '0j';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return '0j';
    }
    
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (days === 0) {
      return `${hours}h`;
    }
    return `${days}j`;
  } catch (error) {
    console.error('Erreur de calcul de temps écoulé:', error);
    return '0j';
  }
}

function getStatusIcon(status) {
  const icons = {
    'signed': 'bi-file-earmark-check',
    'received': 'bi-file-earmark-plus',
    'pending': 'bi-hourglass-split'
  };
  return icons[status] || 'bi-circle';
}

// Méthodes pour la signature
function signDocument(doc) {
  console.log('Ouvrir la popup de signature pour:', doc.document_name);
  currentDocument.value = doc;
  showSignatureModal.value = true;
  resetSignatureForm();
}

function closeSignatureModal() {
  showSignatureModal.value = false;
  resetSignatureForm();
}

function resetSignatureForm() {
  certificateFile.value = null;
  certificatePassword.value = '';
  showPassword.value = false;
  isSigningInProgress.value = false;
  signatureStatus.value = null;
}

function handleCertificateChange(event) {
  const files = event.target.files;
  if (files.length > 0) {
    certificateFile.value = files[0];
  } else {
    certificateFile.value = null;
  }
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
}

async function submitSignature() {
  if (!certificateFile.value || !certificatePassword.value) {
    signatureStatus.value = {
      message: 'Veuillez fournir votre certificat et mot de passe',
      icon: 'bi bi-exclamation-triangle',
      class: 'error'
    };
    return;
  }

  try {
    isSigningInProgress.value = true;
    signatureStatus.value = {
      message: 'Signature en cours...',
      icon: 'bi bi-hourglass-split',
      class: 'pending'
    };

    // Vérifier si le document a un ID
    if (!currentDocument.value.id) {
      throw new Error('ID du document manquant');
    }

    // Récupérer les détails complets du document depuis l'API
    const token = localStorage.getItem('token');
    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      throw new Error('ID d\'organisation manquant');
    }
    
    console.log('Récupération des détails du document ID:', currentDocument.value.id);
    
    // Récupérer les informations complètes du document depuis l'API
    const documentDetailsResponse = await axios.get(
      `https://192.168.4.131/api/documents/qr-positions/${currentDocument.value.id}/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          organization_id: organizationId  // Ajouter l'ID de l'organisation
        }
      }
    );
    
    // Vérifier si la requête a réussi
    if (!documentDetailsResponse.data) {
      throw new Error('Impossible de récupérer les détails du document');
    }
    
    const documentDetails = documentDetailsResponse.data;
    console.log('Détails du document récupérés:', documentDetails);
    
    // Extraire les informations de positionnement du QR code dans le format attendu par le microservice
    // Le microservice attend:
    // {x: %, y: %, size: 'small'|'medium'|'large', pages: 'all'|[1,2,3],
    //  positions: {page_num: {x: %, y: %}, ...}, mode: 'all'|'current'|'custom'|'individual'}
    
    // Vérifier et convertir les valeurs numériques
    const xPosition = parseFloat(documentDetails.qr_x_position);
    const yPosition = parseFloat(documentDetails.qr_y_position);
    
    // Vérifier la taille du QR code (valeur par défaut si non conforme)
    const validSizes = ['small', 'medium', 'large'];
    const qrSize = validSizes.includes(documentDetails.qr_size) ? documentDetails.qr_size : 'medium';
    
    // Vérifier le mode de positionnement
    const validModes = ['all', 'current', 'custom', 'individual'];
    const positionMode = validModes.includes(documentDetails.qr_mode) ? documentDetails.qr_mode : 'all';
    
    // Convertir les positions individuelles en structure correcte si nécessaire
    let positions = {};
    if (documentDetails.qr_positions && typeof documentDetails.qr_positions === 'object') {
      // S'assurer que les clés sont des chaînes (numéros de page)
      positions = documentDetails.qr_positions;
    }
    
    // Traiter correctement le paramètre pages
    let pagesValue = documentDetails.qr_pages || 'all';
    // Si pages est une chaîne mais pas "all", essayer de la convertir en liste d'entiers
    if (pagesValue !== 'all' && typeof pagesValue === 'string') {
      try {
        // Pour un nombre unique, créer une liste avec ce nombre
        if (/^\d+$/.test(pagesValue.trim())) {
          pagesValue = [parseInt(pagesValue.trim(), 10)];
          console.log('Pages converties en liste d\'entiers:', pagesValue);
        }
        // Si c'est une chaîne JSON représentant un tableau, la parser
        else if (pagesValue.startsWith('[') && pagesValue.endsWith(']')) {
          pagesValue = JSON.parse(pagesValue);
          console.log('Pages parsées depuis JSON:', pagesValue);
        }
      } catch (error) {
        console.error('Erreur lors de la conversion des pages:', error);
        pagesValue = 'all'; // Valeur par défaut en cas d'erreur
      }
    }
    
    // Créer l'objet de position avec les valeurs vérifiées
    let qrPosition = {
      x: isNaN(xPosition) ? 85 : xPosition, // Position X par défaut à 85% si invalide
      y: isNaN(yPosition) ? 10 : yPosition, // Position Y par défaut à 10% si invalide
      size: qrSize,
      pages: pagesValue,
      positions: positions,
      mode: positionMode
    };
    
    console.log('Informations de positionnement du QR code formatées:', qrPosition);

    // ========== RÉCUPÉRATION DES INFORMATIONS DE SIGNATURE ==========
    // Récupérer et formater les informations de signature depuis DocumentQRPosition
    let signaturePosition = null;
    
    // Vérifier si le document a des informations de signature
    if (documentDetails.signature_image || documentDetails.signature_positions) {
      console.log('Informations de signature trouvées dans le document:', {
        has_image: !!documentDetails.signature_image,
        has_positions: !!documentDetails.signature_positions,
        signature_size: documentDetails.signature_size
      });
      
      // Construire l'objet signature_position au format attendu par le microservice
      signaturePosition = {};
      
      // Ajouter l'image de signature si disponible
      if (documentDetails.signature_image) {
        // L'image est stockée comme un fichier dans le backend Django
        // On doit la récupérer et la convertir en base64 pour le microservice
        try {
          let imageUrl = documentDetails.signature_image;
          // Construire l'URL absolue si nécessaire
          if (imageUrl.startsWith('/')) {
            imageUrl = `https://192.168.4.131${imageUrl}`;
          } else if (!imageUrl.startsWith('https')) {
            imageUrl = `https://192.168.4.131/${imageUrl}`;
          }
          
          console.log('Récupération de l\'image de signature depuis:', imageUrl);
          
          // Télécharger l'image de signature
          const imageResponse = await axios.get(imageUrl, {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            responseType: 'blob'
          });
          
          // Convertir l'image en base64
          const imageBlob = imageResponse.data;
          const imageBase64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.readAsDataURL(imageBlob);
          });
          
          signaturePosition.signature_image = imageBase64;
          console.log('Image de signature convertie en base64:', imageBase64.substring(0, 50) + '...');
          
        } catch (imageError) {
          console.error('Erreur lors de la récupération de l\'image de signature:', imageError);
          console.log('Signature sera appliquée sans image personnalisée');
        }
      }
      
      // Ajouter les positions de signature si disponibles
      if (documentDetails.signature_positions) {
        try {
          let positions = documentDetails.signature_positions;
          
          // Parser si c'est une chaîne JSON
          if (typeof positions === 'string') {
            positions = JSON.parse(positions);
          }
          
          // Convertir le format objet {page_num: {x, y}} vers tableau [{page, x, y, width, height}]
          const signaturePositionsArray = [];
          
          if (positions && typeof positions === 'object') {
            Object.entries(positions).forEach(([pageNum, position]) => {
              if (position && typeof position === 'object' && position.x !== undefined && position.y !== undefined) {
                signaturePositionsArray.push({
                  page: parseInt(pageNum),
                  x: position.x,
                  y: position.y,
                  width: 20, // Largeur par défaut
                  height: 10 // Hauteur par défaut
                });
              }
            });
          }
          
          signaturePosition.positions = signaturePositionsArray;
          console.log('Positions de signature formatées:', signaturePositionsArray);
          
        } catch (positionError) {
          console.error('Erreur lors du parsing des positions de signature:', positionError);
          signaturePosition.positions = [];
        }
      } else {
        signaturePosition.positions = [];
      }
      
      console.log('Informations de signature finales:', signaturePosition);
    } else {
      console.log('Aucune information de signature trouvée dans le document');
    }
    
    // Vérifier si le document a une URL de fichier
    if (!documentDetails.document_file) {
      throw new Error('Aucun fichier disponible pour ce document');
    }
    
    // Construire l'URL absolue du document
    let fileUrl = documentDetails.document_file;
    // Si l'URL commence par un slash, on le traite comme un chemin relatif au backend
    if (fileUrl.startsWith('/')) {
      fileUrl = `https://192.168.4.131${fileUrl}`;
    } else if (!fileUrl.startsWith('https')) {
      // Si l'URL ne commence pas par https, on ajoute le préfixe
      fileUrl = `https://192.168.4.131/${fileUrl}`;
    }
    
    console.log('Récupération du document à l\'URL:', fileUrl);
    
    // Télécharger le document à partir de son URL
    const response = await axios.get(fileUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      responseType: 'blob'
    });
    
    // Créer un objet File à partir du Blob pour l'envoi
    const documentFile = new File(
      [response.data], 
      documentDetails.document_name || 'document.pdf', 
      { type: 'application/pdf' }
    );

    // Préparer les métadonnées avec la position du QR code et les informations de signature
    const metadataObject = {
      qr_position: qrPosition,
      document_id: documentDetails.id,
      document_title: documentDetails.document_name,
      organization_id: organizationId,  // Ajouter l'ID de l'organisation aux métadonnées
      organization_name: currentUser?.organization?.name || 'Organisation inconnue',  // Nom de l'organisation
      signer_role: currentUser?.position || currentUser?.role || 'Signataire',  // Rôle du signataire
      signer_name: currentUser?.first_name && currentUser?.last_name ? 
        `${currentUser.first_name} ${currentUser.last_name}` : 
        currentUser?.username || 'Signataire'  // Nom complet du signataire
    };
    
    // Ajouter les informations de signature si disponibles (même format que SignSimple.vue)
    if (signaturePosition) {
      metadataObject.signature_position = signaturePosition;
      console.log('Informations de signature ajoutées aux métadonnées:', {
        has_image: !!signaturePosition.signature_image,
        positions_count: signaturePosition.positions?.length || 0,
        positions_detail: signaturePosition.positions
      });
    }
    
    const metadata = JSON.stringify(metadataObject);

    // Afficher les métadonnées qui seront envoyées pour vérification
    console.log('Métadonnées complètes envoyées au microservice de signature:', JSON.parse(metadata));

    // Créer le FormData pour l'envoi au microservice de signature
    const formData = new FormData();
    formData.append('certificate', certificateFile.value);
    formData.append('password', certificatePassword.value);
    formData.append('document', documentFile);
    formData.append('metadata', metadata);
    formData.append('owner_id', currentUser.id);
    formData.append('organization_id', organizationId);
    formData.append('organization_name', currentUser?.organization?.name || 'Organisation inconnue');
    formData.append('signer_role', currentUser?.position || currentUser?.role || 'Signataire');
    formData.append('signer_name', currentUser?.first_name && currentUser?.last_name ? 
      `${currentUser.first_name} ${currentUser.last_name}` : 
      currentUser?.username || 'Signataire');
    
    // Envoyer la requête au microservice de signature via l'API gateway
    const signResponse = await axios.post(
      'https://192.168.4.131/sign/sign',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        responseType: 'blob'
      }
    );

    // Traiter la réponse
    if (signResponse.status === 200) {
      // Extraire le nom du fichier du header Content-Disposition s'il est présent
      const contentDisposition = signResponse.headers['content-disposition'];
      let filename = `${documentDetails.document_name.replace('.pdf', '')}_signé.pdf`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*)\2|[^;\n]*/i);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]*/g, '');
        }
      }
      
      console.log('Téléchargement du document signé:', filename);
      
      // Créer le blob PDF et déclencher le téléchargement
      const blob = new Blob([signResponse.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Libérer l'URL objet
      window.URL.revokeObjectURL(url);
      
      console.log('Document téléchargé, mise à jour du statut...');
      
      try {
        // Mettre à jour le statut du document dans la base de données
        await updateDocumentStatus(currentDocument.value.id, 'signed');
        console.log('Statut du document mis à jour vers "signed"');
        
        // Déplacer le document de la liste "en attente" vers "signés"
        const signedDoc = {
          ...currentDocument.value,
          status: 'signed',
          signedAt: new Date().toISOString(),
          signedBy: AuthService.getCurrentUser()?.username || 'Signataire'
        };
        
        // Ajouter à la liste des documents signés
        signedDocuments.value.unshift(signedDoc);
        
        // Retirer de la liste des documents en attente
        pendingDocuments.value = pendingDocuments.value.filter(doc => doc.id !== currentDocument.value.id);
        
        console.log('Document déplacé vers la section signés');
        
        // Mettre à jour les statistiques
        stats.value.thisWeek += 1;
        stats.value.total += 1;
        
      } catch (statusUpdateError) {
        console.error('Erreur lors de la mise à jour du statut:', statusUpdateError);
        // Ne pas faire échouer toute l'opération si la mise à jour du statut échoue
        signatureStatus.value = {
          message: 'Document signé, mais erreur de synchronisation. Actualisez la page.',
          icon: 'bi bi-exclamation-triangle',
          class: 'warning'
        };
      }
      
      // Mettre à jour le statut d'affichage
      signatureStatus.value = {
        message: 'Document signé avec succès',
        icon: 'bi bi-check-circle',
        class: 'success'
      };
      
      // Fermer la popup après un délai
      setTimeout(() => {
        closeSignatureModal();
      }, 2000);
    } else {
      throw new Error('Erreur lors de la signature');
    }
  } catch (error) {
    console.error('Erreur lors de la signature:', error);
    signatureStatus.value = {
      message: `Erreur: ${error.response?.data?.detail || error.message || 'Erreur inconnue'}`,
      icon: 'bi bi-x-circle',
      class: 'error'
    };
  } finally {
    isSigningInProgress.value = false;
  }
}

function previewDocument(doc) {
  console.log('Prévisualiser le document:', doc.document_name);
  
  // Si le document a une URL de fichier, ouvrir dans un nouvel onglet
  if (doc.document_file) {
    try {
      // Construire l'URL absolue correcte sans double slash
      let fileUrl = doc.document_file;
      
      // Si l'URL commence par un slash, on le traite comme un chemin relatif au backend
      if (fileUrl.startsWith('/')) {
        fileUrl = `https://192.168.4.131${fileUrl}`;
      } else if (!fileUrl.startsWith('https')) {
        // Si l'URL ne commence pas par https, on ajoute le préfixe
        fileUrl = `https://192.168.4.131/${fileUrl}`;
      }
      
      // Ajouter l'ID de l'organisation comme paramètre de requête
      const currentUser = AuthService.getCurrentUser();
      const organizationId = currentUser?.organization?.id;
      
      if (organizationId) {
        // Ajouter l'ID de l'organisation comme paramètre de requête
        const separator = fileUrl.includes('?') ? '&' : '?';
        fileUrl += `${separator}organization_id=${organizationId}`;
      }
      
      console.log('Ouverture du document à l\'URL:', fileUrl);
      window.open(fileUrl, '_blank');
    } catch (error) {
      console.error('Erreur lors de l\'ouverture du document:', error);
      alert('Impossible d\'ouvrir le document. Veuillez réessayer plus tard.');
    }
  } else {
    console.error('Aucun fichier disponible pour ce document');
    alert('Aucun fichier n\'est disponible pour ce document.');
  }
}

function logout() {
  AuthService.logout();
  router.push('/login');
}

async function downloadSignedDocument(doc) {
  console.log('Télécharger le document signé:', doc.document_name || doc.name);
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token d\'authentification manquant');
      return;
    }

    // Récupérer l'ID de l'organisation actuelle
    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    // Utiliser l'endpoint de téléchargement de DocumentSignature
    const downloadUrl = `https://192.168.4.131/api/documents/signatures/${doc.document_id || doc.id}/download/`;
    
    const response = await axios.get(downloadUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId
      },
      responseType: 'blob'
    });

    // Créer le blob et déclencher le téléchargement
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Déterminer le nom du fichier
    let filename = doc.document_name || doc.name || doc.title || 'document_signe.pdf';
    if (!filename.endsWith('.pdf')) {
      filename += '.pdf';
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Libérer l'URL objet
    window.URL.revokeObjectURL(url);
    
    console.log('Document signé téléchargé avec succès');
  } catch (error) {
    console.error('Erreur lors du téléchargement du document signé:', error);
    alert('Erreur lors du téléchargement du document. Veuillez réessayer.');
  }
}

function handleDrop(event) {
  isDragging.value = false;
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (file.name.endsWith('.pfx') || file.name.endsWith('.p12')) {
      certificateFile.value = file;
    } else {
      signatureStatus.value = {
        message: 'Le fichier doit être un certificat (.pfx ou .p12)',
        icon: 'bi bi-exclamation-triangle',
        class: 'error'
      };
    }
  }
}

function removeCertificate(event) {
  event.stopPropagation();
  certificateFile.value = null;
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

// Initialisation
onMounted(() => {
  document.title = 'Signataire - Doc@uthANTIC';
  fetchUserData();
  fetchDocuments();
  initStats();
  
  // Activer la section "pending" par défaut
  activeSection.value = 'pending';
});

// Méthodes supplémentaires
async function fetchPendingDocuments() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token d\'authentification manquant');
      return;
    }

    // Récupérer l'ID de l'organisation actuelle
    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    const config = {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId
      }
    };  

    const response = await axios.get('https://192.168.4.131/api/documents/qr-positions/pending_for_signer/', config);
    if (response.data) {
      pendingDocuments.value = response.data.pending_documents || [];
      
      // Mettre à jour les statistiques
      if (response.data.stats) {
        stats.value.thisWeek = response.data.stats.thisWeek || 0;
        stats.value.total = response.data.stats.total || 0;
        stats.value.avgTime = response.data.stats.avgTime || '0j';
      }
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des documents:', error);
  }
}

// Fonction pour récupérer les documents signés
async function fetchSignedDocuments() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token d\'authentification manquant');
      return;
    }

    // Récupérer l'ID de l'organisation actuelle
    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    const config = {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId
      } 
    };  

    // Récupérer les documents signés depuis l'API DocumentSignature
    const response = await axios.get('https://192.168.4.131/api/documents/signatures/', config);
    if (response.data && response.data.results) {
      signedDocuments.value = response.data.results.map(doc => ({
        ...doc,
        // Mapper les champs pour compatibilité avec l'interface existante
        id: doc.document_id,
        document_name: doc.title,
        name: doc.title,
        signedAt: doc.created_at,
        signedBy: doc.owner_username || 'Signataire',
        organization_name: doc.organization_name || 'Organisation',
        signer_role: doc.signer_role || 'Signataire'
      }));
      
      console.log('Documents signés récupérés depuis DocumentSignature:', signedDocuments.value);
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des documents signés:', error);
  }
}

// Fonction pour mettre à jour le statut d'un document
async function updateDocumentStatus(documentId, newStatus) {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token d\'authentification manquant');
    }

    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      throw new Error('ID d\'organisation manquant');
    }

    // Utiliser FormData au lieu de JSON pour l'API Django
    const formData = new FormData();
    formData.append('status', newStatus);
    
    const response = await axios.patch(
      `https://192.168.4.131/api/documents/qr-positions/${documentId}/`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        params: {
          organization_id: organizationId
        }
      }
    );

    console.log('Statut du document mis à jour:', response.data);
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la mise à jour du statut:', error);
    throw error;
  }
}

// Fonction pour récupérer tous les documents (en attente et signés)
async function fetchDocuments() {
  console.log('Récupération de tous les documents...');
  await Promise.all([
    fetchPendingDocuments(),
    fetchSignedDocuments()
  ]);
}

// Fonction pour récupérer les données de l'utilisateur
function fetchUserData() {
  const user = AuthService.getCurrentUser();
  if (user) {
    userName.value = user.username || 'Utilisateur';
    
    if (user.organization && typeof user.organization === 'object') {
      organizationName.value = user.organization.name || 'Organisation Inconnue';
      organizationStatus.value = user.organization.status || 'inconnu';
    } else {
      organizationName.value = 'N/A';
      organizationStatus.value = 'N/A';
      console.warn("Les informations de l'organisation ne sont pas disponibles ou dans un format incorrect.");
    }
  } else {
    router.push('/login');
  }
}

// Fonction pour initialiser les statistiques
function initStats() {
  // Les statistiques sont mises à jour automatiquement 
  // via fetchPendingDocuments qui récupère les stats du backend
  console.log('Initialisation des statistiques...');
}
</script>

<style scoped>
/* Styles généraux */
.signer-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, 
    var(--bg-color, #f8f9fa) 0%, 
    rgba(255, 149, 0, 0.05) 50%, 
    var(--bg-color, #f8f9fa) 100%);
  color: var(--text-color, #333);
  position: relative;
}

/* Animation de particules */
.particles-container {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 30s infinite linear;
  background: #ff9500;
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.15;
  }
  90% {
    opacity: 0.15;
  }
  100% {
    transform: translateY(-100vh) translateX(30px) rotate(360deg);
    opacity: 0;
  }
}

/* En-tête */
.dashboard-header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 149, 0, 0.2);
  padding: 1.25rem 2.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 15px rgba(255, 149, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  padding-right: 0;
  margin-right: 2rem;
}

.logo-icon-text {
  display: flex;
  align-items: center;
}

.header-logo-img {
  width: 40px;
  height: auto;
  margin-right: 10px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  font-family: "Motoya Maru Std-w6", Arial, sans-serif;
}

.text-green {
  color: #00a651; /* Vert */
}

.text-red {
  color: #e74c3c; /* Rouge */
}

.text-yellow {
  color: #f1c40f; /* Jaune */
}

.logo-container:hover .logo-icon {
  transform: rotate(-10deg);
}

.role-badge.signer.top-right-of-logo {
  position: relative;
  top: 0;
  right: 0;
  font-size: 0.8rem;
  padding: 0.25rem 0.55rem;
  line-height: 1.1;
  border-radius: 0.75rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(45deg, #ff9500, #ffb347);
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  text-transform: uppercase;
  margin-left: 0.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transform: translateX(-40px);
}

.organization-info {
  display: flex;
  align-items: center;
}

.org-name-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  padding-right: 0;
}

.org-name {
  font-weight: 700;
  color: #ff9500;
  font-size: 1.9rem;
  line-height: 1.2;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.05);
  background: linear-gradient(45deg, #ff9500, #ffb347);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.status-badge.org-status.top-right-of-org-name {
  position: relative;
  top: 0;
  right: 0;
  transform: none;
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 0.75rem;
  font-weight: 700;
  line-height: 1.1;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  text-transform: uppercase;
  margin-left: 0.5rem;
}

.status-badge.org-status {
  font-size: 0.65rem;
  padding: 0.2rem 0.55rem;
  border-radius: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  line-height: 1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.status-badge.org-status-active {
  background: linear-gradient(45deg, #28a745, #5bc85a);
  color: white;
}

.status-badge.org-status-pending {
  background: linear-gradient(45deg, #ffc107, #ffd04e);
  color: #333;
}

.status-badge.org-status-inactive, 
.status-badge.org-status-suspended {
  background: linear-gradient(45deg, #6c757d, #9a9fa3);
  color: white;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
}

.user-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #4A4A4A;
  padding: 0.4rem 0.8rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 1.5rem;
  box-shadow: 0 2px 10px rgba(255, 149, 0, 0.12);
  border: 1px solid rgba(255, 149, 0, 0.15);
  backdrop-filter: blur(4px);
  position: relative;
  padding-left: 2rem;
  transition: all 0.3s ease;
}

.user-name::before {
  content: "\F4DA";
  font-family: "bootstrap-icons";
  position: absolute;
  left: 0.7rem;
  font-size: 0.9rem;
  color: #ff9500;
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 149, 0, 0.2);
}

.logout-btn {
  background: transparent;
  border: 2px solid #ff9500;
  color: #ff9500;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #ff9500;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(255, 149, 0, 0.3);
}

/* Popup de signature */
.signature-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.signature-modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(3px);
}

.signature-modal-content {
  position: relative;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalAppear 0.3s ease-out;
  border: 1px solid rgba(255, 149, 0, 0.2);
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.signature-modal-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #ff9500, #ffb347);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.signature-modal-header h3 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.signature-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(85vh - 150px);
}

.document-preview {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  border: 1px dashed rgba(0, 0, 0, 0.1);
}

.document-name {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: #333;
}

.document-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.document-info i {
  color: #ff9500;
  font-size: 1.5rem;
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-title {
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.1rem;
  border-bottom: 2px solid rgba(255, 149, 0, 0.1);
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-group small {
  display: block;
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.8rem;
}

.dropzone {
  border: 2px dashed #ddd;
  border-radius: 0.5rem;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 120px;
  background-color: rgba(255, 255, 255, 0.5);
}

.dropzone.active {
  border-color: #ff9500;
  background-color: rgba(255, 149, 0, 0.05);
  transform: scale(1.02);
}

.dropzone.has-file {
  border-color: #28a745;
  background-color: rgba(40, 167, 69, 0.05);
}

.dropzone-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.dropzone-placeholder i {
  font-size: 2.5rem;
  color: #aaa;
}

.dropzone-text {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.main-text {
  font-weight: 600;
  color: #555;
}

.sub-text {
  font-size: 0.9rem;
  color: #888;
}

.dropzone-file {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.dropzone-file i {
  font-size: 2rem;
  color: #28a745;
}

.file-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.file-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #333;
  word-break: break-all;
}

.file-size {
  font-size: 0.8rem;
  color: #6c757d;
}

.remove-file {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-file:hover {
  background-color: rgba(220, 53, 69, 0.1);
  transform: scale(1.1);
}

.hidden-input {
  display: none;
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-container input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #777;
  cursor: pointer;
}

.signature-modal-footer {
  padding: 1.25rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.signature-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.signature-status.error {
  color: #dc3545;
}

.signature-status.success {
  color: #28a745;
}

.signature-status.pending {
  color: #6c757d;
}

.button-group {
  display: flex;
  gap: 1rem;
}

.btn-cancel {
  background: none;
  border: 1px solid #ddd;
  color: #555;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: #f0f0f0;
}

.btn-sign {
  background: linear-gradient(45deg, #ff9500, #ffb347);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-sign:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 149, 0, 0.3);
}

.btn-sign:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background: linear-gradient(45deg, #ccc, #ddd);
}

/* Contenu principal */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

/* Section de bienvenue */
.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--text-color, #333);
}

.underlined-text {
  position: relative;
  display: inline-block;
}

.underlined-text::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -10px;
  height: 4px;
  width: 100%;
  background: linear-gradient(90deg, #ff9500, #ffb347, #ff9500);
  background-size: 200% 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(255, 149, 0, 0.3);
  animation: gradientMove 3s ease infinite;
}

@keyframes gradientMove {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.highlight-text {
  background: linear-gradient(45deg, #ff9500, #ffb347);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-description {
  font-size: 1.1rem;
  color: var(--text-muted, #6c757d);
  max-width: 600px;
  margin: 0 auto;
}

/* Actions rapides */
.quick-actions {
  margin-bottom: 3rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid transparent;
  border-radius: 1rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  position: relative;
}

.action-card:hover, .action-card.active {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.action-card.urgent {
  border-color: #dc3545;
  background: rgba(220, 53, 69, 0.05);
}

.action-card.urgent:hover {
  border-color: #dc3545;
  box-shadow: 0 10px 30px rgba(220, 53, 69, 0.2);
}

.action-card:not(.urgent):hover, .action-card.active {
  border-color: #ff9500;
  box-shadow: 0 10px 30px rgba(255, 149, 0, 0.15);
}

.action-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.action-card .action-icon {
  background: linear-gradient(45deg, #ff9500, #ffb347);
}

.action-card.urgent .action-icon {
  background: linear-gradient(45deg, #dc3545, #e74c3c);
}

.action-icon.warning {
  background: linear-gradient(45deg, #ff9500, #ffb347);
}

.action-icon.success {
  background: linear-gradient(45deg, #28a745, #5bc85a);
}

.action-icon.primary {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), #5a95ff);
}

.action-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color, #333);
}

.action-description {
  font-size: 0.875rem;
  color: var(--text-muted, #6c757d);
}

.notification-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #dc3545;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  min-width: 1.5rem;
  text-align: center;
}

/* Statistiques */
.stats-section {
  margin-bottom: 3rem;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6c757d);
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.stat-icon.success {
  background: linear-gradient(45deg, #28a745, #5bc85a);
}

.stat-icon.primary {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), #5a95ff);
}

.stat-icon.warning {
  background: linear-gradient(45deg, #ff9500, #ffb347);
}

/* Section de contenu */
.content-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 1.25rem;
  padding: 2.5rem;
  box-shadow: 0 10px 30px rgba(255, 149, 0, 0.1);
  border: 1px solid rgba(255, 149, 0, 0.08);
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.section-content {
  /* Styles existants préservés */
}

.content-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 149, 0, 0.1);
  position: relative;
}

.content-title i {
  color: #ff9500;
  font-size: 1.5rem;
}

.content-title::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #ff9500, #ffb347, #ff9500);
  border-radius: 3px;
}

/* Listes de documents */
.documents-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.document-item {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.document-item.urgent {
  border-left: 4px solid #dc3545;
  background: rgba(220, 53, 69, 0.02);
}

.document-item:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 149, 0, 0.08);
  border-color: rgba(255, 149, 0, 0.12);
}

.document-item.urgent:hover {
  box-shadow: 0 8px 25px rgba(220, 53, 69, 0.1);
  border-color: #dc3545;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex: 1;
}

.doc-info i {
  font-size: 1.75rem;
  color: #ff9500;
  background: rgba(255, 149, 0, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.document-item:hover .doc-info i {
  background: #ff9500;
  color: white;
  transform: scale(1.05);
}

.document-item.urgent .doc-info i {
  color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
}

.document-item.urgent:hover .doc-info i {
  background: #dc3545;
  color: white;
}

.doc-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.doc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.doc-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-color, #333);
}

.urgent-tag {
  background: #dc3545;
  color: white;
  font-size: 0.625rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  text-transform: uppercase;
}

.doc-meta {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.doc-priority {
  margin-top: 0.25rem;
}

.time-elapsed {
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
  padding: 0.2rem 0.6rem;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 1rem;
}

.time-elapsed.urgent {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  font-weight: 500;
}

.signature-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #28a745;
  background: rgba(40, 167, 69, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  margin-top: 0.25rem;
  display: inline-flex;
}

.signer-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #ff9500;
  background: rgba(255, 149, 0, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  margin-top: 0.25rem;
  display: inline-flex;
}

.doc-status {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-badge {
  padding: 0.35rem 0.85rem;
  border-radius: 2rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.signed {
  background: rgba(40, 167, 69, 0.15);
  color: #155724;
}

.doc-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-primary {
  background: linear-gradient(45deg, #ff9500, #ffb347);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 149, 0, 0.3);
}

.btn-icon {
  background: none;
  border: 1.5px solid #ff9500;
  color: #ff9500;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.btn-icon:hover {
  background: #ff9500;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 149, 0, 0.2);
}

/* Historique timeline */
.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.timeline-item {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
}

.timeline-marker {
  width: 3rem;
  height: 3rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.timeline-item:hover .timeline-marker {
  transform: scale(1.05);
}

.timeline-marker.signed {
  background: linear-gradient(45deg, #28a745, #5bc85a);
}

.timeline-marker.received {
  background: linear-gradient(45deg, #ff9500, #ffb347);
}

.timeline-marker.pending {
  background: linear-gradient(45deg, #6c757d, #adb5bd);
}

.timeline-content {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 1rem;
  padding: 1.5rem;
  flex: 1;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.timeline-item:hover .timeline-content {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 149, 0, 0.08);
  border-color: rgba(255, 149, 0, 0.12);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.timeline-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-color, #333);
}

.timeline-date {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.timeline-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.document-name {
  font-weight: 500;
  color: var(--text-color, #333);
  font-size: 0.95rem;
}

.timeline-description {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

/* État vide */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  border: 1px dashed rgba(255, 149, 0, 0.2);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: rgba(255, 149, 0, 0.3);
}

.empty-state p {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-color, #333);
}

.empty-subtitle {
  font-size: 0.95rem;
  opacity: 0.8;
}

/* Contenu par défaut */
.default-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.welcome-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.welcome-card .btn-primary {
  margin: 0 auto;
  display: inline-flex;
}

.welcome-icon {
  width: 5rem;
  height: 5rem;
  border-radius: 1rem;
  background: linear-gradient(45deg, #ff9500, #ffb347);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  margin: 0 auto 1.5rem;
}

.welcome-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 1rem;
}

.welcome-card p {
  color: var(--text-muted, #6c757d);
  margin-bottom: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    padding: 1rem 1.5rem;
  }
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  .logo-icon {
    font-size: 2rem;
  }
  .logo-text {
    font-size: 1.3rem;
  }
  .main-content {
    padding: 1rem;
  }
  .welcome-title {
    font-size: 2rem;
  }
  .actions-grid {
    grid-template-columns: 1fr;
  }
  .stats-container {
    grid-template-columns: 1fr;
  }
  .document-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .doc-actions {
    width: 100%;
    justify-content: flex-end;
  }
  .timeline-item {
    flex-direction: column;
    gap: 0.5rem;
  }
  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  .signature-modal-content {
    width: 95%;
  }
  .button-group {
    flex-direction: column;
    width: 100%;
  }
  .signature-modal-footer {
    flex-direction: column;
    gap: 1rem;
  }
  .signature-status {
    width: 100%;
    justify-content: center;
  }
}
</style> 