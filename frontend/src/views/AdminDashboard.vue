<template>
  <div class="admin-dashboard">
    <!-- Fond animé avec particules -->
    <div class="particles-container">
      <div v-for="i in 15" :key="i" class="particle" 
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
            <div class="logo-icon">
              <i class="bi bi-shield-lock-fill"></i>
            </div>
            <h1 class="logo-text">
              <span class="text-primary">Certi</span><span class="text-accent">Sign</span>
            </h1>
          </div>
          <span class="role-badge admin top-right-of-logo">Administrateur</span>
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
            <span class="underlined-text">Administration de <span class="highlight-text">{{ organizationName }}</span></span>
          </h2>
          <p class="welcome-description">
            Gérez les activités de signature et supervisez les membres de votre organisation
          </p>
        </div>
      </section>

      <!-- Statistiques rapides -->
      <section class="stats-section">
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.signed }}</div>
              <div class="stat-label">Documents signés</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-file-earmark-check-fill"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">En attente</div>
            </div>
            <div class="stat-icon warning">
              <i class="bi bi-hourglass-split"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.members }}</div>
              <div class="stat-label">Membres actifs</div>
            </div>
            <div class="stat-icon accent">
              <i class="bi bi-people-fill"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.todayActivity }}</div>
              <div class="stat-label">Activité aujourd'hui</div>
            </div>
            <div class="stat-icon success">
              <i class="bi bi-activity"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Actions rapides -->
      <section class="quick-actions">
        <h3 class="section-title">Actions rapides</h3>
        <div class="actions-grid">
          <button class="action-card" @click="activeSection = 'pending-docs'" :class="{ 'active': activeSection === 'pending-docs' }">
            <div class="action-icon warning">
              <i class="bi bi-file-earmark-text"></i>
            </div>
            <span>Documents en attente</span>
            <div class="notification-badge" v-if="stats.pending > 0">{{ stats.pending }}</div>
          </button>
          <button class="action-card" @click="activeSection = 'team-activity'" :class="{ 'active': activeSection === 'team-activity' }">
            <div class="action-icon primary">
              <i class="bi bi-person-workspace"></i>
            </div>
            <span>Activité équipe</span>
          </button>
          <button class="action-card" @click="activeSection = 'signed-docs'" :class="{ 'active': activeSection === 'signed-docs' }">
            <div class="action-icon success">
              <i class="bi bi-file-check"></i>
            </div>
            <span>Documents signés</span>
          </button>
          <button class="action-card" @click="activeSection = 'members'" :class="{ 'active': activeSection === 'members' }">
            <div class="action-icon accent">
              <i class="bi bi-people"></i>
            </div>
            <span>Gestion membres</span>
          </button>
        </div>
      </section>

      <!-- Contenu dynamique selon la section active -->
      <section class="content-section">
        <!-- Documents en attente -->
        <div v-if="activeSection === 'pending-docs'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-hourglass-split"></i>
            Documents en attente de signature
          </h3>
          <div class="documents-list">
            <div v-for="doc in pendingDocuments" :key="doc.id" class="document-item">
              <div class="doc-info">
                <i class="bi bi-file-earmark-pdf"></i>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.name }}</span>
                  <span class="doc-meta">Préparé par {{ doc.preparedBy }} • {{ formatDate(doc.createdAt) }}</span>
                </div>
              </div>
              <div class="doc-status">
                <span class="assignee">{{ doc.assignedTo }}</span>
                <div class="doc-actions">
                  <button class="btn-icon" title="Voir détails">
                    <i class="bi bi-eye"></i>
                  </button>
                  <button class="btn-icon" title="Réassigner">
                    <i class="bi bi-arrow-repeat"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="pendingDocuments.length === 0" class="empty-state">
              <i class="bi bi-inbox"></i>
              <p>Aucun document en attente</p>
            </div>
          </div>
        </div>

        <!-- Activité de l'équipe -->
        <div v-if="activeSection === 'team-activity'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-person-workspace"></i>
            Activité de l'équipe
          </h3>
          <div class="activity-list">
            <div v-for="activity in teamActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <i :class="getActivityIcon(activity.type)"></i>
              </div>
              <div class="activity-content">
                <div class="activity-description">{{ activity.description }}</div>
                <div class="activity-meta">{{ activity.user }} • {{ formatTime(activity.timestamp) }}</div>
              </div>
            </div>
            <div v-if="teamActivities.length === 0" class="empty-state">
              <i class="bi bi-clock-history"></i>
              <p>Aucune activité récente</p>
            </div>
          </div>
        </div>

        <!-- Documents signés -->
        <div v-if="activeSection === 'signed-docs'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-file-check"></i>
            Documents récemment signés
          </h3>
          <div class="documents-list">
            <div v-for="doc in signedDocuments" :key="doc.id" class="document-item">
              <div class="doc-info">
                <i class="bi bi-file-earmark-check"></i>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.name }}</span>
                  <span class="doc-meta">Signé par {{ doc.signedBy }} • {{ formatDate(doc.signedAt) }}</span>
                </div>
              </div>
              <div class="doc-status">
                <span class="status-badge signed">Signé</span>
                <div class="doc-actions">
                  <button class="btn-icon" title="Télécharger">
                    <i class="bi bi-download"></i>
                  </button>
                  <button class="btn-icon" title="Vérifier">
                    <i class="bi bi-shield-check"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="signedDocuments.length === 0" class="empty-state">
              <i class="bi bi-file-check"></i>
              <p>Aucun document signé récemment</p>
            </div>
          </div>
        </div>

        <!-- Gestion des membres -->
        <div v-if="activeSection === 'members'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-people"></i>
            Membres de l'organisation
          </h3>
          <div class="members-list">
            <div v-for="member in organizationMembers" :key="member.id" class="member-item">
              <div class="member-info">
                <div class="member-avatar">
                  <i class="bi bi-person-circle"></i>
                </div>
                <div class="member-details">
                  <span class="member-name">{{ member.name }}</span>
                  <span class="member-role" :class="member.role">{{ getRoleDisplay(member.role) }}</span>
                </div>
              </div>
              <div class="member-stats">
                <div class="stat-item">
                  <span class="stat-number">{{ member.documentsCount }}</span>
                  <span class="stat-label">Documents</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ member.lastActivity }}</span>
                  <span class="stat-label">Dernière activité</span>
                </div>
              </div>
            </div>
            <div v-if="organizationMembers.length === 0" class="empty-state">
              <i class="bi bi-people"></i>
              <p>Aucun membre dans l'organisation</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/AuthService';
