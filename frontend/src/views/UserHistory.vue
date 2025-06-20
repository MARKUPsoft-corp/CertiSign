<template>
  <div class="user-history-container">
    <div class="section-header">
      <h2 class="section-title">Historique d'activités</h2>
      <div class="header-actions">
        <div class="filter-buttons">
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'all' }" 
            @click="setFilter('all')"
          >
            Toutes les activités
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'viewed' }" 
            @click="setFilter('viewed')"
          >
            <i class="bi bi-eye"></i> Consultations
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'downloaded' }" 
            @click="setFilter('downloaded')"
          >
            <i class="bi bi-download"></i> Téléchargements
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'signed' }" 
            @click="setFilter('signed')"
          >
            <i class="bi bi-pen"></i> Signatures
          </button>
          <button 
            class="filter-btn" 
            :class="{ active: activeFilter === 'created' }" 
            @click="setFilter('created')"
          >
            <i class="bi bi-plus-circle"></i> Créations
          </button>
        </div>
        <div class="search-container">
          <input 
            type="text" 
            v-model="searchQuery" 
            class="search-input" 
            placeholder="Rechercher une activité..."
            @input="filterActivities"
          >
          <i class="bi bi-search search-icon"></i>
        </div>
      </div>
    </div>

    <!-- Message de chargement -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Chargement de votre historique...</p>
    </div>

    <!-- Message d'erreur -->
    <div v-else-if="error" class="error-message">
      <i class="bi bi-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="fetchActivities">Réessayer</button>
    </div>

    <!-- Message si aucune activité -->
    <div v-else-if="filteredActivities.length === 0" class="empty-state">
      <i class="bi bi-calendar-x"></i>
      <h3>Aucune activité trouvée</h3>
      <p>Aucune activité n'a été enregistrée pour le moment ou ne correspond à votre recherche.</p>
    </div>

    <!-- Tableau des activités -->
    <div v-else>
      <!-- Cartes de statistiques -->
      <div class="activity-stats">
        <div class="stat-card">
          <div class="stat-icon primary">
            <i class="bi bi-eye"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ getActivityTypeCount('viewed') }}</div>
            <div class="stat-label">Consultations</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon warning">
            <i class="bi bi-download"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ getActivityTypeCount('downloaded') }}</div>
            <div class="stat-label">Téléchargements</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon success">
            <i class="bi bi-pen"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ getActivityTypeCount('signed') }}</div>
            <div class="stat-label">Signatures</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon info">
            <i class="bi bi-plus-circle"></i>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ getActivityTypeCount('created') }}</div>
            <div class="stat-label">Créations</div>
          </div>
        </div>
      </div>

      <div class="activities-table-container desktop-activities">
        <table class="activities-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Document</th>
              <th>Type d'activité</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(activity, index) in filteredActivities" :key="index" class="activity-row">
              <td class="date-column">{{ formatDate(activity.timestamp) }}</td>
              <td class="document-column">{{ activity.document_title || 'Document inconnu' }}</td>
              <td class="type-column">
                <span class="activity-badge" :class="getActivityBadgeClass(activity.activity_type)">
                  {{ getActivityTypeLabel(activity.activity_type) }}
                </span>
              </td>
              <td class="description-column">{{ activity.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Version mobile des activités -->
      <div class="mobile-activities">
        <div 
          v-for="(activity, index) in filteredActivities" 
          :key="index" 
          class="mobile-activity-card"
        >
          <div class="mobile-activity-header">
            <div class="mobile-activity-title">{{ activity.document_title || 'Document inconnu' }}</div>
            <span class="activity-badge" :class="getActivityBadgeClass(activity.activity_type)">
              {{ getActivityTypeLabel(activity.activity_type) }}
            </span>
          </div>
          <div class="mobile-activity-content">
            <div class="mobile-activity-description">{{ activity.description }}</div>
          </div>
          <div class="mobile-activity-footer">
            <div class="mobile-activity-date">{{ formatDate(activity.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DocumentService from '@/services/DocumentService';

// Variables réactives
const activities = ref([]);
const filteredActivities = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const activeFilter = ref('all');

// Récupérer l'historique des activités
onMounted(async () => {
  await fetchActivities();
});

// Fonction pour récupérer les activités de l'utilisateur
async function fetchActivities() {
  loading.value = true;
  error.value = null;
  
  try {
    // Récupérer les activités directement du backend sans transformation
    const response = await DocumentService.getMyActivities();
    console.log('Activités récupérées du backend:', response.data);
    
    // Utiliser directement les données du backend
    activities.value = response.data;
    filteredActivities.value = [...response.data]; // Copie initiale pour les filtres
    
    loading.value = false;
  } catch (err) {
    console.error('Erreur lors de la récupération des activités:', err);
    error.value = 'Erreur lors de la récupération de votre historique d\'activités. Veuillez réessayer plus tard.';
    loading.value = false;
  }
}

// Fonction pour filtrer les activités en fonction du type et de la recherche
function filterActivities() {
  const query = searchQuery.value.toLowerCase();
  
  const filtered = activities.value.filter(activity => {
    const matchesSearch = (
      (activity.description && activity.description.toLowerCase().includes(query)) ||
      (activity.document_title && activity.document_title.toLowerCase().includes(query)) ||
      (getActivityTypeLabel(activity.activity_type).toLowerCase().includes(query))
    );
    
    // Filtrer par type d'activité
    const matchesType = activeFilter.value === 'all' || activity.activity_type === activeFilter.value;
    
    return matchesSearch && matchesType;
  });
  
  filteredActivities.value = filtered;
}

// Appliquer le filtre d'activité
function setFilter(filter) {
  activeFilter.value = filter;
  if (filter === 'all') {
    filteredActivities.value = activities.value;
  } else {
    filteredActivities.value = activities.value.filter(activity => activity.activity_type === filter);
  }
}

// Compter le nombre d'activités par type
function getActivityTypeCount(activityType) {
  return activities.value.filter(activity => activity.activity_type === activityType).length;
}

// Formatage de la date
function formatDate(dateString) {
  if (!dateString) return 'Date inconnue';
  
  try {
    const date = new Date(dateString);
    
    // Vérifier si la date est valide
    if (isNaN(date.getTime())) {
      console.error('Format de date invalide:', dateString);
      return 'Date invalide';
    }
    
    // Format: "12 mai 2025 à 14:30"
    const options = { 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return date.toLocaleDateString('fr-FR', options).replace(' à ', ' à ');
  } catch (error) {
    console.error('Erreur lors du formatage de la date:', error);
    return 'Erreur de date';
  }
}

// Récupérer le libellé du type d'activité
function getActivityTypeLabel(activityType) {
  const activityLabels = {
    'viewed': 'Consultation',
    'downloaded': 'Téléchargement',
    'signed': 'Signature',
    'created': 'Création',
    'deleted': 'Suppression',
    'updated': 'Modification'
  };
  
  // Si l'API renvoie directement un libellé via activity_type_display, l'utiliser
  if (activityType && activityType.includes('_display')) {
    return activityType;
  }
  
  return activityLabels[activityType] || 'Autre activité';
}

// Récupérer la classe CSS pour le badge d'activité
function getActivityBadgeClass(activityType) {
  const badgeClasses = {
    'created': 'badge-info',
    'viewed': 'badge-secondary',
    'modified': 'badge-primary',
    'signed': 'badge-success',
    'downloaded': 'badge-warning'
  };
  
  return badgeClasses[activityType] || 'badge-secondary';
}
</script>

<style scoped>
.user-history-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(120deg, rgba(var(--background-color-rgb), 0.7) 0%, rgba(var(--background-color-rgb), 0.9) 100%);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.5s ease-out;
}

/* Animation d'entrée */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 30px;
  position: relative;
}

.section-title {
  font-size: 35px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 20px;
  position: relative;
  display: inline-block;
  animation: fadeInLeft 0.6s cubic-bezier(0.23, 1, 0.32, 1) forwards;
  opacity: 0;
  transform: translateX(-20px);
}

@keyframes fadeInLeft {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.section-title::after {
  content: '';
  display: block;
  width: 80px;
  height: 3px;
  margin-top: 8px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color, #7952b3) 100%);
  border-radius: 2px;
  animation: expandWidth 0.8s ease-out forwards;
  transform-origin: left;
}

@keyframes expandWidth {
  from { width: 0; }
  to { width: 80px; }
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 15px;
  width: 100%;
  animation: slideDown 0.6s cubic-bezier(0.23, 1, 0.32, 1) forwards;
  opacity: 0;
  transform: translateY(-20px);
}

@keyframes slideDown {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-btn {
  padding: 8px 16px;
  border-radius: 30px;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.filter-btn::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: var(--primary-color);
  border-radius: inherit;
  top: 0;
  left: 0;
  opacity: 0;
  transform: scale(0);
  transition: transform 0.4s cubic-bezier(0.3, 0.7, 0.4, 1.5), opacity 0.3s ease;
  z-index: -1;
}

.filter-btn:hover {
  color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  border-color: var(--primary-color);
}

.filter-btn.active {
  color: white;
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(var(--primary-color-rgb), 0.25);
  transform: translateY(-2px);
}

.filter-btn.active:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(var(--primary-color-rgb), 0.3);
}

.filter-btn i {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.filter-btn:hover i {
  transform: scale(1.2);
}

.filter-buttons {
  display: flex;
  gap: 12px;
  margin-right: 20px;
  flex-wrap: wrap;
}

.search-container {
  position: relative;
  flex: 1;
  max-width: 350px;
}

.search-input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border-radius: 30px;
  border: 1px solid var(--border-color);
  background-color: var(--input-bg);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(var(--primary-color-rgb), 0.15);
  transform: translateY(-2px);
}

.search-icon {
  position: absolute;
  top: 50%;
  left: 15px;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 16px;
  pointer-events: none;
  transition: all 0.3s ease;
}

.search-input:focus + .search-icon {
  color: var(--primary-color);
}

/* États d'erreur et de chargement */
.loading-container, .error-message, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background-color: var(--card-bg);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.5s ease-out;
  margin: 20px 0;
}

.loading-container .spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(var(--primary-color-rgb), 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 25px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message i, .empty-state i {
  font-size: 70px;
  color: var(--danger-color, #dc3545);
  margin-bottom: 25px;
  animation: bounceIn 0.8s;
}

@keyframes bounceIn {
  0% { 
    transform: scale(0); 
    opacity: 0;
  }
  60% { 
    transform: scale(1.1); 
    opacity: 1;
  }
  100% { 
    transform: scale(1); 
  }
}

.empty-state i {
  color: var(--text-secondary);
}

.error-message p, .empty-state p {
  margin-bottom: 25px;
  color: var(--text-secondary);
  max-width: 500px;
}

.error-message h3, .empty-state h3 {
  font-size: 24px;
  margin-bottom: 15px;
  color: var(--text-color);
}

/* Cartes de statistiques */
.activity-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
  margin-top: 20px;
}

.stat-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  animation: slideInUp 0.5s forwards;
  opacity: 0;
  transform: translateY(30px);
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, var(--primary-color) 0%, transparent 100%);
  opacity: 0.3;
  transition: all 0.3s ease;
}

.stat-card:hover::after {
  opacity: 0.8;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  margin-right: 20px;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(10deg);
}

.stat-icon.primary {
  background-color: rgba(13, 202, 240, 0.1);
  color: #0dcaf0;
}

.stat-icon.warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
}

.stat-icon.success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.stat-icon.info {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}

.stat-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 5px;
  transition: all 0.3s ease;
}

.stat-card:hover .stat-value {
  transform: scale(1.1);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Tableau des activités */
.activities-table-container {
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  animation: fadeInUp 0.8s ease forwards;
  transform: translateY(30px);
  opacity: 0;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.activities-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 14px;
}

.activities-table th, .activities-table td {
  padding: 16px;
  text-align: left;
  transition: all 0.2s ease;
}

.activities-table th {
  background: linear-gradient(to right, var(--card-header-bg, rgba(0, 0, 0, 0.03)), transparent);
  font-weight: 600;
  color: var(--text-color);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 10;
}

.activities-table th:first-child {
  border-top-left-radius: 16px;
}

.activities-table th:last-child {
  border-top-right-radius: 16px;
}

.activity-row {
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  animation: fadeIn 0.5s forwards;
  opacity: 0;
  position: relative;
}

.activity-row::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 1px;
  width: 0;
  background: linear-gradient(90deg, var(--primary-color), transparent);
  transition: width 0.4s ease;
}

.activity-row:hover::after {
  width: 100%;
}

.activity-row:hover {
  background-color: rgba(var(--primary-color-rgb), 0.03);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.activity-row td {
  border-bottom: 1px solid var(--border-color);
}

.date-column {
  white-space: nowrap;
  color: var(--text-secondary);
  width: 180px;
  font-weight: 500;
}

.document-column {
  font-weight: 600;
  color: var(--text-color);
}

.type-column {
  width: 140px;
}

.activity-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.activity-row:hover .activity-badge {
  transform: scale(1.05);
}

.badge-info {
  background-color: rgba(13, 202, 240, 0.1);
  color: #0dcaf0;
  border: 1px solid rgba(13, 202, 240, 0.2);
}

.badge-primary {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
  border: 1px solid rgba(13, 110, 253, 0.2);
}

.badge-success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
  border: 1px solid rgba(25, 135, 84, 0.2);
}

.badge-warning {
  background-color: rgba(255, 193, 7, 0.1);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.badge-secondary {
  background-color: rgba(108, 117, 125, 0.1);
  color: #6c757d;
  border: 1px solid rgba(108, 117, 125, 0.2);
}

.text-muted {
  color: var(--text-secondary);
  font-style: italic;
}

.description-column {
  color: var(--text-color);
  line-height: 1.5;
  max-width: 400px;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .activity-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}

@media (max-width: 992px) {
  .activities-table {
    font-size: 14px;
  }
  
  .activities-table th, 
  .activities-table td {
    padding: 12px 10px;
  }
  
  .section-title {
    font-size: 22px;
  }
  
  .filter-btn {
    padding: 6px 12px;
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .header-actions {
    width: 100%;
    flex-direction: column;
  }
  
  .filter-buttons {
    flex-wrap: wrap;
    gap: 8px;
    margin-right: 0;
    width: 100%;
  }
  
  .search-container {
    width: 100%;
    max-width: 100%;
  }
  
  .activities-table-container {
    border-radius: 12px;
    overflow-x: auto;
  }
  
  .activities-table {
    min-width: 650px;
  }
  
  .activity-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  /* Ajout d'une version mobile pour les activités */
  .mobile-activities {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 20px;
  }
  
  .desktop-activities {
    display: none;
  }
  
  .mobile-activity-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    animation: fadeInUp 0.5s forwards;
    opacity: 0;
    position: relative;
    border-left: 3px solid var(--primary-color);
    transition: all 0.3s ease;
    margin-bottom: 2px;
  }
  
  .mobile-activity-card:active {
    transform: scale(0.98);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
  }
  
  .mobile-activity-card:hover, .mobile-activity-card:focus {
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
  }
  
  .mobile-activity-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .mobile-activity-title {
    font-weight: 600;
    font-size: 15px;
    color: var(--text-color);
    margin-right: 10px;
    word-break: break-word;
    flex: 1;
    min-width: 60%;
  }
  
  .mobile-activity-date {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 2px;
  }
  
  .mobile-activity-content {
    margin-bottom: 12px;
  }
  
  .mobile-activity-description {
    color: var(--text-color);
    font-size: 14px;
    line-height: 1.4;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    position: relative;
  }
}

@media (max-width: 576px) {
  .activity-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    width: 45px;
    height: 45px;
    font-size: 18px;
  }
  
  .filter-buttons {
    flex-wrap: wrap;
    gap: 8px;
    margin-right: 0;
    width: 100%;
  }
  
  .user-history-container {
    padding: 10px;
  }
  
  .mobile-activities {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}

@media (max-width: 896px) and (orientation: landscape) {
  .activity-stats {
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  
  .stat-card {
    padding: 10px;
  }
  
  .filter-buttons {
    flex-wrap: nowrap;
    overflow-x: auto;
    justify-content: flex-start;
    padding-bottom: 5px;
  }
  
  .user-history-container {
    padding: 10px;
  }
  
  .mobile-activities {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}

/* Version mobile pour petits écrans et version desktop pour grands écrans */
.mobile-activities {
  display: none; /* Masqué par défaut sur grand écran */
}

.desktop-activities {
  display: block; /* Visible par défaut sur grand écran */
}

@media (max-width: 768px) {
  .desktop-activities {
    display: none; /* Masqué sur petit écran */
  }
  
  .mobile-activities {
    display: flex; /* Visible sur petit écran */
  }
}

/* Bulles d'arrière-plan */
.user-history-container::before,
.user-history-container::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  z-index: -1;
  animation: floatBubble 10s ease-in-out infinite;
}

.user-history-container::before {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(var(--primary-color-rgb), 0.1) 0%, rgba(var(--primary-color-rgb), 0) 70%);
  top: -100px;
  right: -100px;
}

.user-history-container::after {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(var(--accent-color-rgb, 121, 82, 179), 0.05) 0%, rgba(var(--accent-color-rgb, 121, 82, 179), 0) 70%);
  bottom: -50px;
  left: -50px;
  animation-delay: 2s;
  animation-duration: 15s;
}

@keyframes floatBubble {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(10px, -10px) scale(1.05);
  }
  50% {
    transform: translate(5px, 15px) scale(0.95);
  }
  75% {
    transform: translate(-10px, 5px) scale(1.02);
  }
}

