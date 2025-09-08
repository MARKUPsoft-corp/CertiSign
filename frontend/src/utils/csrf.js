/**
 * Utilitaires pour la gestion des tokens CSRF
 */

/**
 * Récupère le token CSRF depuis les cookies
 * @returns {string|null} Le token CSRF ou null s'il n'existe pas
 */
export function getCSRFToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  
  return cookieValue;
}

/**
 * Récupère le token CSRF depuis les cookies ou en fait une requête GET
 * @returns {Promise<string>} Le token CSRF
 */
export async function ensureCSRFToken() {
  let token = getCSRFToken();
  
  if (!token) {
    // Si pas de token dans les cookies, faire une requête GET pour en obtenir un
    try {
      console.log('Tentative de récupération du token CSRF depuis les organisations...');
      
      const response = await fetch('https://ppd.camgovca.cm/api/users/organizations/', {
        method: 'GET',
        credentials: 'include', // Important pour recevoir les cookies
        headers: {
          'Accept': 'application/json',
        }
      });
      
      if (response.ok) {
        // Récupérer le token depuis les cookies après la requête
        token = getCSRFToken();
        
        if (token) {
          console.log('Token CSRF récupéré avec succès:', token.substring(0, 20) + '...');
        } else {
          console.warn('Impossible de récupérer le token CSRF après la requête');
        }
      } else {
        console.error('Erreur lors de la récupération des organisations:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Erreur lors de la récupération du token CSRF:', error);
    }
  } else {
    console.log('Token CSRF déjà présent:', token.substring(0, 20) + '...');
  }
  
  return token;
}

/**
 * Ajoute le token CSRF aux headers d'une requête axios
 * @param {Object} config - Configuration axios
 * @returns {Object} Configuration modifiée
 */
export function addCSRFTokenToHeaders(config) {
  const token = getCSRFToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers['X-CSRFToken'] = token;
  }
  return config;
} 