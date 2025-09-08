/**
 * Configuration globale pour Axios avec gestion automatique des tokens CSRF
 */

import axios from 'axios';
import { getCSRFToken, ensureCSRFToken } from '@/utils/csrf';

// Configuration de base pour axios
axios.defaults.baseURL = 'https://ppd.camgovca.cm';
axios.defaults.withCredentials = true; // Important pour les cookies CSRF
axios.defaults.timeout = 15000;

// Intercepteur pour ajouter automatiquement le token CSRF aux requêtes
axios.interceptors.request.use(
  async (config) => {
    // Ajouter le token CSRF pour les méthodes qui modifient les données
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method?.toUpperCase())) {
      try {
        // Récupérer le token CSRF existant
        const csrfToken = getCSRFToken();
        if (csrfToken) {
          config.headers = config.headers || {};
          config.headers['X-CSRFToken'] = csrfToken;
          console.log('Token CSRF ajouté à la requête:', config.url);
        } else {
          console.warn('Aucun token CSRF trouvé pour la requête:', config.url);
        }
      } catch (error) {
        console.warn('Impossible d\'ajouter le token CSRF:', error);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs CSRF
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Si l'erreur est liée au CSRF, essayer de récupérer un nouveau token
    if (error.response?.status === 403 && 
        error.response?.data?.detail?.includes('CSRF')) {
      console.log('Erreur CSRF détectée, tentative de récupération d\'un nouveau token...');
      
      try {
        // Forcer la récupération d'un nouveau token CSRF
        await ensureCSRFToken();
        
        // Retenter la requête originale
        const originalRequest = error.config;
        const csrfToken = getCSRFToken();
        
        if (csrfToken) {
          originalRequest.headers['X-CSRFToken'] = csrfToken;
          return axios(originalRequest);
        }
      } catch (retryError) {
        console.error('Échec de la récupération du token CSRF:', retryError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axios; 