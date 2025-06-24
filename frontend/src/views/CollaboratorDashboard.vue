<template>
  <div class="collaborator-dashboard">
    <!-- Fond animé avec particules -->
    <div class="particles-container">
      <div v-for="i in 12" :key="i" class="particle" 
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
          <span class="role-badge collaborator top-right-of-logo">Collaborateur</span>
        </div>
        
        <div class="user-info">
          <div class="organization-info">
            <div class="org-name-wrapper">
              <span class="org-name">{{ organizationName }}</span>
              <span v-if="organizationStatus" 
                    class="status-badge org-status top-right-of-org-name" 
                    :class="`org-status-${organizationStatus?.toLowerCase()}`">
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
            <span class="underlined-text">Préparation de <span class="highlight-text">documents</span></span>
          </h2>
          <p class="welcome-description">
            Préparez et organisez les documents pour la signature électronique
          </p>
          
          <!-- Indicateur d'organisation active -->
          <div class="organization-filter-info">
            <i class="bi bi-filter-circle"></i>
            <span>Données filtrées pour l'organisation <strong>{{ organizationName }}</strong></span>
            <button @click="refreshData" class="refresh-btn" title="Actualiser les données">
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </section>

      <!-- Statistiques -->
      <section class="stats-section">
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.thisWeek }}</div>
              <div class="stat-label">Documents cette semaine</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-calendar-week"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.thisMonth }}</div>
              <div class="stat-label">Documents ce mois</div>
            </div>
            <div class="stat-icon accent">
              <i class="bi bi-calendar-month"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.avgTime }}</div>
              <div class="stat-label">Temps moyen de traitement</div>
            </div>
            <div class="stat-icon warning">
              <i class="bi bi-clock"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Actions rapides -->
      <section class="quick-actions">
        <div class="actions-grid">
          <button class="action-card primary" @click="openPrepareDocument">
            <div class="action-icon">
              <i class="bi bi-file-earmark-plus"></i>
            </div>
            <span class="action-title">Nouveau document</span>
            <span class="action-description">Préparer un document pour signature</span>
          </button>
          <button class="action-card" @click="activeSection = 'drafts'" :class="{ 'active': activeSection === 'drafts' }">
            <div class="action-icon accent">
              <i class="bi bi-file-earmark-text"></i>
            </div>
            <span class="action-title">Brouillons</span>
            <span class="action-description">{{ drafts.length }} documents en préparation</span>
          </button>
          <button class="action-card" @click="activeSection = 'pending'" :class="{ 'active': activeSection === 'pending' }">
            <div class="action-icon warning">
              <i class="bi bi-hourglass-split"></i>
            </div>
            <span class="action-title">En attente</span>
            <span class="action-description">{{ pendingDocuments.length }} documents assignés</span>
          </button>
          <button class="action-card" @click="activeSection = 'completed'" :class="{ 'active': activeSection === 'completed' }">
            <div class="action-icon success">
              <i class="bi bi-file-check"></i>
            </div>
            <span class="action-title">Terminés</span>
            <span class="action-description">{{ completedDocuments.length }} documents signés</span>
          </button>
        </div>
      </section>

      <!-- Contenu dynamique selon la section active -->
      <section class="content-section" v-if="activeSection">
        <!-- Brouillons -->
        <div v-if="activeSection === 'drafts'" class="section-content">
          <div class="section-header">
            <h3 class="content-title">
              <i class="bi bi-file-earmark-text"></i>
              Documents en préparation
            </h3>
            <button class="btn-primary" @click="openPrepareDocument">
              <i class="bi bi-plus"></i>
              Nouveau document
            </button>
          </div>
          
          <div class="documents-list">
            <div v-for="doc in drafts" :key="doc.id" class="document-item">
              <div class="doc-info">
                <i class="bi bi-file-earmark"></i>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.name }}</span>
                  <span class="doc-meta">Créé le {{ formatDate(doc.createdAt) }}</span>
                </div>
              </div>
              <div class="doc-status">
                <span class="status-badge draft">Brouillon</span>
                <div class="doc-actions">
                  <button class="btn-icon primary" title="Continuer l'édition" @click="continueEdit(doc)">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn-icon success" title="Assigner pour signature" @click="assignForSignature(doc)">
                    <i class="bi bi-person-check"></i>
                  </button>
                  <button class="btn-icon danger" title="Supprimer" @click="deleteDraft(doc)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="drafts.length === 0" class="empty-state">
              <i class="bi bi-file-earmark-plus"></i>
              <p>Aucun brouillon</p>
              <button class="btn-primary" @click="openPrepareDocument">
                Créer votre premier document
              </button>
            </div>
          </div>
        </div>

        <!-- Documents en attente -->
        <div v-if="activeSection === 'pending'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-hourglass-split"></i>
            Documents en attente de signature
          </h3>
          
          <div class="documents-list">
            <div v-for="doc in pendingDocuments" :key="doc.id" class="document-item">
              <div class="doc-info">
                <i class="bi bi-file-earmark-clock"></i>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.name }}</span>
                  <span class="doc-meta">Assigné à {{ doc.assignedTo }} le {{ formatDate(doc.assignedAt) }}</span>
                </div>
              </div>
              <div class="doc-status">
                <div class="status-info">
                  <span class="time-elapsed">{{ getTimeElapsed(doc.assignedAt) }}</span>
                  <span class="status-badge pending">En attente</span>
                </div>
                <div class="doc-actions">
                  <button class="btn-icon" title="Voir détails">
                    <i class="bi bi-eye"></i>
                  </button>
                  <button class="btn-icon warning" title="Relancer" @click="remindSigner(doc)">
                    <i class="bi bi-bell"></i>
                  </button>
                  <button class="btn-icon" title="Réassigner">
                    <i class="bi bi-arrow-repeat"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="pendingDocuments.length === 0" class="empty-state">
              <i class="bi bi-hourglass-split"></i>
              <p>Aucun document en attente</p>
            </div>
          </div>
        </div>

        <!-- Documents terminés -->
        <div v-if="activeSection === 'completed'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-file-check"></i>
            Documents signés
          </h3>
          
          <div class="documents-list">
            <div v-for="doc in completedDocuments" :key="doc.id" class="document-item">
              <div class="doc-info">
                <i class="bi bi-file-earmark-check"></i>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.name }}</span>
                  <span class="doc-meta">Signé par {{ doc.signedBy }} le {{ formatDate(doc.signedAt) }}</span>
                </div>
              </div>
              <div class="doc-status">
                <span class="status-badge signed">Signé</span>
                <div class="doc-actions">
                  <button class="btn-icon" title="Télécharger">
                    <i class="bi bi-download"></i>
                  </button>
                  <button class="btn-icon" title="Vérifier signature">
                    <i class="bi bi-shield-check"></i>
                  </button>
                  <button class="btn-icon" title="Partager">
                    <i class="bi bi-share"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="completedDocuments.length === 0" class="empty-state">
              <i class="bi bi-file-check"></i>
              <p>Aucun document signé</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Section par défaut si aucune section active -->
      <section v-if="!activeSection" class="default-content">
        <div class="welcome-card">
          <div class="welcome-icon">
            <i class="bi bi-person-workspace"></i>
          </div>
          <h3>Bienvenue dans votre espace de travail</h3>
          <p>Gérez vos documents et suivez leur progression de signature</p>
          <button class="btn-primary" @click="openPrepareDocument">
            <i class="bi bi-file-earmark-plus"></i>
            Commencer maintenant
          </button>
        </div>
      </section>
    </main>

    <!-- Modal de choix du type de préparation -->
    <div v-if="showPrepareChoice" class="modal-overlay">
      <div class="preparation-choice-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">
              <i class="bi bi-file-earmark-plus"></i>
              Préparer un document
            </h3>
            <button @click="closePrepareChoice" class="close-button">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          
          <div class="modal-body">
            <p class="choice-description">
              Comment souhaitez-vous préparer votre document ?
            </p>
            
            <div class="preparation-options">
              <!-- Option Template -->
              <div class="preparation-option" @click="selectTemplatePreparation">
                <div class="option-icon template">
                  <i class="bi bi-file-earmark-richtext"></i>
                </div>
                <div class="option-content">
                  <h4 class="option-title">À partir d'un template</h4>
                  <p class="option-description">
                    Utiliser un modèle existant avec positions prédéfinies pour QR code et signature
                  </p>
                  <div class="option-features">
                    <span class="feature">
                      <i class="bi bi-check2"></i>
                      Positions pré-configurées
                    </span>
                    <span class="feature">
                      <i class="bi bi-check2"></i>
                      Processus accéléré
                    </span>
                    <span class="feature">
                      <i class="bi bi-check2"></i>
                      Cohérence organisationnelle
                    </span>
                  </div>
                </div>
                <div class="option-arrow">
                  <i class="bi bi-chevron-right"></i>
                </div>
              </div>
              
              <!-- Option Directe -->
              <div class="preparation-option" @click="selectDirectPreparation">
                <div class="option-icon direct">
                  <i class="bi bi-file-earmark"></i>
                </div>
                <div class="option-content">
                  <h4 class="option-title">Préparation directe</h4>
                  <p class="option-description">
                    Préparer le document manuellement en définissant vous-même les positions
                  </p>
                  <div class="option-features">
                    <span class="feature">
                      <i class="bi bi-check2"></i>
                      Contrôle total
                    </span>
                    <span class="feature">
                      <i class="bi bi-check2"></i>
                      Personnalisation maximale
                    </span>
                    <span class="feature">
                      <i class="bi bi-check2"></i>
                      Flexibilité complète
                    </span>
                  </div>
                </div>
                <div class="option-arrow">
                  <i class="bi bi-chevron-right"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pour la préparation de document directe -->
    <div v-if="showPrepareDocument" class="modal-overlay">
      <prepare-document 
        @close="closePrepareDocument" 
        @documentPrepared="onDocumentPrepared"
      />
    </div>

    <!-- Modal pour la préparation avec template -->
    <div v-if="showTemplatePreparation" class="modal-overlay">
      <div class="template-preparation-modal">
        <div class="modal-content large">
          <div class="modal-header">
            <h3 class="modal-title">
              <i class="bi bi-file-earmark-richtext"></i>
              Préparer avec un template
            </h3>
            <button @click="closeTemplatePreparation" class="close-button">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          
          <div class="modal-body">
            <p class="template-description">
              Sélectionnez un template existant pour préparer votre document rapidement.
            </p>
            
            <!-- Ici on intégrera la sélection de templates -->
            <div class="coming-soon">
              <i class="bi bi-hourglass-split"></i>
              <h4>Fonctionnalité en cours de développement</h4>
              <p>La préparation avec templates sera bientôt disponible.</p>
              <button @click="selectDirectPreparation" class="btn-primary">
                Utiliser la préparation directe
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import PrepareDocument from '@/views/PrepareDocument.vue';
import AuthService from '@/services/AuthService';

