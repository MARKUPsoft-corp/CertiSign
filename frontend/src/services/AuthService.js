/**
 * Service d'authentification pour CertiSign
 * Gère la connexion, la déconnexion et la session utilisateur
 */

import axios from 'axios';

const API_URL = 'https://ppd.camgovca.cm';

// ID de l'intercepteur pour pouvoir l'enlever si nécessaire
let interceptorId = null;

class AuthService {
  /**
   * Initialisation du service d'authentification
   */
  constructor() {
    this.token = localStorage.getItem('token');
    this.user = JSON.parse(localStorage.getItem('user')) || null;
    
    // Si un token existe déjà au démarrage, configurer l'intercepteur
    if (this.token) {
      this.setupAxiosInterceptors();
    }
  }

  /**
   * Authentifier un utilisateur avec ses identifiants
   * @param {Object} credentials - Les identifiants de l'utilisateur
   * @returns {Promise} - Promesse résolue avec les données utilisateur
   */
  async login(credentials) {
    try {
      const response = await axios.post(`${API_URL}/api/users/login/`, credentials);
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Mettre à jour les propriétés locales
        this.token = response.data.token;
        this.user = response.data.user;
        
        // Configurer l'intercepteur pour les futures requêtes
        this.setupAxiosInterceptors();
        
        // Enregistrer l'activité de connexion
        this.logActivity('login', 'Connexion au système');
      }
      return response.data;
    } catch (error) {
      console.error('Erreur de connexion:', error);
      throw error;
    }
  }

  /**
   * Déconnecter l'utilisateur actuel
   */
  logout() {
    // Enregistrer l'activité de déconnexion avant de supprimer les tokens
    if (this.user) {
      this.logActivity('logout', 'Déconnexion du système');
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.token = null;
    this.user = null;
  }

  /**
   * Vérifier si l'utilisateur est authentifié
   * @returns {Boolean} - Vrai si l'utilisateur est authentifié
   */
  isAuthenticated() {
    return !!this.token && !!this.user;
  }
  
  /**
   * Obtenir le token d'authentification
   * @returns {String|null} - Token JWT ou null si non authentifié
   */
  getToken() {
    return this.token;
  }

  /**
   * Obtenir l'utilisateur actuellement connecté
   * @returns {Object|null} - Données de l'utilisateur ou null
   */
  getCurrentUser() {
    return this.user;
  }

  /**
   * Mettre à jour les informations de l'utilisateur actuel
   * @param {Object} userData - Nouvelles données utilisateur
   */
  updateCurrentUser(userData) {
    this.user = { ...this.user, ...userData };
    localStorage.setItem('user', JSON.stringify(this.user));
  }

  /**
   * Configurer l'intercepteur axios pour ajouter automatiquement le token
   */
  setupAxiosInterceptors() {
    // Supprimer l'ancien intercepteur s'il existe pour éviter les doublons
    if (interceptorId !== null) {
      axios.interceptors.request.eject(interceptorId);
    }
    
    // Ajouter le nouvel intercepteur
    interceptorId = axios.interceptors.request.use(
      config => {
        if (this.token) {
          config.headers['Authorization'] = `Bearer ${this.token}`;
        }
        return config;
      },
      error => {
        return Promise.reject(error);
      }
    );
    
    console.log('Intercepteur Axios configuré avec le token JWT');
  }

  /**
   * Enregistrer une activité utilisateur
   * @param {String} actionType - Type d'action (login, logout, etc.)
   * @param {String} description - Description de l'activité
   */
  async logActivity(actionType, description) {
    if (!this.user) return;
    
    try {
      await axios.post(`${API_URL}/api/users/activity-log/`, {
        action_type: actionType,
        description: description
      });
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement de l\'activité:', error);
    }
  }

  /**
   * Vérifier si le token est toujours valide
   * @returns {Promise<Boolean>} - Vrai si le token est valide
   */
  async validateToken() {
    if (!this.token) return false;
    
    try {
      console.log('Vérification de la validité du token JWT:', this.token);
      // Appel à l'API sans utiliser la réponse, juste pour vérifier si le token est valide
      await axios.post(`${API_URL}/api/users/token-verify/`, {
        token: this.token
      });
      console.log('Token JWT valide');
      return true;
    } catch (error) {
      console.error('Token JWT invalide ou expiré, déconnexion...', error);
      this.logout();
      return false;
    }
  }
}

// Exporter une instance unique du service d'authentification
export default new AuthService();