import axios from 'axios';

const router = useRouter();

// État réactif
const activeSection = ref('pending-docs');
const userName = ref('');
const organizationName = ref('');
const organizationStatus = ref('');

// Données statistiques
const stats = ref({
  signed: 24,
  pending: 7,
  members: 12,
  todayActivity: 18
});

// Documents en attente (données exemples)
const pendingDocuments = ref([
  {
    id: 1,
    name: 'Contrat de partenariat 2024.pdf',
    preparedBy: 'Jean Dupont',
    assignedTo: 'Marie Martin',
    createdAt: new Date('2024-01-15')
  },
  {
    id: 2,
    name: 'Accord de confidentialité.pdf',
    preparedBy: 'Paul Durand',
    assignedTo: 'Sophie Leblanc',
    createdAt: new Date('2024-01-14')
  }
]);

// Documents signés (données exemples)
const signedDocuments = ref([
  {
    id: 1,
    name: 'Rapport annuel 2023.pdf',
    signedBy: 'Directeur Général',
    signedAt: new Date('2024-01-15')
  }
]);

// Activités de l'équipe (données exemples)
const teamActivities = ref([
  {
    id: 1,
    type: 'document-prepared',
    description: 'Document préparé pour signature',
    user: 'Jean Dupont',
    timestamp: new Date('2024-01-15T14:30:00')
  },
  {
    id: 2,
    type: 'document-signed',
    description: 'Document signé avec succès',
    user: 'Marie Martin',
    timestamp: new Date('2024-01-15T13:45:00')
  }
]);

// Membres de l'organisation (données exemples)
const organizationMembers = ref([
  {
    id: 1,
    name: 'Jean Dupont',
    role: 'collaborator',
    documentsCount: 8,
    lastActivity: '2h'
  },
  {
    id: 2,
    name: 'Marie Martin',
    role: 'signer',
    documentsCount: 15,
    lastActivity: '1h'
  }
]);

// Positionnement des particules
const particlePositions = Array.from({ length: 15 }, () => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 8 + 4,
  duration: Math.random() * 20 + 15,
  delay: Math.random() * 5
}));

// Méthodes
function formatDate(date) {
  return new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  }).format(date);
}

function formatTime(date) {
  const now = new Date();
  const diff = now - date;
  const hours = Math.floor(diff / (1000 * 60 * 60));
  
  if (hours < 1) {
    const minutes = Math.floor(diff / (1000 * 60));
    return `il y a ${minutes}min`;
  }
  if (hours < 24) {
    return `il y a ${hours}h`;
  }
  return formatDate(date);
}

function getActivityIcon(type) {
  const icons = {
    'document-prepared': 'bi bi-file-earmark-plus',
    'document-signed': 'bi bi-file-earmark-check',
    'member-login': 'bi bi-box-arrow-in-right'
  };
  return icons[type] || 'bi bi-circle';
}

function getRoleDisplay(role) {
  const roles = {
    'collaborator': 'Collaborateur',
    'signer': 'Signataire',
    'admin': 'Administrateur'
  };
  return roles[role] || role;
}

