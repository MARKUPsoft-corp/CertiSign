/**
 * Service pour la gestion des utilisateurs et des interactions avec le backend Django
 * Gère les opérations CRUD pour les utilisateurs, documents et signatures
 * Utilise CryptoService pour les communications sécurisées
 */
import CryptoService from './CryptoService';
import axios from 'axios';

class UserService {
  constructor() {
    this.baseUrl = 'https://ppd.camgovca.cm';
  }

  /**
   * Récupère les informations de l'utilisateur actuel
   * @returns {Promise<Object>} - Informations de l'utilisateur
   */
  async getCurrentUser() {
    try {
      // Établir une connexion sécurisée si nécessaire
      if (!CryptoService.secureConnectionEstablished) {
        await CryptoService.initSecureConnection();
      }

      // Récupérer l'ID de l'utilisateur depuis le localStorage
      const certificateInfo = localStorage.getItem('certificateInfo');
      if (!certificateInfo) {
        throw new Error('Informations de certificat non disponibles');
      }

      const parsedInfo = JSON.parse(certificateInfo);
      if (!parsedInfo.user_id) {
        throw new Error('ID utilisateur non disponible');
      }

      // Appeler le backend pour obtenir les informations complètes de l'utilisateur
      const response = await CryptoService.sendEncryptedData('/gateway/users/current/', {});
      
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des informations utilisateur:', error);
      throw error;
    }
  }

  /**
   * Récupère la liste des utilisateurs (pour les administrateurs)
   * @param {Object} filters - Filtres optionnels pour la recherche
   * @returns {Promise<Array>} - Liste des utilisateurs
   */
  async getAllUsers(filters = {}) {
    try {
      // Vérifier si l'utilisateur est administrateur
      const isAdmin = localStorage.getItem('isAdmin') === 'true';
      if (!isAdmin) {
        throw new Error('Accès non autorisé');
      }

      // Appeler le backend pour obtenir la liste des utilisateurs
      const response = await CryptoService.sendEncryptedData('/gateway/admin/users/', filters);
      
      return response.users || [];
    } catch (error) {
      console.error('Erreur lors de la récupération de la liste des utilisateurs:', error);
      throw error;
    }
  }