const router = useRouter();

// État réactif
const activeSection = ref('');
const userName = ref('');
const organizationName = ref('');
const organizationStatus = ref('');

// État pour l'affichage des modales
const showPrepareChoice = ref(false);
const showPrepareDocument = ref(false);
const showTemplatePreparation = ref(false);

// Statistiques
const stats = {
  thisWeek: ref(5),
  thisMonth: ref(18),
  avgTime: ref('2j')
};

// Documents brouillons
const drafts = ref([
  {
    id: 1,
    name: 'Contrat fournisseur - Brouillon.pdf',
    createdAt: new Date('2024-01-14')
  },
  {
    id: 2,
    name: 'Accord de partenariat.pdf',
    createdAt: new Date('2024-01-13')
  }
]);

// Documents en attente
const pendingDocuments = ref([
  {
    id: 1,
    name: 'Rapport annuel 2023.pdf',
    assignedTo: 'Directeur Général',
    assignedAt: new Date('2024-01-13')
  },
  {
    id: 2,
    name: 'Budget prévisionnel.pdf',
    assignedTo: 'Chef comptable',
    assignedAt: new Date('2024-01-12')
  }
]);

// Documents terminés
const completedDocuments = ref([
  {
    id: 1,
    name: 'Convention collective.pdf',
    signedBy: 'RH Manager',
    signedAt: new Date('2024-01-11')
  }
]);