// Nouvelle fonction pour récupérer les données
async function fetchData() {
  try {
    // Récupérer l'ID de l'organisation actuelle
    const user = AuthService.getCurrentUser();
    if (!user) {
      console.error('Utilisateur non connecté');
      return;
    }
    
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
        organization_id: organizationId  // Ajouter l'ID de l'organisation à la requête
      }
    };

    // Récupérer les documents et les statistiques
    const response = await axios.get('https://192.168.4.131/api/admin/dashboard/', config);
    
    if (response.data) {
      // Mettre à jour les documents en attente
      if (response.data.pending_documents) {
        pendingDocuments.value = response.data.pending_documents.map(doc => ({
          id: doc.id,
          name: doc.document_name || 'Document sans nom',
          preparedBy: doc.prepared_by || 'Collaborateur',
          assignedTo: doc.assigned_to || 'Signataire',
          createdAt: new Date(doc.created_at)
        }));
      }
      
      // Mettre à jour les documents signés
      if (response.data.signed_documents) {
        signedDocuments.value = response.data.signed_documents.map(doc => ({
          id: doc.id,
          name: doc.document_name || 'Document sans nom',
          signedBy: doc.signed_by || 'Signataire',
          signedAt: new Date(doc.signed_at || doc.updated_at)
        }));
      }
      
      // Mettre à jour les statistiques
      if (response.data.stats) {
        stats.value.signed = response.data.stats.signed || 0;
        stats.value.pending = response.data.stats.pending || 0;
        stats.value.members = response.data.stats.members || 0;
        stats.value.todayActivity = response.data.stats.today_activity || 0;
      }
      
      // Mettre à jour les activités de l'équipe
      if (response.data.team_activities) {
        teamActivities.value = response.data.team_activities.map(activity => ({
          id: activity.id,
          type: activity.type || 'document-prepared',
          description: activity.description || 'Activité',
          user: activity.user || 'Utilisateur',
          timestamp: new Date(activity.timestamp)
        }));
      }
      
      // Mettre à jour les membres de l'organisation
      if (response.data.organization_members) {
        organizationMembers.value = response.data.organization_members.map(member => ({
          id: member.id,
          name: member.username || 'Utilisateur',
          role: member.role || 'collaborator',
          documentsCount: member.documents_count || 0,
          lastActivity: member.last_activity || 'N/A'
        }));
      }
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des données:', error);
  }
}

function logout() {
  AuthService.logout();
  router.push('/login');
}

// Initialisation
onMounted(() => {
  document.title = 'Administration - CertiSign';
  
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
    
    // Récupérer les données du tableau de bord
    fetchData();
  } else {
    router.push('/login');
  }
});
</script>

<style scoped>
/* Styles généraux */
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, 
    var(--bg-color, #f8f9fa) 0%, 
    rgba(58, 134, 255, 0.05) 50%, 
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
  opacity: 0.2;
  animation: float 20s infinite linear;
  background: var(--primary-color, #3a86ff);
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.3;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-100vh) translateX(100px) rotate(360deg);
    opacity: 0;
  }
}

/* En-tête */
.dashboard-header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(58, 134, 255, 0.2);
  padding: 1.25rem 2.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 15px rgba(58, 134, 255, 0.1);
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
  gap: 0.75rem;
}

.logo-icon {
  color: var(--primary-color, #3a86ff);
  font-size: 2.25rem;
  transition: transform 0.3s ease;
}

.logo-container:hover .logo-icon {
  transform: rotate(-10deg);
}

.logo-text {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  line-height: 1;
}

.text-primary {
  color: #4A4A4A;
}

.text-accent {
  color: var(--primary-color, #3a86ff);
}

.role-badge.admin.top-right-of-logo {
  position: relative;
  top: 0;
  right: 0;
  font-size: 0.8rem;
  padding: 0.25rem 0.55rem;
  line-height: 1.1;
  border-radius: 0.75rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5));
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
  color: var(--primary-color, #3a86ff);
  font-size: 1.9rem;
  line-height: 1.2;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.05);
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), #5a95ff);
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
  box-shadow: 0 2px 10px rgba(58, 134, 255, 0.12);
  border: 1px solid rgba(58, 134, 255, 0.15);
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
  color: var(--primary-color, #3a86ff);
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 134, 255, 0.2);
}

