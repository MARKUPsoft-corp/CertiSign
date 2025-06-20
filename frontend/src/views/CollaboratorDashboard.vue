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

    <!-- Composant pour préparer un document -->
    <div v-if="showPrepareDocument" class="modal-overlay">
      <prepare-document 
        @close="closePrepareDocument" 
        @documentPrepared="onDocumentPrepared"
      />
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
const showPrepareDocument = ref(false);

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
  showPrepareDocument.value = true;
}

function closePrepareDocument() {
  showPrepareDocument.value = false;
}

async function fetchDocuments() {
  try {
    // Récupérer l'ID de l'utilisateur connecté
    const user = AuthService.getCurrentUser();
    if (!user || !user.id) {
      console.error('Utilisateur non connecté ou ID manquant');
      return;
    }

    // Récupérer le nom de l'organisation actuelle
    const organizationName = user?.organization?.name;
    
    if (!organizationName) {
      console.error('Nom d\'organisation manquant');
      return;
    }

    // Appel direct à l'API Django
    const token = localStorage.getItem('token');
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_name: organizationName  // Utiliser le nom de l'organisation plutôt que l'ID
      }
    };

    // Utiliser l'endpoint by_collaborator qui retourne les documents par statut
    const response = await axios.get(`https://192.168.4.131:8000/api/documents/qr-positions/by_collaborator/`, config);
    
    if (response.data) {
      // Filtrer les documents pour n'afficher que ceux de l'organisation actuelle
      // Mettre à jour les documents brouillons
      if (response.data.drafts) {
        drafts.value = response.data.drafts
          .filter(doc => doc.organization_name === organizationName)
          .map(doc => ({
            id: doc.id,
            name: doc.document_name,
            createdAt: new Date(doc.created_at),
            status: 'draft'
          }));
      }
      
      // Mettre à jour les documents en attente
      if (response.data.pending) {
        pendingDocuments.value = response.data.pending
          .filter(doc => doc.organization_name === organizationName)
          .map(doc => ({
            id: doc.id,
            name: doc.document_name,
            assignedAt: new Date(doc.created_at),
            assignedTo: doc.collaborator_username || 'En attente de signature',
            status: 'pending'
          }));
      }
      
      // Mettre à jour les documents complétés
      if (response.data.completed) {
        completedDocuments.value = response.data.completed
          .filter(doc => doc.organization_name === organizationName)
          .map(doc => ({
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
  
  // Récupérer le nom de l'organisation actuelle
  const user = AuthService.getCurrentUser();
  const organizationName = user?.organization?.name;
  
  if (!organizationName) {
    console.error('Nom d\'organisation manquant');
    return;
  }
  
  // Rediriger vers la page d'édition avec l'ID du document et le nom de l'organisation
  router.push({
    name: 'edit-document',
    params: { id: doc.id },
    query: { organization_name: organizationName }
  });
}

function assignForSignature(doc) {
  console.log('Assigner pour signature:', doc.name);
  
  // Récupérer le nom de l'organisation actuelle
  const user = AuthService.getCurrentUser();
  const organizationName = user?.organization?.name;
  
  if (!organizationName) {
    console.error('Nom d\'organisation manquant');
    return;
  }
  
  // Rediriger vers la page d'assignation avec l'ID du document et le nom de l'organisation
  router.push({
    name: 'assign-document',
    params: { id: doc.id },
    query: { organization_name: organizationName }
  });
}

async function deleteDraft(doc) {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce brouillon ?')) {
    try {
      // Récupérer le nom de l'organisation actuelle
      const user = AuthService.getCurrentUser();
      const organizationName = user?.organization?.name;
      
      if (!organizationName) {
        console.error('Nom d\'organisation manquant');
        return;
      }
      
      // Appel à l'API pour supprimer le document
      const token = localStorage.getItem('token');
      await axios.delete(`http://192.168.4.131:8000/api/documents/qr-positions/${doc.id}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          organization_name: organizationName
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
    // Récupérer le nom de l'organisation actuelle
    const user = AuthService.getCurrentUser();
    const organizationName = user?.organization?.name;
    
    if (!organizationName) {
      console.error('Nom d\'organisation manquant');
      return;
    }
    
    // Appel à l'API pour envoyer un rappel
    const token = localStorage.getItem('token');
    await axios.post(`http://192.168.4.131:8000/api/documents/remind/${doc.id}/`, 
      { organization_name: organizationName },
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
</style> 