// Positionnement des particules
const particlePositions = Array.from({ length: 12 }, () => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 6 + 3,
  duration: Math.random() * 25 + 20,
  delay: Math.random() * 8
}));

// Méthodes
function formatDate(date) {
  return new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  }).format(date);
}

function getTimeElapsed(date) {
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60));
    return `${hours}h`;
  }
  return `${days}j`;
}

function openPrepareDocument() {
  showPrepareChoice.value = true;
}

function closePrepareChoice() {
  showPrepareChoice.value = false;
}

function selectTemplatePreparation() {
  closePrepareChoice();
  showTemplatePreparation.value = true;
}

function selectDirectPreparation() {
  closePrepareChoice();
  showPrepareDocument.value = true;
}

function closePrepareDocument() {
  showPrepareDocument.value = false;
}

function closeTemplatePreparation() {
  showTemplatePreparation.value = false;
}

async function fetchDocuments() {
  try {
    // Récupérer l'ID de l'utilisateur connecté
    const user = AuthService.getCurrentUser();
    if (!user || !user.id) {
      console.error('Utilisateur non connecté ou ID manquant');
      return;
    }

    // Récupérer l'ID de l'organisation actuelle
    const organizationId = user?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    // Appel direct à l'API Django
    const token = localStorage.getItem('token');
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId  // Utiliser l'ID de l'organisation pour être cohérent
      }
    };

    // Utiliser l'endpoint by_collaborator qui retourne les documents par statut
    const response = await axios.get(`https://192.168.4.131:8000/api/documents/qr-positions/by_collaborator/`, config);
    
    if (response.data) {
      // Maintenant que le filtrage se fait automatiquement côté backend avec organization_id,
      // nous n'avons plus besoin de filtrer côté frontend
      // Mettre à jour les documents brouillons
      if (response.data.drafts) {
        drafts.value = response.data.drafts.map(doc => ({
          id: doc.id,
          name: doc.document_name,
          createdAt: new Date(doc.created_at),
          status: 'draft'
        }));
      }
      
      // Mettre à jour les documents en attente
      if (response.data.pending) {
        pendingDocuments.value = response.data.pending.map(doc => ({
          id: doc.id,
          name: doc.document_name,
          assignedAt: new Date(doc.created_at),
          assignedTo: doc.collaborator_username || 'En attente de signature',
          status: 'pending'
        }));
      }
      
      // Mettre à jour les documents complétés
      if (response.data.completed) {
        completedDocuments.value = response.data.completed.map(doc => ({
          id: doc.id,
          name: doc.document_name,
          signedAt: new Date(doc.updated_at),
          signedBy: doc.organization_name || 'Signataire',
          status: 'completed'
        }));
      }
      
      // Mettre à jour les statistiques en fonction des documents filtrés
      stats.thisWeek.value = response.data.stats?.this_week || 0;
      stats.thisMonth.value = response.data.stats?.this_month || 0;
      stats.avgTime.value = response.data.stats?.avg_time || '1j';
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des documents:', error);
  }
}