.logout-btn {
  background: transparent;
  border: 2px solid var(--primary-color, #3a86ff);
  color: var(--primary-color, #3a86ff);
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: var(--primary-color, #3a86ff);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(58, 134, 255, 0.3);
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
  background: linear-gradient(90deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5), var(--primary-color, #3a86ff));
  background-size: 200% 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(58, 134, 255, 0.3);
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

.welcome-description {
  font-size: 1.1rem;
  color: var(--text-muted, #6c757d);
  max-width: 600px;
  margin: 0 auto;
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

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color, #333);
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

.stat-icon.warning {
  background: linear-gradient(45deg, #ff9500, #ffb347);
}

.stat-icon.accent {
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
}

.stat-icon.success {
  background: linear-gradient(45deg, #28a745, #5bc85a);
}

/* Actions rapides */
.quick-actions {
  margin-bottom: 3rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--text-color, #333);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-card {
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid transparent;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.action-card:hover, .action-card.active {
  background: rgba(255, 255, 255, 1);
  border-color: var(--primary-color, #3a86ff);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(58, 134, 255, 0.15);
}

.action-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.action-icon.primary {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), #5a95ff);
}

.action-icon.warning {
  background: linear-gradient(45deg, #ff9500, #ffb347);
}

.action-icon.success {
  background: linear-gradient(45deg, #28a745, #5bc85a);
}

.action-icon.accent {
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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

/* Section de contenu */
.content-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 1.25rem;
  padding: 2.5rem;
  box-shadow: 0 10px 30px rgba(58, 134, 255, 0.1);
  border: 1px solid rgba(58, 134, 255, 0.08);
  transition: all 0.3s ease;
  margin-top: 1rem;
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
  border-bottom: 1px solid rgba(58, 134, 255, 0.1);
  position: relative;
}

.content-title i {
  color: var(--primary-color, #3a86ff);
  font-size: 1.5rem;
}

.content-title::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5));
  border-radius: 3px;
}

/* Listes */
.documents-list, .activity-list, .members-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.document-item, .activity-item, .member-item {
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

.document-item:hover, .activity-item:hover, .member-item:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(58, 134, 255, 0.08);
  border-color: rgba(58, 134, 255, 0.12);
}

.doc-info, .member-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.doc-info i, .member-avatar i {
  font-size: 1.75rem;
  color: var(--primary-color, #3a86ff);
  background: rgba(58, 134, 255, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.document-item:hover .doc-info i,
.member-item:hover .member-avatar i {
  background: var(--primary-color, #3a86ff);
  color: white;
  transform: scale(1.05);
}

.doc-details, .member-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.doc-name, .member-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-color, #333);
}

.doc-meta, .member-role {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.member-role {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.8rem;
  font-weight: 500;
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
}

.member-role.collaborator {
  background: rgba(6, 255, 165, 0.1);
  color: var(--accent-color, #06ffa5);
}

.member-role.signer {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.member-role.admin {
  background: rgba(58, 134, 255, 0.15);
  color: var(--primary-color, #3a86ff);
}

.doc-status {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.doc-actions {
  display: flex;
  gap: 0.75rem;
}

.assignee {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--primary-color, #3a86ff);
  background: rgba(58, 134, 255, 0.1);
  padding: 0.35rem 0.85rem;
  border-radius: 2rem;
}

.btn-icon {
  background: none;
  border: 1.5px solid var(--primary-color, #3a86ff);
  color: var(--primary-color, #3a86ff);
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
  background: var(--primary-color, #3a86ff);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 134, 255, 0.2);
}

.status-badge.signed {
  background: rgba(40, 167, 69, 0.15);
  color: #28a745;
  padding: 0.35rem 0.85rem;
  border-radius: 2rem;
  font-weight: 500;
  font-size: 0.9rem;
}

/* Activités */
.activity-item {
  align-items: flex-start;
}

.activity-icon {
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

.activity-item:hover .activity-icon {
  transform: scale(1.05);
}

.activity-icon.document-prepared {
  background: linear-gradient(45deg, #06ffa5, #39ffb4);
}

.activity-icon.document-signed {
  background: linear-gradient(45deg, #3a86ff, #5a95ff);
}

.activity-icon.member-login {
  background: linear-gradient(45deg, #28a745, #5bc85a);
}

.activity-content {
  flex: 1;
  padding: 0.25rem 0;
}

.activity-description {
  font-weight: 500;
  font-size: 1rem;
  color: var(--text-color, #333);
  margin-bottom: 0.25rem;
}

.activity-meta {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

/* État vide */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  border: 1px dashed rgba(58, 134, 255, 0.2);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: rgba(58, 134, 255, 0.3);
}

.empty-state p {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-color, #333);
}

/* Statistiques des membres */
.member-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.6);
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(58, 134, 255, 0.1);
  min-width: 90px;
}

.stat-number {
  font-weight: 700;
  color: var(--primary-color, #3a86ff);
  font-size: 1.1rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted, #6c757d);
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
  
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .document-item, .member-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .doc-status {
    width: 100%;
    justify-content: space-between;
  }
}

.highlight-text {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card:hover {
  transform: translateY(-5px);
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
</style> 