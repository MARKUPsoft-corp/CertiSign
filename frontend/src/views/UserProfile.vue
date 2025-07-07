<template>
  <div class="profile-container" :class="{ 'animated': isAnimated }">
    <!-- En-tête de profil avec avatar et nom mis en évidence -->
    <div class="profile-header" data-animate="fade-in">
      <div class="profile-header-main">
        <div class="profile-avatar-large">
          <i class="bi bi-person-circle"></i>
          <div class="avatar-status" :class="{ 'active': user.is_active }"></div>
        </div>
        <div class="profile-name-container">
          <div class="username-display">{{ user.username }}</div>
          <h1 class="profile-name-large">{{ user.first_name }} {{ user.last_name }}</h1>
          
          <div class="profile-details">
            <div class="profile-detail-row">
              <p class="profile-email">
                <i class="bi bi-envelope"></i>
                <span>{{ user.email }}</span>
              </p>
            </div>
            
            <div class="profile-detail-row">
              <div class="profile-badges">
                <span class="profile-badge" :class="getRoleClass">
                  <i class="bi bi-shield-lock"></i>
                  {{ getUserRole }}
                </span>
                <span class="profile-badge status-badge" :class="{ 'active-badge': user.is_active }">
                  {{ user.is_active ? 'Actif' : 'Inactif' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="profile-info">
        <div class="profile-actions">
          <button class="action-btn primary" @click="editProfile">
            <i class="bi bi-pencil"></i>
            <span>Modifier</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Statistiques d'utilisation -->
    <div class="stats-container" data-animate="fade-in-up" data-delay="0.2">
      <h3 class="section-title">Statistiques</h3>
      <div class="stats-grid">
        <div class="stat-card" data-animate="fade-in-up" data-delay="0.3">
          <div class="stat-icon primary">
            <i class="bi bi-file-earmark"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistiques.total_documents || 0 }}</div>
            <div class="stat-label">Documents</div>
          </div>
        </div>

        <div class="stat-card" data-animate="fade-in-up" data-delay="0.4">
          <div class="stat-icon success">
            <i class="bi bi-file-earmark-check"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistiques.documents_signes || 0 }}</div>
            <div class="stat-label">Signés</div>
          </div>
        </div>

        <div class="stat-card" data-animate="fade-in-up" data-delay="0.5">
          <div class="stat-icon warning">
            <i class="bi bi-clock-history"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistiques.activites || 0 }}</div>
            <div class="stat-label">Activités</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Informations détaillées du compte -->
    <div class="details-container" data-animate="fade-in-up" data-delay="0.6">
      <h3 class="section-title">Informations du compte</h3>
      <div class="details-card">
        <div class="detail-item">
          <div class="detail-label">Date d'inscription</div>
          <div class="detail-value">{{ formatDate(user.date_joined) }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">Organisation</div>
          <div class="detail-value">{{ user.organization_name || 'Non spécifiée' }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">Téléphone</div>
          <div class="detail-value">{{ user.phone_number || 'Non spécifié' }}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">Statut</div>
          <div class="detail-value status" :class="{ 'active': user.is_active }">
            {{ user.is_active ? 'Actif' : 'Inactif' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Activités récentes -->
    <div class="recent-activities" data-animate="fade-in-up" data-delay="0.8">
      <h3 class="section-title">Activités récentes</h3>
      
      <div v-if="activites.length === 0" class="empty-activities">
        <i class="bi bi-clock-history"></i>
        <p>Aucune activité récente</p>
      </div>
      
      <div v-else class="activity-timeline">
        <div v-for="(activite, index) in activites" :key="index" class="timeline-item"
             data-animate="fade-in-left" :data-delay="0.8 + (index * 0.1)">
          <div class="timeline-icon" :class="getActivityIconClass(activite.activity_type)">
            <i :class="getActivityIcon(activite.activity_type)"></i>
          </div>
          <div class="timeline-content">
            <h4 class="timeline-title">{{ activite.activity_type_display }}</h4>
            <p class="timeline-text">{{ activite.document_title || 'Document sans titre' }}</p>
            <span class="timeline-date">{{ formatDate(activite.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pour l'édition du profil -->
    <div v-if="showEditModal" class="edit-profile-modal">
      <div class="modal-backdrop" @click="showEditModal = false"></div>
      <div class="modal-content" data-animate="fade-in-up">
        <div class="modal-header">
          <h3>Modifier mon profil</h3>
          <button class="close-btn" @click="showEditModal = false">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="firstName">Prénom</label>
            <input type="text" id="firstName" v-model="editedUser.first_name" class="form-input">
          </div>
          <div class="form-group">
            <label for="lastName">Nom</label>
            <input type="text" id="lastName" v-model="editedUser.last_name" class="form-input">
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="editedUser.email" class="form-input">
          </div>
          <div class="form-group">
            <label for="phone">Téléphone</label>
            <input type="tel" id="phone" v-model="editedUser.phone_number" class="form-input">
          </div>
          <div class="form-group">
            <label for="organization">Organisation</label>
            <input type="text" id="organization" v-model="editedUser.organization_name" class="form-input">
          </div>
        </div>
        <div class="modal-footer">
          <button class="action-btn secondary" @click="showEditModal = false">Annuler</button>
          <button class="action-btn primary" @click="saveProfile">Enregistrer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import AuthService from '@/services/AuthService';
import DocumentService from '@/services/DocumentService';
import axios from 'axios';

// États réactifs
const user = ref({
  id: null,
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  organization_name: '',
  is_active: true,
  is_superadmin: false,
  is_org_admin: false,
  date_joined: null,
  last_login: null
});

const editedUser = ref({...user.value});
const activites = ref([]);
const statistiques = ref({
  total_documents: 0,
  documents_signes: 0,
  activites: 0
});
const isAnimated = ref(false);
const showEditModal = ref(false);
const loading = ref(true);
const error = ref(null);

// Propriétés calculées
const getUserRole = computed(() => {
  if (user.value.is_superadmin) return 'Super Admin';
  if (user.value.is_org_admin) return 'Admin Organisation';
  return 'Utilisateur';
});

const getRoleClass = computed(() => {
  if (user.value.is_superadmin) return 'superadmin-badge';
  if (user.value.is_org_admin) return 'admin-badge';
  return 'user-badge';
});

// Méthodes
const fetchUserProfile = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // D'abord récupérer les informations de base depuis le service d'authentification
    const currentUser = AuthService.getCurrentUser();
    
    if (!currentUser) {
      throw new Error('Aucun utilisateur connecté');
    }
    
    // Initialiser les données de base
    user.value = {
      ...user.value,
      ...currentUser,
      id: currentUser.id || currentUser.user_id, // Gestion des différents formats possibles
      is_active: currentUser.is_active !== false // Par défaut actif si non spécifié
    };
    
    // Récupérer les données complètes du profil depuis l'API
    try {
      console.log('Récupération des données détaillées du profil depuis l\'API...');
      const token = AuthService.getToken();
      const apiUrl = DocumentService.API_URL || 'https://ppd.camgovca.cm';
      
      const profileResponse = await axios.get(`${apiUrl}/api/users/me/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (profileResponse.data) {
        // Mettre à jour les données utilisateur avec les informations complètes
        user.value = {
          ...user.value,
          ...profileResponse.data,
          // Conserver l'ID et les valeurs booléennes spécifiques
          id: user.value.id,
          is_active: profileResponse.data.is_active !== false,
          is_superadmin: profileResponse.data.role === 'superadmin',
          is_org_admin: profileResponse.data.role === 'admin',
          organization_name: profileResponse.data.organization?.name || 'Non spécifiée'
        };
        
        console.log('Données complètes du profil récupérées:', user.value);
      }
    } catch (apiErr) {
      console.warn('Impossible de récupérer les données détaillées du profil:', apiErr);
      console.log('Utilisation des données locales seulement.');
    }
    
    // Mettre à jour l'utilisateur modifiable avec les données récupérées
    editedUser.value = {...user.value};
    console.log('Données utilisateur finales:', user.value);
    
    loading.value = false;
  } catch (err) {
    console.error('Erreur lors de la récupération du profil:', err);
    error.value = 'Impossible de charger les informations du profil.';
    loading.value = false;
  }
};

const fetchUserStatistics = async () => {
  try {
    console.log('Récupération des statistiques utilisateur...');
    let totalDocs = 0;
    let signedDocs = 0;
    
    // Récupérer les documents pour calculer les statistiques
    try {
      const documentsResponse = await DocumentService.getDocuments();
      
      if (documentsResponse && documentsResponse.data) {
        // Vérifier si la réponse est un tableau ou un objet avec une propriété results
        let documents = [];
        
        if (Array.isArray(documentsResponse.data)) {
          documents = documentsResponse.data;
        } else if (documentsResponse.data.results && Array.isArray(documentsResponse.data.results)) {
          documents = documentsResponse.data.results;
        }
        
        // Calculer les statistiques de documents
        totalDocs = documents.length;
        signedDocs = documents.filter(doc => doc.status === 'signed').length;
        
        console.log('Documents récupérés:', documents);
        console.log('Statistiques de documents calculées:', {
          total: totalDocs,
          signés: signedDocs
        });
      } else {
        console.warn('Format de réponse inattendu pour les documents:', documentsResponse);
      }
    } catch (docError) {
      console.error('Erreur lors de la récupération des documents:', docError);
    }
    
    // Récupérer les activités de l'utilisateur pour avoir un décompte précis
    try {
      const activitiesResponse = await DocumentService.getMyActivities();
      
      if (activitiesResponse && activitiesResponse.data) {
        // Vérifier si la réponse est un tableau ou un objet avec une propriété results
        let activities = [];
        
        if (Array.isArray(activitiesResponse.data)) {
          activities = activitiesResponse.data;
        } else if (activitiesResponse.data.results && Array.isArray(activitiesResponse.data.results)) {
          activities = activitiesResponse.data.results;
        }
        
        // Calculer le nombre total d'activités
        statistiques.value.activites = activities.length;
        
        // Compter les documents uniques à partir des activités
        const uniqueDocumentIds = new Set();
        const signedDocumentIds = new Set();
        
        activities.forEach(activity => {
          if (activity.document_id) {
            uniqueDocumentIds.add(activity.document_id);
            
            if (activity.activity_type === 'signed') {
              signedDocumentIds.add(activity.document_id);
            }
          }
        });
        
        // Mettre à jour le total si on trouve plus de documents dans les activités
        const totalFromActivities = uniqueDocumentIds.size;
        if (totalFromActivities > totalDocs) {
          totalDocs = totalFromActivities;
          console.log('Mise à jour du nombre total de documents à partir des activités:', totalDocs);
        }
        
        // Mettre à jour les signés si on trouve plus dans les activités
        const signedFromActivities = signedDocumentIds.size;
        if (signedFromActivities > signedDocs) {
          signedDocs = signedFromActivities;
          console.log('Mise à jour du nombre de documents signés à partir des activités:', signedDocs);
        }
        
        console.log('Statistiques d\'activités calculées:', {
          total: activities.length,
          documents_uniques: uniqueDocumentIds.size,
          documents_signés: signedDocumentIds.size
        });
      } else {
        console.warn('Aucune activité trouvée ou format de réponse inattendu');
        statistiques.value.activites = 0;
      }
    } catch (actError) {
      console.error('Erreur lors de la récupération des activités:', actError);
    }
    
    // Mettre à jour les statistiques finales
    statistiques.value.total_documents = totalDocs;
    statistiques.value.documents_signes = signedDocs;
  } catch (err) {
    console.error('Erreur lors de la récupération des statistiques:', err);
  }
};

const fetchUserActivities = async () => {
  try {
    // Récupérer les activités récentes de l'utilisateur depuis le service de documents
    const response = await DocumentService.getMyActivities();
    
    if (response && response.data) {
      const activities = Array.isArray(response.data) ? response.data : [];
      activites.value = activities.slice(0, 5); // Limiter aux 5 dernières activités
      console.log('Activités récupérées:', activites.value);
    } else {
      console.warn('Aucune activité trouvée ou format de réponse inattendu');
      activites.value = [];
    }
  } catch (err) {
    console.error('Erreur lors de la récupération des activités:', err);
    activites.value = [];
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'Non disponible';
  try {
    return format(parseISO(dateString), 'dd MMMM yyyy à HH:mm', { locale: fr });
  } catch (error) {
    return dateString;
  }
};

const getActivityIcon = (type) => {
  const icons = {
    'viewed': 'bi-eye',
    'downloaded': 'bi-download',
    'uploaded': 'bi-upload',
    'signed': 'bi-pen',
    'shared': 'bi-share',
    'created': 'bi-plus-circle',
    'updated': 'bi-pencil'
  };
  return icons[type] || 'bi-activity';
};

const getActivityIconClass = (type) => {
  const classes = {
    'viewed': 'info',
    'downloaded': 'success',
    'uploaded': 'primary',
    'signed': 'warning',
    'shared': 'accent',
    'created': 'primary',
    'updated': 'info'
  };
  return classes[type] || 'primary';
};

const editProfile = () => {
  editedUser.value = {...user.value};
  showEditModal.value = true;
};

const saveProfile = async () => {
  try {
    loading.value = true;
    
    // Pour le moment, mise à jour locale
    // Dans une application réelle, on appellerait une API
    user.value = {...editedUser.value};
    
    // Mettre à jour les informations utilisateur dans le service d'authentification
    AuthService.updateCurrentUser(user.value);
    
    showEditModal.value = false;
    loading.value = false;
  } catch (err) {
    console.error('Erreur lors de la mise à jour du profil:', err);
    loading.value = false;
  }
};

// Cycle de vie
onMounted(async () => {
  console.log('Initialisation du profil utilisateur...');
  try {
    // Charger d'abord les données de base de l'utilisateur
    await fetchUserProfile();
    
    // Puis charger les activités et calculer les statistiques en parallèle
    await Promise.all([
      fetchUserActivities(),
      fetchUserStatistics()
    ]);
    
    console.log('Toutes les données du profil sont chargées');
    
    // Ajouter la classe animée après un court délai
    setTimeout(() => {
      isAnimated.value = true;
    }, 100);
    
    // Activer les animations avec data-animate
    setTimeout(() => {
      const animatedElements = document.querySelectorAll('[data-animate]');
      animatedElements.forEach(el => {
        const delay = parseFloat(el.getAttribute('data-delay') || 0);
        setTimeout(() => {
          el.classList.add(el.getAttribute('data-animate'));
        }, delay * 1000);
      });
    }, 300);
  } catch (err) {
    console.error('Erreur lors du chargement des données du profil:', err);
    error.value = 'Une erreur est survenue lors du chargement des données.';
  }
});
</script>

<style scoped>
/* Variables pour faciliter la thématisation */
:root {
  --primary-color: #007bff;
  --success-color: #28a745;
  --warning-color: #ffc107;
  --danger-color: #dc3545;
  --info-color: #17a2b8;
  --accent-color: #6f42c1;
  --card-bg: white;
  --border-color: #ddd;
  --text-color: #495057;
  --text-secondary: #6c757d;
}

/* Animations */
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
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* Classes d'animation */
.fade-in {
  animation: fadeIn 0.5s ease forwards;
}

.fade-in-up {
  animation: fadeInUp 0.5s ease forwards;
}

.fade-in-left {
  animation: fadeInLeft 0.5s ease forwards;
}

/* Styles de base */
.profile-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.profile-container.animated {
  opacity: 1;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--text-color);
}

/* Nouveau style pour le header avec mise en évidence du nom */
.profile-header {
  background: linear-gradient(to right, rgba(0,123,255,0.1), rgba(111,66,193,0.05));
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.profile-header:hover {
  box-shadow: 0 6px 12px rgba(0,0,0,0.08);
}

.profile-header-main {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.profile-avatar-large {
  position: relative;
  font-size: 6rem;
  color: var(--primary-color);
  margin-right: 30px;
  line-height: 1;
}

.avatar-status {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #ccc;
  border: 2px solid white;
}

.avatar-status.active {
  background-color: #28a745;
}

.profile-name-container {
  flex: 1;
}

.username-display {
  font-size: 1.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--primary-color);
  margin-bottom: 5px;
  position: relative;
  display: inline-block;
  padding-bottom: 2px;
}

.username-display::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background-color: var(--primary-color);
}

.profile-name-large {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 10px 0;
  color: var(--text-color);
}

.profile-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.profile-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.profile-badge i {
  margin-right: 5px;
}

.superadmin-badge {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.admin-badge {
  background-color: rgba(111, 66, 193, 0.1);
  color: #6f42c1;
}

.user-badge {
  background-color: rgba(0, 123, 255, 0.1);
  color: #007bff;
}

.status-badge {
  background-color: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.status-badge.active-badge {
  background-color: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.profile-details {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.profile-info {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.profile-detail-row {
  display: flex;
  align-items: center;
}

.profile-email {
  display: flex;
  align-items: center;
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 0;
}

.profile-email i {
  margin-right: 8px;
  color: var(--primary-color);
}

.section-title {
  position: relative;
  display: inline-block;
}

.section-title::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -8px;
  width: 50px;
  height: 3px;
  background-color: var(--primary-color);
  border-radius: 2px;
}

/* En-tête de profil */
.profile-header {
  display: flex;
  align-items: center;
  padding: 2rem;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.profile-avatar {
  position: relative;
  min-width: 100px;
  height: 100px;
  margin-right: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-avatar i {
  font-size: 4rem;
  color: var(--primary-color);
}

.avatar-status {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: var(--danger-color);
  border: 2px solid var(--card-bg);
}

.avatar-status.active {
  background-color: var(--success-color);
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-color);
}

.profile-role,
.profile-email {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  color: var(--text-secondary);
}

.profile-role i,
.profile-email i {
  margin-right: 8px;
  font-size: 1rem;
}

.profile-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 15px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn i {
  margin-right: 5px;
}

.action-btn.primary {
  background-color: var(--primary-color);
  color: white;
}

.action-btn.primary:hover {
  background-color: #0069d9;
}

.action-btn.secondary {
  background-color: #f8f9fa;
  color: var(--text-color);
  border: 1px solid #dee2e6;
}

.action-btn.secondary:hover {
  background-color: #e9ecef;
}

/* Statistiques */
.stats-container {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 2rem;
}

.stat-card {
  background-color: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  min-width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.stat-icon.primary {
  background-color: rgba(0, 123, 255, 0.1);
  color: var(--primary-color);
}

.stat-icon.success {
  background-color: rgba(40, 167, 69, 0.1);
  color: var(--success-color);
}

.stat-icon.warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: var(--warning-color);
}

.stat-icon.info {
  background-color: rgba(23, 162, 184, 0.1);
  color: var(--info-color);
}

.stat-icon i {
  font-size: 1.5rem;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* Informations détaillées */
.details-container {
  margin-bottom: 2rem;
}

.details-card {
  background-color: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.detail-item {
  padding: 1rem;
  border-radius: 8px;
  background-color: rgba(0, 0, 0, 0.02);
}

.detail-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.detail-value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  word-break: break-word;
}

.detail-value.status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  background-color: var(--danger-color);
  color: white;
}

.detail-value.status.active {
  background-color: var(--success-color);
}

/* Activités récentes */
.recent-activities {
  margin-bottom: 2rem;
}

.empty-activities {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: var(--card-bg);
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.empty-activities i {
  font-size: 3rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  opacity: 0.5;
}

.activity-timeline {
  background-color: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-icon {
  min-width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.timeline-icon.primary {
  background-color: rgba(0, 123, 255, 0.1);
  color: var(--primary-color);
}

.timeline-icon.success {
  background-color: rgba(40, 167, 69, 0.1);
  color: var(--success-color);
}

.timeline-icon.warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: var(--warning-color);
}

.timeline-icon.info {
  background-color: rgba(23, 162, 184, 0.1);
  color: var(--info-color);
}

.timeline-icon.accent {
  background-color: rgba(111, 66, 193, 0.1);
  color: var(--accent-color);
}

.timeline-icon i {
  font-size: 1.5rem;
}

.timeline-content {
  flex: 1;
}

.timeline-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 5px;
  color: var(--text-color);
}

.timeline-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.timeline-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
  opacity: 0.8;
}

/* Modal d'édition */
.edit-profile-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
}

.modal-content {
  position: relative;
  width: 90%;
  max-width: 500px;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  z-index: 1001;
  transform: translateY(20px);
  opacity: 0;
  animation: fadeInUp 0.3s forwards;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: var(--danger-color);
}

.modal-body {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg, white);
  color: var(--text-color);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

/* Boutons d'action */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1.2rem;
  border-radius: 30px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  gap: 0.5rem;
}

.action-btn i {
  font-size: 1.1rem;
}

.action-btn.primary {
  background-color: var(--primary-color);
  color: white;
}

.action-btn.primary:hover {
  background-color: #0069d9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 123, 255, 0.3);
}

.action-btn.secondary {
  background-color: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.action-btn.secondary:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Responsive */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }
  
  .profile-avatar {
    margin-right: 0;
    margin-bottom: 1.5rem;
  }
  
  .profile-actions {
    margin-left: 0;
    margin-top: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .details-card {
    grid-template-columns: 1fr;
  }
}

/* Support du thème sombre */
:global(.dark-theme) .profile-container {
  --card-bg: #2d3748;
  --text-color: #f7fafc;
  --text-secondary: #cbd5e0;
  --border-color: #4a5568;
  --input-bg: #2d3748;
}
</style>