function onDocumentPrepared(document) {
  console.log('Document préparé:', document);
  
  // Si le document est un brouillon, l'ajouter à la liste des brouillons
  if (document.status === 'draft') {
    drafts.value.unshift({
      id: document.id,
      name: document.name,
      createdAt: new Date(),
      status: 'draft'
    });
  } 
  // Sinon, l'ajouter à la liste des documents en attente
  else if (document.status === 'pending_signature') {
    pendingDocuments.value.unshift({
      id: document.id,
      name: document.name,
      assignedAt: new Date(),
      status: 'pending',
      assignedTo: 'En attente de signature'
    });
  }
  
  // Actualiser les données
  fetchDocuments();
}

function continueEdit(doc) {
  console.log('Continuer l\'édition de:', doc.name);
  
  // Récupérer l'ID de l'organisation actuelle
  const user = AuthService.getCurrentUser();
  const organizationId = user?.organization?.id;
  
  if (!organizationId) {
    console.error('ID d\'organisation manquant');
    return;
  }
  
  // Rediriger vers la page d'édition avec l'ID du document et l'ID de l'organisation
  router.push({
    name: 'edit-document',
    params: { id: doc.id },
    query: { organization_id: organizationId }
  });
}

function assignForSignature(doc) {
  console.log('Assigner pour signature:', doc.name);
  
  // Récupérer l'ID de l'organisation actuelle
  const user = AuthService.getCurrentUser();
  const organizationId = user?.organization?.id;
  
  if (!organizationId) {
    console.error('ID d\'organisation manquant');
    return;
  }
  
  // Rediriger vers la page d'assignation avec l'ID du document et l'ID de l'organisation
  router.push({
    name: 'assign-document',
    params: { id: doc.id },
    query: { organization_id: organizationId }
  });
}

