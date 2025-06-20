import axios from 'axios';
import AuthService from './AuthService';

// URL de l'API définie globalement pour le service
const API_URL = process.env.VUE_APP_API_URL || 'https://192.168.4.131:8000';

class DocumentService {
  /**
   * Récupère tous les documents signés de l'utilisateur connecté
   */
  async getDocuments() {
    const token = AuthService.getToken();
    console.log('Token d\'authentification:', token ? 'Présent' : 'Manquant');
    
    // Utiliser l'endpoint des signatures au lieu des documents
    const url = `${API_URL}/api/documents/signatures/`;
    console.log('Récupération des documents signés depuis:', url);
    
    try {
      const response = await axios.get(url, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      // Log de la réponse pour le débogage
      console.log('Réponse de l\'API:', response.status, response.statusText);
      console.log('Données reçues:', response.data);
      
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des documents signés:', error.message);
      if (error.response) {
        console.error('Statut:', error.response.status);
        console.error('Données d\'erreur:', error.response.data);
      }
      throw error;
    }
  }
  
  /**
   * Récupère un document signé spécifique par son ID
   */
  async getDocument(documentId) {
    const token = AuthService.getToken();
    return axios.get(`${API_URL}/api/documents/signatures/${documentId}/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
  
  /**
   * Télécharge un document signé
   */
  async downloadDocument(documentId) {
    const token = AuthService.getToken();
    return axios.get(`${API_URL}/api/documents/signatures/${documentId}/download/`, {
      headers: { 'Authorization': `Bearer ${token}` },
      responseType: 'blob'
    });
  }
  
  /**
   * Télécharge spécifiquement le document original (non signé)
   */
  async downloadOriginalDocument(documentId) {
    const token = AuthService.getToken();
    return axios.get(`${API_URL}/api/documents/signatures/${documentId}/download_original/`, {
      headers: { 'Authorization': `Bearer ${token}` },
      responseType: 'blob'
    });
  }
  
  /**
   * Téléverse un document pour signature via le store_original endpoint
   */
  async uploadDocument(documentData) {
    const token = AuthService.getToken();
    const formData = new FormData();
    
    // Ajouter toutes les propriétés à FormData
    Object.keys(documentData).forEach(key => {
      formData.append(key, documentData[key]);
    });
    
    return axios.post(`${API_URL}/api/documents/store_original/`, formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
  }
  
  /**
   * Met à jour un document signé existant
   */
  async updateDocument(documentId, documentData) {
    const token = AuthService.getToken();
    const formData = new FormData();
    
    // Ajouter toutes les propriétés à FormData
    Object.keys(documentData).forEach(key => {
      formData.append(key, documentData[key]);
    });
    
    return axios.patch(`${API_URL}/api/documents/signatures/${documentId}/`, formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
  }
  
  /**
   * Supprime un document signé
   */
  async deleteDocument(documentId) {
    const token = AuthService.getToken();
    return axios.delete(`${API_URL}/api/documents/signatures/${documentId}/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
  
  /**
   * Enregistre une activité utilisateur sur un document
   * @param {string} documentId - L'ID du document concerné
   * @param {string} activityType - Le type d'activité (created, viewed, modified, signed, downloaded)
   * @param {string} description - Description de l'activité (optionnel)
   * @param {Object} metadata - Métadonnées supplémentaires au format JSON (optionnel)
   */
  async recordActivity(documentId, activityType, description = '', metadata = {}) {
    try {
      const token = AuthService.getToken();
      if (!token) {
        console.warn('Impossible d\'enregistrer l\'activité: utilisateur non authentifié');
        return null;
      }
      
      // Préparer les données pour l'API
      const activityData = {
        document_id: documentId,
        activity_type: activityType,
        description: description
      };
      
      // Ajouter les métadonnées si présentes
      if (Object.keys(metadata).length > 0) {
        activityData.metadata = metadata;
      }
      
      // Envoyer la requête
      const response = await axios.post(
        `${API_URL}/api/documents/activities/record_activity/`,
        activityData,
        {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement de l\'activité:', error);
      // Ne pas propager l'erreur pour éviter de perturber l'expérience utilisateur
      return null;
    }
  }
  
  /**
   * Signe un document
   */
  async signDocument(id, signedFile, signatureData) {
    const token = AuthService.getToken();
    const formData = new FormData();
    formData.append('signed_file', signedFile);
    formData.append('signature_data', JSON.stringify(signatureData));
    
    return axios.post(`${API_URL}/api/documents/documents/${id}/sign/`, formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    });
  }
  
  /**
   * Récupère les activités liées aux documents
   */
  async getDocumentActivities() {
    const token = AuthService.getToken();
    return axios.get(`${API_URL}/api/documents/activities/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
  
  /**
   * Récupère les activités personnelles de l'utilisateur
   */
  async getMyActivities() {
    const token = AuthService.getToken();
    return axios.get(`${API_URL}/api/documents/activities/my_activities/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
  
  // La méthode recordActivity est déjà définie plus haut dans le fichier
}

const documentService = new DocumentService();

// Exporter l'API_URL pour qu'il soit accessible depuis d'autres fichiers
documentService.API_URL = API_URL;

export default documentService;