@media (max-width: 576px) {
  .user-history-container::before,
  .user-history-container::after {
    opacity: 0.5; /* Réduire l'opacité sur mobile pour de meilleures performances */
  }
}

/* Améliorer l'affichage sur mobile avec des styles spécifiques pour les petits écrans et les très petits écrans (comme iPhone SE) */
@media (max-width: 576px) {
  .activity-stats {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .stat-card {
    padding: 15px;
    margin-bottom: 0;
  }
  
  .stat-icon {
    width: 45px;
    height: 45px;
    font-size: 18px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .stat-label {
    font-size: 12px;
  }
  
  .filter-buttons {
    justify-content: flex-start;
    padding-bottom: 8px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none; /* Firefox */
    white-space: nowrap;
    flex-wrap: nowrap;
    gap: 8px;
  }
  
  .filter-buttons::-webkit-scrollbar {
    display: none; /* Chrome, Safari */
  }
  
  .filter-btn {
    flex: 0 0 auto;
    padding: 6px 12px;
    font-size: 13px;
    border-radius: 20px;
    white-space: nowrap;
  }
  
  .filter-btn i {
    margin-right: 4px;
  }
  
  .search-input {
    padding: 10px 15px 10px 35px;
    font-size: 14px;
    height: 40px;
  }
  
  .search-container {
    width: 100%;
  }
  
  .section-title {
    font-size: 40px;
    margin-bottom: 15px;
  }
  
  .section-title::after {
    width: 60px;
    height: 3px;
  }
  
  .user-history-container {
    padding: 15px 10px;
  }
  
  .mobile-activities {
    gap: 10px;
    flex-direction: column;
  }
  
  .mobile-activity-card {
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 5px;
  }
  
  .mobile-activity-header {
    margin-bottom: 8px;
  }
  
  .mobile-activity-title {
    font-size: 14px;
    line-height: 1.3;
  }
  
  .mobile-activity-description {
    font-size: 13px;
    line-height: 1.4;
  }
  
  .mobile-activity-date {
    font-size: 11px;
    opacity: 0.8;
  }
  
  .activity-badge {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  /* Améliorations pour les états d'erreur et de chargement */
  .loading-container {
    padding: 30px 15px;
  }
  
  .spinner {
    width: 35px;
    height: 35px;
    border-width: 3px;
  }
  
  .empty-state {
    padding: 40px 15px;
  }
  
  .empty-state i {
    font-size: 36px;
    margin-bottom: 15px;
  }
  
  .empty-state h3 {
    font-size: 18px;
    margin-bottom: 8px;
  }
  
  .empty-state p {
    font-size: 14px;
    line-height: 1.4;
    max-width: 270px;
    margin: 0 auto;
  }
  
  .error-message {
    padding: 20px 15px;
  }
  
  .error-message i {
    font-size: 32px;
    margin-bottom: 10px;
  }
  
  .error-message p {
    font-size: 14px;
    margin-bottom: 15px;
  }
}

/* Optimisations pour iPhone SE et autres très petits écrans */
@media (max-width: 375px) {
  .stat-card {
    padding: 12px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
    margin-right: 10px;
  }
  
  .filter-btn {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  .section-title {
    font-size: 18px;
  }
  
  .user-history-container {
    padding: 10px 8px;
  }
  
  .mobile-activity-title {
    font-size: 13px;
  }
  
  .mobile-activity-description {
    font-size: 12px;
  }
  
  .search-input {
    font-size: 13px;
    height: 38px;
  }
}
</style>