async function deleteDraft(doc) {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce brouillon ?')) {
    try {
      // Récupérer l'ID de l'organisation actuelle
      const user = AuthService.getCurrentUser();
      const organizationId = user?.organization?.id;
      
      if (!organizationId) {
        console.error('ID d\'organisation manquant');
        return;
      }
      
      // Appel à l'API pour supprimer le document
      const token = localStorage.getItem('token');
      await axios.delete(`http://192.168.4.131:8000/api/documents/qr-positions/${doc.id}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          organization_id: organizationId
        }
      });
      
      // Supprimer le document de la liste des brouillons
      const index = drafts.value.findIndex(d => d.id === doc.id);
      if (index > -1) {
        drafts.value.splice(index, 1);
      }
    } catch (error) {
      console.error('Erreur lors de la suppression du brouillon:', error);
    }
  }
}

async function remindSigner(doc) {
  console.log('Relancer le signataire pour:', doc.name);
  
  try {
    // Récupérer l'ID de l'organisation actuelle
    const user = AuthService.getCurrentUser();
    const organizationId = user?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }
    
    // Appel à l'API pour envoyer un rappel
    const token = localStorage.getItem('token');
    await axios.post(`http://192.168.4.131:8000/api/documents/remind/${doc.id}/`, 
      { organization_id: organizationId },
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    alert('Un rappel a été envoyé au signataire.');
  } catch (error) {
    console.error('Erreur lors de l\'envoi du rappel:', error);
    alert('Erreur lors de l\'envoi du rappel.');
  }
}

function logout() {
  AuthService.logout();
  router.push('/login');
}

function refreshData() {
  fetchDocuments();
}

// Initialisation
onMounted(() => {
  document.title = 'Collaborateur - Doc@uthANTIC';
  
  // Fonction pour charger les données de l'utilisateur et des documents
  function loadUserAndDocuments() {
    const user = AuthService.getCurrentUser();
    if (user) {
      userName.value = user.username || 'Utilisateur';
      
      if (user.organization && typeof user.organization === 'object') {
        organizationName.value = user.organization.name || 'Organisation Inconnue';
        organizationStatus.value = user.organization.status || 'inconnu';
      } else {
        organizationName.value = user.organization || 'Mon Organisation';
        organizationStatus.value = 'N/A';
      }
      
      // Récupérer les documents
      fetchDocuments();
    } else {
      router.push('/login');
    }
  }
  
  // Chargement initial des données
  loadUserAndDocuments();
  
  // Ajouter un écouteur d'événement pour détecter les changements d'organisation
  window.addEventListener('organization-changed', () => {
    console.log('Changement d\'organisation détecté. Actualisation des données...');
    loadUserAndDocuments();
  });
  
  // Nettoyage de l'écouteur lors de la destruction du composant
  return () => {
    window.removeEventListener('organization-changed', loadUserAndDocuments);
  };
});
</script>

<style scoped>
/* Styles généraux */
.collaborator-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, 
    var(--bg-color, #f8f9fa) 0%, 
    rgba(6, 255, 165, 0.05) 50%, 
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
  opacity: 0.15;
  animation: float 25s infinite linear;
  background: var(--accent-color, #06ffa5);
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.2;
  }
  90% {
    opacity: 0.2;
  }
  100% {
    transform: translateY(-100vh) translateX(50px) rotate(360deg);
    opacity: 0;
  }
}

/* En-tête */
.dashboard-header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(6, 255, 165, 0.2);
  padding: 1.25rem 2.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 15px rgba(6, 255, 165, 0.1);
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

.role-badge.collaborator.top-right-of-logo {
  position: relative;
  top: 0;
  right: 0;
  font-size: 0.8rem;
  padding: 0.25rem 0.55rem;
  line-height: 1.1;
  border-radius: 0.75rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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
  color: var(--accent-color, #06ffa5);
  font-size: 1.9rem;
  line-height: 1.2;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.05);
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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
  box-shadow: 0 2px 10px rgba(6, 255, 165, 0.12);
  border: 1px solid rgba(6, 255, 165, 0.15);
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
  color: var(--accent-color, #06ffa5);
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.2);
}

.logout-btn {
  background: transparent;
  border: 2px solid var(--accent-color, #06ffa5);
  color: var(--accent-color, #06ffa5);
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: var(--accent-color, #06ffa5);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(6, 255, 165, 0.3);
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
  background: linear-gradient(90deg, var(--accent-color, #06ffa5), #39ffb4, var(--accent-color, #06ffa5));
  background-size: 200% 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(6, 255, 165, 0.3);
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
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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

/* Indicateur d'organisation active */
.organization-filter-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: rgba(6, 255, 165, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  margin: 1.5rem auto 0;
  max-width: 80%;
  font-size: 0.9rem;
  color: var(--text-color, #333);
  border: 1px dashed rgba(6, 255, 165, 0.3);
}

.organization-filter-info i {
  color: var(--accent-color, #06ffa5);
  font-size: 1.1rem;
}

.organization-filter-info strong {
  color: var(--accent-color, #06ffa5);
  font-weight: 700;
}

.refresh-btn {
  background: transparent;
  border: none;
  color: var(--accent-color, #06ffa5);
  cursor: pointer;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.5rem;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background-color: rgba(6, 255, 165, 0.2);
  transform: rotate(180deg);
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
}

.action-card:hover, .action-card.active {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.action-card.primary:hover {
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 10px 30px rgba(58, 134, 255, 0.2);
}

.action-card:not(.primary):hover, .action-card.active {
  border-color: var(--accent-color, #06ffa5);
  box-shadow: 0 10px 30px rgba(6, 255, 165, 0.15);
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
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
}

.action-card.primary .action-icon {
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

.stat-icon.primary {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), #5a95ff);
}

.stat-icon.accent {
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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
  box-shadow: 0 10px 30px rgba(6, 255, 165, 0.1);
  border: 1px solid rgba(6, 255, 165, 0.08);
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
  position: relative;
}

.section-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-color, #06ffa5), #39ffb4, var(--accent-color, #06ffa5));
  border-radius: 3px;
}

.content-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.content-title i {
  color: var(--accent-color, #06ffa5);
  font-size: 1.5rem;
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

.document-item:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(6, 255, 165, 0.08);
  border-color: rgba(6, 255, 165, 0.12);
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.doc-info i {
  font-size: 1.75rem;
  color: var(--accent-color, #06ffa5);
  background: rgba(6, 255, 165, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.document-item:hover .doc-info i {
  background: var(--accent-color, #06ffa5);
  color: white;
  transform: scale(1.05);
}

.doc-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.doc-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-color, #333);
  margin-bottom: 0;
}

.doc-meta {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.doc-status {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.time-elapsed {
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
  background: rgba(0, 0, 0, 0.05);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
}

.status-badge {
  padding: 0.35rem 0.85rem;
  border-radius: 2rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.draft {
  background: rgba(73, 80, 87, 0.15);
  color: #495057;
}

.status-badge.pending {
  background: rgba(255, 193, 7, 0.15);
  color: #856404;
}

.status-badge.signed {
  background: rgba(40, 167, 69, 0.15);
  color: #155724;
}

.doc-actions {
  display: flex;
  gap: 0.75rem;
}

/* Boutons */
.btn-primary {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), #5a95ff);
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
  box-shadow: 0 8px 25px rgba(58, 134, 255, 0.3);
}

.empty-state .btn-primary {
  margin: 1.5rem auto 0;
}

.btn-icon {
  background: none;
  border: 1.5px solid;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.btn-icon.primary {
  border-color: var(--primary-color, #3a86ff);
  color: var(--primary-color, #3a86ff);
}

.btn-icon.primary:hover {
  background: var(--primary-color, #3a86ff);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 134, 255, 0.2);
}

.btn-icon.success {
  border-color: #28a745;
  color: #28a745;
}

.btn-icon.success:hover {
  background: #28a745;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
}

.btn-icon.danger {
  border-color: #dc3545;
  color: #dc3545;
}

.btn-icon.danger:hover {
  background: #dc3545;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2);
}

.btn-icon.warning {
  border-color: #ffc107;
  color: #f57c00;
}

.btn-icon.warning:hover {
  background: #ffc107;
  color: #212529;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
}

.btn-icon:not(.primary):not(.success):not(.danger):not(.warning) {
  border-color: var(--accent-color, #06ffa5);
  color: var(--accent-color, #06ffa5);
}

.btn-icon:not(.primary):not(.success):not(.danger):not(.warning):hover {
  background: var(--accent-color, #06ffa5);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.2);
}

/* État vide */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  border: 1px dashed rgba(6, 255, 165, 0.2);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: rgba(6, 255, 165, 0.3);
}

.empty-state p {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  color: var(--text-color, #333);
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
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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
  .header-content {
    flex-direction: column;
    gap: 1rem;
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
  
  .doc-status {
    width: 100%;
    justify-content: space-between;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

/* Modal overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(33, 37, 41, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Modal de choix de préparation */
.preparation-choice-modal .modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 60px rgba(6, 255, 165, 0.15);
  border: 1px solid rgba(6, 255, 165, 0.1);
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slide-up 0.4s ease;
  position: relative;
}

.preparation-choice-modal .modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--accent-color, #06ffa5), #39ffb4, var(--accent-color, #06ffa5));
  background-size: 200% 100%;
  border-radius: 1.25rem 1.25rem 0 0;
  animation: gradientMove 3s ease infinite;
}

.preparation-choice-modal .modal-header {
  padding: 2.5rem 2.5rem 1.5rem;
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.preparation-choice-modal .modal-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 2.5rem;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-color, #06ffa5), #39ffb4);
  border-radius: 3px;
}

.preparation-choice-modal .modal-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preparation-choice-modal .modal-title i {
  color: var(--accent-color, #06ffa5);
  font-size: 2rem;
  background: rgba(6, 255, 165, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
}

.preparation-choice-modal .close-button {
  background: rgba(255, 255, 255, 0.7);
  border: 2px solid rgba(6, 255, 165, 0.2);
  font-size: 1.2rem;
  color: var(--text-muted, #6c757d);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.preparation-choice-modal .close-button:hover {
  background: var(--accent-color, #06ffa5);
  border-color: var(--accent-color, #06ffa5);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.3);
}

.preparation-choice-modal .modal-body {
  padding: 2.5rem;
}

.choice-description {
  font-size: 1.2rem;
  color: var(--text-muted, #6c757d);
  text-align: center;
  margin-bottom: 3rem;
  line-height: 1.6;
}

.preparation-options {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preparation-option {
  display: flex;
  align-items: center;
  padding: 2rem;
  border: 2px solid rgba(6, 255, 165, 0.1);
  border-radius: 1.25rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.preparation-option::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(6, 255, 165, 0.05), transparent);
  transition: left 0.5s ease;
}

.preparation-option:hover::before {
  left: 100%;
}

.preparation-option:hover {
  border-color: var(--accent-color, #06ffa5);
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(6, 255, 165, 0.15);
}

.option-icon {
  width: 5rem;
  height: 5rem;
  border-radius: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  margin-right: 2rem;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.option-icon::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(45deg);
  transition: all 0.3s ease;
  opacity: 0;
}

.preparation-option:hover .option-icon::after {
  opacity: 1;
  animation: shimmer 0.6s ease;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.option-icon.template {
  background: linear-gradient(45deg, #e91e63, #ff5722);
  box-shadow: 0 8px 25px rgba(233, 30, 99, 0.3);
}

.option-icon.direct {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5));
  box-shadow: 0 8px 25px rgba(58, 134, 255, 0.3);
}

.option-content {
  flex: 1;
}

.option-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin-bottom: 0.75rem;
  position: relative;
}

.option-description {
  color: var(--text-muted, #6c757d);
  margin-bottom: 1.5rem;
  line-height: 1.6;
  font-size: 1rem;
}

.option-features {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.95rem;
  color: var(--text-muted, #6c757d);
  background: rgba(6, 255, 165, 0.08);
  padding: 0.5rem 1rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(6, 255, 165, 0.15);
  transition: all 0.2s ease;
}

.preparation-option:hover .feature {
  background: rgba(6, 255, 165, 0.12);
  border-color: rgba(6, 255, 165, 0.25);
  transform: translateY(-1px);
}

.feature i {
  color: #28a745;
  font-size: 0.9rem;
  background: rgba(40, 167, 69, 0.1);
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.option-arrow {
  font-size: 2rem;
  color: var(--accent-color, #06ffa5);
  margin-left: 1.5rem;
  transition: all 0.3s ease;
  opacity: 0.6;
}

.preparation-option:hover .option-arrow {
  opacity: 1;
  transform: translateX(8px);
}

/* Modal de template */
.template-preparation-modal .modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 60px rgba(6, 255, 165, 0.15);
  border: 1px solid rgba(6, 255, 165, 0.1);
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slide-up 0.4s ease;
  position: relative;
}

.template-preparation-modal .modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #e91e63, #ff5722, #e91e63);
  background-size: 200% 100%;
  border-radius: 1.25rem 1.25rem 0 0;
  animation: gradientMove 3s ease infinite;
}

.template-preparation-modal .modal-content.large {
  max-width: 1200px;
}

.template-preparation-modal .modal-header {
  padding: 2.5rem 2.5rem 1.5rem;
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.template-preparation-modal .modal-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 2.5rem;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #e91e63, #ff5722);
  border-radius: 3px;
}

.template-preparation-modal .modal-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.template-preparation-modal .modal-title i {
  color: #e91e63;
  font-size: 2rem;
  background: rgba(233, 30, 99, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
}

.template-preparation-modal .close-button {
  background: rgba(255, 255, 255, 0.7);
  border: 2px solid rgba(233, 30, 99, 0.2);
  font-size: 1.2rem;
  color: var(--text-muted, #6c757d);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.template-preparation-modal .close-button:hover {
  background: #e91e63;
  border-color: #e91e63;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(233, 30, 99, 0.3);
}

.template-preparation-modal .modal-body {
  padding: 2.5rem;
}

.template-description {
  font-size: 1.2rem;
  color: var(--text-muted, #6c757d);
  text-align: center;
  margin-bottom: 3rem;
  line-height: 1.6;
}

.coming-soon {
  text-align: center;
  padding: 4rem 3rem;
  background: linear-gradient(135deg, 
    rgba(6, 255, 165, 0.08), 
    rgba(58, 134, 255, 0.05), 
    rgba(233, 30, 99, 0.05)
  );
  border-radius: 1.25rem;
  border: 2px dashed rgba(6, 255, 165, 0.2);
  position: relative;
  overflow: hidden;
}

.coming-soon::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(6, 255, 165, 0.05), transparent);
  animation: rotate 10s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.coming-soon i {
  font-size: 5rem;
  color: var(--accent-color, #06ffa5);
  margin-bottom: 2rem;
  opacity: 0.8;
  position: relative;
  z-index: 1;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
}

.coming-soon h4 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

.coming-soon p {
  color: var(--text-muted, #6c757d);
  margin-bottom: 2.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.coming-soon .btn-primary {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5));
  border: none;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 2rem;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  box-shadow: 0 8px 25px rgba(58, 134, 255, 0.3);
}

.coming-soon .btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(58, 134, 255, 0.4);
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive pour les modales */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 1rem;
  }
  
  .preparation-choice-modal .modal-content,
  .template-preparation-modal .modal-content {
    max-width: 100%;
  }
  
  .preparation-options {
    gap: 1.5rem;
  }
  
  .preparation-option {
    flex-direction: column;
    text-align: center;
    padding: 2rem 1.5rem;
  }
  
  .option-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .option-arrow {
    display: none;
  }
  
  .option-features {
    justify-content: center;
  }
}
</style> 