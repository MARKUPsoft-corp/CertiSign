import DocumentService from './DocumentService';
import axios from 'axios';

class AnalyticsService {
  
  /**
   * Récupère les statistiques globales pour la homepage
   * @returns {Promise<Object>} - Statistiques avec le nombre d'utilisateurs actifs, documents signés, etc.
   */
  async getHomepageStats() {
    try {
      // Essayer d'abord l'URL de production
      let response;
      try {
        response = await axios.get('https://ppd.camgovca.cm/api/users/homepage-stats/', {
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
      } catch (prodError) {
        console.log('Erreur avec l\'URL de production, essai avec localhost...');
        // En cas d'échec, essayer localhost (HTTP pour les connexions internes)
        response = await axios.get('http://127.0.0.1:8000/api/users/homepage-stats/', {
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
      }
      
      console.log('Statistiques récupérées avec succès:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques homepage:', error);
      console.error('Détails de l\'erreur:', error.response?.data || error.message);
      // Retourner des valeurs par défaut en cas d'erreur
      return {
        signed_documents: 0,
        active_users: 0,
        availability: "99.9%",
        legal_compliance: "100%"
      };
    }
  }
  
  /**
   * Récupère et analyse les données d'activité pour les graphiques
   */
  async getActivityAnalytics() {
    try {
      // Récupérer toutes les activités
      const activitiesResponse = await DocumentService.getMyActivities();
      const activities = activitiesResponse.data || [];
      
      // Analyser les activités par mois pour les 12 derniers mois
      const monthlyData = this.processMonthlyActivities(activities);
      
      return {
        monthlySignatures: monthlyData.signatures,
        monthlyVerifications: monthlyData.verifications,
        labels: monthlyData.labels
      };
    } catch (error) {
      console.error('Erreur lors de la récupération des analytics d\'activité:', error);
      return {
        monthlySignatures: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        monthlyVerifications: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
      };
    }
  }
  
  /**
   * Récupère et analyse les types de documents
   */
  async getDocumentTypeAnalytics() {
    try {
      // Récupérer tous les documents
      const documentsResponse = await DocumentService.getDocuments();
      const documents = documentsResponse.data || [];
      
      // Analyser les types de documents
      const typeStats = this.processDocumentTypes(documents);
      
      return typeStats;
    } catch (error) {
      console.error('Erreur lors de la récupération des analytics de documents:', error);
      return {
        labels: ['PDF'],
        data: [100],
        colors: ['#3a86ff']
      };
    }
  }
  
  /**
   * Traite les activités par mois
   */
  processMonthlyActivities(activities) {
    const now = new Date();
    const months = [];
    const signatures = new Array(12).fill(0);
    const verifications = new Array(12).fill(0);
    
    // Générer les labels des 12 derniers mois
    const monthNames = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
    for (let i = 11; i >= 0; i--) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      months.push({
        month: date.getMonth(),
        year: date.getFullYear(),
        label: monthNames[date.getMonth()]
      });
    }
    
    // Compter les activités par mois
    activities.forEach(activity => {
      const activityDate = new Date(activity.timestamp || activity.created_at);
      const activityMonth = activityDate.getMonth();
      const activityYear = activityDate.getFullYear();
      
      // Trouver l'index du mois correspondant
      const monthIndex = months.findIndex(m => m.month === activityMonth && m.year === activityYear);
      
      if (monthIndex !== -1) {
        // Classer les types d'activités
        if (this.isSignatureActivity(activity.activity_type)) {
          signatures[monthIndex]++;
        } else if (this.isVerificationActivity(activity.activity_type)) {
          verifications[monthIndex]++;
        }
      }
    });
    
    return {
      signatures,
      verifications,
      labels: months.map(m => m.label)
    };
  }
  
  /**
   * Traite les types de documents
   */
  processDocumentTypes(documents) {
    const typeCount = {};
    
    documents.forEach(doc => {
      // Extraire l'extension du fichier
      const fileName = doc.original_file_name || doc.file_name || 'unknown';
      const extension = this.getFileExtension(fileName);
      const category = this.categorizeFileType(extension);
      
      typeCount[category] = (typeCount[category] || 0) + 1;
    });
    
    // Convertir en format pour Chart.js
    const labels = Object.keys(typeCount);
    const data = Object.values(typeCount);
    const colors = this.generateColors(labels.length);
    
    return { labels, data, colors };
  }
  
  /**
   * Détermine si une activité est liée à la signature
   */
  isSignatureActivity(activityType) {
    const signatureTypes = [
      'signed',
      'signature_simple',
      'signature_multiple', 
      'signature_with_template',
      'template_used'
    ];
    return signatureTypes.includes(activityType);
  }
  
  /**
   * Détermine si une activité est liée à la vérification
   */
  isVerificationActivity(activityType) {
    const verificationTypes = [
      'viewed',
      'original_viewed',
      'downloaded',
      'signed_downloaded',
      'original_downloaded'
    ];
    return verificationTypes.includes(activityType);
  }
  
  /**
   * Extrait l'extension d'un nom de fichier
   */
  getFileExtension(fileName) {
    const parts = fileName.split('.');
    return parts.length > 1 ? parts.pop().toLowerCase() : 'unknown';
  }
  
  /**
   * Catégorise un type de fichier
   */
  categorizeFileType(extension) {
    const categories = {
      'pdf': 'PDF',
      'doc': 'Word',
      'docx': 'Word',
      'xls': 'Excel',
      'xlsx': 'Excel',
      'ppt': 'PowerPoint',
      'pptx': 'PowerPoint',
      'jpg': 'Images',
      'jpeg': 'Images',
      'png': 'Images',
      'gif': 'Images',
      'svg': 'Images',
      'txt': 'Texte',
      'rtf': 'Texte'
    };
    
    return categories[extension] || 'Autres';
  }
  
  /**
   * Génère des couleurs pour les graphiques
   */
  generateColors(count) {
    const baseColors = [
      '#3a86ff', // Bleu
      '#4cb58e', // Vert
      '#ff6b6b', // Rouge
      '#ffd166', // Jaune
      '#9d8df1', // Violet
      '#ff8fab', // Rose
      '#06d6a0', // Vert turquoise
      '#f72585', // Rouge magenta
      '#4361ee', // Bleu indigo
      '#f77f00'  // Orange
    ];
    
    const colors = [];
    for (let i = 0; i < count; i++) {
      colors.push(baseColors[i % baseColors.length]);
    }
    
    return colors;
  }
  
  /**
   * Récupère les statistiques générales
   */
  async getGeneralStats() {
    try {
      const [documentsResponse, activitiesResponse] = await Promise.all([
        DocumentService.getDocuments(),
        DocumentService.getMyActivities()
      ]);
      
      const documents = documentsResponse.data || [];
      const activities = activitiesResponse.data || [];
      
      // Calculer les statistiques
      const stats = {
        totalDocuments: documents.length,
        signedDocuments: documents.filter(doc => doc.status === 'signed' || doc.is_signed).length,
        pendingDocuments: documents.filter(doc => doc.status === 'pending_signature' || !doc.is_signed).length,
        totalVerifications: activities.filter(act => this.isVerificationActivity(act.activity_type)).length,
        totalDownloads: activities.filter(act => ['downloaded', 'signed_downloaded', 'original_downloaded'].includes(act.activity_type)).length
      };
      
      return stats;
    } catch (error) {
      console.error('Erreur lors de la récupération des statistiques générales:', error);
      return {
        totalDocuments: 0,
        signedDocuments: 0, 
        pendingDocuments: 0,
        totalVerifications: 0,
        totalDownloads: 0
      };
    }
  }
}

//const analyticsService = new AnalyticsService();
export default AnalyticsService; 