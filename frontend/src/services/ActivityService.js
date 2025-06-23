import DocumentService from './DocumentService';

/**
 * Service pour l'enregistrement automatique des activités utilisateur
 * Centralise toutes les actions de journalisation
 */
class ActivityService {
  
  /**
   * Enregistre une activité générique sur un document
   */
  async recordDocumentActivity(documentId, activityType, description = '', metadata = {}) {
    try {
      const result = await DocumentService.recordActivity(documentId, activityType, description, metadata);
      console.log(`✅ Activité enregistrée: ${activityType} pour document ${documentId}`);
      return result;
    } catch (error) {
      console.error(`❌ Erreur enregistrement activité ${activityType}:`, error);
      return null;
    }
  }

  /**
   * Enregistre la création d'un template
   */
  async recordTemplateCreation(templateId, templateName, metadata = {}) {
    const description = `Création du template: ${templateName}`;
    const enrichedMetadata = {
      templateId,
      templateName,
      action: 'template_creation',
      ...metadata
    };

    // Pour les templates, on peut créer une activité générale
    return this.recordGeneralActivity('template_created', description, enrichedMetadata);
  }

  /**
   * Enregistre l'utilisation d'un template
   */
  async recordTemplateUsage(templateId, templateName, documentIds = [], metadata = {}) {
    const description = `Utilisation du template: ${templateName} pour ${documentIds.length} document(s)`;
    const enrichedMetadata = {
      templateId,
      templateName,
      documentIds,
      action: 'template_usage',
      ...metadata
    };

    // Enregistrer pour chaque document créé avec le template
    const promises = documentIds.map(docId => 
      this.recordDocumentActivity(docId, 'template_used', description, enrichedMetadata)
    );

    await Promise.all(promises);
    return this.recordGeneralActivity('template_used', description, enrichedMetadata);
  }

  /**
   * Enregistre une signature simple
   */
  async recordSimpleSignature(documentIds, signatureType = 'simple', metadata = {}) {
    const description = `Signature ${signatureType} de ${documentIds.length} document(s)`;
    const enrichedMetadata = {
      signatureType,
      documentCount: documentIds.length,
      action: 'signature',
      ...metadata
    };

    // Enregistrer pour chaque document signé
    const promises = documentIds.map(docId => 
      this.recordDocumentActivity(docId, 'signature_simple', description, enrichedMetadata)
    );

    return Promise.all(promises);
  }

  /**
   * Enregistre une signature multiple
   */
  async recordMultipleSignature(documentIds, metadata = {}) {
    const description = `Signature multiple de ${documentIds.length} documents`;
    const enrichedMetadata = {
      signatureType: 'multiple',
      documentCount: documentIds.length,
      action: 'signature',
      ...metadata
    };

    // Enregistrer pour chaque document signé
    const promises = documentIds.map(docId => 
      this.recordDocumentActivity(docId, 'signature_multiple', description, enrichedMetadata)
    );

    return Promise.all(promises);
  }

  /**
   * Enregistre une signature avec template
   */
  async recordTemplateSignature(documentIds, templateId, templateName, metadata = {}) {
    const description = `Signature avec template "${templateName}" de ${documentIds.length} document(s)`;
    const enrichedMetadata = {
      templateId,
      templateName,
      signatureType: 'with_template',
      documentCount: documentIds.length,
      action: 'signature',
      ...metadata
    };

    // Enregistrer pour chaque document signé
    const promises = documentIds.map(docId => 
      this.recordDocumentActivity(docId, 'signature_with_template', description, enrichedMetadata)
    );

    return Promise.all(promises);
  }

  /**
   * Enregistre la consultation d'un document original
   */
  async recordOriginalView(documentId, documentTitle, metadata = {}) {
    const description = `Consultation du document original: ${documentTitle}`;
    const enrichedMetadata = {
      documentTitle,
      action: 'view_original',
      ...metadata
    };

    return this.recordDocumentActivity(documentId, 'original_viewed', description, enrichedMetadata);
  }

  /**
   * Enregistre le téléchargement d'un document signé
   */
  async recordSignedDownload(documentId, documentTitle, metadata = {}) {
    const description = `Téléchargement du document signé: ${documentTitle}`;
    const enrichedMetadata = {
      documentTitle,
      action: 'download_signed',
      ...metadata
    };

    return this.recordDocumentActivity(documentId, 'signed_downloaded', description, enrichedMetadata);
  }

  /**
   * Enregistre le téléchargement d'un document original
   */
  async recordOriginalDownload(documentId, documentTitle, metadata = {}) {
    const description = `Téléchargement du document original: ${documentTitle}`;
    const enrichedMetadata = {
      documentTitle,
      action: 'download_original',
      ...metadata
    };

    return this.recordDocumentActivity(documentId, 'original_downloaded', description, enrichedMetadata);
  }

  /**
   * Enregistre la consultation d'un document (vue générale)
   */
  async recordDocumentView(documentId, documentTitle, metadata = {}) {
    const description = `Consultation du document: ${documentTitle}`;
    const enrichedMetadata = {
      documentTitle,
      action: 'view_document',
      ...metadata
    };

    return this.recordDocumentActivity(documentId, 'viewed', description, enrichedMetadata);
  }

  /**
   * Enregistre une activité générale (sans document spécifique)
   * Utilisé pour les templates et autres actions globales
   */
  async recordGeneralActivity(activityType, description, metadata = {}) {
    try {
      // Pour les activités générales, on peut utiliser l'API directement
      // ou créer un endpoint spécial si nécessaire
      console.log(`📝 Activité générale: ${activityType} - ${description}`, metadata);
      return { success: true, type: activityType, description, metadata };
    } catch (error) {
      console.error(`❌ Erreur activité générale ${activityType}:`, error);
      return null;
    }
  }

  /**
   * Méthode utilitaire pour créer des métadonnées enrichies
   */
  createMetadata(baseMetadata = {}) {
    return {
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      ...baseMetadata
    };
  }
}

const activityService = new ActivityService();
export default activityService; 