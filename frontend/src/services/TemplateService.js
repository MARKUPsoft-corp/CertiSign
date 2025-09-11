import axios from 'axios';
import AuthService from './AuthService';

const API_URL = process.env.VUE_APP_API_URL || 'https://ppd.camgovca.cm/api';

class TemplateService {
  /**
   * Récupère tous les templates de signature de l'utilisateur
   */
  async getTemplates(organizationName) {
    const token = AuthService.getToken();
    
    try {
      const config = {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {}
      };

      if (organizationName) {
        config.params.organization_name = organizationName;
      }

      const response = await axios.get(`${API_URL}/signature-templates/templates/`, config);
      
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des templates:', error);
      throw error;
    }
  }
  
  /**
   * Récupère un template spécifique par son ID
   */
  async getTemplate(templateId) {
    const token = AuthService.getToken();
    
    try {
      console.log("🔍 [DEBUG] Requête API pour template:", `${API_URL}/signature-templates/templates/${templateId}/`);
      const response = await axios.get(`${API_URL}/signature-templates/templates/${templateId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log("🔍 [DEBUG] Réponse API template:", response.data);
      return response.data;
    } catch (error) {
      console.error(`Erreur lors de la récupération du template ${templateId}:`, error);
      throw error;
    }
  }
  
  /**
   * Crée un nouveau template de signature
   */
  async createTemplate(templateData) {
    const token = AuthService.getToken();
    
    // Création d'un FormData pour l'envoi de fichiers
    const formData = new FormData();
    
    // Ajout des champs de base
    formData.append('name', templateData.name);
    
    // Ajout des fichiers
    if (templateData.original_document) {
      formData.append('original_document', templateData.original_document);
    }
    
    if (templateData.signature_image) {
      formData.append('signature_image', templateData.signature_image);
    }
    
    if (templateData.preview_document) {
      formData.append('preview_document', templateData.preview_document);
    }
    
    // Ajout des configurations
    formData.append('qr_size', templateData.qr_size || 'medium');
    formData.append('page_application', templateData.page_application || 'all');
    
    // Ajout des positions au format JSON
    if (templateData.qr_positions) {
      formData.append('qr_positions', JSON.stringify(templateData.qr_positions));
    }
    
    if (templateData.signature_positions) {
      formData.append('signature_positions', JSON.stringify(templateData.signature_positions));
    }
    
    if (templateData.selected_pages) {
      formData.append('selected_pages', JSON.stringify(templateData.selected_pages));
    }
    
    // Ajout de la taille de la signature
    if (templateData.signature_size) {
      formData.append('signature_size', templateData.signature_size);
    }
    
    // Ajout des informations d'organisation si disponibles
    if (templateData.organization_name) {
      formData.append('organization_name', templateData.organization_name);
    }
    
    if (templateData.user_role) {
      formData.append('user_role', templateData.user_role);
    }
    
    if (templateData.organization_role) {
      formData.append('organization_role', templateData.organization_role);
    }
    
    try {
      const response = await axios.post(`${API_URL}/signature-templates/templates/`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la création du template:', error);
      throw error;
    }
  }
  
  /**
   * Met à jour un template existant
   */
  async updateTemplate(templateId, templateData) {
    const token = AuthService.getToken();
    
    // Création d'un FormData pour l'envoi de fichiers
    const formData = new FormData();
    
    // Ajout des champs à mettre à jour
    Object.keys(templateData).forEach(key => {
      // Pour les fichiers, vérifier s'ils sont des objets File
      if (key === 'original_document' || key === 'signature_image' || key === 'preview_document') {
        if (templateData[key] && templateData[key] instanceof File) {
          formData.append(key, templateData[key]);
        }
      }
      // Pour les objets JSON, les convertir en chaîne
      else if (key === 'qr_positions' || key === 'signature_positions' || key === 'selected_pages') {
        if (templateData[key]) {
          formData.append(key, JSON.stringify(templateData[key]));
        }
      }
      // Pour les autres champs, les ajouter directement
      else {
        formData.append(key, templateData[key]);
      }
    });
    
    try {
      const response = await axios.patch(`${API_URL}/signature-templates/templates/${templateId}/`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data;
    } catch (error) {
      if (error.response && error.response.data) {
        console.error(`Erreur lors de la mise à jour du template ${templateId}:`, error.response.data);
      } else {
        console.error(`Erreur lors de la mise à jour du template ${templateId}:`, error);
      }
      throw error;
    }
  }
  
  /**
   * Supprime un template
   */
  async deleteTemplate(templateId) {
    const token = AuthService.getToken();
    
    try {
      const response = await axios.delete(`${API_URL}/signature-templates/templates/${templateId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data;
    } catch (error) {
      console.error(`Erreur lors de la suppression du template ${templateId}:`, error);
      throw error;
    }
  }
  
  /**
   * Télécharge le document original d'un template
   */
  async downloadOriginal(templateId) {
    const token = AuthService.getToken();
    
    try {
      const response = await axios.get(`${API_URL}/signature-templates/templates/${templateId}/download_original/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      });
      
      return response.data;
    } catch (error) {
      console.error(`Erreur lors du téléchargement du document original du template ${templateId}:`, error);
      throw error;
    }
  }
  
  /**
   * Télécharge l'aperçu d'un template
   */
  async downloadPreview(templateId) {
    const token = AuthService.getToken();
    
    try {
      const response = await axios.get(`${API_URL}/signature-templates/templates/${templateId}/download_preview/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      });
      
      return response.data;
    } catch (error) {
      console.error(`Erreur lors du téléchargement de l'aperçu du template ${templateId}:`, error);
      throw error;
    }
  }
  
  /**
   * Récupère l'URL de l'aperçu d'un template pour affichage inline (pas de téléchargement)
   */
  getPreviewUrl(templateId) {
    // Ajouter un paramètre de cache-busting pour forcer le rechargement
    const timestamp = new Date().getTime();
    return `${API_URL}/signature-templates/templates/${templateId}/preview_document/?v=${timestamp}`;
  }
}

export default new TemplateService(); 