  /**
   * Supprime un utilisateur (pour les administrateurs)
   * @param {string} userId - ID de l'utilisateur à supprimer
   * @returns {Promise<Object>} - Résultat de l'opération
   */
  async deleteUser(userId) {
    try {
      // Vérifier si l'utilisateur est administrateur
      const isAdmin = localStorage.getItem('isAdmin') === 'true';
      if (!isAdmin) {
        throw new Error('Accès non autorisé');
      }

      // Appeler le backend pour supprimer l'utilisateur
      const response = await CryptoService.sendEncryptedData('/gateway/admin/users/delete/', {
        user_id: userId
      });
      
      return response;
    } catch (error) {
      console.error(`Erreur lors de la suppression de l'utilisateur ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Récupère les documents signés d'un utilisateur
   * @param {string} userId - ID de l'utilisateur (optionnel, utilise l'utilisateur courant par défaut)
   * @returns {Promise<Array>} - Liste des documents signés
   */
  async getUserDocuments(userId = null) {
    try {
      // Si aucun ID utilisateur n'est fourni, utiliser l'utilisateur courant
      if (!userId) {
        const certificateInfo = localStorage.getItem('certificateInfo');
        if (!certificateInfo) {
          throw new Error('Informations de certificat non disponibles');
        }

        const parsedInfo = JSON.parse(certificateInfo);
        userId = parsedInfo.user_id;
      }

      // Vérifier si l'accès est autorisé (admin ou propriétaire)
      const isAdmin = localStorage.getItem('isAdmin') === 'true';
      const isOwner = userId === JSON.parse(localStorage.getItem('certificateInfo')).user_id;
      
      if (!isAdmin && !isOwner) {
        throw new Error('Accès non autorisé');
      }

      // Endpoint différent selon le type d'utilisateur
      const endpoint = isAdmin 
        ? '/gateway/admin/documents/' 
        : '/gateway/documents/';

      // Appeler le backend pour obtenir les documents
      const response = await CryptoService.sendEncryptedData(endpoint, {
        user_id: userId
      });
      
      return response.documents || [];
    } catch (error) {
      console.error('Erreur lors de la récupération des documents:', error);
      throw error;
    }
  }

  /**
   * Signe un document PDF
   * @param {File} pdfFile - Fichier PDF à signer
   * @param {string} certificatePassword - Mot de passe du certificat
   * @returns {Promise<Object>} - Résultat de l'opération de signature
   */
  async signDocument(pdfFile, certificatePassword) {
    try {
      // Vérifier si les informations du certificat sont disponibles
      const certificateInfo = localStorage.getItem('certificateInfo');
      if (!certificateInfo) {
        throw new Error('Informations de certificat non disponibles');
      }
      
      // Récupérer le certificat PFX stocké (ou utiliser celui par défaut de la session)
      const certificateData = JSON.parse(certificateInfo);
      const pfxFile = this.getPfxFile(certificateData);
      
      if (!pfxFile) {
        throw new Error('Certificat PFX non disponible');
      }

      // Préparation des données pour la signature
      const formData = new FormData();
      formData.append('document', pdfFile);
      formData.append('certificate', pfxFile);
      formData.append('password', certificatePassword);
      
      // Endpoint pour l'API Gateway
      const endpoint = '/gateway/sign/';
      
      // Utiliser fetch directement pour gérer les téléchargements de fichiers
      const response = await fetch(this.baseUrl + endpoint, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la signature du document');
      }
      
      // Récupérer le fichier PDF signé
      const blob = await response.blob();
      
      // Extraire le nom de fichier du header Content-Disposition s'il est présent
      let filename = `${pdfFile.name.replace('.pdf', '')}_signed.pdf`;
      const contentDisposition = response.headers.get('content-disposition');
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*)\2|[^;\n]*/i);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]*/g, '');
        }
      }
      
      return {
        success: true,
        signedDocument: URL.createObjectURL(blob),
        filename: filename
      };
    } catch (error) {
      console.error('Erreur lors de la signature du document:', error);
      throw error;
    }
  }

  /**
   * Authentifie un utilisateur avec son certificat PFX
   * @param {Object} authData - Données d'authentification
   * @param {string} authData.certificate - Contenu du certificat PFX en Base64
   * @param {string} authData.password - Mot de passe du certificat
   * @param {string} authData.role - Rôle demandé (user, admin, superadmin)
   * @param {string} authData.filename - Nom du fichier de certificat
   * @returns {Promise<Object>} - Statut de l'authentification et infos du certificat
   */
  async authenticateWithCertificate(authData) {
    try {
      // D'abord essayer avec le nouvel endpoint non chiffré pour débogage
      return await this.authenticateWithCertificateUnencrypted(authData);
      
      // Si nous voulons revenir à la version chiffrée plus tard, décommenter ce code:
      /*
      // Établir une connexion sécurisée si nécessaire
      if (!CryptoService.secureConnectionEstablished) {
        await CryptoService.initSecureConnection();
      }

      // Envoyer les données d'authentification à l'API Gateway
      const response = await CryptoService.sendEncryptedData('/gateway/auth/certificate/', authData);
      
      return response;
      */
    } catch (error) {
      console.error('Erreur lors de l\'authentification par certificat:', error);
      throw error;
    }
  }
  
  /**
   * Authentifie un utilisateur avec son certificat PFX (version non chiffrée pour déboguer)
   * @param {Object} authData - Données d'authentification
   * @param {string} authData.certificate - Contenu du certificat PFX en Base64
   * @param {string} authData.password - Mot de passe du certificat
   * @param {string} authData.role - Rôle demandé (user, admin, superadmin)
   * @param {string} authData.filename - Nom du fichier de certificat
   * @returns {Promise<Object>} - Statut de l'authentification et infos du certificat
   */
  async authenticateWithCertificateUnencrypted(authData) {
    try {
      console.log('Utilisation de l\'endpoint non chiffré pour l\'authentification par certificat');
      
      // Envoyer les données d'authentification directement à l'API Gateway sans chiffrement - Via Nginx
      const response = await axios.post(
        'https://ppd.camgovca.cm/gateway/unencrypted/auth/certificate/',
        authData,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 30000 // Timeout de 30 secondes
        }
      );
      
      console.log('Réponse de l\'authentification non chiffrée:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'authentification non chiffrée par certificat:', error);
      throw error;
    }
  }

  /**
   * Vérifie la signature d'un document
   * @param {File} signedPdfFile - Fichier PDF signé à vérifier
   * @returns {Promise<Object>} - Résultat de la vérification
   */
  async verifySignature(signedPdfFile) {
    try {
      // Préparation des données pour la vérification
      const formData = new FormData();
      formData.append('document', signedPdfFile);
      
      // Endpoint pour l'API Gateway
      const endpoint = '/gateway/verify/';
      
      // Utiliser fetch directement pour gérer les téléchargements de fichiers
      const response = await fetch(this.baseUrl + endpoint, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la vérification de la signature');
      }
      
      // Retourner le résultat de la vérification
      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la vérification de la signature:', error);
      throw error;
    }
  }

  /**
   * Récupère le fichier PFX à partir des données stockées
   * @param {Object} certificateData - Données du certificat
   * @returns {File|null} - Fichier PFX ou null si non disponible
   */
  getPfxFile(certificateData) {
    // Si un certificat est stocké en base64, le convertir en Blob puis en File
    if (certificateData.pfx_base64) {
      const binary = atob(certificateData.pfx_base64);
      const array = [];
      for (let i = 0; i < binary.length; i++) {
        array.push(binary.charCodeAt(i));
      }
      const blob = new Blob([new Uint8Array(array)], {type: 'application/x-pkcs12'});
      return new File([blob], certificateData.filename || 'certificate.pfx', {type: 'application/x-pkcs12'});
    }
    
    // Si aucun certificat n'est disponible
    return null;
  }

  /**
   * Récupère les statistiques du système (pour les administrateurs)
   * @returns {Promise<Object>} - Statistiques du système
   */
  async getSystemStats() {
    try {
      // Vérifier si l'utilisateur est administrateur
      const isAdmin = localStorage.getItem('isAdmin') === 'true';
      if (!isAdmin) {
        throw new Error('Accès non autorisé');
      }

      // Appeler le backend pour obtenir les statistiques
      const response = await CryptoService.sendEncryptedData('/gateway/admin/stats/', {});
      
      return response;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques:', error);
      throw error;
    }
  }

  /**
   * Déconnecte l'utilisateur actuel
   */
  logout() {
    localStorage.removeItem('certificateInfo');
    localStorage.removeItem('isAdmin');
    // Autres nettoyages si nécessaire
  }

  /**
   * Vérifie si un certificat est valide pour l'authentification d'un administrateur d'organisation
   * @param {Object} certData - Données du certificat
   * @param {string} certData.certificate - Contenu du certificat PFX en Base64
   * @param {string} certData.password - Mot de passe du certificat
   * @param {string} certData.role - Rôle demandé (admin)
   * @returns {Promise<Object>} - Résultat de la vérification et informations de l'organisation si existe
   */
  async verifyAdminCertificate(certData) {
    try {
      console.log('Vérification du certificat administrateur...');
      
      // Appel à l'API de vérification - Via Nginx
      const response = await axios.post(
        'https://ppd.camgovca.cm/api/users/auth-org-admin/verify/',
        certData,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 10000 // Timeout de 10 secondes
        }
      );
      
      console.log('Réponse de la vérification du certificat admin:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la vérification du certificat administrateur:', error);
      // Gérer les erreurs et extraire les messages pertinents de l'API
      if (error.response && error.response.data) {
        return {
          valid: false,
          errorTitle: error.response.data.detail || 'Erreur de vérification',
          errorMessage: error.response.data.message || 'Une erreur est survenue lors de la vérification du certificat.'
        };
      }
      // Erreur générique
      return {
        valid: false,
        errorTitle: 'Erreur de connexion',
        errorMessage: 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.'
      };
    }
  }

  /**
   * Authentifie ou crée un administrateur d'organisation avec les informations d'organisation fournies
   * @param {Object} authData - Données d'authentification
   * @param {string} authData.certificate - Contenu du certificat PFX en Base64
   * @param {string} authData.password - Mot de passe du certificat
   * @param {Object} authData.organization - Informations de l'organisation
   * @param {string} authData.organization.name - Nom de l'organisation
   * @param {string} authData.organization.registration_number - Numéro d'immatriculation
   * @param {string} authData.organization.address - Adresse (optionnelle)
   * @param {string} authData.filename - Nom du fichier de certificat
   * @returns {Promise<Object>} - Statut de l'authentification et infos du certificat + organisation
   */
  async authenticateOrgAdmin(authData) {
    try {
      console.log('Authentification administrateur d\'organisation...');
      
      // Appel à l'API d'authentification des admins d'organisation - Via Nginx
      const response = await axios.post(
        'https://ppd.camgovca.cm/api/users/auth-org-admin/authenticate/',
        authData,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 15000 // Timeout de 15 secondes
        }
      );
      
      console.log('Réponse de l\'authentification admin organisation:', response.data);
      
      // Si authentification réussie, stocker les informations dans le localStorage
      if (response.data.status === 'active') {
        // Stocker les informations du certificat et de l'utilisateur
        localStorage.setItem('certificateInfo', JSON.stringify({
          user_id: response.data.user_id,
          username: response.data.username,
          role: response.data.role,
          certificate_info: response.data.certificate_info
        }));
        
        // Marquer comme administrateur
        localStorage.setItem('isAdmin', 'true');
        
        // Stocker les informations de l'organisation
        localStorage.setItem('organizationInfo', JSON.stringify(response.data.organization));
      }
      
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'authentification administrateur d\'organisation:', error);
      // Gérer les erreurs et extraire les messages pertinents de l'API
      if (error.response && error.response.data) {
        return {
          status: 'error',
          message: error.response.data.detail || error.response.data.message || 'Une erreur est survenue lors de l\'authentification.'
        };
      }
      // Erreur générique
      return {
        status: 'error',
        message: 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.'
      };
    }
  }
  
  /**
   * Récupère la liste des organisations disponibles
   * @returns {Promise<Array>} - Liste des organisations actives
   */
  async getOrganizations() {
    try {
      console.log('Récupération de la liste des organisations');
      
      // Appel à l'API pour récupérer la liste des organisations
      const response = await axios.get(
        `${this.baseUrl}/api/users/organizations/`,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 10000 // Timeout de 10 secondes
        }
      );
      
      console.log('Réponse de la récupération des organisations:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des organisations:', error);
      // En cas d'erreur, retourner un tableau vide
      return [];
    }
  }
  
  /**
   * Authentifie un utilisateur avec son certificat et l'associe à une organisation
   * @param {Object} authData - Données d'authentification incluant le certificat et l'organisation sélectionnée
   * @returns {Promise<Object>} - Résultat de l'authentification
   */
  async authenticateWithOrganization(authData) {
    try {
      console.log('Authentification avec organisation:', authData.organization_id);
      
      // Appel à l'API d'authentification avec organisation
      const response = await axios.post(
        `${this.baseUrl}/api/users/auth/with-organization/`,
        authData,
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 15000 // Timeout de 15 secondes
        }
      );
      
      console.log('Réponse de l\'authentification avec organisation:', response.data);
      
      // Si l'authentification est réussie, stocker les informations pertinentes
      if (response.data.status === 'active') {
        localStorage.setItem('certificateInfo', JSON.stringify({
          user_id: response.data.user_id,
          username: response.data.username,
          role: response.data.role,
          certificate_info: response.data.certificate_info
        }));
        
        // Stocker le rôle spécifique
        if (response.data.role === 'admin') {
          localStorage.setItem('isAdmin', 'true');
        } else if (response.data.role === 'collaborator') {
          localStorage.setItem('isCollaborator', 'true');
        } else if (response.data.role === 'signer') {
          localStorage.setItem('isSigner', 'true');
        }
        
        // Stocker les informations de l'organisation si disponible
        if (response.data.organization) {
          localStorage.setItem('organizationInfo', JSON.stringify(response.data.organization));
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'authentification avec organisation:', error);
      // Gérer les erreurs et extraire les messages pertinents
      if (error.response && error.response.data) {
        return {
          status: 'error',
          message: error.response.data.detail || error.response.data.message || 'Une erreur est survenue lors de l\'authentification.'
        };
      }
      // Erreur générique
      return {
        status: 'error',
        message: 'Impossible de communiquer avec le serveur. Vérifiez votre connexion.'
      };
    }
  }
}

// Exporter une instance unique du service (pattern Singleton)


export default new UserService(); 