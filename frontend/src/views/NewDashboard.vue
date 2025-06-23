<template>
  <div class="dashboard-container">
    <!-- Fond animé avec particules -->
    <div class="particles-container">
      <div v-for="i in 20" :key="i" class="particle" 
        :class="{ 'particle-primary': i % 3 === 0, 'particle-accent': i % 3 === 1, 'particle-light': i % 3 === 2 }"
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

    <!-- En-tête avec logo et navigation -->
    <header class="header">
      <div class="logo-container">
        <img src="@/assets/doc.png" alt="Logo" class="header-logo-img">
        <h1 class="logo-text">
          <span class="text-green">Doc</span>
          <span class="text-red">@uth</span>
          <span class="text-yellow">ANTIC</span>
        </h1>
      </div>
      <nav class="nav-menu" :class="{ 'active': isMenuOpen }">
        <div class="mobile-menu-close" @click="toggleMenu">
          <i class="bi bi-x-lg"></i>
        </div>
        <ul>
          <li><a href="javascript:void(0)" onclick="window.location.reload()" class="nav-link" :class="{ 'active': activeContent === 'dashboard' }">Tableau de bord</a></li>
          <li><a href="#" @click.prevent="setActiveContent('documents')" class="nav-link" :class="{ 'active': activeContent === 'documents' }">Mes documents</a></li>
          <li><a href="#" @click.prevent="setActiveContent('templates')" class="nav-link" :class="{ 'active': activeContent === 'templates' }">Templates</a></li>
          <li><a href="#" @click.prevent="setActiveContent('history')" class="nav-link" :class="{ 'active': activeContent === 'history' }">Historique</a></li>
          <li>
            <ThemeToggler class="theme-toggler" />
          </li>
          <li class="user-menu">
            <div class="user-info">
              <i class="bi bi-person-circle"></i>
              <span class="user-name">{{ truncatedUserName }}</span>
            </div>
            <div class="dropdown-menu">
              <a href="#" @click.prevent="setActiveContent('profile')" class="dropdown-item">
                <i class="bi bi-person"></i> Mon profil
              </a>
              <hr>
              <a href="#" @click="logout" class="dropdown-item">
                <i class="bi bi-box-arrow-right"></i> Déconnexion
              </a>
            </div>
          </li>
        </ul>
      </nav>
      <!-- Menu mobile -->
      <div class="mobile-menu-toggle" @click="toggleMenu">
        <i class="bi" :class="isMenuOpen ? 'bi-x-lg' : 'bi-list'"></i>
      </div>
    </header>

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- Modal de sélection du type de signature -->
      <div v-if="showSignatureOptionsModal" class="modal-overlay" @click.self="hideSignatureOptions">
        <div class="signature-options-modal">
          <div class="modal-header">
            <h3 class="modal-title">Choisir un mode de signature</h3>
            <button class="modal-close" @click="hideSignatureOptions">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          <div class="modal-body signature-options-body">
            <div class="signature-options-grid">
              <!-- Option 1: Signer à partir d'un template -->
              <div class="signature-option-card" @click="selectSignatureOption('template')">
                <div class="option-icon template">
                  <i class="bi bi-file-earmark-check"></i>
                </div>
                <div class="option-content">
                  <h4 class="option-title">Signer à partir d'un template</h4>
                  <p class="option-description">Utilisez un template prédéfini pour signer rapidement votre document</p>
                </div>
                <div class="option-arrow">
                  <i class="bi bi-chevron-right"></i>
                </div>
              </div>
              
              <!-- Option 2: Signature rapide -->
              <div class="signature-option-card" @click="selectSignatureOption('quick')">
                <div class="option-icon quick">
                  <i class="bi bi-lightning-charge"></i>
                </div>
                <div class="option-content">
                  <h4 class="option-title">Signature rapide</h4>
                  <p class="option-description">Signez un document rapidement en quelques étapes simples</p>
                </div>
                <div class="option-arrow">
                  <i class="bi bi-chevron-right"></i>
                </div>
              </div>
              
              <!-- Option 3: Signature multiple de documents -->
              <div class="signature-option-card" @click="selectSignatureOption('multiple')">
                <div class="option-icon multiple">
                  <i class="bi bi-files"></i>
                </div>
                <div class="option-content">
                  <h4 class="option-title">Signature multiple de documents</h4>
                  <p class="option-description">Signez plusieurs documents à la fois avec le même certificat</p>
                </div>
                <div class="option-arrow">
                  <i class="bi bi-chevron-right"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Composant de signature intégré -->
      <div v-if="activeContent === 'sign'" class="integrated-component-container">
        <SignDocument @close="setActiveContent('dashboard')" />
      </div>
      
      <!-- Composant de signature à partir d'un template -->
      <div v-else-if="activeContent === 'sign-template'" class="integrated-component-container">
        <div class="template-selection-container">
          <div class="section-header">
            <h2 class="section-title">Signer avec un template</h2>
            <button class="btn btn-outline-secondary" @click="setActiveContent('dashboard')">
              <i class="bi bi-arrow-left"></i> Retour
            </button>
          </div>
          
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Chargement des templates...</p>
          </div>
          
          <div v-else-if="templates.length === 0" class="empty-templates">
            <i class="bi bi-file-earmark-text"></i>
            <p>Vous n'avez pas encore de templates</p>
            <button class="btn btn-primary" @click="setActiveContent('templates')">Créer un template</button>
          </div>
          
          <div v-else class="templates-grid template-selection-grid">
            <div v-for="(template, index) in templates" :key="index" class="template-card">
              <div class="template-header">
                <div class="template-icon">
                  <i class="bi bi-file-earmark-pdf"></i>
                </div>
                <div class="template-status">
                  <span class="template-badge">Template</span>
                </div>
              </div>
              <div class="template-content">
                <h3 class="template-title" :title="template.name">{{ template.name }}</h3>
                <div class="template-meta">
                  <div class="meta-item">
                    <i class="bi bi-calendar"></i>
                    <span>Créé le: {{ template.date }}</span>
                  </div>
                  <div class="meta-item">
                    <i class="bi bi-grid"></i>
                    <span>{{ template.pageApplication === 'all' ? 'Toutes les pages' : 'Pages spécifiques' }}</span>
                  </div>
                </div>
              </div>
              <div class="template-main-actions">
                <button class="action-btn primary full-width sign-template-btn" @click="signWithTemplate(template)">
                  <i class="bi bi-pen"></i> 
                  <span>Signer avec ce template</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Composant de signature avec template intégré -->
      <div v-else-if="activeContent === 'sign-with-template'" class="integrated-component-container">
        <SignWithTemplate :template-data="selectedTemplate" @close="setActiveContent('dashboard')" />
      </div>
      
      <!-- Section de signature multiple de documents -->
      <div v-else-if="activeContent === 'sign-multiple'" class="integrated-component-container">
        <SignWithTemplateMultiple @close="setActiveContent('dashboard')" />
          </div>
      
      <!-- Composant SignSimple pour signature rapide -->
      <div v-else-if="activeContent === 'signSimple'">
        <SignSimple @close="setActiveContent('dashboard')" />
      </div>
      
      <!-- Composant Mes Documents intégré -->
      <div v-else-if="activeContent === 'documents'" class="integrated-component-container">
        <MyDocuments />
      </div>
      
      <!-- Composant Historique intégré -->
      <div v-else-if="activeContent === 'history'" class="integrated-component-container">
        <div class="history-component" ref="historyComponent">
          <div class="history-bg-decoration"></div>
          <div class="history-bg-circles">
            <div class="circle circle-1"></div>
            <div class="circle circle-2"></div>
            <div class="circle circle-3"></div>
          </div>
          <UserHistory />
        </div>
      </div>
      
      <!-- Composant Profil intégré -->
      <div v-else-if="activeContent === 'profile'" class="integrated-component-container">
        <UserProfile />
      </div>
      
      <!-- Composant Templates intégré -->
      <div v-else-if="activeContent === 'templates'" class="integrated-component-container">
        <div class="templates-section">
          <div class="section-card">
            <div class="section-header">
              <h2 class="section-title">Mes templates</h2>
              <button class="action-button primary" @click="showNewTemplateModal = true">
                <i class="bi bi-plus-circle"></i>
                <span>Nouveau template</span>
              </button>
            </div>
            
            <div v-if="loading" class="loading-state">
              <div class="spinner"></div>
              <p>Chargement des templates...</p>
            </div>
            
            <div v-else-if="templates.length === 0" class="empty-templates">
              <i class="bi bi-file-earmark-text"></i>
              <p>Vous n'avez pas encore de templates</p>
              <button class="btn btn-primary" @click="showNewTemplateModal = true">Créer un template</button>
            </div>
            
            <div v-else class="templates-grid">
              <div v-for="(template, index) in templates" :key="index" class="template-card">
                <div class="template-header">
                  <div class="template-icon">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </div>
                  <div class="template-status">
                    <span class="template-badge">Template</span>
                  </div>
                </div>
                <div class="template-content">
                  <h3 class="template-title" :title="template.name">{{ template.name }}</h3>
                  
                  <div class="template-meta">
                    <div class="meta-item">
                      <i class="bi bi-calendar"></i>
                      <span>Créé le: {{ template.date }}</span>
                    </div>
                    <div class="meta-item">
                      <i class="bi bi-grid"></i>
                      <span>{{ template.pageApplication === 'all' ? 'Toutes les pages' : 'Pages spécifiques' }}</span>
                    </div>
                    <div class="meta-item">
                      <i class="bi bi-qr-code"></i>
                      <span>Taille QR: {{ getQrSizeLabel(template.qrSize) }}</span>
                    </div>
                  </div>
                </div>
                <div class="template-main-actions">
                  <button class="action-btn primary full-width" @click="previewTemplate(template)">
                    <i class="bi bi-eye"></i> Aperçu
                  </button>
                  <button class="action-btn secondary" @click="editTemplate(template)">
                    <i class="bi bi-pencil"></i> Modifier
                  </button>
                </div>
                <div class="template-secondary-buttons">
                  <button class="action-btn text" @click="confirmDeleteTemplate(template)">
                    <i class="bi bi-trash"></i> Supprimer
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Modal pour l'aperçu du template -->
        <div v-if="showPreviewModal" class="modal-overlay" @click.self="showPreviewModal = false">
          <div class="preview-modal">
            <div class="modal-header">
              <h3 class="modal-title">Aperçu du template: {{ selectedTemplate?.name }}</h3>
              <button class="modal-close" @click="showPreviewModal = false">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body preview-body">
              <div v-if="loadingPreview" class="loading-preview">
                <div class="spinner"></div>
                <p>Chargement de l'aperçu...</p>
              </div>
              <iframe v-else-if="previewUrl" :src="previewUrl" class="preview-iframe" title="Aperçu du template"></iframe>
              <div v-else class="preview-error">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <p>Impossible de charger l'aperçu.</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Modal de confirmation pour la suppression -->
        <div v-if="showDeleteConfirmModal" class="modal-overlay" @click.self="showDeleteConfirmModal = false">
          <div class="confirm-modal">
            <div class="modal-header">
              <h3 class="modal-title">Confirmer la suppression</h3>
              <button class="modal-close" @click="showDeleteConfirmModal = false">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div class="modal-body">
              <p>Êtes-vous sûr de vouloir supprimer le template <strong>{{ selectedTemplate?.name }}</strong> ?</p>
              <p class="text-danger">Cette action est irréversible.</p>
            </div>
            <div class="modal-footer">
              <button class="btn btn-outline-secondary" @click="showDeleteConfirmModal = false">Annuler</button>
              <button class="btn btn-danger" @click="deleteTemplateConfirmed" :disabled="isDeleting">
                <span v-if="isDeleting"><i class="bi bi-hourglass-split spin"></i> Suppression...</span>
                <span v-else><i class="bi bi-trash"></i> Supprimer</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Composant Vérification intégré -->
      <div v-else-if="activeContent === 'verify'" class="integrated-component-container">
        <div class="placeholder-message">
          <i class="bi bi-exclamation-triangle-fill text-warning icon-xl"></i>
          <h3>Module de vérification indisponible</h3>
          <p>Le module de vérification de documents a été temporairement retiré pour maintenance.</p>
          <button class="btn btn-primary" @click="setActiveContent('dashboard')">Retour au tableau de bord</button>
        </div>
      </div>
      
      <!-- Contenu principal du tableau de bord -->
      <div v-else-if="activeContent === 'dashboard'">
      <!-- Section de bienvenue -->
      <section class="welcome-section" data-animate="fade-in-up">
        <div class="welcome-content">
          <h2 class="welcome-title">
            Bienvenue, <span class="highlight-text">{{ userName }}</span> !
          </h2>
          <p class="welcome-subtitle" v-if="userRole">Vous êtes connecté en tant que <span class="badge role-badge">{{ userRole }}</span></p>
          <p class="welcome-subtitle">Gérez vos signatures électroniques en toute sécurité</p>
        </div>
        <div class="quick-actions">
          <button @click="setActiveContent('sign-options')" class="action-button primary">
            <i class="bi bi-pen"></i>
            <span>Signer un document</span>
          </button>
          <button @click="setActiveContent('verify')" class="action-button accent">
            <i class="bi bi-check-circle"></i>
            <span>Vérifier un document</span>
          </button>
        </div>
      </section>

      <!-- Section des statistiques -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card" data-animate="fade-in-up" data-delay="0.1">
            <div class="stat-icon primary">
              <i class="bi bi-file-earmark-check"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.signed }}</div>
              <div class="stat-label">Documents signés</div>
            </div>
            <div class="stat-trend up">
              <i class="bi bi-arrow-up-right"></i>
              <span>+12%</span>
            </div>
          </div>

          <div class="stat-card" data-animate="fade-in-up" data-delay="0.2">
            <div class="stat-icon accent">
              <i class="bi bi-shield-check"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.verified }}</div>
              <div class="stat-label">Documents vérifiés</div>
            </div>
            <div class="stat-trend up">
              <i class="bi bi-arrow-up-right"></i>
              <span>+8%</span>
            </div>
          </div>

          <div class="stat-card" data-animate="fade-in-up" data-delay="0.3">
            <div class="stat-icon neutral">
              <i class="bi bi-hourglass-split"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">En attente</div>
            </div>
            <div class="stat-trend neutral">
              <i class="bi bi-dash"></i>
              <span>0%</span>
            </div>
          </div>

          <div class="stat-card" data-animate="fade-in-up" data-delay="0.4">
            <div class="stat-icon success">
              <i class="bi bi-people"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.shared }}</div>
              <div class="stat-label">Partagés</div>
            </div>
            <div class="stat-trend up">
              <i class="bi bi-arrow-up-right"></i>
              <span>+20%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Section des graphiques -->
      <div class="charts-grid">
        <section class="chart-section" data-animate="fade-in-up" data-delay="0.5">
          <div class="section-card">
            <div class="section-header">
              <h3 class="section-title">Activité de signature</h3>
              <div class="chart-legend">
                <span class="legend-item">
                  <span class="legend-color primary"></span>
                  Signatures
                </span>
                <span class="legend-item">
                  <span class="legend-color accent"></span>
                  Vérifications
                </span>
              </div>
            </div>
            <div class="chart-container responsive-chart">
              <canvas ref="activityChart"></canvas>
            </div>
          </div>
        </section>

        <section class="chart-section" data-animate="fade-in-up" data-delay="0.6">
          <div class="section-card">
            <div class="section-header">
              <h3 class="section-title">Types de documents</h3>
            </div>
            <div class="chart-container responsive-chart">
              <canvas ref="docTypesChart"></canvas>
            </div>
          </div>
        </section>
      </div>

      <!-- Section historique récent -->
      <section class="history-section" data-animate="fade-in-up" data-delay="0.7">
        <div class="section-card">
          <div class="section-header">
            <h3 class="section-title">Activité récente</h3>
            <button class="view-all-btn" @click="setActiveContent('history')">
              Voir tout <i class="bi bi-arrow-right"></i>
            </button>
          </div>
          <div class="history-list">
            <div v-for="(item, index) in recentActivity" :key="index" class="history-item" data-animate="fade-in-left" :data-delay="0.8 + (index * 0.1)">
              <div class="history-icon" :class="item.type">
                <i :class="item.icon"></i>
              </div>
              <div class="history-content">
                <h4 class="history-title username-truncate">{{ item.title }}</h4>
                <p class="history-text" v-html="item.description"></p>
              </div>
              <div class="history-time">
                <span>{{ item.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
      </div>
    </main>
    
    <!-- Modal pour le nouveau template -->
    <div v-if="showNewTemplateModal" class="modal-overlay" @click.self="showNewTemplateModal = false">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">Nouveau template de signature</h3>
          <button class="modal-close" @click="showNewTemplateModal = false">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="template-form">
            <div class="form-group">
              <label for="template-name">Nom du template</label>
              <input type="text" id="template-name" v-model="newTemplate.name" placeholder="Saisissez un nom pour ce template" class="form-control">
            </div>
            <div class="form-group">
              <label for="template-file">Document PDF</label>
              <div class="file-input-container">
                <input type="file" id="template-file" @change="handleFileSelect" accept=".pdf" class="file-input">
                <label for="template-file" class="file-label">
                  <i class="bi bi-file-earmark-pdf"></i>
                  <span v-if="!newTemplate.file">Sélectionner un fichier PDF</span>
                  <span v-else>{{ newTemplate.file.name }}</span>
                </label>
              </div>
            </div>
          </div>
          
          <!-- Afficher QR Positioner une fois le fichier sélectionné -->
          <div v-if="newTemplate.file" class="qr-positioner-wrapper">
            <QrPositioner 
              :pdfFile="newTemplate.file"
              :preloadedPositions="newTemplate.qrPositions"
              @position-confirmed="handlePositionConfirmed"
              @signature-uploaded="handleSignatureUploaded"
              @pdf-generated="handlePdfGenerated"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showNewTemplateModal = false" :disabled="isSaving">Annuler</button>
          <button class="btn btn-primary" @click="saveTemplate" :disabled="!canSaveTemplate || isSaving">
            <span v-if="isSaving"><i class="bi bi-hourglass-split spin"></i> Enregistrement...</span>
            <span v-else>Enregistrer</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import ThemeToggler from '@/components/ThemeToggler.vue';
import SignDocument from '@/views/SignDocument.vue';
import MyDocuments from '@/views/MyDocuments.vue';
import UserHistory from '@/views/UserHistory.vue';
import UserProfile from '@/views/UserProfile.vue';
import SignWithTemplate from '@/views/SignWithTemplate.vue'; // Importer le nouveau composant
import SignWithTemplateMultiple from '@/views/SignWithTemplateMultiple.vue'; // Importer le composant de signature multiple
import SignSimple from '@/views/SignSimple.vue'; // Importer le composant de signature rapide
// VerifyDocument a été supprimé
import AuthService from '@/services/AuthService';
import AnalyticsService from '@/services/AnalyticsService';
import DocumentService from '@/services/DocumentService';
import { initScrollAnimations } from '@/assets/js/scrollAnimations.js';
import QrPositioner from '@/components/QrPositioner.vue';

const router = useRouter();
const isMenuOpen = ref(false);
const activeContent = ref('dashboard'); // 'dashboard', 'documents', 'sign', 'history', 'templates', 'sign-template', 'sign-multiple'
const showNewTemplateModal = ref(false);
const showSignatureOptionsModal = ref(false);

// Références pour les graphiques
const activityChart = ref(null);
const docTypesChart = ref(null);
const activityChartInstance = ref(null);
const docTypesChartInstance = ref(null);

// Données pour les graphiques
const chartData = ref({
  activity: {
    signatures: [],
    verifications: [],
    labels: []
  },
  documentTypes: {
    labels: [],
    data: [],
    colors: []
  }
});

// Variables pour les templates
const templates = ref([]);
const newTemplate = ref({
  name: '',
  file: null,
  qrPositions: null,
  date: '',
  signatureImage: null,
  generatedPdfFile: null,
  generatedPdfBlob: null,
  generatedPdfDataUrl: null
});

// Computed property pour vérifier si on peut sauvegarder le template
const canSaveTemplate = computed(() => {
  return newTemplate.value.name && 
         newTemplate.value.file && 
         newTemplate.value.qrPositions;
});

// Fonction pour afficher les options de signature
function showSignatureOptions() {
  showSignatureOptionsModal.value = true;
}

// Fonction pour masquer les options de signature
function hideSignatureOptions() {
  showSignatureOptionsModal.value = false;
}

// Gérer la sélection d'une option de signature
function selectSignatureOption(option) {
  hideSignatureOptions();
  
  switch(option) {
    case 'template':
      setActiveContent('sign-template');
      break;
    case 'quick':
      setActiveContent('signSimple');
      break;
    case 'multiple':
      setActiveContent('sign-multiple');
      break;
    default:
      setActiveContent('dashboard');
  }
}

// Fonction pour signer avec un template spécifique
function signWithTemplate(template) {
  console.log('Signature avec le template (structure brute):', template);
  
  // Inspection détaillée du template pour trouver l'image de signature
  console.log('Inspection du template:');
  console.log('- ID du template:', template.id);
  
  // Récupérer le template complet depuis le service pour obtenir l'image de signature
  TemplateService.getTemplate(template.id)
    .then(templateDetails => {
      console.log('Template complet récupéré depuis API:', templateDetails);
      
      // Préparer le template avec les données nécessaires pour la signature
      const preparedTemplate = {
        ...template,
        // S'assurer que toutes les données nécessaires sont présentes et correctement formatées
        signatureImage: templateDetails.signature_image || null,
        signaturePositions: templateDetails.signature_positions || [],
        pageApplication: templateDetails.page_application || template.pageApplication || 'all',
        qrSize: templateDetails.qr_size || template.qrSize || 'medium',
        qrPositions: {
          positions: templateDetails.qr_positions || []
        },
        selectedPages: templateDetails.selected_pages || []
      };
      
      console.log('Template préparé pour la signature:', preparedTemplate);
      console.log('Image de signature extraite:', preparedTemplate.signatureImage ? 'Présente' : 'Absente');
      console.log('Positions de signature:', preparedTemplate.signaturePositions);
      
      // Stocker le template préparé pour le passer au composant
      selectedTemplate.value = preparedTemplate;
      
      // Changer l'affichage vers le composant de signature avec template
      activeContent.value = 'sign-with-template';
    })
    .catch(error => {
      console.error('Erreur lors de la récupération des détails du template:', error);
      // Fallback en cas d'erreur
      selectedTemplate.value = template;
      activeContent.value = 'sign-with-template';
    });
}

// Fonctions de navigation
function setActiveContent(contentType) {
  // Cas particulier pour la signature, on affiche le modal d'options
  if (contentType === 'sign-options') {
    showSignatureOptions();
    return;
  }
  
  // Si on clique sur Tableau de bord et qu'on est déjà sur le tableau de bord ou page vide
  if (contentType === 'dashboard' && (activeContent.value === 'dashboard' || activeContent.value === null)) {
    // Rafraîchir directement la page pour un rechargement complet
    window.location.reload();
    return;
  }
  
  // Pour les autres cas, animation de transition entre les contenus
  activeContent.value = null;
  
  setTimeout(() => {
    activeContent.value = contentType;
    
    // Applique l'animation au composant d'historique si nécessaire
    if (contentType === 'history') {
      setTimeout(() => {
        const historyComponent = document.querySelector('.history-component');
        if (historyComponent) {
          historyComponent.classList.add('animated');
        }
      }, 100);
    }
  }, 300);
}

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value;
}

// Données statistiques (initialisées avec des valeurs par défaut)
const stats = ref({
  signed: 0,
  verified: 0,
  pending: 0,
  shared: 0
});

// Activité récente (données dynamiques)
const recentActivity = ref([]);

// Fonction pour charger les activités récentes
const loadRecentActivities = async () => {
  try {
    console.log('Chargement des 4 activités récentes depuis UserHistory...');
    const activitiesResponse = await DocumentService.getMyActivities();
    const activities = activitiesResponse.data || [];
    
    console.log('Activités brutes récupérées:', activities);
    console.log('Nombre total d\'activités:', activities.length);
    
    // Prendre les 4 dernières activités et les transformer
    const latestActivities = activities
      .slice(0, 4)
      .map(activity => ({
        type: activity.activity_type,
        icon: getActivityIcon(activity.activity_type),
        title: getActivityTitle(activity.activity_type),
        description: activity.description || `Activité de type ${activity.activity_type}`,
        time: formatRelativeTime(activity.timestamp || activity.created_at)
      }));
    
    recentActivity.value = latestActivities;
    console.log('4 activités récentes chargées et transformées:', latestActivities);
  } catch (error) {
    console.error('Erreur lors du chargement des activités récentes:', error);
    // En cas d'erreur, garder les données par défaut (tableau vide)
  }
};

// Fonction utilitaire pour obtenir l'icône d'une activité
const getActivityIcon = (activityType) => {
  const iconMap = {
    'signed': 'bi bi-file-earmark-check',
    'signature_simple': 'bi bi-pen',
    'signature_multiple': 'bi bi-files',
    'signature_with_template': 'bi bi-file-earmark-medical',
    'template_created': 'bi bi-file-earmark-plus',
    'template_used': 'bi bi-file-earmark-check',
    'viewed': 'bi bi-eye',
    'original_viewed': 'bi bi-file-earmark',
    'downloaded': 'bi bi-download',
    'signed_downloaded': 'bi bi-file-earmark-arrow-down',
    'original_downloaded': 'bi bi-file-arrow-down',
    'created': 'bi bi-file-plus',
    'modified': 'bi bi-file-earmark-text'
  };
  return iconMap[activityType] || 'bi bi-file-earmark';
};

// Fonction utilitaire pour obtenir le titre d'une activité
const getActivityTitle = (activityType) => {
  const titleMap = {
    'signed': 'Document signé',
    'signature_simple': 'Signature simple',
    'signature_multiple': 'Signature multiple',
    'signature_with_template': 'Signature avec template',
    'template_created': 'Template créé',
    'template_used': 'Template utilisé',
    'viewed': 'Document consulté',
    'original_viewed': 'Document original consulté',
    'downloaded': 'Document téléchargé',
    'signed_downloaded': 'Document signé téléchargé',
    'original_downloaded': 'Document original téléchargé',
    'created': 'Document créé',
    'modified': 'Document modifié'
  };
  return titleMap[activityType] || 'Activité';
};

// Fonction utilitaire pour formater le temps relatif
const formatRelativeTime = (timestamp) => {
  const now = new Date();
  const activityDate = new Date(timestamp);
  const diffMs = now - activityDate;
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffMinutes < 60) {
    return `Il y a ${diffMinutes} min`;
  } else if (diffHours < 24) {
    return `Il y a ${diffHours} h`;
  } else if (diffDays < 7) {
    return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`;
  } else {
    return activityDate.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  }
};

// Positionnement aléatoire des particules
const particlePositions = Array.from({ length: 20 }, () => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 10 + 5,
  duration: Math.random() * 15 + 10,
  delay: Math.random() * 5
}));

// Gestion de l'utilisateur connecté
const currentUser = ref(AuthService.getCurrentUser());

// Récupérer les informations de l'utilisateur pour l'affichage
const userName = computed(() => {
  if (currentUser.value) {
    if (currentUser.value.first_name && currentUser.value.last_name) {
      return `${currentUser.value.first_name} ${currentUser.value.last_name}`;
    } else if (currentUser.value.name) {
      return currentUser.value.name;
    } else {
      return currentUser.value.username || 'Utilisateur';
    }
  }
  return 'Utilisateur';
});

// Récupérer le rôle de l'utilisateur
const userRole = computed(() => {
  if (currentUser.value && currentUser.value.role) {
    switch(currentUser.value.role) {
      case 'superadmin':
        return 'Super Administrateur';
      case 'admin':
        return 'Administrateur';
      case 'collaborator':
        return 'Collaborateur';
      case 'signer':
        return 'Signataire';
      default:
        return 'Utilisateur';
    }
  }
  return null;
});

// Version tronquée du nom pour l'affichage mobile
const truncatedUserName = computed(() => {
  if (userName.value.length > 10) {
    return userName.value.substring(0, 10) + '...';
  }
  return userName.value;
});

// Fonction de déconnexion
const logout = async () => {
  try {
    // Enregistrer l'activité dans le backend
    await AuthService.logActivity('dashboard_access', 'Accès au tableau de bord');
    
    // Déconnecter l'utilisateur
    AuthService.logout();
    
    // Rediriger vers la page de connexion
    router.push('/login');
  } catch (error) {
    console.error('Erreur lors de la déconnexion:', error);
  }
};

// Fonction pour charger les données des graphiques
const loadChartData = async () => {
  try {
    console.log('Chargement des données pour les graphiques...');
    
    // Charger les données d'activité et de types de documents en parallèle
    const [activityData, documentTypeData] = await Promise.all([
      AnalyticsService.getActivityAnalytics(),
      AnalyticsService.getDocumentTypeAnalytics()
    ]);
    
    console.log('Données d\'activité reçues:', activityData);
    console.log('Données de types de documents reçues:', documentTypeData);
    
    // Mettre à jour les données
    chartData.value.activity = activityData;
    chartData.value.documentTypes = documentTypeData;
    
    // Réinitialiser les graphiques avec les nouvelles données
    await initCharts();
    
  } catch (error) {
    console.error('Erreur lors du chargement des données des graphiques:', error);
    // En cas d'erreur, initialiser avec des données par défaut
    await initCharts();
  }
};
  
// Fonction pour initialiser les graphiques
const initCharts = async () => {
  try {
    const { Chart, registerables } = await import('chart.js');
    Chart.register(...registerables);

    // Détruire les graphiques existants s'ils existent
    if (activityChartInstance.value) {
      activityChartInstance.value.destroy();
    }
    if (docTypesChartInstance.value) {
      docTypesChartInstance.value.destroy();
    }

    // Graphique d'activité avec vraies données
    if (activityChart.value) {
      const activityLabels = chartData.value.activity.labels.length > 0 
        ? chartData.value.activity.labels 
        : ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil'];
      
      const signaturesData = chartData.value.activity.monthlySignatures.length > 0 
        ? chartData.value.activity.monthlySignatures 
        : [0, 0, 0, 0, 0, 0, 0];
      
      const verificationsData = chartData.value.activity.monthlyVerifications.length > 0 
        ? chartData.value.activity.monthlyVerifications 
        : [0, 0, 0, 0, 0, 0, 0];

      activityChartInstance.value = new Chart(activityChart.value.getContext('2d'), {
        type: 'line',
        data: {
          labels: activityLabels,
          datasets: [
            {
              label: 'Signatures',
              data: signaturesData,
              borderColor: '#3a86ff',
              backgroundColor: 'rgba(58, 134, 255, 0.1)',
              tension: 0.3,
              fill: true
            },
            {
              label: 'Vérifications',
              data: verificationsData,
              borderColor: '#4cb58e',
              backgroundColor: 'rgba(76, 181, 142, 0.1)',
              tension: 0.3,
              fill: true
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                display: true,
                color: 'rgba(0, 0, 0, 0.05)'
              },
              ticks: {
                font: {
                  size: 10
                },
                stepSize: 1 // Pour afficher seulement les entiers
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                font: {
                  size: 10
                }
              }
            }
          }
        }
      });
    }

    // Graphique des types de documents avec vraies données
    if (docTypesChart.value) {
      const typeLabels = chartData.value.documentTypes.labels.length > 0 
        ? chartData.value.documentTypes.labels 
        : ['PDF'];
      
      const typeData = chartData.value.documentTypes.data.length > 0 
        ? chartData.value.documentTypes.data 
        : [100];
      
      const typeColors = chartData.value.documentTypes.colors.length > 0 
        ? chartData.value.documentTypes.colors 
        : ['#3a86ff'];

      docTypesChartInstance.value = new Chart(docTypesChart.value.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: typeLabels,
          datasets: [{
            data: typeData,
            backgroundColor: typeColors,
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 15,
                boxWidth: 10,
                font: {
                  size: 10
                }
              }
            }
          },
          cutout: '70%'
        }
      });
    }
  } catch (error) {
    console.error('Erreur lors de l\'initialisation des graphiques:', error);
  }
};

// Fonction pour charger les statistiques
const loadStatistics = async () => {
  try {
    console.log('Chargement des statistiques...');
    const generalStats = await AnalyticsService.getGeneralStats();
    console.log('Statistiques reçues:', generalStats);
    
    // Mettre à jour les statistiques
    stats.value = {
      signed: generalStats.signedDocuments,
      verified: generalStats.totalVerifications,
      pending: generalStats.pendingDocuments,
      shared: generalStats.totalDownloads
    };
  } catch (error) {
    console.error('Erreur lors du chargement des statistiques:', error);
    // En cas d'erreur, garder les valeurs par défaut
  }
};

// Initialisation au chargement
onMounted(async () => {
  // Initialiser les animations
  initScrollAnimations();
  
  document.title = 'Tableau de bord - Doc@uthANTIC';
  
  // Vérifier si l'utilisateur est authentifié
  if (AuthService.isAuthenticated()) {
    // Valider le token
    const isValid = await AuthService.validateToken();
    
    if (isValid) {
      currentUser.value = AuthService.getCurrentUser();
      
      // Enregistrer l'activité d'accès au tableau de bord
      try {
        await AuthService.logActivity('dashboard_access', 'Accès au tableau de bord');
      } catch (error) {
        console.error('Erreur lors de l\'enregistrement de l\'activité:', error);
      }
      
      // Charger toutes les données en parallèle
      await Promise.all([
        loadTemplates(),
        loadChartData(),
        loadStatistics(),
        loadRecentActivities()
      ]);
    } else {
      // Rediriger vers la page de connexion si le token n'est pas valide
      router.push('/login');
    }
  } else {
    // Rediriger vers la page de connexion si l'utilisateur n'est pas authentifié
    router.push('/login');
  }
});

// Observer les changements d'authentification
watch(() => AuthService.isAuthenticated(), (isAuthenticated) => {
  if (!isAuthenticated) {
    router.push('/login');
  }
});

// Gestionnaire de redimensionnement pour les graphiques
const handleResizeCharts = () => {
  if (activityChartInstance.value) {
    activityChartInstance.value.resize();
  }
  if (docTypesChartInstance.value) {
    docTypesChartInstance.value.resize();
  }
};

// Gestion des écouteurs d'événements et nettoyage
onMounted(() => {
  // Ajouter l'écouteur quand le composant est monté
  window.addEventListener('resize', handleResizeCharts);
  
  // Retourner une fonction de nettoyage qui sera appelée quand le composant est démonté
  return () => {
    window.removeEventListener('resize', handleResizeCharts);
  };
});

// Fonctions pour gérer les templates
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file && file.type === 'application/pdf') {
    newTemplate.value.file = file;
  } else {
    alert('Veuillez sélectionner un fichier PDF valide.');
    event.target.value = null;
  }
}

function handlePositionConfirmed(positionData) {
  newTemplate.value.qrPositions = positionData;
}

// Fonction pour gérer l'upload de signature
function handleSignatureUploaded(file) {
  console.log('Signature uploadée:', file.name);
  newTemplate.value.signatureImage = file;
}

// Fonction pour gérer la génération de PDF
function handlePdfGenerated(pdfData) {
  console.log('PDF généré:', pdfData.file.name);
  newTemplate.value.generatedPdfBlob = pdfData.blob;
  newTemplate.value.generatedPdfFile = pdfData.file;
  newTemplate.value.generatedPdfDataUrl = pdfData.dataUrl;
}

import TemplateService from '@/services/TemplateService';

// ... autres imports

const isSaving = ref(false);
const loading = ref(false);
const loadingPreview = ref(false);
const isDeleting = ref(false);
const showPreviewModal = ref(false);
const showDeleteConfirmModal = ref(false);
const selectedTemplate = ref(null);
const previewUrl = ref(null);

// Fonction pour charger les templates depuis l'API
async function loadTemplates() {
  try {
    loading.value = true;
    const response = await TemplateService.getTemplates();
    
    // Transformer les données de l'API pour correspondre à notre format local
    templates.value = response.results.map(template => ({
      id: template.id.toString(),
      name: template.name,
      date: new Date(template.created_at).toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }),
      qrSize: template.qr_size,
      pageApplication: template.page_application
    }));
  } catch (error) {
    console.error('Erreur lors du chargement des templates:', error);
  } finally {
    loading.value = false;
  }
}

// Fonction pour afficher l'aperçu d'un template
async function previewTemplate(template) {
  try {
    selectedTemplate.value = template;
    showPreviewModal.value = true;
    loadingPreview.value = true;
    
    // Récupérer le blob du fichier d'aperçu
    const previewBlob = await TemplateService.downloadPreview(template.id);
    
    // Créer une URL pour le blob
    const url = URL.createObjectURL(previewBlob);
    previewUrl.value = url;
    
    // Nettoyer l'URL lorsque la modale est fermée
    const cleanupUrl = () => {
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value);
        previewUrl.value = null;
      }
      
      // Supprimer l'écouteur d'événements après usage
      showPreviewModal.value = false;
    };
    
    // Ajouter un écouteur d'événements pour nettoyer lorsque la modale est fermée
    watch(showPreviewModal, (isOpen) => {
      if (!isOpen) {
        cleanupUrl();
      }
    }, { once: true });
    
  } catch (error) {
    console.error('Erreur lors du chargement de l\'aperçu:', error);
    previewUrl.value = null;
  } finally {
    loadingPreview.value = false;
  }
}

// Fonction pour éditer un template
async function editTemplate(template) {
  try {
    loading.value = true;
    selectedTemplate.value = template;
    
    // Récupérer les détails complets du template depuis l'API
    const templateDetails = await TemplateService.getTemplate(template.id);
    
    // Récupérer le fichier PDF original pour l'afficher dans QrPositioner
    let originalPdfBlob = null;
    try {
      originalPdfBlob = await TemplateService.downloadOriginal(template.id);
    } catch (pdfError) {
      console.error('Erreur lors du téléchargement du PDF original:', pdfError);
    }
    
    // Créer un File à partir du Blob si disponible
    let originalFile = null;
    if (originalPdfBlob) {
      originalFile = new File([originalPdfBlob], `${templateDetails.name}.pdf`, { 
        type: 'application/pdf' 
      });
    }
    
    // Ouvrir la modale avec les détails du template
    newTemplate.value = {
      name: templateDetails.name,
      id: templateDetails.id,
      file: originalFile, // Le fichier PDF original si disponible
      qrPositions: {
        qr: {
          size: templateDetails.qr_size,
          positions: templateDetails.qr_positions,
          pages: templateDetails.selected_pages && templateDetails.selected_pages.length > 0 ? 
                 templateDetails.selected_pages : 'all'
        },
        mode: templateDetails.page_application,
        signature: templateDetails.signature_positions ? {
          positions: templateDetails.signature_positions,
          size: templateDetails.signature_size || 50
        } : null
      },
      date: template.date,
      isEditing: true // Indicateur que nous sommes en mode édition
    };
    
    // Ouvrir la modale d'édition
    showNewTemplateModal.value = true;
  } catch (error) {
    console.error('Erreur lors de la récupération des détails du template:', error);
    alert('Une erreur est survenue lors de la récupération des détails du template.');
  } finally {
    loading.value = false;
  }
}

// Fonction pour confirmer la suppression d'un template
function confirmDeleteTemplate(template) {
  selectedTemplate.value = template;
  showDeleteConfirmModal.value = true;
}

// Fonction pour effectuer la suppression une fois confirmée
async function deleteTemplateConfirmed() {
  if (!selectedTemplate.value) return;
  
  try {
    isDeleting.value = true;
    await TemplateService.deleteTemplate(selectedTemplate.value.id);
    
    // Supprimer le template de la liste locale
    templates.value = templates.value.filter(t => t.id !== selectedTemplate.value.id);
    
    // Fermer la modale de confirmation
    showDeleteConfirmModal.value = false;
    selectedTemplate.value = null;
    
    // Afficher un message de succès
    alert('Template supprimé avec succès !');
  } catch (error) {
    console.error('Erreur lors de la suppression du template:', error);
    alert('Une erreur est survenue lors de la suppression du template.');
  } finally {
    isDeleting.value = false;
  }
}

// Fonction pour convertir la taille du QR en libellé
function getQrSizeLabel(size) {
  switch(size) {
    case 'small': return 'Petit';
    case 'medium': return 'Moyen';
    case 'large': return 'Grand';
    default: return 'Moyen';
  }
}

async function saveTemplate() {
  if (canSaveTemplate.value) {
    try {
      // Afficher un indicateur de chargement
      isSaving.value = true;
      
      // Vérifier si nous avons un PDF généré
      if (!newTemplate.value.generatedPdfFile) {
        alert('Veuillez d\'abord générer un aperçu du document et confirmer.');
        isSaving.value = false;
        return;
      }
      
      // Préparer les données pour l'API
      const templateData = {
        name: newTemplate.value.name,
        qr_size: newTemplate.value.qrPositions.qr.size,
        page_application: newTemplate.value.qrPositions.mode,
        qr_positions: newTemplate.value.qrPositions.qr.positions,
        signature_positions: newTemplate.value.qrPositions.signature ? 
                            newTemplate.value.qrPositions.signature.positions : null,
        signature_size: newTemplate.value.qrPositions.signature ? 
                       newTemplate.value.qrPositions.signature.size : 50,
        selected_pages: newTemplate.value.qrPositions.qr.pages !== 'all' ? 
                       newTemplate.value.qrPositions.qr.pages : []
      };
      
      // Si nous avons le fichier PDF original, l'ajouter
      if (newTemplate.value.file) {
        templateData.original_document = newTemplate.value.file;
      }
      
      // Si nous avons une image de signature, l'ajouter
      if (newTemplate.value.signatureImage) {
        templateData.signature_image = newTemplate.value.signatureImage;
      }
      
      // Si nous avons un PDF généré, l'ajouter
      if (newTemplate.value.generatedPdfFile) {
        templateData.preview_document = newTemplate.value.generatedPdfFile;
      }
      
      let response;
      
      // Si nous sommes en mode édition, mettre à jour le template existant
      if (newTemplate.value.isEditing && newTemplate.value.id) {
        response = await TemplateService.updateTemplate(newTemplate.value.id, templateData);
        
        // Mettre à jour le template dans la liste locale
        const index = templates.value.findIndex(t => t.id === newTemplate.value.id);
        if (index !== -1) {
          templates.value[index] = {
            ...templates.value[index],
            name: templateData.name,
            qrSize: templateData.qr_size,
            pageApplication: templateData.page_application,
          };
        }
      } else {
        // Sinon, créer un nouveau template
        response = await TemplateService.createTemplate(templateData);
        
        // Créer une copie du template avec la date actuelle
        const now = new Date();
        const formattedDate = now.toLocaleDateString('fr-FR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
        
        // Ajouter à la liste des templates avec l'ID retourné par l'API
        const templateToSave = {
          id: response.id.toString(),
          name: templateData.name,
          date: formattedDate,
          qrSize: templateData.qr_size,
          pageApplication: templateData.page_application
        };
        
        templates.value.unshift(templateToSave);
      }
      
      // Afficher un message de succès
      alert(newTemplate.value.isEditing ? 
            'Template mis à jour avec succès !' : 
            'Template enregistré avec succès !');
      
      // Réinitialiser le formulaire
      newTemplate.value = {
        name: '',
        file: null,
        qrPositions: null,
        date: '',
        signatureImage: null,
        generatedPdfFile: null,
        generatedPdfBlob: null,
        generatedPdfDataUrl: null
      };
      
      // Fermer la modale
      showNewTemplateModal.value = false;
    } catch (error) {
      console.error('Erreur lors de l\'opération sur le template:', error);
      alert('Une erreur est survenue lors de l\'opération sur le template. Veuillez réessayer.');
    } finally {
      isSaving.value = false;
    }
  }
}
</script>

<style scoped>
/* Importation des animations */
@import '@/assets/css/animations.css';

/* Styles généraux */
.dashboard-container {
  min-height: 100vh;
  position: relative;
  background-color: var(--bg-color);
  color: var(--text-color);
  overflow-x: hidden;
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
}

.particle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  animation: float 20s infinite linear;
  box-shadow: 0 0 10px 2px rgba(46, 139, 87, 0.2);
}

.particle-primary {
  background-color: var(--primary-color);
}

.particle-accent {
  background-color: var(--accent-color);
}

.particle-light {
  background-color: var(--primary-light);
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.5;
  }
  90% {
    opacity: 0.5;
  }
  100% {
    transform: translateY(-100vh) translateX(100vw) rotate(360deg);
    opacity: 0;
  }
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background-color: var(--bg-light);
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: 10;
  animation: slideInDown 0.8s forwards;
}

.logo-container {
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

.logo-icon {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-right: 10px;
  animation: pulse 2s infinite;
}

.badge-cert {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0 -5px;
  z-index: 2;
  animation: tada 2s infinite;
  animation-delay: 2s;
}

.badge-cert i {
  font-size: 1.3rem;
  color: #2c7be5;
}

/* Navigation */
.nav-menu ul {
  display: flex;
  list-style-type: none;
  margin: 0;
  padding: 0;
  gap: 20px;
  align-items: center;
}

.nav-link {
  color: var(--text-color);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 8px 15px;
  border-radius: 4px;
  position: relative;
}

.nav-link:hover, .nav-link.active {
  color: var(--primary-color);
}

.nav-link:before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background-color: var(--primary-color);
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.nav-link:hover:before, .nav-link.active:before {
  width: 80%;
}

/* User menu */
.user-menu {
  position: relative;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 15px;
  border-radius: 30px;
  background-color: var(--bg-dark);
  transition: all 0.3s ease;
  max-width: 150px;
  overflow: hidden;
}

.user-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.9rem;
}

.user-info:hover {
  background-color: var(--primary-color);
  color: white;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  padding: 10px 0;
  min-width: 200px;
  display: none;
  z-index: 1000;
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.3s, transform 0.3s;
}

.user-menu:hover .dropdown-menu {
  display: block;
  opacity: 1;
  transform: translateY(0);
  animation: fadeIn 0.3s forwards;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  color: var(--text-color);
  text-decoration: none;
  transition: all 0.3s ease;
}

.dropdown-item:hover {
  background-color: var(--bg-dark);
  color: var(--primary-color);
}

.dropdown-item hr {
  margin: 10px 0;
  border: none;
  border-top: 1px solid var(--border-color);
}

/* Mobile menu toggle */
.mobile-menu-toggle {
  display: none;
  font-size: 1.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mobile-menu-toggle.active i {
  transform: rotate(90deg);
}

/* Mobile menu close button */
.mobile-menu-close {
  display: none;
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 1.8rem;
  cursor: pointer;
  color: var(--text-color);
  transition: all 0.3s ease;
}

.mobile-menu-close:hover {
  color: var(--primary-color);
  transform: scale(1.1);
}

/* Main content */
.main-content {
  padding: 40px;
  position: relative;
  z-index: 1;
  max-width: 1750px;
  margin: 0 auto;
}

/* Welcome section */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 30px;
  background-color: var(--card-bg);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  transition: transform 0.5s ease, box-shadow 0.5s ease;
}

.welcome-section:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.welcome-title {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.highlight-text {
  color: var(--primary-color);
  position: relative;
}

.highlight-text::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  border-radius: 3px;
}

.welcome-subtitle {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.quick-actions {
  display: flex;
  gap: 15px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-button.primary {
  background-color: var(--primary-color);
  color: white;
}

.action-button.accent {
  background-color: var(--accent-color);
  color: white;
}

.action-button:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* Stats section */
.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 25px;
  display: flex;
  align-items: flex-start;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  opacity: 0;
  transform: translateY(20px);
}

.stat-card.animated {
  opacity: 1;
  transform: translateY(0);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-right: 15px;
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
}

.stat-icon.primary {
  background-color: rgba(58, 134, 255, 0.1);
  color: var(--primary-color);
}

.stat-icon.accent {
  background-color: rgba(76, 181, 142, 0.1);
  color: var(--accent-color);
}

.stat-icon.neutral {
  background-color: rgba(108, 117, 125, 0.1);
  color: var(--neutral-color);
}

.stat-icon.success {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
  font-weight: 600;
}

.stat-trend.up {
  color: #28a745;
}

.stat-trend.down {
  color: #dc3545;
}

.stat-trend.neutral {
  color: var(--neutral-color);
}

/* Charts section */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.chart-section {
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 25px;
  box-shadow: var(--shadow-sm);
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease;
}

.chart-section.animated {
  opacity: 1;
  transform: translateY(0);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.primary {
  background-color: var(--primary-color);
}

.legend-color.accent {
  background-color: var(--accent-color);
}

.chart-container {
  height: 300px;
  position: relative;
}

/* History section */
.history-section {
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 25px;
  box-shadow: var(--shadow-sm);
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease;
}

.history-section.animated {
  opacity: 1;
  transform: translateY(0);
}

.view-all-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 15px;
  border-radius: 20px;
  background-color: var(--bg-dark);
  color: var(--text-color);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 12px;
  background-color: var(--bg-dark);
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateX(-20px);
  border: 1px solid transparent;
}

.history-item.animated {
  opacity: 1;
  transform: translateX(0);
}

.history-item:hover {
  transform: translateX(5px);
  background-color: var(--hover-bg);
  border-left: 3px solid var(--primary-color);
  box-shadow: 0 4px 12px rgba(var(--primary-color-rgb), 0.15);
}

.history-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.history-item:hover .history-icon {
  transform: scale(1.1) rotate(5deg);
}

.history-icon.signed {
  background-color: rgba(58, 134, 255, 0.1);
  color: var(--primary-color);
}

.history-icon.shared {
  background-color: rgba(76, 181, 142, 0.1);
  color: var(--accent-color);
}

.history-icon.verified {
  background-color: rgba(108, 117, 125, 0.1);
  color: var(--neutral-color);
}

.history-content {
  flex: 1;
}

.history-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.history-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.history-time {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

/* Animations améliorées */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInDown {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes tada {
  0% { transform: scale(1); }
  10%, 20% { transform: scale(0.9) rotate(-3deg); }
  30%, 50%, 70%, 90% { transform: scale(1.1) rotate(3deg); }
  40%, 60%, 80% { transform: scale(1.1) rotate(-3deg); }
  100% { transform: scale(1) rotate(0); }
}

/* Responsive design amélioré */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-section {
    padding: 25px;
  }
  
  .welcome-title {
    font-size: 2.2rem;
  }
  
  .chart-container {
    height: 250px;
  }
}

@media (max-width: 992px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .quick-actions {
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .nav-menu {
    position: fixed;
    top: 0;
    right: -100%;
    width: 250px;
    height: 100vh;
    background-color: var(--bg-light);
    box-shadow: var(--shadow-lg);
    transition: right 0.3s ease;
    z-index: 1000;
    padding: 80px 20px 20px;
  }
  
  .nav-menu.active {
    right: 0;
  }
  
  .nav-menu ul {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .mobile-menu-close {
    display: block;
  }
  
  .chart-container {
    height: 220px;
  }
  
  .user-info {
    max-width: 120px;
  }
  
  .user-name {
    max-width: 70px;
  }

  .main-content {
    padding: 30px;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 15px 20px;
  }

  .main-content {
    padding: 20px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .welcome-title {
    font-size: 2rem;
  }
  
  .logo-text {
    font-size: 1.3rem;
  }
  
  .header-logo-img {
    width: 35px;
  }
  
  .chart-container {
    height: 200px;
  }
  
  .chart-legend {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .legend-item {
    margin-bottom: 4px;
  }
  
  .username-truncate {
    max-width: 150px;
  }
}

@media (max-width: 576px) {
  .quick-actions {
    flex-direction: column;
    width: 100%;
  }

  .action-button {
    width: 100%;
    justify-content: center;
  }

  .history-item {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }
  
  .history-icon {
    margin: 0 auto 10px;
  }

  .history-time {
    margin-top: 10px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .view-all-btn {
    align-self: flex-start;
  }
  
  .chart-container {
    height: 180px;
  }
  
  .user-info {
    max-width: 80px;
  }
  
  .user-name {
    max-width: 30px;
  }

  .main-content {
    padding: 15px;
  }

  .header-logo-img {
    width: 30px;
  }
  
  .logo-text {
    font-size: 1.1rem;
  }
}

/* Dark mode optimisé */
:global(.dark-theme) .stat-card,
:global(.dark-theme) .chart-section,
:global(.dark-theme) .history-section,
:global(.dark-theme) .welcome-section {
  background-color: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .history-item {
  background-color: rgba(255, 255, 255, 0.05);
}

:global(.dark-theme) .history-item:hover {
  background-color: rgba(58, 134, 255, 0.15);
}

:global(.dark-theme) .stat-icon.primary {
  background-color: rgba(58, 134, 255, 0.2);
}

:global(.dark-theme) .stat-icon.accent {
  background-color: rgba(76, 181, 142, 0.2);
}

:global(.dark-theme) .stat-icon.neutral {
  background-color: rgba(108, 117, 125, 0.2);
}

:global(.dark-theme) .stat-icon.success {
  background-color: rgba(40, 167, 69, 0.2);
}

:global(.dark-theme) .user-info {
  background-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme) .user-info:hover {
  background-color: var(--primary-color);
}

:global(.dark-theme) .dropdown-menu {
  background-color: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .dropdown-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme) .view-all-btn {
  background-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme) .view-all-btn:hover {
  background-color: var(--primary-color);
}

:global(.dark-theme) .nav-link:hover,
:global(.dark-theme) .nav-link.active {
  color: var(--primary-light);
}

:global(.dark-theme) .nav-link:before {
  background-color: var(--primary-light);
}

/* Ajout d'une variable pour les couleurs RGB */
:root {
  --primary-color-rgb: 58, 134, 255;
  --accent-color-rgb: 76, 181, 142;
}

/* Responsive charts */
.responsive-chart {
  height: 300px;
  position: relative;
  width: 100%;
}

/* History items hover effect */
.history-item {
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.history-item:hover {
  background-color: var(--hover-bg);
  border-left: 3px solid var(--primary-color);
  transform: translateX(5px);
}

.history-item:hover .history-icon {
  transform: scale(1.1) rotate(5deg);
}

.history-item:hover .history-title {
  color: var(--primary-color);
}

/* Username truncation */
.username-truncate {
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

/* Composant intégré */
.integrated-component-container {
  position: relative;
  animation: fadeIn 0.5s ease-out forwards;
  opacity: 0;
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

.history-component {
  position: relative;
  background: var(--card-bg);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  padding: 25px;
  margin: 20px;
  overflow: hidden;
  animation: slideUp 0.6s cubic-bezier(0.23, 1, 0.32, 1) forwards;
  transform: translateY(40px);
  opacity: 0;
  isolation: isolate; /* Create stacking context */
}

.history-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(to bottom, var(--primary-color), var(--accent-color, #6c5ce7));
  background-size: 100% 200px;
  background-position: 0 100%;
  background-repeat: no-repeat;
  opacity: 0.05;
  z-index: -1;
  border-radius: inherit;
}

.history-bg-circles {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: inherit;
  z-index: -1;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, var(--primary-color), transparent 70%);
  opacity: 0.1;
  animation: pulse 10s infinite alternate ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 500px;
  height: 500px;
  bottom: -200px;
  right: -100px;
  background: radial-gradient(circle at 70% 70%, var(--accent-color, #6c5fe5), transparent 70%);
  animation-delay: 3s;
}

.circle-3 {
  width: 400px;
  height: 400px;
  top: 50%;
  left: -200px;
  background: radial-gradient(circle at 30% 30%, var(--info-color, #0dcaf0), transparent 70%);
  animation-delay: 6s;
  animation-duration: 15s;
}

@keyframes pulse {
  0% {
    transform: scale(1) translate(0, 0);
    opacity: 0.1;
  }
  50% {
    transform: scale(1.05) translate(10px, -10px);
    opacity: 0.15;
  }
  100% {
    transform: scale(0.95) translate(-5px, 5px);
    opacity: 0.08;
  }
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

@media (max-width: 992px) {
  .history-component {
    margin: 15px;
    padding: 20px;
  }
  
  .circle-1 {
    width: 200px;
    height: 200px;
  }
  
  .circle-2 {
    width: 300px;
    height: 300px;
  }
  
  .circle-3 {
    width: 250px;
    height: 250px;
  }
}

@media (max-width: 768px) {
  .history-component {
    margin: 10px;
    padding: 15px;
    border-radius: 15px;
  }
  
  .integrated-component-container {
    padding: 0;
  }
}

/* Styles pour le message de maintenance */
.placeholder-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin: 2rem auto;
}

.placeholder-message .icon-xl {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.placeholder-message h3 {
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.placeholder-message p {
  margin-bottom: 1.5rem;
  color: var(--text-color);
}

.placeholder-message .btn {
  min-width: 200px;
}

:global(.dark-theme) .placeholder-message {
  background: rgba(30, 41, 59, 0.9);
  color: #f1f5f9;
}

:global(.dark-theme) .placeholder-message p {
  color: #cbd5e1;
}

@media (max-width: 576px) {
  .history-component {
    margin: 5px;
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  }
  
  .circle {
    opacity: 0.05;
  }
}

@keyframes slideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Styles pour les templates */
.templates-section {
  width: 100%;
  padding: 20px;
}

.empty-templates {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  text-align: center;
}

.empty-templates i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: var(--text-secondary);
}

.empty-templates p {
  font-size: 1.2rem;
  margin-bottom: 20px;
  color: var(--text-secondary);
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.template-card {
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  padding: 15px;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
}

.template-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.template-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  margin-right: 10px;
}

.template-status {
  padding: 5px 10px;
  border-radius: 4px;
  background-color: #dc3545;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
}

.template-content {
  flex: 1;
}

.template-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.template-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.template-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
}

.template-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.preview {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.action-btn.preview:hover {
  background-color: var(--primary-color);
  color: white;
}

.action-btn.edit {
  background-color: var(--primary-light);
  color: var(--primary-color);
}

.action-btn.edit:hover {
  background-color: var(--primary-color);
  color: white;
}

.action-btn.delete {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.action-btn.delete:hover {
  background-color: #dc3545;
  color: white;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000; /* Augmenter cette valeur pour être sûr que la modale est au-dessus de tous les éléments */
  overflow-y: auto;
  padding: 20px;
}

.modal-container {
  background-color: var(--bg-light);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: fadeInUp 0.3s ease-out;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.modal-close:hover {
  color: var(--primary-color);
  transform: scale(1.1);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.modal-footer {
  padding: 15px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--border-color);
}

.template-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.2);
  outline: none;
}

.file-input-container {
  position: relative;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.file-label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.file-label:hover {
  border-color: var(--primary-color);
  background-color: rgba(var(--primary-color-rgb), 0.05);
}

.file-label i {
  font-size: 1.5rem;
  color: #dc3545;
}

.qr-positioner-wrapper {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  background-color: var(--bg-dark);
}

/* Responsive pour la modale */
@media (max-width: 992px) {
  .modal-container {
    width: 95%;
  }
}

@media (max-width: 768px) {
  .modal-container {
    width: 100%;
    max-height: 95vh;
  }
  
  .modal-body {
    max-height: calc(95vh - 130px);
  }
  
  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  }
}

@media (max-width: 576px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-header {
    padding: 15px;
  }
  
  .modal-body {
    padding: 15px;
  }
  
  .modal-footer {
    padding: 15px;
    flex-direction: column;
  }
  
  .modal-footer button {
    width: 100%;
  }
}

/* Dark mode styles */
:global(.dark-theme) .template-card {
  background-color: rgba(30, 41, 59, 0.7);
}

:global(.dark-theme) .template-preview {
  background-color: rgba(15, 23, 42, 0.7);
}

:global(.dark-theme) .modal-container {
  background-color: rgba(30, 41, 59, 0.95);
}

:global(.dark-theme) .qr-positioner-wrapper {
  background-color: rgba(15, 23, 42, 0.7);
}

:global(.dark-theme) .file-label:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme) .form-control {
  background-color: rgba(15, 23, 42, 0.7);
  color: #f1f5f9;
}

/* Animation */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Template Cards Enhanced Styles */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.template-card {
  background-color: var(--card-bg, #ffffff);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.07);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color, #eaeaea);
  padding: 20px;
  height: 100%;
  transform-origin: center bottom;
  animation: fadeIn 0.5s ease-out;
  animation-fill-mode: both;
}

.template-card:nth-child(1) { animation-delay: 0.1s; }
.template-card:nth-child(2) { animation-delay: 0.2s; }
.template-card:nth-child(3) { animation-delay: 0.3s; }
.template-card:nth-child(4) { animation-delay: 0.4s; }
.template-card:nth-child(n+5) { animation-delay: 0.5s; }

.template-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color, #3a86ff);
}

.template-badge {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.template-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(220, 53, 69, 0.1);
  transition: all 0.3s ease;
}

.template-icon i {
  font-size: 1.5rem;
  color: #dc3545;
}

.template-card:hover .template-icon {
  transform: scale(1.1) rotate(5deg);
}

.template-meta {
  display: flex;
  flex-direction: column;
  margin-top: 10px;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-secondary, #6c757d);
}

.meta-item i {
  font-size: 1rem;
  width: 20px;
  color: var(--primary-color);
}

/* Empty Templates */
.empty-templates {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  text-align: center;
}

.empty-templates i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: var(--text-secondary);
  opacity: 0.5;
}

.empty-templates p {
  font-size: 1.2rem;
  margin-bottom: 20px;
  color: var(--text-secondary);
}

/* Loading State */
.loading-state, .loading-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(var(--primary-color-rgb), 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

/* Preview Modal */
.preview-modal {
  background-color: var(--bg-light);
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 1000px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  animation: modalIn 0.3s ease-out;
}

.preview-body {
  flex: 1;
  padding: 0;
  position: relative;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background-color: #fff;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--danger-color);
}

.preview-error i {
  font-size: 3rem;
  margin-bottom: 20px;
}

/* Confirm Modal */
.confirm-modal {
  background-color: var(--bg-light);
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  animation: modalIn 0.3s ease-out;
}

.text-danger {
  color: var(--danger-color);
}

/* Animation for modals */
@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Fix for the spin animation used in buttons */
.spin {
  display: inline-block;
  animation: spin 1s linear infinite;
}

:global(.dark-theme) .template-icon {
  background-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme) .template-badge {
  background-color: rgba(220, 53, 69, 0.2);
}

:global(.dark-theme) .preview-modal,
:global(.dark-theme) .confirm-modal {
  background-color: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(10px);
}

@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
  
  .preview-modal {
    width: 95%;
    height: 90vh;
  }
}

@media (max-width: 576px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
}

/* Section Templates Styling */
.section-card {
  background-color: var(--card-bg);
  border-radius: 16px;
  box-shadow: var(--shadow-md);
  padding: 25px;
  position: relative;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-title {
  font-size: 28px;
  margin: 0;
  position: relative;
  color: var(--text-color);
  font-weight: 600;
  display: inline-block;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 60px;
  height: 3px;
  background: var(--primary-color);
  border-radius: 3px;
}

/* Templates Grid */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

/* Template Card */
.template-card {
  background-color: var(--card-bg, #ffffff);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.07);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color, #eaeaea);
  padding: 20px;
  height: 100%;
  transform-origin: center bottom;
  animation: fadeIn 0.5s ease-out;
  animation-fill-mode: both;
}

.template-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color, #3a86ff);
}

/* Template Header */
.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.template-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  transition: all 0.3s ease;
}

.template-card:hover .template-icon {
  transform: scale(1.1) rotate(5deg);
}

.template-badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

/* Template Content */
.template-content {
  padding: 20px 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.template-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #333);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Template Meta */
.template-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: auto;
  padding-top: 15px;
  font-size: 13px;
  color: var(--text-secondary, #6c757d);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-item i {
  width: 16px;
  text-align: center;
  color: var(--text-secondary, #6c757d);
  opacity: 0.7;
}

/* Template Actions */
.template-main-actions {
  display: flex;
  gap: 10px;
  padding: 12px 15px;
  border-top: 1px solid var(--border-color, #f0f0f0);
}

.action-btn {
  padding: 8px 15px;
  font-size: 14px;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border: none;
  flex: 1;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1.275);
  letter-spacing: 0.2px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  text-transform: uppercase;
}

.action-btn.full-width {
  flex: 2;
}

.action-btn.primary {
  background-color: var(--primary-color, #007bff);
  color: white;
}

.action-btn.primary:hover {
  background-color: var(--primary-dark, #0069d9);
  box-shadow: 0 5px 15px rgba(0, 123, 255, 0.3);
  transform: translateY(-2px);
}

.action-btn.secondary {
  background-color: var(--light-bg, #f8f9fa);
  color: var(--text-color, #495057);
  border: 1px solid var(--border-color, #ddd);
}

.action-btn.secondary:hover {
  background-color: var(--hover-bg, #e9ecef);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Template Secondary Actions */
.template-secondary-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  padding: 5px 15px 15px;
  border-top: 1px solid rgba(0, 0, 0, 0.03);
}

.action-btn.text {
  background: transparent;
  color: var(--text-secondary, #6c757d);
  border: none;
  box-shadow: none;
  padding: 8px 12px;
  text-transform: none;
  font-weight: 500;
  font-size: 14px;
  letter-spacing: normal;
}

.action-btn.text:hover {
  background-color: rgba(0, 0, 0, 0.03);
  color: var(--danger-color, #dc3545);
  box-shadow: none;
  transform: none;
}

.action-btn i {
  margin-right: 6px;
}

/* Empty Templates */
.empty-templates {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  text-align: center;
  min-height: 300px;
}

.empty-templates i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: var(--text-secondary);
  opacity: 0.5;
}

.empty-templates p {
  font-size: 1.2rem;
  margin-bottom: 20px;
  color: var(--text-secondary);
}

/* Loading State */
.loading-state, .loading-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(var(--primary-color-rgb), 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

/* Preview Modal */
.preview-modal {
  background-color: var(--bg-light);
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 1000px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  animation: modalIn 0.3s ease-out;
}

.preview-body {
  flex: 1;
  padding: 0;
  position: relative;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background-color: #fff;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--danger-color);
}

.preview-error i {
  font-size: 3rem;
  margin-bottom: 20px;
}

/* Confirm Modal */
.confirm-modal {
  background-color: var(--bg-light);
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  animation: modalIn 0.3s ease-out;
}

.text-danger {
  color: var(--danger-color);
}

/* Dark Mode Optimization */
:global(.dark-theme) .template-card {
  background-color: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .template-icon {
  background-color: rgba(255, 255, 255, 0.1);
}

:global(.dark-theme) .template-badge {
  background-color: rgba(220, 53, 69, 0.2);
}

:global(.dark-theme) .preview-modal,
:global(.dark-theme) .confirm-modal {
  background-color: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(10px);
}

@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
  
  .preview-modal {
    width: 95%;
    height: 90vh;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .section-title {
    margin-bottom: 15px;
  }
}

@media (max-width: 576px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .template-main-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}

/* Signature Options Modal */
.signature-options-modal {
  background-color: var(--bg-light);
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  animation: modalIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  z-index: 10001;
  position: relative;
}

.signature-options-body {
  padding: 30px;
}

.signature-options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.signature-option-card {
  background-color: var(--card-bg);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  padding: 25px;
  display: flex;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.signature-option-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.option-icon {
  width: 60px;
  height: 60px;
  min-width: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  transition: all 0.3s ease;
  font-size: 1.8rem;
}

.signature-option-card:hover .option-icon {
  transform: scale(1.1) rotate(5deg);
}

.option-icon.template {
  background-color: rgba(58, 134, 255, 0.1);
  color: var(--primary-color);
}

.option-icon.quick {
  background-color: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.option-icon.multiple {
  background-color: rgba(76, 181, 142, 0.1);
  color: var(--accent-color);
}

.option-content {
  flex: 1;
}

.option-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: var(--text-color);
}

.option-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.option-arrow {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.5rem;
  color: var(--text-secondary);
  opacity: 0.5;
  transition: all 0.3s ease;
}

.signature-option-card:hover .option-arrow {
  right: 15px;
  opacity: 1;
  color: var(--primary-color);
}

.option-badge {
  position: absolute;
  bottom: 15px;
  right: 15px;
  background-color: rgba(220, 53, 69, 0.9);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 5px;
}

.option-badge i {
  font-size: 14px;
}

.signature-option-card.multiple-option {
  position: relative;
  overflow: visible;
}

.signature-option-card.multiple-option::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    rgba(0, 0, 0, 0.02),
    rgba(0, 0, 0, 0.02) 10px,
    rgba(0, 0, 0, 0.05) 10px,
    rgba(0, 0, 0, 0.05) 20px
  );
  pointer-events: none;
  border-radius: 16px;
  opacity: 0.5;
}

/* Coming Soon Container */
.coming-soon-container {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
  padding: 60px 20px;
  animation: fadeIn 0.5s ease-out;
}

.coming-soon-icon {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  margin: 0 auto 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  color: white;
  animation: pulse 2s infinite;
}

.coming-soon-title {
  font-size: 2rem;
  margin-bottom: 20px;
  color: var(--text-color);
}

.coming-soon-description {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin-bottom: 30px;
  line-height: 1.6;
}

/* Template Selection Container */
.template-selection-container {
  max-width: 1400px;
  width: 90%;
  margin: 0 auto;
  padding: 40px 30px;
  animation: fadeIn 0.5s ease-out;
}

/* Template Selection Grid */
.template-selection-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 35px;
  margin-top: 40px;
  margin-bottom: 40px;
}

@media (max-width: 1200px) {
  .template-selection-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .signature-options-modal {
    width: 95%;
  }
  
  .signature-options-grid {
    grid-template-columns: 1fr;
  }
  
  .template-selection-grid {
    grid-template-columns: 1fr;
  }
  
  .signature-option-card {
    padding: 20px;
  }
  
  .option-icon {
    width: 50px;
    height: 50px;
    min-width: 50px;
    font-size: 1.5rem;
    margin-right: 15px;
  }
}

.template-selection-grid .template-card {
  min-height: 280px;
  transform-origin: center center;
  padding: 25px;
}

.template-selection-grid .template-icon {
  width: 60px;
  height: 60px;
  font-size: 1.8rem;
}

.template-selection-grid .template-title {
  font-size: 20px;
  margin-bottom: 15px;
}

.template-selection-grid .meta-item {
  font-size: 14px;
  margin-bottom: 5px;
}

.template-selection-grid .action-btn {
  padding: 14px 20px;
  font-size: 16px;
  margin-top: 15px;
  white-space: nowrap;
  height: auto;
  min-height: 50px;
  width: 100%;
  text-transform: none;
  letter-spacing: 0.5px;
}

.sign-template-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-weight: 600;
  padding: 16px 24px;
  border-radius: 25px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(var(--primary-color-rgb), 0.3);
}

.sign-template-btn i {
  font-size: 18px;
  margin: 0;
}

.sign-template-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(var(--primary-color-rgb), 0.4);
}
</style>