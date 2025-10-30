<template>
  <div class="signer-dashboard">
    <!-- Fond animé avec particules -->
    <div class="particles-container">
      <div v-for="i in 10" :key="i" class="particle" 
        :style="{
          top: particlePositions[(i-1) % particlePositions.length].top,
          left: particlePositions[(i-1) % particlePositions.length].left,
          width: particlePositions[(i-1) % particlePositions.length].size + 'px',
          height: particlePositions[(i-1) % particlePositions.length].size + 'px',
          animationDuration: particlePositions[(i-1) % particlePositions.length].duration + 's',
          animationDelay: particlePositions[(i-1) % particlePositions.length].delay + 's'
        }">
      </div>
    </div>

    <!-- En-tête -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="logo-container">
          <div class="logo-icon-text">
            <img src="@/assets/doc.png" alt="Logo" class="header-logo-img">
            <h1 class="logo-text">
              <span class="text-green">Doc</span>
              <span class="text-red">@uth</span>
              <span class="text-yellow">ANTIC</span>
            </h1>
          </div>
          <span class="role-badge signer top-right-of-logo">Signataire</span>
        </div>
        
        <div class="user-info">
          <div class="organization-info">
            <div class="org-name-wrapper">
              <span class="org-name">{{ organizationName }}</span>
              <span v-if="organizationStatus" 
                    class="status-badge org-status top-right-of-org-name" 
                    :class="`org-status-${organizationStatus.toLowerCase()}`">
                {{ organizationStatus }}
              </span>
            </div>
          </div>
          <div class="user-profile">
            <span class="user-name">{{ userName }}</span>
            <button class="logout-btn" @click="logout">
              <i class="bi bi-box-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- Modal de choix de signature (inspiré de CollaboratorDashboard) -->
      <div v-if="showPrepareChoice" class="modal-overlay" @click.self="closePrepareChoice">
        <div class="choice-modal">
          <div class="modal-header">
            <div class="header-left">
              <div class="modal-icon">
                <i class="bi bi-pen"></i>
              </div>
              <h3 class="modal-title">Préparer et signer un document</h3>
            </div>
            <button class="modal-close" @click="closePrepareChoice">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          
          <div class="modal-body">
            <p class="choice-description">Comment souhaitez-vous signer votre document ?</p>
            
            <div class="choice-options">
              <button class="choice-option" @click="selectTemplatePreparation">
                <div class="option-icon template">
                  <i class="bi bi-file-earmark-richtext"></i>
                </div>
                <div class="option-content">
                  <h4 class="option-title">Signature avec template</h4>
                  <p class="option-description">Utilisez un template prédéfini pour signer rapidement</p>
                </div>
                <div class="option-arrow">
                  <i class="bi bi-chevron-right"></i>
                </div>
              </button>
              
              <button class="choice-option" @click="selectDirectPreparation" :disabled="isProcessingChoice">
                <div class="option-icon direct">
                  <i class="bi bi-lightning-charge"></i>
                </div>
                <div class="option-content">
                  <h4 class="option-title">Signature rapide</h4>
                  <p class="option-description">Signez un document rapidement en quelques étapes</p>
                </div>
                <div class="option-arrow">
                  <i class="bi bi-chevron-right"></i>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal de modification de template -->
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="edit-modal">
          <div class="modal-header">
            <div class="modal-title-section">
              <div class="modal-icon">
                <i class="bi bi-pencil"></i>
              </div>
              <h3 class="modal-title">Modifier le template : {{ editingTemplate?.name }}</h3>
            </div>
            <button class="modal-close" @click="closeEditModal">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="template-form">
              <div class="form-group">
                <label for="edit-template-name">Nom du template</label>
                <input 
                  type="text" 
                  id="edit-template-name" 
                  v-model="editingTemplate.name" 
                  placeholder="Saisissez un nom pour ce template" 
                  class="form-control"
                >
              </div>
            </div>
            
            <!-- Afficher QR Positioner pour modification -->
            <div v-if="editingTemplate.file" class="qr-positioner-wrapper">
              <QrPositioner 
                :pdfFile="editingTemplate.file"
                :preloadedPositions="editingTemplate.qrPositions"
                @position-confirmed="handleEditPositionConfirmed"
                @signature-uploaded="handleEditSignatureUploaded"
                @pdf-generated="handleEditPdfGenerated"
              />
            </div>
            <div v-else-if="loadingEditFile" class="loading-edit-file">
              <div class="spinner"></div>
              <p>Chargement du fichier PDF original...</p>
            </div>
            <div v-else class="edit-file-error">
              <i class="bi bi-exclamation-triangle-fill"></i>
              <p>Impossible de charger le fichier PDF original pour modification.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeEditModal" :disabled="isUpdating">Annuler</button>
            <button class="btn btn-primary" @click="updateTemplate" :disabled="!canUpdateTemplate || isUpdating">
              <span v-if="isUpdating"><i class="bi bi-hourglass-split spin"></i> Mise à jour...</span>
              <span v-else>Mettre à jour</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Section de bienvenue -->
      <section class="welcome-section">
        <div class="welcome-content">
          <h2 class="welcome-title">
            <span class="underlined-text">Espace de <span class="highlight-text">signature</span></span>
          </h2>
          <p class="welcome-description">
            Signez vos documents assignés de manière sécurisée
          </p>
        </div>
      </section>

      <!-- Statistiques -->
      <section class="stats-section" v-if="activeSection !== 'sign-simple' && activeSection !== 'create-template' && activeSection !== 'sign-with-template' && activeSection !== 'edit-template'">
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.thisWeek }}</div>
              <div class="stat-label">Signés cette semaine</div>
            </div>
            <div class="stat-icon success">
              <i class="bi bi-calendar-week"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ totalSignedCount }}</div>
              <div class="stat-label">Total signé</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-file-earmark-check"></i>
            </div>
          </div>
          <button class="stat-card action-stat" @click="openPrepareDocument">
            <div class="stat-content">
              <div class="stat-value"><i class="bi bi-plus-circle"></i></div>
              <div class="stat-label">Préparez et signez vous-même</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-file-earmark-plus"></i>
            </div>
          </button>
        </div>
      </section>

      <!-- Actions rapides -->
      <section class="quick-actions" v-if="activeSection !== 'sign-simple' && activeSection !== 'create-template' && activeSection !== 'sign-with-template' && activeSection !== 'edit-template'">
        <div class="actions-grid">
          <div class="action-card urgent" v-if="urgentDocuments.length > 0" @click="activeSection = 'urgent'" :class="{ 'active': activeSection === 'urgent' }">
            <div class="action-icon">
              <i class="bi bi-exclamation-triangle-fill"></i>
            </div>
            <span class="action-title">Urgent</span>
            <span class="action-description">{{ urgentDocuments.length }} documents urgents</span>
            <div class="notification-badge">{{ urgentDocuments.length }}</div>
          </div>
          <button class="action-card" @click="activeSection = 'pending'" :class="{ 'active': activeSection === 'pending' }">
            <div class="action-icon warning">
              <i class="bi bi-file-earmark-plus"></i>
            </div>
            <span class="action-title">À signer</span>
            <span class="action-description">{{ pendingDocuments.length }} documents en attente</span>
          </button>
          <button class="action-card" @click="activeSection = 'my-templates'" :class="{ 'active': activeSection === 'my-templates' }">
            <div class="action-icon accent">
              <i class="bi bi-file-earmark-richtext"></i>
            </div>
            <span class="action-title">Mes Templates</span>
            <span class="action-description">{{ myTemplates.length }} modèles créés</span>
          </button>

          <button class="action-card" @click="activeSection = 'signed'" :class="{ 'active': activeSection === 'signed' }">
            <div class="action-icon success">
              <i class="bi bi-file-earmark-check"></i>
            </div>
            <span class="action-title">Signés</span>
            <span class="action-description">{{ signedDocuments.length }} documents signés</span>
          </button>
        </div>
      </section>

      <!-- Contenu dynamique selon la section active -->
      <section class="content-section" v-if="activeSection">
        <!-- Documents à signer -->
        <div v-if="activeSection === 'pending'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-file-earmark-plus"></i>
            Documents à signer
          </h3>
          
          <div class="documents-list">
            <!-- Onglets -->
            <div class="pending-tabs">
              <button class="tab-btn" :class="{ active: pendingTab === 'quick' }" @click="pendingTab = 'quick'">
                Préparation directe
              </button>
              <button class="tab-btn" :class="{ active: pendingTab === 'template' }" @click="pendingTab = 'template'">
                Avec template
              </button>
            </div>

            <!-- Contenu selon onglet -->
            <template v-if="pendingTab === 'quick'">
              <!-- Barre de recherche pour les documents quick -->
              <div class="search-container">
                <input 
                  type="text" 
                  v-model="searchQueryQuick" 
                  class="search-input" 
                  placeholder="Rechercher un document..."
                  @input="filterQuickDocuments"
                >
                <i class="bi bi-search search-icon"></i>
              </div>

              <div v-for="doc in paginatedQuickDocuments" :key="doc.id" class="document-item" :class="{ 'urgent': doc.is_urgent }">
                <div class="doc-info">
                  <i class="bi" :class="doc.is_urgent ? 'bi-exclamation-triangle-fill' : 'bi-file-earmark'"></i>
                  <div class="doc-details">
                    <div class="doc-header">
                      <span class="doc-name">{{ doc.document_name || 'Document sans nom' }}</span>
                      <span v-if="doc.is_urgent" class="urgent-tag">URGENT</span>
                    </div>
                    <span class="doc-meta">
                      Préparé par {{ doc.preparedBy || doc.collaborator_username || 'Collaborateur' }} • 
                      {{ formatDate(doc.assignedAt || doc.created_at) }}
                    </span>
                    <div class="doc-priority">
                      <span class="time-elapsed" :class="{ 'urgent': doc.is_urgent }">
                        {{ getTimeElapsed(doc.assignedAt || doc.created_at) }} d'attente
                      </span>
                    </div>
                  </div>
                </div>
                <div class="doc-actions">
                  <button class="btn-primary" @click="signDocument(doc)">
                    <i class="bi bi-pen"></i>
                    Signer maintenant
                  </button>
                  <button class="btn-icon" title="Prévisualiser" @click="previewDocument(doc)">
                    <i class="bi bi-eye"></i>
                  </button>
                </div>
              </div>
              
              <!-- Pagination pour quick documents -->
              <div v-if="totalPagesQuick > 1" class="pagination-container">
                <div class="pagination-info">
                  <span>Page {{ currentPageQuick }} sur {{ totalPagesQuick }}</span>
                  <span class="documents-count">({{ filteredQuickDocuments.length }} documents au total)</span>
                </div>
                
                <div class="pagination-controls">
                  <!-- Bouton Précédent -->
                  <button 
                    class="pagination-btn prev" 
                    :disabled="currentPageQuick === 1"
                    @click="previousPageQuick"
                    title="Page précédente"
                  >
                    <i class="bi bi-chevron-left"></i>
                    Précédent
                  </button>
                  
                  <!-- Première page si pas visible -->
                  <button 
                    v-if="visiblePagesQuick[0] > 1"
                    class="pagination-btn page"
                    @click="goToPageQuick(1)"
                  >
                    1
                  </button>
                  
                  <!-- Points de suspension si nécessaire -->
                  <span v-if="visiblePagesQuick[0] > 2" class="pagination-dots">...</span>
                  
                  <!-- Pages visibles -->
                  <button 
                    v-for="page in visiblePagesQuick"
                    :key="page"
                    class="pagination-btn page"
                    :class="{ 'active': page === currentPageQuick }"
                    @click="goToPageQuick(page)"
                  >
                    {{ page }}
                  </button>
                  
                  <!-- Points de suspension si nécessaire -->
                  <span v-if="visiblePagesQuick[visiblePagesQuick.length - 1] < totalPagesQuick - 1" class="pagination-dots">...</span>
                  
                  <!-- Dernière page si pas visible -->
                  <button 
                    v-if="visiblePagesQuick[visiblePagesQuick.length - 1] < totalPagesQuick"
                    class="pagination-btn page"
                    @click="goToPageQuick(totalPagesQuick)"
                  >
                    {{ totalPagesQuick }}
                  </button>
                  
                  <!-- Bouton Suivant -->
                  <button 
                    class="pagination-btn next" 
                    :disabled="currentPageQuick === totalPagesQuick"
                    @click="nextPageQuick"
                    title="Page suivante"
                  >
                    Suivant
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </div>
              </div>

              <div v-if="filteredQuickDocuments.length === 0" class="empty-state">
                <i class="bi bi-file-earmark-check"></i>
                <p v-if="searchQueryQuick">Aucun résultat trouvé pour "{{ searchQueryQuick }}"</p>
                <p v-else>Aucun document à signer</p>
              </div>
            </template>

            <template v-else>
              <!-- Cartes templates -->
              <div v-if="!selectedPendingTemplateId" class="template-cards-grid">
                <div v-for="tpl in pendingTemplateCards" :key="tpl.templateId" class="template-card-pending">
                  <h4 class="template-card-title">{{ tpl.templateName }}</h4>
                  <p class="template-card-count">{{ tpl.documents.length }} document(s)</p>
                  <div class="template-card-actions">
                    <button class="btn-icon" @click="previewTemplateById(tpl.templateId)" title="Aperçu template">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn-icon primary" @click="selectedPendingTemplateId = tpl.templateId" title="Voir documents">
                      <i class="bi bi-list"></i>
                    </button>
                  </div>
                </div>
                <div v-if="pendingTemplateCards.length === 0" class="empty-state">
                  <i class="bi bi-hourglass-split"></i>
                  <p>Aucun document via template</p>
                </div>
              </div>
              <!-- Liste documents d'un template -->
              <div v-else>
                <div class="template-docs-header">
                  <h4 class="template-docs-title">{{ currentTemplateName }}</h4>
                  <button class="btn-secondary" @click="selectedPendingTemplateId = null">Retour aux templates →</button>
                </div>
                
                <!-- Barre de recherche pour les documents template -->
                <div class="search-container">
                  <input 
                    type="text" 
                    v-model="searchQueryTemplate" 
                    class="search-input" 
                    placeholder="Rechercher un document..."
                    @input="filterTemplateDocuments"
                  >
                  <i class="bi bi-search search-icon"></i>
                </div>

                <div v-for="doc in paginatedTemplateDocuments" :key="doc.id" class="document-item" :class="{ 'urgent': doc.is_urgent }">
                  <div class="doc-info">
                    <i class="bi bi-file-earmark"></i>
                    <div class="doc-details">
                      <span class="doc-name">{{ doc.document_name || 'Document sans nom' }}</span>
                      <span class="doc-meta">Assigné le {{ formatDate(doc.assignedAt) }}</span>
                    </div>
                  </div>
                  <div class="doc-actions">
                    <button class="btn-primary" @click="signDocument(doc)">
                      <i class="bi bi-pen"></i>
                      Signer maintenant
                    </button>
                    <button class="btn-icon" @click="previewDocument(doc)" title="Prévisualiser">
                      <i class="bi bi-eye"></i>
                    </button>
                  </div>
                </div>
                
                <!-- Pagination pour template documents -->
                <div v-if="totalPagesTemplate > 1" class="pagination-container">
                  <div class="pagination-info">
                    <span>Page {{ currentPageTemplate }} sur {{ totalPagesTemplate }}</span>
                    <span class="documents-count">({{ filteredTemplateDocuments.length }} documents au total)</span>
                  </div>
                  
                  <div class="pagination-controls">
                    <!-- Bouton Précédent -->
                    <button 
                      class="pagination-btn prev" 
                      :disabled="currentPageTemplate === 1"
                      @click="previousPageTemplate"
                      title="Page précédente"
                    >
                      <i class="bi bi-chevron-left"></i>
                      Précédent
                    </button>
                    
                    <!-- Première page si pas visible -->
                    <button 
                      v-if="visiblePagesTemplate[0] > 1"
                      class="pagination-btn page"
                      @click="goToPageTemplate(1)"
                    >
                      1
                    </button>
                    
                    <!-- Points de suspension si nécessaire -->
                    <span v-if="visiblePagesTemplate[0] > 2" class="pagination-dots">...</span>
                    
                    <!-- Pages visibles -->
                    <button 
                      v-for="page in visiblePagesTemplate"
                      :key="page"
                      class="pagination-btn page"
                      :class="{ 'active': page === currentPageTemplate }"
                      @click="goToPageTemplate(page)"
                    >
                      {{ page }}
                    </button>
                    
                    <!-- Points de suspension si nécessaire -->
                    <span v-if="visiblePagesTemplate[visiblePagesTemplate.length - 1] < totalPagesTemplate - 1" class="pagination-dots">...</span>
                    
                    <!-- Dernière page si pas visible -->
                    <button 
                      v-if="visiblePagesTemplate[visiblePagesTemplate.length - 1] < totalPagesTemplate"
                      class="pagination-btn page"
                      @click="goToPageTemplate(totalPagesTemplate)"
                    >
                      {{ totalPagesTemplate }}
                    </button>
                    
                    <!-- Bouton Suivant -->
                    <button 
                      class="pagination-btn next" 
                      :disabled="currentPageTemplate === totalPagesTemplate"
                      @click="nextPageTemplate"
                      title="Page suivante"
                    >
                      Suivant
                      <i class="bi bi-chevron-right"></i>
                    </button>
                  </div>
                </div>

                <div v-if="filteredTemplateDocuments.length === 0" class="empty-state">
                  <i class="bi bi-hourglass-split"></i>
                  <p v-if="searchQueryTemplate">Aucun résultat trouvé pour "{{ searchQueryTemplate }}"</p>
                  <p v-else>Aucun document pour ce template</p>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- Documents signés -->
        <div v-if="activeSection === 'signed'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-file-earmark-check"></i>
            Documents récemment signés
          </h3>
          
          <div class="documents-list">
            <!-- Barre de recherche unique -->
            <div class="search-container">
              <input type="text" v-model="searchQuerySigned" class="search-input" placeholder="Rechercher un document...">
              <i class="bi bi-search search-icon"></i>
            </div>

            <div v-for="doc in paginatedSignedDocuments" :key="doc.id" class="document-item">
              <div class="doc-info">
                <i class="bi bi-file-earmark-check"></i>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.document_name || doc.name || 'Document sans nom' }}</span>
                  <span class="doc-meta">Signé le {{ formatDate(doc.signedAt || doc.updated_at) }}</span>
                  <div class="signer-info" v-if="doc.organization_name || doc.signer_role">
                    <i class="bi bi-building"></i>
                    <span>{{ doc.organization_name }}{{ doc.signer_role ? ` - ${doc.signer_role}` : '' }}</span>
                  </div>
                </div>
              </div>
              <div class="doc-status">
                <span class="status-badge signed">Signé</span>
                <div class="doc-actions">
                  <button class="btn-icon" title="Télécharger" @click="downloadSignedDocument(doc)"><i class="bi bi-download"></i></button>
                </div>
              </div>
            </div>

            <!-- Pagination globale -->
            <div v-if="totalPagesSigned > 1" class="pagination-container">
              <div class="pagination-info">
                <span>Page {{ currentPageSigned }} sur {{ totalPagesSigned }}</span>
                <span class="documents-count">({{ filteredSignedDocuments.length }} documents au total)</span>
              </div>
              <div class="pagination-controls">
                <button class="pagination-btn prev" :disabled="currentPageSigned === 1" @click="previousPageSigned"><i class="bi bi-chevron-left"></i> Précédent</button>
                <button v-if="visiblePagesSigned[0] > 1" class="pagination-btn page" @click="goToPageSigned(1)">1</button>
                <span v-if="visiblePagesSigned[0] > 2" class="pagination-dots">...</span>
                <button v-for="page in visiblePagesSigned" :key="page" class="pagination-btn page" :class="{ 'active': page === currentPageSigned }" @click="goToPageSigned(page)">{{ page }}</button>
                <span v-if="visiblePagesSigned[visiblePagesSigned.length - 1] < totalPagesSigned - 1" class="pagination-dots">...</span>
                <button v-if="visiblePagesSigned[visiblePagesSigned.length - 1] < totalPagesSigned" class="pagination-btn page" @click="goToPageSigned(totalPagesSigned)">{{ totalPagesSigned }}</button>
                <button class="pagination-btn next" :disabled="currentPageSigned === totalPagesSigned" @click="nextPageSigned">Suivant <i class="bi bi-chevron-right"></i></button>
              </div>
            </div>

            <div v-if="filteredSignedDocuments.length === 0" class="empty-state">
              <i class="bi bi-file-earmark"></i>
              <p v-if="searchQuerySigned">Aucun résultat trouvé pour "{{ searchQuerySigned }}"</p>
              <p v-else>Aucun document signé pour cette organisation</p>
            </div>
          </div>
        </div>

        <!-- Documents urgents -->
        <div v-if="activeSection === 'urgent'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-exclamation-triangle-fill"></i>
            Documents urgents
          </h3>
          
          <div class="documents-list">
            <!-- Onglets -->
            <div class="pending-tabs">
              <button class="tab-btn" :class="{ active: urgentTab === 'quick' }" @click="urgentTab = 'quick'">
                Préparation directe
              </button>
              <button class="tab-btn" :class="{ active: urgentTab === 'template' }" @click="urgentTab = 'template'">
                Avec template
              </button>
            </div>

            <!-- Contenu selon onglet -->
            <template v-if="urgentTab === 'quick'">
              <!-- Barre de recherche pour les documents quick -->
              <div class="search-container">
                <input 
                  type="text" 
                  v-model="searchQueryUrgentQuick" 
                  class="search-input" 
                  placeholder="Rechercher un document urgent..."
                  @input="filterUrgentQuickDocuments"
                >
                <i class="bi bi-search search-icon"></i>
              </div>

              <div v-for="doc in paginatedUrgentQuickDocuments" :key="doc.id" class="document-item urgent">
                <div class="doc-info">
                  <i class="bi bi-exclamation-triangle-fill"></i>
                  <div class="doc-details">
                    <div class="doc-header">
                      <span class="doc-name">{{ doc.document_name || 'Document sans nom' }}</span>
                      <span class="urgent-tag">URGENT</span>
                    </div>
                    <span class="doc-meta">
                      Préparé par {{ doc.preparedBy || doc.collaborator_username || 'Collaborateur' }} • 
                      {{ formatDate(doc.assignedAt || doc.created_at) }}
                    </span>
                    <div class="doc-priority">
                      <span class="time-elapsed urgent">
                        {{ getTimeElapsed(doc.assignedAt || doc.created_at) }} d'attente
                      </span>
                    </div>
                  </div>
                </div>
                <div class="doc-actions">
                  <button class="btn-primary" @click="signDocument(doc)">
                    <i class="bi bi-pen"></i>
                    Signer maintenant
                  </button>
                  <button class="btn-icon" title="Prévisualiser" @click="previewDocument(doc)">
                    <i class="bi bi-eye"></i>
                  </button>
                </div>
              </div>
              
              <!-- Pagination pour documents urgents quick -->
              <div v-if="totalPagesUrgentQuick > 1" class="pagination-container">
                <div class="pagination-info">
                  <span>Page {{ currentPageUrgentQuick }} sur {{ totalPagesUrgentQuick }}</span>
                  <span class="documents-count">({{ filteredUrgentQuickDocuments.length }} documents urgents au total)</span>
                </div>
                
                <div class="pagination-controls">
                  <button class="pagination-btn prev" :disabled="currentPageUrgentQuick === 1" @click="previousPageUrgentQuick">
                    <i class="bi bi-chevron-left"></i> Précédent
                  </button>
                  <button v-if="visiblePagesUrgentQuick[0] > 1" class="pagination-btn page" @click="goToPageUrgentQuick(1)">1</button>
                  <span v-if="visiblePagesUrgentQuick[0] > 2" class="pagination-dots">...</span>
                  <button v-for="page in visiblePagesUrgentQuick" :key="page" class="pagination-btn page" :class="{ 'active': page === currentPageUrgentQuick }" @click="goToPageUrgentQuick(page)">{{ page }}</button>
                  <span v-if="visiblePagesUrgentQuick[visiblePagesUrgentQuick.length - 1] < totalPagesUrgentQuick - 1" class="pagination-dots">...</span>
                  <button v-if="visiblePagesUrgentQuick[visiblePagesUrgentQuick.length - 1] < totalPagesUrgentQuick" class="pagination-btn page" @click="goToPageUrgentQuick(totalPagesUrgentQuick)">{{ totalPagesUrgentQuick }}</button>
                  <button class="pagination-btn next" :disabled="currentPageUrgentQuick === totalPagesUrgentQuick" @click="nextPageUrgentQuick">Suivant <i class="bi bi-chevron-right"></i></button>
                </div>
              </div>

              <div v-if="filteredUrgentQuickDocuments.length === 0" class="empty-state">
                <i class="bi bi-exclamation-triangle"></i>
                <p v-if="searchQueryUrgentQuick">Aucun résultat urgent trouvé pour "{{ searchQueryUrgentQuick }}"</p>
                <p v-else>Aucun document urgent à signer</p>
              </div>
            </template>

            <!-- Onglet Template pour urgents -->
            <template v-else>
              <div v-if="!selectedUrgentTemplateId" class="template-cards-grid">
                <div v-for="tpl in urgentTemplateCards" :key="tpl.templateId" class="template-card-pending">
                  <h4 class="template-card-title">{{ tpl.templateName }}</h4>
                  <p class="template-card-count">{{ tpl.documents.length }} document(s) urgent(s)</p>
                  <div class="template-card-actions">
                    <button class="btn-icon" @click="previewTemplateById(tpl.templateId)" title="Aperçu template">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn-icon primary" @click="selectedUrgentTemplateId = tpl.templateId" title="Voir documents">
                      <i class="bi bi-list"></i>
                    </button>
                  </div>
                </div>
                <div v-if="urgentTemplateCards.length === 0" class="empty-state">
                  <i class="bi bi-exclamation-triangle"></i>
                  <p>Aucun template urgent</p>
                </div>
              </div>

              <div v-else>
                <div class="template-docs-header">
                  <h4 class="template-docs-title">{{ currentUrgentTemplateName }}</h4>
                  <button class="btn-secondary" @click="selectedUrgentTemplateId = null">Retour aux templates →</button>
                </div>
                
                <div class="search-container">
                  <input type="text" v-model="searchQueryUrgentTemplate" class="search-input" placeholder="Rechercher un document urgent..." @input="filterUrgentTemplateDocuments">
                  <i class="bi bi-search search-icon"></i>
                </div>

                <div v-for="doc in paginatedUrgentTemplateDocuments" :key="doc.id" class="document-item urgent">
                  <div class="doc-info">
                    <i class="bi bi-exclamation-triangle-fill"></i>
                    <div class="doc-details">
                      <div class="doc-header">
                        <span class="doc-name">{{ doc.document_name || 'Document sans nom' }}</span>
                        <span class="urgent-tag">URGENT</span>
                      </div>
                      <span class="doc-meta">Template: {{ doc.templateName }} • {{ formatDate(doc.assignedAt || doc.created_at) }}</span>
                    </div>
                  </div>
                  <div class="doc-actions">
                    <button class="btn-primary" @click="signDocument(doc)">
                      <i class="bi bi-pen"></i>
                      Signer maintenant
                    </button>
                    <button class="btn-icon" title="Prévisualiser" @click="previewDocument(doc)">
                      <i class="bi bi-eye"></i>
                    </button>
                  </div>
                </div>

                <div v-if="totalPagesUrgentTemplate > 1" class="pagination-container">
                  <div class="pagination-info">
                    <span>Page {{ currentPageUrgentTemplate }} sur {{ totalPagesUrgentTemplate }}</span>
                    <span class="documents-count">({{ filteredUrgentTemplateDocuments.length }} documents urgents au total)</span>
                  </div>
                  <div class="pagination-controls">
                    <button class="pagination-btn prev" :disabled="currentPageUrgentTemplate === 1" @click="previousPageUrgentTemplate"><i class="bi bi-chevron-left"></i> Précédent</button>
                    <button v-if="visiblePagesUrgentTemplate[0] > 1" class="pagination-btn page" @click="goToPageUrgentTemplate(1)">1</button>
                    <span v-if="visiblePagesUrgentTemplate[0] > 2" class="pagination-dots">...</span>
                    <button v-for="page in visiblePagesUrgentTemplate" :key="page" class="pagination-btn page" :class="{ 'active': page === currentPageUrgentTemplate }" @click="goToPageUrgentTemplate(page)">{{ page }}</button>
                    <span v-if="visiblePagesUrgentTemplate[visiblePagesUrgentTemplate.length - 1] < totalPagesUrgentTemplate - 1" class="pagination-dots">...</span>
                    <button v-if="visiblePagesUrgentTemplate[visiblePagesUrgentTemplate.length - 1] < totalPagesUrgentTemplate" class="pagination-btn page" @click="goToPageUrgentTemplate(totalPagesUrgentTemplate)">{{ totalPagesUrgentTemplate }}</button>
                    <button class="pagination-btn next" :disabled="currentPageUrgentTemplate === totalPagesUrgentTemplate" @click="nextPageUrgentTemplate">Suivant <i class="bi bi-chevron-right"></i></button>
                  </div>
                </div>

                <div v-if="filteredUrgentTemplateDocuments.length === 0" class="empty-state">
                  <i class="bi bi-exclamation-triangle"></i>
                  <p v-if="searchQueryUrgentTemplate">Aucun résultat urgent trouvé pour "{{ searchQueryUrgentTemplate }}"</p>
                  <p v-else>Aucun document urgent pour ce template</p>
                </div>
              </div>
            </template>
          </div>
        </div>



        <!-- Gestion de mes templates -->
        <div v-if="activeSection === 'my-templates'" class="section-content">
          <div class="section-header">
            <h3 class="content-title">
              <i class="bi bi-file-earmark-richtext"></i>
              Mes Templates de Signature
            </h3>
            <button class="btn-primary" @click="activeSection = 'create-template'">
              <i class="bi bi-plus"></i>
              Nouveau Template
            </button>
          </div>
          
          <div v-if="loadingTemplates" class="loading-state">
            <div class="spinner"></div>
            <p>Chargement des templates...</p>
          </div>
          
          <div v-else-if="myTemplates.length === 0" class="empty-state">
            <i class="bi bi-file-earmark-richtext"></i>
            <p>Aucun template créé</p>
            <span class="empty-description">
              Créez votre premier template pour accélérer la préparation de vos documents
            </span>
          </div>
          
          <div v-else class="templates-grid">
            <div v-for="template in myTemplates" :key="template.id" class="template-card">
              <div class="template-header">
                <div class="template-icon">
                  <i class="bi bi-file-earmark-pdf"></i>
                </div>
                <div class="template-status">
                  <span class="template-badge">Template</span>
                </div>
              </div>
              <div class="template-content">
                <h4 class="template-title" :title="template.name">{{ template.name }}</h4>
                <div class="template-meta">
                  <div class="meta-item">
                    <i class="bi bi-calendar"></i>
                    <span>Créé le {{ formatDate(template.createdAt) }}</span>
                  </div>
                  <div class="meta-item">
                    <i class="bi bi-grid"></i>
                    <span>{{ template.pageApplication === 'all' ? 'Toutes les pages' : 'Pages spécifiques' }}</span>
                  </div>
                  <div class="meta-item">
                    <i class="bi bi-qr-code"></i>
                    <span>Taille QR: {{ getQrSizeLabel(template.qrSize) }}</span>
                  </div>
                </div>
              </div>
              <div class="template-actions">
                <button class="btn-icon" title="Aperçu" @click="previewTemplate(template)">
                  <i class="bi bi-eye"></i>
                </button>
                <button class="btn-icon primary" title="Modifier" @click="editTemplate(template)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn-icon success" title="Utiliser ce template" @click="useTemplate(template)">
                  <i class="bi bi-file-earmark-plus"></i>
                </button>
                <button class="btn-icon danger" title="Supprimer" @click="confirmDeleteTemplate(template)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>



        <!-- Création de template -->
        <div v-if="activeSection === 'create-template'" class="section-content create-template-section">
          <CreateTemplate @close="activeSection = ''" @template-created="onTemplateCreated"/>
        </div>

        <!-- Signature avec template -->
        <div v-if="activeSection === 'sign-with-template'" class="section-content sign-with-template-section">
          <SignWithTemplateMultiple @close="activeSection = ''" />
        </div>

        <!-- Signature directe par le signataire -->
        <div v-if="activeSection === 'sign-simple'" class="section-content sign-section">
          <SignSimpleSigner @close="activeSection = ''" :organization-name="organizationName" />
        </div>

        <!-- Édition de template -->
        <div v-if="activeSection === 'edit-template'" class="section-content edit-template-section">
          <div class="edit-template-header">
            <div class="header-left">
              <div class="modal-icon">
                <i class="bi bi-pencil"></i>
              </div>
              <h3 class="modal-title">Modifier le template : {{ editingTemplate?.name }}</h3>
            </div>
            <button class="modal-close" @click="closeEditModal">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>

          <div class="edit-template-body">
            <div class="template-form">
              <div class="form-group">
                <label for="edit-template-name">Nom du template</label>
                <input 
                  type="text" 
                  id="edit-template-name" 
                  v-model="editingTemplate.name" 
                  placeholder="Saisissez un nom pour ce template" 
                  class="form-control"
                >
              </div>
            </div>

            <div v-if="editingTemplate.file" class="qr-positioner-wrapper">
              <QrPositioner 
                :pdfFile="editingTemplate.file"
                :preloadedPositions="editingTemplate.qrPositions"
                @position-confirmed="handleEditPositionConfirmed"
                @signature-uploaded="handleEditSignatureUploaded"
                @pdf-generated="handleEditPdfGenerated"
              />
            </div>
            <div v-else-if="loadingEditFile" class="loading-edit-file">
              <div class="spinner"></div>
              <p>Chargement du fichier PDF original...</p>
            </div>
            <div v-else class="edit-file-error">
              <i class="bi bi-exclamation-triangle-fill"></i>
              <p>Impossible de charger le fichier PDF original pour modification.</p>
            </div>
          </div>

          <div class="edit-template-footer">
            <button class="btn btn-secondary" @click="closeEditModal" :disabled="isUpdating">Annuler</button>
            <button class="btn btn-primary" @click="updateTemplate" :disabled="!canUpdateTemplate || isUpdating">
              <span v-if="isUpdating"><i class="bi bi-hourglass-split spin"></i> Mise à jour...</span>
              <span v-else>Mettre à jour</span>
            </button>
          </div>
        </div>
      </section>

      <!-- Section par défaut si aucune section active -->
      <section v-if="!activeSection" class="default-content">
        <div class="welcome-card">
          <div class="welcome-icon">
            <i class="bi bi-pen-fill"></i>
          </div>
          <h3>Prêt à signer ?</h3>
          <p>Consultez vos documents en attente de signature</p>
          <button class="btn-primary" @click="activeSection = 'pending'">
            <i class="bi bi-file-earmark-plus"></i>
            Voir les documents
          </button>
        </div>
      </section>
    </main>

    <!-- Popup de signature -->
    <div class="signature-modal" v-if="showSignatureModal">
      <div class="signature-modal-overlay" @click="closeSignatureModal"></div>
      <div class="signature-modal-content">
        <div class="signature-modal-header">
          <h3>
            <i class="bi bi-pen-fill"></i>
            Signature de document
          </h3>
          <button class="close-btn" @click="closeSignatureModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <div class="signature-modal-body">
          <!-- 🆕 SECTION TYPE DE SIGNATURE -->
          <div class="signature-type-section">
            <div class="section-title">Type de signature</div>
            <div class="signature-type-options">
              <div class="signature-type-option" 
                   :class="{ selected: signatureType === 'permanent' }"
                   @click="signatureType = 'permanent'">
                <div class="type-icon permanent">
                  <i class="bi bi-shield-lock-fill"></i>
                </div>
                <div class="type-content">
                  <h4>Signature Pérenne</h4>
                  <p>Valide indéfiniment</p>
                </div>
                <div class="type-badge" v-if="signatureType === 'permanent'">
                  <i class="bi bi-check-circle-fill"></i>
                </div>
              </div>
              
              <div class="signature-type-option"
                   :class="{ selected: signatureType === 'ephemeral' }"
                   @click="signatureType = 'ephemeral'">
                <div class="type-icon ephemeral">
                  <i class="bi bi-clock-history"></i>
                </div>
                <div class="type-content">
                  <h4>Signature Éphémère</h4>
                  <p>Avec date d'expiration</p>
                </div>
                <div class="type-badge" v-if="signatureType === 'ephemeral'">
                  <i class="bi bi-check-circle-fill"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- 🆕 SECTION CONFIGURATION EXPIRATION (si éphémère) -->
          <div v-if="signatureType === 'ephemeral'" class="expiration-section">
            <div class="section-title">Période de validité</div>
            
            <!-- Durées pré-définies -->
            <div class="duration-presets">
              <div class="presets-grid">
                <button v-for="preset in durationPresets" 
                       :key="preset.value"
                       :class="['preset-btn', { active: selectedDuration === preset.value }]"
                       @click="selectDuration(preset.value)">
                  <div class="preset-icon">
                    <i :class="preset.icon"></i>
                  </div>
                  <div class="preset-label">{{ preset.label }}</div>
                  <div class="preset-desc">{{ preset.description }}</div>
                </button>
                
                <!-- Option personnalisée -->
                <button :class="['preset-btn', 'custom', { active: selectedDuration === 'custom' }]"
                       @click="selectDuration('custom')">
                  <div class="preset-icon">
                    <i class="bi bi-calendar-plus"></i>
                  </div>
                  <div class="preset-label">Personnalisé</div>
                  <div class="preset-desc">Choisir une date</div>
                </button>
              </div>
            </div>

            <!-- Sélecteur de date personnalisée -->
            <div v-if="selectedDuration === 'custom'" class="custom-date-selector">
              <label>Date et heure d'expiration</label>
              <input type="datetime-local" 
                     v-model="customExpirationDate"
                     :min="minExpirationDate"
                     class="date-input">
              <small>La signature expirera le {{ formatExpirationDisplay }}</small>
            </div>

            <!-- Résumé de l'expiration -->
            <div v-if="expirationDate" class="expiration-summary">
              <i class="bi bi-info-circle"></i>
              <span>La signature expirera <strong>{{ durationDescription }}</strong></span>
            </div>
          </div>

          <div class="document-preview">
            <div class="document-name">{{ currentDocument?.document_name || 'Document' }}</div>
            <div class="document-info">
              <i class="bi bi-file-earmark-pdf"></i>
              <span>{{ currentDocument?.document_name || 'Document sans nom' }}</span>
            </div>
          </div>
          
          <div class="form-section">
            <div class="form-title">Votre certificat de signature</div>
            <div class="form-group">
              <label for="certificate">Certificat PFX</label>
              <div 
                class="dropzone"
                :class="{ 'active': isDragging, 'has-file': certificateFile }"
                @dragenter.prevent="isDragging = true"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleDrop"
                @click="$refs.certificateInput.click()"
              >
                <input 
                  type="file" 
                  id="certificate" 
                  ref="certificateInput" 
                  @change="handleCertificateChange" 
                  accept=".pfx,.p12" 
                  class="hidden-input" 
                />
                
                <div v-if="!certificateFile" class="dropzone-placeholder">
                  <i class="bi bi-file-earmark-lock2"></i>
                  <div class="dropzone-text">
                    <span class="main-text">Glissez votre certificat ici</span>
                    <span class="sub-text">ou cliquez pour parcourir</span>
                  </div>
                </div>
                
                <div v-else class="dropzone-file">
                  <i class="bi bi-file-earmark-check"></i>
                  <div class="file-info">
                    <span class="file-name">{{ certificateFile.name }}</span>
                    <span class="file-size">{{ formatFileSize(certificateFile.size) }}</span>
                  </div>
                  <button class="remove-file" @click.stop="removeCertificate">
                    <i class="bi bi-x-circle"></i>
                  </button>
                </div>
              </div>
              <small>Sélectionnez votre certificat de signature (.pfx ou .p12)</small>
            </div>
            
            <div class="form-group">
              <label for="password">Mot de passe du certificat</label>
              <div class="password-input-container">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  id="password" 
                  v-model="certificatePassword"
                  placeholder="Entrez le mot de passe"
                />
                <button class="toggle-password" @click="togglePasswordVisibility">
                  <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="signature-modal-footer">
          <div class="signature-status" v-if="signatureStatus">
            <i :class="signatureStatus.icon"></i>
            <span :class="signatureStatus.class">{{ signatureStatus.message }}</span>
          </div>
          <div class="button-group">
            <button class="btn-cancel" @click="closeSignatureModal">Annuler</button>
            <button 
              class="btn-sign" 
              @click="submitSignature" 
              :disabled="isSigningInProgress || !certificateFile || !certificatePassword"
            >
              <i class="bi" :class="isSigningInProgress ? 'bi-hourglass-split' : 'bi-pen-fill'"></i>
              {{ isSigningInProgress ? 'Signature en cours...' : 'Signer le document' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal d'aperçu de template -->
    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content preview-modal">
        <div class="modal-header">
          <h3>
            <i class="bi bi-eye"></i>
            Aperçu du template : {{ selectedTemplate?.name }}
          </h3>
          <button class="modal-close" @click="closePreviewModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="modal-body preview-body">
          <div v-if="loadingPreview" class="loading-preview">
            <div class="spinner"></div>
            <p>Chargement de l'aperçu...</p>
          </div>
          <iframe v-else-if="previewUrl" :src="previewUrl" class="preview-iframe" title="Aperçu du template"></iframe>
          <div v-else class="preview-error">
            <i class="bi bi-exclamation-triangle-fill"></i>
            <p v-if="selectedTemplate?.preview_document">
              Impossible de charger l'aperçu du template.
            </p>
            <p v-else>
              Ce template n'a pas encore d'aperçu généré. 
              <br>L'aperçu sera disponible après la génération du PDF avec QR code.
            </p>
            <div class="preview-actions">
              <button class="btn btn-primary" @click="editTemplate(selectedTemplate)">
                <i class="bi bi-pencil"></i> Modifier le template
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-unused-vars */
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/AuthService';
import axios from 'axios';
import TemplateService from '@/services/TemplateService.js';
import SignSimpleSigner from '@/views/SignSimpleSigner.vue';
import CreateTemplate from '@/views/CreateTemplate.vue';
import PrepareDocumentWithTemplate from '@/views/PrepareDocumentWithTemplate.vue';
import SignWithTemplateMultiple from '@/views/SignWithTemplateMultiple.vue';
import QrPositioner from '@/components/QrPositioner.vue';

const router = useRouter();

// État réactif
const activeSection = ref('');
const userName = ref('');
const organizationName = ref('');
const organizationStatus = ref('');

// État pour la popup de signature
const showSignatureModal = ref(false);
const currentDocument = ref(null);
const certificateFile = ref(null);
const certificatePassword = ref('');
const showPassword = ref(false);
const isSigningInProgress = ref(false);
const signatureStatus = ref(null);
const isDragging = ref(false);

// 🆕 NOUVELLES VARIABLES POUR SIGNATURES ÉPHÉMÈRES
const signatureType = ref('permanent'); // 'permanent' ou 'ephemeral'
const selectedDuration = ref('1month'); // Durée sélectionnée par défaut
const customExpirationDate = ref(''); // Date personnalisée

// Durées pré-définies
const durationPresets = [
  { 
    value: '1day', 
    label: '1 jour', 
    description: 'Idéal pour documents urgents',
    hours: 24,
    icon: 'bi-hourglass-split'
  },
  { 
    value: '1month', 
    label: '1 mois', 
    description: 'Standard pour la plupart des cas',
    hours: 720,
    icon: 'bi-calendar-month'
  },
  { 
    value: '3months', 
    label: '3 mois', 
    description: 'Pour les documents importants',
    hours: 2160,
    icon: 'bi-calendar-range'
  },
  { 
    value: '6months', 
    label: '6 mois', 
    description: 'Validité prolongée',
    hours: 4320,
    icon: 'bi-calendar-date'
  },
  { 
    value: '1year', 
    label: '1 an', 
    description: 'Validité maximale recommandée',
    hours: 8760,
    icon: 'bi-calendar-check'
  }
];

// Statistiques
const stats = ref({
  thisWeek: 0,
  total: 0,
  avgTime: '0j'
});

// Documents à signer
const pendingDocuments = ref([]);

// Documents signés
const signedDocuments = ref([]);



// Variables pour la gestion des templates
const myTemplates = ref([]);
const loadingTemplates = ref(false);
const selectedTemplate = ref(null);

// Variables pour l'aperçu de template
const showPreviewModal = ref(false);
const loadingPreview = ref(false);
const previewUrl = ref(null);

// Variables pour l'édition de template
const showEditModal = ref(false);
const editingTemplate = ref({
  id: null,
  name: '',
  file: null,
  qrPositions: null,
  signatureImage: null,
  generatedPdfFile: null,
  generatedPdfBlob: null,
  generatedPdfDataUrl: null
});
const loadingEditFile = ref(false);
const isUpdating = ref(false);

// Variables pour la modale de choix de signature (inspiré du CollaboratorDashboard)
const showPrepareChoice = ref(false);
const isProcessingChoice = ref(false); // Protection contre les clics multiples

// Classification des documents en attente par mode de préparation
const pendingTab = ref('quick'); // 'quick' ou 'template'

const pendingQuickDocuments = computed(() => pendingDocuments.value.filter(doc => !doc.isTemplate));
const pendingTemplateDocuments = computed(() => pendingDocuments.value.filter(doc => doc.isTemplate));

const selectedPendingTemplateId = ref(null);

const pendingTemplateCards = computed(() => {
  const map = {};
  pendingTemplateDocuments.value.forEach(doc => {
    if (!doc.templateId) return;
    if (!map[doc.templateId]) {
      map[doc.templateId] = {
        templateId: doc.templateId,
        templateName: doc.templateName || `Template ${doc.templateId}`,
        documents: []
      };
    }
    map[doc.templateId].documents.push(doc);
  });
  return Object.values(map);
});

const currentTemplateDocs = computed(() => {
  if (!selectedPendingTemplateId.value) return [];
  return pendingTemplateDocuments.value.filter(doc => doc.templateId === selectedPendingTemplateId.value);
});

const currentTemplateName = computed(() => {
  const d = currentTemplateDocs.value[0];
  return d ? (d.templateName || `Template ${d.templateId}`) : '';
});

watch(pendingTab, (newVal) => {
  if (newVal !== 'template') {
    selectedPendingTemplateId.value = null;
  }
});

// Watcher pour rafraîchir les données quand la section active change
watch(activeSection, (newSection) => {
  console.log('Section active changée vers:', newSection);
  
  if (newSection === 'pending') {
    fetchPendingDocuments();
  } else if (newSection === 'signed') {
    fetchSignedDocuments();
  } else if (newSection === 'history') {
    // L'historique est statique pour l'instant
    console.log('Section historique activée');
  }
});

// Computed
const urgentDocuments = computed(() => {
  return pendingDocuments.value.filter(doc => doc.is_urgent);
});

const sortedPendingDocuments = computed(() => {
  return [...pendingDocuments.value].sort((a, b) => {
    if (a.is_urgent && !b.is_urgent) return -1;
    if (!a.is_urgent && b.is_urgent) return 1;
    return new Date(b.assignedAt) - new Date(a.assignedAt);
  });
});

// Positionnement des particules
const particlePositions = Array.from({ length: 10 }, () => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 5 + 2,
  duration: Math.random() * 30 + 25,
  delay: Math.random() * 10
}));

// Méthodes
function formatDate(dateStr) {
  if (!dateStr) return 'Date inconnue';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return 'Date invalide';
    }
    
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(date);
  } catch (error) {
    console.error('Erreur de formatage de date:', error);
    return 'Date invalide';
  }
}



function getTimeElapsed(dateStr) {
  if (!dateStr) return '0j';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return '0j';
    }
    
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (days === 0) {
      return `${hours}h`;
    }
    return `${days}j`;
  } catch (error) {
    console.error('Erreur de calcul de temps écoulé:', error);
    return '0j';
  }
}



// 🆕 PROPRIÉTÉS CALCULÉES POUR SIGNATURES ÉPHÉMÈRES
// Date minimale pour l'expiration (demain)
const minExpirationDate = computed(() => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().slice(0, 16);
});

// Date d'expiration calculée
const expirationDate = computed(() => {
  if (signatureType.value !== 'ephemeral') return null;
  
  if (selectedDuration.value === 'custom' && customExpirationDate.value) {
    return new Date(customExpirationDate.value);
  }
  
  const preset = durationPresets.find(p => p.value === selectedDuration.value);
  if (preset) {
    const date = new Date();
    date.setHours(date.getHours() + preset.hours);
    return date;
  }
  
  return null;
});

// Formatage de l'affichage de l'expiration
const formatExpirationDisplay = computed(() => {
  if (!expirationDate.value) return 'Non définie';
  
  return expirationDate.value.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
});

// Description de la durée
const durationDescription = computed(() => {
  if (signatureType.value !== 'ephemeral') return '';
  
  if (selectedDuration.value === 'custom') {
    if (!expirationDate.value) return 'Date personnalisée';
    
    const now = new Date();
    const diff = expirationDate.value - now;
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    
    if (days === 1) return 'dans 1 jour';
    if (days < 30) return `dans ${days} jours`;
    if (days < 365) return `dans ${Math.ceil(days / 30)} mois`;
    return `dans ${Math.ceil(days / 365)} an(s)`;
  } else {
    const preset = durationPresets.find(p => p.value === selectedDuration.value);
    return preset ? preset.description : '';
  }
});

// 🆕 MÉTHODE POUR LA SÉLECTION DE DURÉE
function selectDuration(duration) {
  selectedDuration.value = duration;
  if (duration !== 'custom') {
    customExpirationDate.value = '';
  }
}

// Méthodes pour la signature
function signDocument(doc) {
  console.log('Ouvrir la popup de signature pour:', doc.document_name);
  currentDocument.value = doc;
  showSignatureModal.value = true;
  resetSignatureForm();
}

function closeSignatureModal() {
  showSignatureModal.value = false;
  resetSignatureForm();
}

function resetSignatureForm() {
  certificateFile.value = null;
  certificatePassword.value = '';
  showPassword.value = false;
  isSigningInProgress.value = false;
  signatureStatus.value = null;
}

function handleCertificateChange(event) {
  const files = event.target.files;
  if (files.length > 0) {
    certificateFile.value = files[0];
  } else {
    certificateFile.value = null;
  }
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
}

async function submitSignature() {
  if (!certificateFile.value || !certificatePassword.value) {
    signatureStatus.value = {
      message: 'Veuillez fournir votre certificat et mot de passe',
      icon: 'bi bi-exclamation-triangle',
      class: 'error'
    };
    return;
  }

  try {
    isSigningInProgress.value = true;
    signatureStatus.value = {
      message: 'Signature en cours...',
      icon: 'bi bi-hourglass-split',
      class: 'pending'
    };

    // Vérifier si le document a un ID
    if (!currentDocument.value.id) {
      throw new Error('ID du document manquant');
    }

    // Récupérer les détails complets du document depuis l'API
    const token = localStorage.getItem('token');
    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      throw new Error('ID d\'organisation manquant');
    }
    
    console.log('Récupération des détails du document ID:', currentDocument.value.id);
    
    // Récupérer les informations complètes du document depuis l'API
    const documentDetailsResponse = await axios.get(
      `https://ppd.camgovca.cm/api/documents/qr-positions/${currentDocument.value.id}/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          organization_id: organizationId  // Ajouter l'ID de l'organisation
        }
      }
    );
    
    // Vérifier si la requête a réussi
    if (!documentDetailsResponse.data) {
      throw new Error('Impossible de récupérer les détails du document');
    }
    
    const documentDetails = documentDetailsResponse.data;
    console.log('Détails du document récupérés:', documentDetails);
    
    // Extraire les informations de positionnement du QR code dans le format attendu par le microservice
    // Le microservice attend:
    // {x: %, y: %, size: 'small'|'medium'|'large', pages: 'all'|[1,2,3],
    //  positions: {page_num: {x: %, y: %}, ...}, mode: 'all'|'current'|'custom'|'individual'}
    
    // Vérifier et convertir les valeurs numériques
    const xPosition = parseFloat(documentDetails.qr_x_position);
    const yPosition = parseFloat(documentDetails.qr_y_position);
    
    // Vérifier la taille du QR code (valeur par défaut si non conforme)
    const validSizes = ['small', 'medium', 'large'];
    const qrSize = validSizes.includes(documentDetails.qr_size) ? documentDetails.qr_size : 'medium';
    
    // Vérifier le mode de positionnement
    const validModes = ['all', 'current', 'custom', 'individual'];
    const positionMode = validModes.includes(documentDetails.qr_mode) ? documentDetails.qr_mode : 'all';
    
    // Convertir les positions individuelles en structure correcte si nécessaire
    let positions = {};
    if (documentDetails.qr_positions && typeof documentDetails.qr_positions === 'object') {
      // S'assurer que les clés sont des chaînes (numéros de page)
      positions = documentDetails.qr_positions;
    }
    
    // Traiter correctement le paramètre pages
    let pagesValue = documentDetails.qr_pages || 'all';
    // Si pages est une chaîne mais pas "all", essayer de la convertir en liste d'entiers
    if (pagesValue !== 'all' && typeof pagesValue === 'string') {
      try {
        // Pour un nombre unique, créer une liste avec ce nombre
        if (/^\d+$/.test(pagesValue.trim())) {
          pagesValue = [parseInt(pagesValue.trim(), 10)];
          console.log('Pages converties en liste d\'entiers:', pagesValue);
        }
        // Si c'est une chaîne JSON représentant un tableau, la parser
        else if (pagesValue.startsWith('[') && pagesValue.endsWith(']')) {
          pagesValue = JSON.parse(pagesValue);
          console.log('Pages parsées depuis JSON:', pagesValue);
        }
      } catch (error) {
        console.error('Erreur lors de la conversion des pages:', error);
        pagesValue = 'all'; // Valeur par défaut en cas d'erreur
      }
    }
    
    // Créer l'objet de position avec les valeurs vérifiées
    let qrPosition = {
      size: qrSize,
      pages: pagesValue,
      positions: positions,
      mode: positionMode
    };
    
    // En mode "individual", NE PAS envoyer x et y par défaut
    // car chaque page a sa propre position dans "positions"
    if (positionMode !== 'individual') {
      qrPosition.x = isNaN(xPosition) ? 85 : xPosition; // Position X par défaut à 85% si invalide
      qrPosition.y = isNaN(yPosition) ? 10 : yPosition; // Position Y par défaut à 10% si invalide
    }
    
    // Ajouter les données d'orientation si disponibles
    if (documentDetails.orientation_mode || documentDetails.orientation_data) {
      qrPosition.orientation = {
        mode: documentDetails.orientation_mode || 'auto',
        effective: documentDetails.orientation_data?.effective || 'portrait',
        previewWidth: documentDetails.orientation_data?.previewWidth || 595,
        previewHeight: documentDetails.orientation_data?.previewHeight || 842
      };
      console.log('Orientation ajoutée au QR position:', qrPosition.orientation);
    }
    
    console.log('Informations de positionnement du QR code formatées:', qrPosition);

    // ========== RÉCUPÉRATION DES INFORMATIONS DE SIGNATURE ==========
    // Récupérer et formater les informations de signature depuis DocumentQRPosition
    let signaturePosition = null;
    
    // Vérifier si le document a des informations de signature
    if (documentDetails.signature_image_url || documentDetails.signature_positions) {
      console.log('Informations de signature trouvées dans le document:', {
        has_image: !!documentDetails.signature_image_url,
        has_positions: !!documentDetails.signature_positions,
        signature_size: documentDetails.signature_size
      });
      
      // Construire l'objet signature_position au format attendu par le microservice
      signaturePosition = {};
      
      // Ajouter l'image de signature si disponible
      if (documentDetails.signature_image_url) {
        // L'image est accessible via l'endpoint SFTP
        try {
          console.log('Récupération de l\'image de signature via SFTP...');
          
          // Utiliser l'endpoint SFTP pour télécharger l'image de signature
          const imageResponse = await axios.get(documentDetails.signature_image_url, {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            responseType: 'blob'
          });
          
          // Convertir l'image en base64 avec le bon type MIME
          const imageBlob = imageResponse.data;
          const imageBase64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => {
              // Remplacer le type MIME par image/png
              const base64String = String(reader.result);
              const correctedBase64 = base64String.replace('application/octet-stream', 'image/png');
              resolve(correctedBase64);
            };
            reader.readAsDataURL(imageBlob);
          });
          
          signaturePosition.signature_image = imageBase64;
          console.log('Image de signature récupérée via SFTP et convertie en base64 (PNG):', imageBase64.substring(0, 50) + '...');
          
        } catch (imageError) {
          console.error('Erreur lors de la récupération de l\'image de signature via SFTP:', imageError);
          console.log('Signature sera appliquée sans image personnalisée');
        }
      }
      
      // Ajouter la taille de signature si disponible
      if (documentDetails.signature_size) {
        signaturePosition.signature_size = documentDetails.signature_size;
        console.log('Taille de signature récupérée:', documentDetails.signature_size);
      } else {
        signaturePosition.signature_size = 50; // Valeur par défaut
        console.log('Aucune taille de signature spécifiée, utilisation de la valeur par défaut: 50%');
      }
      
      // Ajouter les positions de signature si disponibles
      if (documentDetails.signature_positions) {
        try {
          let positions = documentDetails.signature_positions;
          
          // Parser si c'est une chaîne JSON
          if (typeof positions === 'string') {
            positions = JSON.parse(positions);
          }
          
          // Convertir le format objet {page_num: {x, y}} vers tableau [{page, x, y, width, height}]
          const signaturePositionsArray = [];
          
          if (positions && typeof positions === 'object') {
            Object.entries(positions).forEach(([pageKey, position]) => {
              if (pageKey === 'default') {
                // Pour les positions par défaut (mode "all"), envoyer une seule position avec page: "all"
                console.log('Mode "all" détecté pour signature, envoi d\'une position avec page: "all"');
                
                signaturePositionsArray.push({
                  page: "all",
                  x: position.x,
                  y: position.y,
                  width: 20, // Largeur par défaut
                  height: 10 // Hauteur par défaut
                });
                
                console.log('Position de signature avec mode "all" générée');
              } else if (position && typeof position === 'object' && position.x !== undefined && position.y !== undefined) {
                // Positions individuelles par page
                const pageNumber = parseInt(pageKey);
                
                // Vérifier que pageNumber est valide
                if (!isNaN(pageNumber)) {
                  signaturePositionsArray.push({
                    page: pageNumber,
                    x: position.x,
                    y: position.y,
                    width: 20, // Largeur par défaut
                    height: 10 // Hauteur par défaut
                  });
                }
              }
            });
          }
          
          signaturePosition.positions = signaturePositionsArray;
          console.log('Positions de signature formatées:', signaturePositionsArray);
          
        } catch (positionError) {
          console.error('Erreur lors du parsing des positions de signature:', positionError);
          signaturePosition.positions = [];
        }
      } else {
        signaturePosition.positions = [];
      }
      
      console.log('Informations de signature finales:', signaturePosition);
    } else {
      console.log('Aucune information de signature trouvée dans le document');
    }
    
    // Vérifier si le document a une URL de fichier disponible
    if (!documentDetails.document_file_url && !documentDetails.generated_pdf_url) {
      throw new Error('Aucun fichier PDF disponible pour ce document');
    }
    
    // Récupérer le document via l'endpoint SFTP au lieu de l'URL directe
    console.log('Récupération du document via l\'endpoint SFTP...');
    
    // Utiliser l'endpoint SFTP pour télécharger le document
    const response = await axios.get(
      `https://ppd.camgovca.cm/api/documents/qr-positions/${documentDetails.id}/download_document/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      }
    );
    
    // Créer un objet File à partir du Blob pour l'envoi
    const documentFile = new File(
      [response.data], 
      documentDetails.document_name || 'document.pdf', 
      { type: 'application/pdf' }
    );

    // Préparer les métadonnées avec la position du QR code et les informations de signature
    const metadataObject = {
      qr_position: qrPosition,
      document_id: documentDetails.id,
      document_title: documentDetails.document_name,
      organization_id: organizationId,  // Ajouter l'ID de l'organisation aux métadonnées
      organization_name: currentUser?.organization?.name || 'Organisation inconnue',  // Nom de l'organisation
      signer_role: currentUser?.position || currentUser?.role || 'Signataire',  // Rôle du signataire
      signer_name: currentUser?.first_name && currentUser?.last_name ? 
        `${currentUser.first_name} ${currentUser.last_name}` : 
        currentUser?.username || 'Signataire'  // Nom complet du signataire
    };
    
    // Ajouter les informations de signature si disponibles (même format que SignSimple.vue)
    if (signaturePosition) {
      metadataObject.signature_position = signaturePosition;
      console.log('Informations de signature ajoutées aux métadonnées:', {
        has_image: !!signaturePosition.signature_image,
        positions_count: signaturePosition.positions?.length || 0,
        positions_detail: signaturePosition.positions
      });
    }
    
    // 🆕 AJOUTER LES DONNÉES D'EXPIRATION POUR SIGNATURES ÉPHÉMÈRES DANS LES MÉTADONNÉES
    metadataObject.signature_type = signatureType.value === 'ephemeral' ? 'ephemeral' : 'permanent';
    
    if (signatureType.value === 'ephemeral' && expirationDate.value) {
      metadataObject.expiration_date = expirationDate.value.toISOString();
      console.log('🕐 Signature éphémère configurée, expiration:', expirationDate.value.toISOString());
    } else {
      console.log('🔒 Signature pérenne configurée (pas d\'expiration)');
    }
    
    const metadata = JSON.stringify(metadataObject);

    // Afficher les métadonnées qui seront envoyées pour vérification
    console.log('Métadonnées complètes envoyées au microservice de signature:', JSON.parse(metadata));

    // Créer le FormData pour l'envoi au microservice de signature
    const formData = new FormData();
    formData.append('certificate', certificateFile.value);
    formData.append('password', certificatePassword.value);
    formData.append('document', documentFile);
    formData.append('metadata', metadata);
    formData.append('owner_id', currentUser.id);
    formData.append('organization_id', organizationId);
    formData.append('organization_name', currentUser?.organization?.name || 'Organisation inconnue');
    formData.append('signer_role', currentUser?.position || currentUser?.role || 'Signataire');
    formData.append('signer_name', currentUser?.first_name && currentUser?.last_name ? 
      `${currentUser.first_name} ${currentUser.last_name}` : 
      currentUser?.username || 'Signataire');
    
    // Envoyer la requête au microservice de signature via l'API gateway
    const signResponse = await axios.post(
      'https://ppd.camgovca.cm/sign/sign',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        responseType: 'blob'
      }
    );

    // Traiter la réponse
    if (signResponse.status === 200) {
      // Extraire le nom du fichier du header Content-Disposition s'il est présent
      const contentDisposition = signResponse.headers['content-disposition'];
      let filename = `${documentDetails.document_name.replace('.pdf', '')}_signé.pdf`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*)\2|[^;\n]*/i);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]*/g, '');
        }
      }
      
      console.log('Téléchargement du document signé:', filename);
      
      // Créer le blob PDF et déclencher le téléchargement
      const blob = new Blob([signResponse.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Libérer l'URL objet
      window.URL.revokeObjectURL(url);
      
      console.log('Document téléchargé, mise à jour du statut...');
      
      try {
        // Mettre à jour le statut du document dans la base de données
        await updateDocumentStatus(currentDocument.value.id, 'signed');
        console.log('Statut du document mis à jour vers "signed"');
        
        // Déplacer le document de la liste "en attente" vers "signés"
        const signedDoc = {
          ...currentDocument.value,
          status: 'signed',
          signedAt: new Date().toISOString(),
          signedBy: AuthService.getCurrentUser()?.username || 'Signataire'
        };
        
        // Ajouter à la liste des documents signés
        signedDocuments.value.unshift(signedDoc);
        
        // Retirer de la liste des documents en attente
        pendingDocuments.value = pendingDocuments.value.filter(doc => doc.id !== currentDocument.value.id);
        
        console.log('Document déplacé vers la section signés');
        
        // Mettre à jour les statistiques
        stats.value.thisWeek += 1;
        stats.value.total += 1;
        
      } catch (statusUpdateError) {
        console.error('Erreur lors de la mise à jour du statut:', statusUpdateError);
        // Ne pas faire échouer toute l'opération si la mise à jour du statut échoue
        signatureStatus.value = {
          message: 'Document signé, mais erreur de synchronisation. Actualisez la page.',
          icon: 'bi bi-exclamation-triangle',
          class: 'warning'
        };
      }
      
      // Mettre à jour le statut d'affichage
      signatureStatus.value = {
        message: 'Document signé avec succès',
        icon: 'bi bi-check-circle',
        class: 'success'
      };
      
      // Fermer la popup après un délai
      setTimeout(() => {
        closeSignatureModal();
      }, 2000);
    } else {
      throw new Error('Erreur lors de la signature');
    }
  } catch (error) {
    console.error('Erreur lors de la signature:', error);
    signatureStatus.value = {
      message: `Erreur: ${error.response?.data?.detail || error.message || 'Erreur inconnue'}`,
      icon: 'bi bi-x-circle',
      class: 'error'
    };
  } finally {
    isSigningInProgress.value = false;
  }
}

function previewDocument(doc) {
  console.log('Prévisualiser le document:', doc.document_name);
  
  // Utiliser les URLs SFTP pour la prévisualisation
  if (doc.document_file_url || doc.generated_pdf_url) {
    try {
      // Priorité au PDF généré, sinon utiliser le document original
      let fileUrl = doc.generated_pdf_url || doc.document_file_url;
      
      console.log('Ouverture du document via SFTP à l\'URL:', fileUrl);
      window.open(fileUrl, '_blank');
    } catch (error) {
      console.error('Erreur lors de l\'ouverture du document:', error);
      alert('Impossible d\'ouvrir le document. Veuillez réessayer plus tard.');
    }
  } else {
    console.error('Aucune URL de fichier disponible pour ce document');
    alert('Aucun fichier n\'est disponible pour ce document.');
  }
}

function logout() {
  AuthService.logout();
  router.push('/login');
}

async function downloadSignedDocument(doc) {
  console.log('Télécharger le document signé:', doc.document_name || doc.name);
  
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token d\'authentification manquant');
      return;
    }

    // Récupérer l'ID de l'organisation actuelle
    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    // Utiliser l'endpoint de téléchargement de DocumentSignature
    const downloadUrl = `https://ppd.camgovca.cm/api/documents/signatures/${doc.document_id || doc.id}/download/`;
    
    const response = await axios.get(downloadUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId
      },
      responseType: 'blob'
    });

    // Créer le blob et déclencher le téléchargement
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Déterminer le nom du fichier
    let filename = doc.document_name || doc.name || doc.title || 'document_signe.pdf';
    if (!filename.endsWith('.pdf')) {
      filename += '.pdf';
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Libérer l'URL objet
    window.URL.revokeObjectURL(url);
    
    console.log('Document signé téléchargé avec succès');
  } catch (error) {
    console.error('Erreur lors du téléchargement du document signé:', error);
    alert('Erreur lors du téléchargement du document. Veuillez réessayer.');
  }
}

function handleDrop(event) {
  isDragging.value = false;
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (file.name.endsWith('.pfx') || file.name.endsWith('.p12')) {
      certificateFile.value = file;
    } else {
      signatureStatus.value = {
        message: 'Le fichier doit être un certificat (.pfx ou .p12)',
        icon: 'bi bi-exclamation-triangle',
        class: 'error'
      };
    }
  }
}

function removeCertificate(event) {
  event.stopPropagation();
  certificateFile.value = null;
}

function formatFileSize(size) {
  if (size < 1024) {
    return size + ' octets';
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' Ko';
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' Mo';
  }
}

// Initialisation
onMounted(() => {
  document.title = 'Signataire - Doc@uthANTIC';
  fetchUserData();
  fetchDocuments();
  loadMyTemplates(); // Charger les templates du signataire
  initStats();
  
  // Activer la section "pending" par défaut
  activeSection.value = 'pending';
});

// Méthodes supplémentaires
async function fetchPendingDocuments() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token d\'authentification manquant');
      return;
    }

    // Récupérer l'ID de l'organisation actuelle
    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    const config = {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId
      }
    };  

    const response = await axios.get('https://ppd.camgovca.cm/api/documents/qr-positions/pending_for_signer/', config);
    if (response.data) {
      pendingDocuments.value = (response.data.pending_documents || []).map(doc => ({
        ...doc,
        id: doc.id,
        assignedAt: doc.assignedAt || doc.created_at,
        isTemplate: !!(doc.metadata && doc.metadata.template_used),
        templateId: doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_id : null,
        templateName: doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_name : null
      }));
      
      // Mettre à jour les statistiques
      if (response.data.stats) {
        stats.value.thisWeek = response.data.stats.thisWeek || 0;
        stats.value.total = response.data.stats.total || 0;
        stats.value.avgTime = response.data.stats.avgTime || '0j';
      }
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des documents:', error);
  }
}

// Fonction pour récupérer les documents signés
async function fetchSignedDocuments() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('Token d\'authentification manquant');
      return;
    }

    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    const baseUrl = 'https://ppd.camgovca.cm/api/documents/signatures/';
    let nextUrl = `${baseUrl}?organization_id=${organizationId}&page_size=100`;

    signedDocuments.value = [];

    while (nextUrl) {
      const response = await axios.get(nextUrl, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data && response.data.results) {
        const pageDocs = response.data.results.map(doc => {
          const tplId = doc.template_id ||
                       (doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_id : null) ||
                       (doc.metadata && doc.metadata.template_id ? doc.metadata.template_id : null);
          const tplName = doc.template_name ||
                         (doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_name : null) ||
                         (doc.metadata && doc.metadata.template_name ? doc.metadata.template_name : null);

          return {
            ...doc,
            id: doc.document_id,
            document_name: doc.title,
            name: doc.title,
            signedAt: doc.created_at,
            signedBy: doc.owner_username || 'Signataire',
            organization_name: doc.organization_name || 'Organisation',
            signer_role: doc.signer_role || 'Signataire',
            isTemplate: !!tplId,
            templateId: tplId,
            templateName: tplName
          };
        });

        signedDocuments.value.push(...pageDocs);
        nextUrl = response.data.next;
      } else {
        nextUrl = null;
      }
    }

    console.log('Documents signés récupérés (pagination complète):', signedDocuments.value.length);
  } catch (error) {
    console.error('Erreur lors de la récupération des documents signés:', error);
  }
}

// Fonction pour mettre à jour le statut d'un document
async function updateDocumentStatus(documentId, newStatus) {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token d\'authentification manquant');
    }

    const currentUser = AuthService.getCurrentUser();
    const organizationId = currentUser?.organization?.id;
    
    if (!organizationId) {
      throw new Error('ID d\'organisation manquant');
    }

    // Utiliser FormData au lieu de JSON pour l'API Django
    const formData = new FormData();
    formData.append('status', newStatus);
    
    const response = await axios.patch(
      `https://ppd.camgovca.cm/api/documents/qr-positions/${documentId}/`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        params: {
          organization_id: organizationId
        }
      }
    );

    console.log('Statut du document mis à jour:', response.data);
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la mise à jour du statut:', error);
    throw error;
  }
}

// Fonction pour récupérer tous les documents (en attente et signés)
async function fetchDocuments() {
  console.log('Récupération de tous les documents...');
  await Promise.all([
    fetchPendingDocuments(),
    fetchSignedDocuments()
  ]);
}

// Fonction pour récupérer les données de l'utilisateur
function fetchUserData() {
  const user = AuthService.getCurrentUser();
  if (user) {
    userName.value = user.username || 'Utilisateur';
    
    if (user.organization && typeof user.organization === 'object') {
      organizationName.value = user.organization.name || 'Organisation Inconnue';
      organizationStatus.value = user.organization.status || 'inconnu';
    } else {
      organizationName.value = 'N/A';
      organizationStatus.value = 'N/A';
      console.warn("Les informations de l'organisation ne sont pas disponibles ou dans un format incorrect.");
    }
  } else {
    router.push('/login');
  }
}

// Fonction pour initialiser les statistiques
function initStats() {
  // Les statistiques sont mises à jour automatiquement 
  // via fetchPendingDocuments qui récupère les stats du backend
  console.log('Initialisation des statistiques...');
}

function openBlobInNewTab(blob) {
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank');
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}

async function previewTemplateById(tplId) {
  try {
    // Récupérer les détails du template pour utiliser la modale d'aperçu
    const templateDetails = await TemplateService.getTemplate(tplId);
    
    // Utiliser la fonction previewTemplate existante qui affiche la modale
    await previewTemplate({
      id: templateDetails.id,
      name: templateDetails.name,
      preview_document: templateDetails.preview_document
    });
  } catch (err) {
    console.error('Erreur lors de l\'ouverture de l\'aperçu du template:', err);
    alert('Impossible d\'afficher ce template.');
  }
}

// Variables de pagination et recherche pour les documents en attente
const searchQueryQuick = ref('');
const searchQueryTemplate = ref('');
const currentPageQuick = ref(1);
const currentPageTemplate = ref(1);
const itemsPerPage = 5; // Maximum 5 documents par page comme demandé

// Documents filtrés pour l'onglet quick
const filteredQuickDocuments = ref([]);

// Documents filtrés pour l'onglet template
const filteredTemplateDocuments = ref([]);

// Propriétés calculées pour la pagination - Onglet Quick
const paginatedQuickDocuments = computed(() => {
  const start = (currentPageQuick.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredQuickDocuments.value.slice(start, end);
});

const totalPagesQuick = computed(() => {
  return Math.ceil(filteredQuickDocuments.value.length / itemsPerPage);
});

const visiblePagesQuick = computed(() => {
  const pages = [];
  const total = totalPagesQuick.value;
  const current = currentPageQuick.value;
  
  // Afficher au maximum 5 pages à la fois
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  
  // Ajuster si on est au début ou à la fin
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});

// Propriétés calculées pour la pagination - Onglet Template
const paginatedTemplateDocuments = computed(() => {
  const start = (currentPageTemplate.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredTemplateDocuments.value.slice(start, end);
});

const totalPagesTemplate = computed(() => {
  return Math.ceil(filteredTemplateDocuments.value.length / itemsPerPage);
});

const visiblePagesTemplate = computed(() => {
  const pages = [];
  const total = totalPagesTemplate.value;
  const current = currentPageTemplate.value;
  
  // Afficher au maximum 5 pages à la fois
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  
  // Ajuster si on est au début ou à la fin
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});

// Fonctions de filtrage
function filterQuickDocuments() {
  const query = searchQueryQuick.value.toLowerCase();
  
  filteredQuickDocuments.value = pendingQuickDocuments.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(query)) ||
           (doc.collaborator_username && doc.collaborator_username.toLowerCase().includes(query)) ||
           (doc.preparedBy && doc.preparedBy.toLowerCase().includes(query));
  });
  
  // Réinitialiser à la première page après un filtrage
  currentPageQuick.value = 1;
}

function filterTemplateDocuments() {
  const query = searchQueryTemplate.value.toLowerCase();
  
  filteredTemplateDocuments.value = currentTemplateDocs.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(query)) ||
           (doc.collaborator_username && doc.collaborator_username.toLowerCase().includes(query));
  });
  
  // Réinitialiser à la première page après un filtrage
  currentPageTemplate.value = 1;
}

// Fonctions de pagination - Onglet Quick
function goToPageQuick(page) {
  if (page >= 1 && page <= totalPagesQuick.value) {
    currentPageQuick.value = page;
  }
}

function previousPageQuick() {
  if (currentPageQuick.value > 1) {
    currentPageQuick.value--;
  }
}

function nextPageQuick() {
  if (currentPageQuick.value < totalPagesQuick.value) {
    currentPageQuick.value++;
  }
}

// Fonctions de pagination - Onglet Template
function goToPageTemplate(page) {
  if (page >= 1 && page <= totalPagesTemplate.value) {
    currentPageTemplate.value = page;
  }
}

function previousPageTemplate() {
  if (currentPageTemplate.value > 1) {
    currentPageTemplate.value--;
  }
}

function nextPageTemplate() {
  if (currentPageTemplate.value < totalPagesTemplate.value) {
    currentPageTemplate.value++;
  }
}

// Watcher pour mettre à jour les documents filtrés quand les données changent
watch(pendingQuickDocuments, () => {
  filterQuickDocuments();
}, { immediate: true });

watch(currentTemplateDocs, () => {
  filterTemplateDocuments();
}, { immediate: true });

// Watcher pour réinitialiser la pagination quand on change d'onglet
watch(pendingTab, () => {
  currentPageQuick.value = 1;
  currentPageTemplate.value = 1;
});

// Watcher pour réinitialiser la recherche template quand on change de template
watch(selectedPendingTemplateId, () => {
  searchQueryTemplate.value = '';
  currentPageTemplate.value = 1;
});

// === Gestion des documents SIGNÉS (onglets, recherche, pagination) ===
const signedTab = ref('quick');
const signedQuickDocuments = computed(() => signedDocuments.value.filter(doc => !doc.isTemplate));
const signedTemplateDocuments = computed(() => signedDocuments.value.filter(doc => doc.isTemplate));

const selectedSignedTemplateId = ref(null);

const signedTemplateCards = computed(() => {
  const map = {};
  signedTemplateDocuments.value.forEach(doc => {
    if (!doc.templateId) return;
    if (!map[doc.templateId]) {
      map[doc.templateId] = {
        templateId: doc.templateId,
        templateName: doc.templateName || `Template ${doc.templateId}`,
        documents: []
      };
    }
    map[doc.templateId].documents.push(doc);
  });
  return Object.values(map);
});

const currentSignedTemplateDocs = computed(() => {
  if (!selectedSignedTemplateId.value) return [];
  return signedTemplateDocuments.value.filter(doc => doc.templateId === selectedSignedTemplateId.value);
});

// Recherche & Pagination
const searchQuerySignedQuick = ref('');
const searchQuerySignedTemplate = ref('');
const currentPageSignedQuick = ref(1);
const currentPageSignedTemplate = ref(1);

const filteredSignedQuickDocuments = ref([]);
const filteredSignedTemplateDocuments = ref([]);

const paginatedSignedQuickDocuments = computed(() => {
  const start = (currentPageSignedQuick.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredSignedQuickDocuments.value.slice(start, end);
});

const totalPagesSignedQuick = computed(() => Math.ceil(filteredSignedQuickDocuments.value.length / itemsPerPage));

const visiblePagesSignedQuick = computed(() => {
  const pages = [];
  const total = totalPagesSignedQuick.value;
  const current = currentPageSignedQuick.value;
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

const paginatedSignedTemplateDocuments = computed(() => {
  const start = (currentPageSignedTemplate.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredSignedTemplateDocuments.value.slice(start, end);
});

const totalPagesSignedTemplate = computed(() => Math.ceil(filteredSignedTemplateDocuments.value.length / itemsPerPage));

const visiblePagesSignedTemplate = computed(() => {
  const pages = [];
  const total = totalPagesSignedTemplate.value;
  const current = currentPageSignedTemplate.value;
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

// Fonctions de filtrage
function filterSignedQuickDocuments() {
  const query = searchQuerySignedQuick.value.toLowerCase();
  filteredSignedQuickDocuments.value = signedQuickDocuments.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(query)) ||
           (doc.signedBy && doc.signedBy.toLowerCase().includes(query));
  });
  currentPageSignedQuick.value = 1;
}

function filterSignedTemplateDocuments() {
  const query = searchQuerySignedTemplate.value.toLowerCase();
  filteredSignedTemplateDocuments.value = currentSignedTemplateDocs.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(query)) ||
           (doc.signedBy && doc.signedBy.toLowerCase().includes(query));
  });
  currentPageSignedTemplate.value = 1;
}

// Pagination helpers
function goToPageSignedQuick(page) { if (page >= 1 && page <= totalPagesSignedQuick.value) currentPageSignedQuick.value = page; }
function previousPageSignedQuick() { if (currentPageSignedQuick.value > 1) currentPageSignedQuick.value--; }
function nextPageSignedQuick() { if (currentPageSignedQuick.value < totalPagesSignedQuick.value) currentPageSignedQuick.value++; }

function goToPageSignedTemplate(page) { if (page >= 1 && page <= totalPagesSignedTemplate.value) currentPageSignedTemplate.value = page; }
function previousPageSignedTemplate() { if (currentPageSignedTemplate.value > 1) currentPageSignedTemplate.value--; }
function nextPageSignedTemplate() { if (currentPageSignedTemplate.value < totalPagesSignedTemplate.value) currentPageSignedTemplate.value++; }

// Watchers
watch(signedQuickDocuments, () => { filterSignedQuickDocuments(); }, { immediate: true });
watch(currentSignedTemplateDocs, () => { filterSignedTemplateDocuments(); }, { immediate: true });
watch(signedTab, () => {
  currentPageSignedQuick.value = 1;
  currentPageSignedTemplate.value = 1;
  if (signedTab.value !== 'template') selectedSignedTemplateId.value = null;
});
watch(selectedSignedTemplateId, () => {
  searchQuerySignedTemplate.value = '';
  currentPageSignedTemplate.value = 1;
});
// === Fin gestion documents signés ===

const searchQuerySigned = ref('');
const filteredSignedDocuments = computed(() => {
  return signedDocuments.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(searchQuerySigned.value.toLowerCase())) ||
           (doc.name && doc.name.toLowerCase().includes(searchQuerySigned.value.toLowerCase())) ||
           (doc.organization_name && doc.organization_name.toLowerCase().includes(searchQuerySigned.value.toLowerCase()));
  });
});

// === Pagination combinée pour signed ===
const currentPageSigned = ref(1);
watch(filteredSignedDocuments, () => { currentPageSigned.value = 1; });

const paginatedSignedDocuments = computed(() => {
  const start = (currentPageSigned.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredSignedDocuments.value.slice(start, end);
});

const totalPagesSigned = computed(() => Math.ceil(filteredSignedDocuments.value.length / itemsPerPage));

const visiblePagesSigned = computed(() => {
  const pages = [];
  const total = totalPagesSigned.value;
  const current = currentPageSigned.value;
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

function goToPageSigned(page) { if (page >= 1 && page <= totalPagesSigned.value) currentPageSigned.value = page; }
function previousPageSigned() { if (currentPageSigned.value > 1) currentPageSigned.value--; }
function nextPageSigned() { if (currentPageSigned.value < totalPagesSigned.value) currentPageSigned.value++; }
// === Fin pagination combinée ===

const totalSignedCount = computed(() => signedDocuments.value.length);

// Variables de pagination et recherche pour les documents urgents
const urgentTab = ref('quick');
const urgentQuickDocuments = computed(() => urgentDocuments.value.filter(doc => !doc.isTemplate));
const urgentTemplateDocuments = computed(() => urgentDocuments.value.filter(doc => doc.isTemplate));

const selectedUrgentTemplateId = ref(null);

const urgentTemplateCards = computed(() => {
  const map = {};
  urgentTemplateDocuments.value.forEach(doc => {
    if (!doc.templateId) return;
    if (!map[doc.templateId]) {
      map[doc.templateId] = {
        templateId: doc.templateId,
        templateName: doc.templateName || `Template ${doc.templateId}`,
        documents: []
      };
    }
    map[doc.templateId].documents.push(doc);
  });
  return Object.values(map);
});

const currentUrgentTemplateDocs = computed(() => {
  if (!selectedUrgentTemplateId.value) return [];
  return urgentTemplateDocuments.value.filter(doc => doc.templateId === selectedUrgentTemplateId.value);
});

const currentUrgentTemplateName = computed(() => {
  const d = currentUrgentTemplateDocs.value[0];
  return d ? (d.templateName || `Template ${d.templateId}`) : '';
});

// Recherche & Pagination
const searchQueryUrgentQuick = ref('');
const searchQueryUrgentTemplate = ref('');
const currentPageUrgentQuick = ref(1);
const currentPageUrgentTemplate = ref(1);

const filteredUrgentQuickDocuments = ref([]);
const filteredUrgentTemplateDocuments = ref([]);

const paginatedUrgentQuickDocuments = computed(() => {
  const start = (currentPageUrgentQuick.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredUrgentQuickDocuments.value.slice(start, end);
});

const totalPagesUrgentQuick = computed(() => Math.ceil(filteredUrgentQuickDocuments.value.length / itemsPerPage));

const visiblePagesUrgentQuick = computed(() => {
  const pages = [];
  const total = totalPagesUrgentQuick.value;
  const current = currentPageUrgentQuick.value;
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

const paginatedUrgentTemplateDocuments = computed(() => {
  const start = (currentPageUrgentTemplate.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredUrgentTemplateDocuments.value.slice(start, end);
});

const totalPagesUrgentTemplate = computed(() => Math.ceil(filteredUrgentTemplateDocuments.value.length / itemsPerPage));

const visiblePagesUrgentTemplate = computed(() => {
  const pages = [];
  const total = totalPagesUrgentTemplate.value;
  const current = currentPageUrgentTemplate.value;
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

// Fonctions de filtrage
function filterUrgentQuickDocuments() {
  const query = searchQueryUrgentQuick.value.toLowerCase();
  filteredUrgentQuickDocuments.value = urgentQuickDocuments.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(query)) ||
           (doc.collaborator_username && doc.collaborator_username.toLowerCase().includes(query)) ||
           (doc.preparedBy && doc.preparedBy.toLowerCase().includes(query));
  });
  currentPageUrgentQuick.value = 1;
}

function filterUrgentTemplateDocuments() {
  const query = searchQueryUrgentTemplate.value.toLowerCase();
  filteredUrgentTemplateDocuments.value = currentUrgentTemplateDocs.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(query)) ||
           (doc.collaborator_username && doc.collaborator_username.toLowerCase().includes(query));
  });
  currentPageUrgentTemplate.value = 1;
}

// Pagination helpers
function goToPageUrgentQuick(page) { if (page >= 1 && page <= totalPagesUrgentQuick.value) currentPageUrgentQuick.value = page; }
function previousPageUrgentQuick() { if (currentPageUrgentQuick.value > 1) currentPageUrgentQuick.value--; }
function nextPageUrgentQuick() { if (currentPageUrgentQuick.value < totalPagesUrgentQuick.value) currentPageUrgentQuick.value++; }

function goToPageUrgentTemplate(page) { if (page >= 1 && page <= totalPagesUrgentTemplate.value) currentPageUrgentTemplate.value = page; }
function previousPageUrgentTemplate() { if (currentPageUrgentTemplate.value > 1) currentPageUrgentTemplate.value--; }
function nextPageUrgentTemplate() { if (currentPageUrgentTemplate.value < totalPagesUrgentTemplate.value) currentPageUrgentTemplate.value++; }

// Watchers
watch(urgentQuickDocuments, () => { filterUrgentQuickDocuments(); }, { immediate: true });
watch(currentUrgentTemplateDocs, () => { filterUrgentTemplateDocuments(); }, { immediate: true });
watch(urgentTab, () => {
  currentPageUrgentQuick.value = 1;
  currentPageUrgentTemplate.value = 1;
  if (urgentTab.value !== 'template') selectedUrgentTemplateId.value = null;
});
watch(selectedUrgentTemplateId, () => {
  searchQueryUrgentTemplate.value = '';
  currentPageUrgentTemplate.value = 1;
});
// === Fin gestion documents urgents ===

const searchQueryUrgent = ref('');
const filteredUrgentDocuments = computed(() => {
  return urgentDocuments.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(searchQueryUrgent.value.toLowerCase())) ||
           (doc.name && doc.name.toLowerCase().includes(searchQueryUrgent.value.toLowerCase())) ||
           (doc.organization_name && doc.organization_name.toLowerCase().includes(searchQueryUrgent.value.toLowerCase()));
  });
});

// === Pagination combinée pour urgents ===
const currentPageUrgent = ref(1);
watch(filteredUrgentDocuments, () => { currentPageUrgent.value = 1; });

const paginatedUrgentDocuments = computed(() => {
  const start = (currentPageUrgent.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredUrgentDocuments.value.slice(start, end);
});

const totalPagesUrgent = computed(() => Math.ceil(filteredUrgentDocuments.value.length / itemsPerPage));

const visiblePagesUrgent = computed(() => {
  const pages = [];
  const total = totalPagesUrgent.value;
  const current = currentPageUrgent.value;
  let start = Math.max(1, current - 2);
  let end = Math.min(total, current + 2);
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4);
    } else if (end === total) {
      start = Math.max(1, end - 4);
    }
  }
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

function goToPageUrgent(page) { if (page >= 1 && page <= totalPagesUrgent.value) currentPageUrgent.value = page; }
function previousPageUrgent() { if (currentPageUrgent.value > 1) currentPageUrgent.value--; }
function nextPageUrgent() { if (currentPageUrgent.value < totalPagesUrgent.value) currentPageUrgent.value++; }
// === Fin pagination combinée ===

const totalUrgentCount = computed(() => urgentDocuments.value.length);

// Computed property pour vérifier si le template peut être mis à jour
const canUpdateTemplate = computed(() => {
  return editingTemplate.value.name && 
         editingTemplate.value.file && 
         editingTemplate.value.qrPositions;
});

// === NOUVELLES MÉTHODES POUR LA GESTION DES TEMPLATES ===

// Méthodes de gestion des templates
async function loadMyTemplates() {
  try {
    loadingTemplates.value = true;
    console.log('Chargement des templates du signataire...');
    
    const response = await TemplateService.getTemplates(organizationName.value);
    myTemplates.value = response.results.map(template => ({
      id: template.id,
      name: template.name,
      createdAt: new Date(template.created_at),
      pageApplication: template.page_application,
      qrSize: template.qr_size,
      hasSignature: !!template.signature_image,
      preview_document: template.preview_document // Added this line
    }));
    
    console.log('Templates chargés:', myTemplates.value.length);
  } catch (error) {
    console.error('Erreur lors du chargement des templates:', error);
    myTemplates.value = [];
  } finally {
    loadingTemplates.value = false;
  }
}



function onTemplateCreated(templateData) {
  console.log('Template créé avec succès:', templateData);
  
  // Ajouter le nouveau template à la liste locale
  const newTemplateForList = {
    id: templateData.id,
    name: templateData.name,
    createdAt: new Date(templateData.createdAt),
    pageApplication: templateData.pageApplication,
    qrSize: templateData.qrSize,
    hasSignature: templateData.hasSignature,
    preview_document: templateData.preview_document // Added this line
  };
  
  myTemplates.value.unshift(newTemplateForList);
  
  // Passer à la section templates pour voir le nouveau template
  activeSection.value = 'my-templates';
  
  console.log('Template ajouté à la liste avec succès');
}

function openCreateTemplateFromPrepare() {
  // Ouvrir la création de template
  activeSection.value = 'create-template';
}

// === NOUVELLES MÉTHODES POUR LA MODALE DE SIGNATURE (basé sur CollaboratorDashboard) ===

// Fonction pour ouvrir la modale de choix de signature
function openPrepareDocument() {
  showPrepareChoice.value = true;
}

// Fonction pour fermer la modale de choix
function closePrepareChoice() {
  showPrepareChoice.value = false;
}

// Sélection de la signature avec template
function selectTemplatePreparation() {
  closePrepareChoice();
  // Ouvrir directement la vue de signature avec template
  activeSection.value = 'sign-with-template';
}

// Sélection de la signature rapide
function selectDirectPreparation() {
  console.log('selectDirectPreparation appelée', activeSection.value);
  
  // Éviter les appels multiples
  if (activeSection.value === 'sign-simple' || isProcessingChoice.value) {
    console.log('Section déjà active ou en cours de traitement, ignoring...');
    return;
  }
  
  // Marquer comme en cours de traitement
  isProcessingChoice.value = true;
  
  // Fermer la modal de choix
  closePrepareChoice();
  
  // Afficher la section de signature rapide
  activeSection.value = 'sign-simple';
  console.log('Section activeSection définie à:', activeSection.value);
  
  // Réinitialiser le flag après un délai
  setTimeout(() => {
    isProcessingChoice.value = false;
  }, 1000);
}



// Fonctions utilitaires pour les templates (reprises du CollaboratorDashboard)
function getQrSizeLabel(size) {
  const sizeLabels = {
    small: 'Petit',
    medium: 'Moyen',
    large: 'Grand'
  };
  return sizeLabels[size] || 'Moyen';
}

async function previewTemplate(template) {
  try {
    console.log('🔍 [DEBUG] Ouverture de l\'aperçu pour template:', template);
    selectedTemplate.value = template;
    showPreviewModal.value = true;
    loadingPreview.value = true;
    
    // Vérifier d'abord si le template a un preview_document
    if (!template.preview_document) {
      console.warn('Template sans aperçu:', template);
      previewUrl.value = null;
      return;
    }
    
    // Utiliser directement l'URL de l'endpoint preview_document avec cache-busting
    const previewUrlValue = TemplateService.getPreviewUrl(template.id);
    console.log('🔍 [DEBUG] URL d\'aperçu générée:', previewUrlValue);
    
    // Forcer le rechargement en réinitialisant d'abord l'URL
    previewUrl.value = null;
    
    // Puis définir la nouvelle URL après un petit délai
    setTimeout(() => {
      previewUrl.value = previewUrlValue;
      console.log('✅ [DEBUG] URL d\'aperçu définie:', previewUrl.value);
    }, 100);
    
  } catch (error) {
    console.error('Erreur lors du chargement de l\'aperçu:', error);
    previewUrl.value = null;
    
    // Afficher un message d'erreur plus informatif
    if (error.response?.status === 404) {
      console.warn('Aperçu non disponible pour ce template');
    }
  } finally {
    loadingPreview.value = false;
  }
}

// Fonction pour fermer la modal d'aperçu
function closePreviewModal() {
  showPreviewModal.value = false;
  
  // Nettoyer l'URL pour libérer la mémoire
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = null;
  }
  
  selectedTemplate.value = null;
}

// Fonction pour éditer un template
async function editTemplate(template) {
  try {
    loadingEditFile.value = true;
    selectedTemplate.value = template;
    
    console.log("🔍 [DEBUG] Édition du template:", template);
    console.log("🔍 [DEBUG] Template ID:", template.id);
    
    // Récupérer les détails complets du template depuis l'API
    const templateDetails = await TemplateService.getTemplate(template.id);
    console.log("🔍 [DEBUG] Détails du template depuis l'API:", templateDetails);
    console.log("🔍 [DEBUG] QR Positions:", templateDetails.qr_positions);
    console.log("🔍 [DEBUG] Signature Positions:", templateDetails.signature_positions);
    console.log("🔍 [DEBUG] Page Application:", templateDetails.page_application);
    console.log("🔍 [DEBUG] Selected Pages:", templateDetails.selected_pages);
    console.log("🔍 [DEBUG] Signature Size:", templateDetails.signature_size);
    console.log("🔍 [DEBUG] Has Signature Image:", !!templateDetails.signature_image);
    
    // Récupérer le fichier PDF original pour l'afficher dans QrPositioner
    let originalPdfBlob = null;
    try {
      originalPdfBlob = await TemplateService.downloadOriginal(template.id);
    } catch (pdfError) {
      console.error('Erreur lors du téléchargement du PDF original:', pdfError);
    }
    
    // Créer un File à partir du Blob si disponible
    let originalFile = null;
    if (originalPdfBlob) {
      originalFile = new File([originalPdfBlob], `${templateDetails.name}.pdf`, { 
        type: 'application/pdf' 
      });
    }
    
    // Préparer les données pour l'édition
    editingTemplate.value = {
      id: templateDetails.id,
      name: templateDetails.name,
      file: originalFile,
      qrPositions: {
        qr: {
          size: templateDetails.qr_size,
          positions: templateDetails.qr_positions,
          pages: templateDetails.selected_pages && templateDetails.selected_pages.length > 0 ? 
                 templateDetails.selected_pages : 'all'
        },
        mode: templateDetails.page_application,
        signature: templateDetails.signature_positions ? {
          positions: templateDetails.signature_positions,
          size: templateDetails.signature_size || 50
        } : null,
        orientation: {
          mode: templateDetails.orientation_mode || 'auto',
          effective: templateDetails.orientation_data?.effective || 'portrait',
          previewWidth: templateDetails.orientation_data?.previewWidth || 595,
          previewHeight: templateDetails.orientation_data?.previewHeight || 842
        }
      },
      signatureImage: null,
      generatedPdfFile: null,
      generatedPdfBlob: null,
      generatedPdfDataUrl: null
    };
    
    console.log("🔍 [DEBUG] Structure des données préparée pour QrPositioner:", editingTemplate.value.qrPositions);
    // Télécharger l'image de signature si disponible
    if (templateDetails.signature_image) {
      try {
        const imgResponse = await fetch(templateDetails.signature_image);
        if (imgResponse.ok) {
          const imgBlob = await imgResponse.blob();
          const imgExtension = (imgBlob.type && imgBlob.type.split('/')[1]) ? imgBlob.type.split('/')[1].replace('jpeg', 'jpg') : 'png';
          const imgFile = new File([imgBlob], `signature_image.${imgExtension}`, { type: imgBlob.type || 'image/png' });
          editingTemplate.value.signatureImage = imgFile;
          // Ajouter la référence de l'image dans les positions préchargées
          if (editingTemplate.value.qrPositions.signature) {
            editingTemplate.value.qrPositions.signature.image = URL.createObjectURL(imgFile);
          }
        }
      } catch (imgError) {
        console.warn('Impossible de télécharger l\'image de signature:', imgError);
      }
    }
    
    // Ouvrir la section d'édition
    activeSection.value = 'edit-template';
  } catch (error) {
    console.error('Erreur lors de la récupération des détails du template:', error);
    alert('Une erreur est survenue lors de la récupération des détails du template.');
  } finally {
    loadingEditFile.value = false;
  }
}

// Fonction pour fermer la modal d'édition
function closeEditModal() {
  activeSection.value = '';
  showEditModal.value = false;
  editingTemplate.value = {
    id: null,
    name: '',
    file: null,
    qrPositions: null,
    signatureImage: null,
    generatedPdfFile: null,
    generatedPdfBlob: null,
    generatedPdfDataUrl: null
  };
  selectedTemplate.value = null;
}

// Fonctions pour gérer les événements du QrPositioner en mode édition
function handleEditPositionConfirmed(positionData) {
  editingTemplate.value.qrPositions = positionData;
}

function handleEditSignatureUploaded(file) {
  console.log('Signature uploadée pour édition:', file.name);
  editingTemplate.value.signatureImage = file;
}

function handleEditPdfGenerated(pdfData) {
  console.log('PDF généré pour édition:', pdfData.file.name);
  editingTemplate.value.generatedPdfBlob = pdfData.blob;
  editingTemplate.value.generatedPdfFile = pdfData.file;
  editingTemplate.value.generatedPdfDataUrl = pdfData.dataUrl;
}

// Fonction pour mettre à jour un template
async function updateTemplate() {
  if (!canUpdateTemplate.value) return;
  
  try {
    isUpdating.value = true;
    
    // Vérifier si nous avons un PDF généré
    if (!editingTemplate.value.generatedPdfFile) {
      alert('Veuillez d\'abord générer un aperçu du document et confirmer.');
      return;
    }
    
    // Préparer les données pour l'API
    const templateData = {
      name: editingTemplate.value.name,
      qr_size: editingTemplate.value.qrPositions.qr.size,
      page_application: editingTemplate.value.qrPositions.mode,
      qr_positions: editingTemplate.value.qrPositions.qr.positions,
      signature_positions: editingTemplate.value.qrPositions.signature ? 
                          editingTemplate.value.qrPositions.signature.positions : null,
      signature_size: editingTemplate.value.qrPositions.signature ? 
                     editingTemplate.value.qrPositions.signature.size : 50,
      selected_pages: editingTemplate.value.qrPositions.qr.pages !== 'all' ? 
                     editingTemplate.value.qrPositions.qr.pages : []
    };
    
    // Ajouter les fichiers si disponibles
    if (editingTemplate.value.file) {
      templateData.original_document = editingTemplate.value.file;
    }
    
    if (editingTemplate.value.signatureImage) {
      templateData.signature_image = editingTemplate.value.signatureImage;
    }
    
    if (editingTemplate.value.generatedPdfFile) {
      templateData.preview_document = editingTemplate.value.generatedPdfFile;
    }
    
    // Mettre à jour le template via l'API
    await TemplateService.updateTemplate(editingTemplate.value.id, templateData);
    
    // Récupérer le template complet mis à jour depuis l'API pour avoir le nouveau preview_document
    const updatedTemplate = await TemplateService.getTemplate(editingTemplate.value.id);
    console.log('✅ [DEBUG] Template mis à jour récupéré:', updatedTemplate);
    
    // Mettre à jour le template dans la liste locale avec toutes les nouvelles données
    const index = myTemplates.value.findIndex(t => t.id === editingTemplate.value.id);
    if (index !== -1) {
      myTemplates.value[index] = {
        ...myTemplates.value[index],
        name: updatedTemplate.name,
        qrSize: updatedTemplate.qr_size,
        pageApplication: updatedTemplate.page_application,
        hasSignature: !!updatedTemplate.signature_image,
        preview_document: updatedTemplate.preview_document // ← Nouveau aperçu mis à jour
      };
      console.log('✅ [DEBUG] Template mis à jour dans la liste locale:', myTemplates.value[index]);
    }
    
    // Afficher un message de succès
    alert('Template mis à jour avec succès !');
    
    // Fermer la modale
    closeEditModal();
  } catch (error) {
    if (error.response && error.response.data) {
      console.error('Détails du backend:', error.response.data);
      alert(`Erreur du serveur : ${JSON.stringify(error.response.data)}`);
    } else {
      console.error('Erreur lors de la mise à jour du template:', error);
      alert('Une erreur est survenue lors de la mise à jour du template.');
    }
  } finally {
    isUpdating.value = false;
  }
}

function useTemplate(template) {
  console.log('Utilisation du template:', template.name);
  // Stocker l'ID du template dans le localStorage pour pré-sélection ultérieure
  try {
    localStorage.setItem('selectedTemplateId', template.id);
  } catch (e) {
    console.warn('Impossible de sauvegarder le template sélectionné dans le localStorage', e);
  }
  // Ouvrir directement la section de signature avec template
  activeSection.value = 'sign-with-template';
}

function confirmDeleteTemplate(template) {
  console.log('Confirmation de suppression du template:', template.name);
  if (confirm(`Êtes-vous sûr de vouloir supprimer le template "${template.name}" ?`)) {
    deleteTemplate(template);
  }
}

async function deleteTemplate(template) {
  try {
    await TemplateService.deleteTemplate(template.id);
    
    // Supprimer le template de la liste locale
    myTemplates.value = myTemplates.value.filter(t => t.id !== template.id);
    
    console.log('Template supprimé avec succès');
    alert('Template supprimé avec succès !');
  } catch (error) {
    console.error('Erreur lors de la suppression du template:', error);
    alert('Une erreur est survenue lors de la suppression du template.');
  }
}

</script>

<style scoped>
/* Styles généraux */
.signer-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, 
    var(--bg-color, #f8f9fa) 0%, 
    rgba(255, 149, 0, 0.05) 50%, 
    var(--bg-color, #f8f9fa) 100%);
  color: var(--text-color, #333);
  position: relative;
}

/* Animation de particules */
.particles-container {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 30s infinite linear;
  background: #ff9500;
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.15;
  }
  90% {
    opacity: 0.15;
  }
  100% {
    transform: translateY(-100vh) translateX(30px) rotate(360deg);
    opacity: 0;
  }
}

/* En-tête */
.dashboard-header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 149, 0, 0.2);
  padding: 1.25rem 2.5rem;
  position: relative; /* le header défile maintenant avec la page */
  top: auto;
  z-index: initial;
  box-shadow: 0 2px 15px rgba(255, 149, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  padding-right: 0;
  margin-right: 2rem;
}

.logo-icon-text {
  display: flex;
  align-items: center;
}

.header-logo-img {
  width: 40px;
  height: auto;
  margin-right: 10px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  font-family: "Motoya Maru Std-w6", Arial, sans-serif;
}

.text-green {
  color: #00a651; /* Vert */
}

.text-red {
  color: #e74c3c; /* Rouge */
}

.text-yellow {
  color: #f1c40f; /* Jaune */
}

.logo-container:hover .logo-icon {
  transform: rotate(-10deg);
}

.role-badge.signer.top-right-of-logo {
  position: relative;
  top: 0;
  right: 0;
  font-size: 0.8rem;
  padding: 0.25rem 0.55rem;
  line-height: 1.1;
  border-radius: 0.75rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(45deg, #ff9500, #ffb347);
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  text-transform: uppercase;
  margin-left: 0.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transform: translateX(-40px);
}

.organization-info {
  display: flex;
  align-items: center;
}

.org-name-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  padding-right: 0;
}

.org-name {
  font-weight: 700;
  color: #ff9500;
  font-size: 1.9rem;
  line-height: 1.2;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.05);
  background: linear-gradient(45deg, #ff9500, #ffb347);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.status-badge.org-status.top-right-of-org-name {
  position: relative;
  top: 0;
  right: 0;
  transform: none;
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 0.75rem;
  font-weight: 700;
  line-height: 1.1;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  text-transform: uppercase;
  margin-left: 0.5rem;
}

.status-badge.org-status {
  font-size: 0.65rem;
  padding: 0.2rem 0.55rem;
  border-radius: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  line-height: 1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.status-badge.org-status-active {
  background: linear-gradient(45deg, #28a745, #5bc85a);
  color: white;
}

.status-badge.org-status-pending {
  background: linear-gradient(45deg, #ffc107, #ffd04e);
  color: #333;
}

.status-badge.org-status-inactive, 
.status-badge.org-status-suspended {
  background: linear-gradient(45deg, #6c757d, #9a9fa3);
  color: white;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
}

.user-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #4A4A4A;
  padding: 0.4rem 0.8rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 1.5rem;
  box-shadow: 0 2px 10px rgba(255, 149, 0, 0.12);
  border: 1px solid rgba(255, 149, 0, 0.15);
  backdrop-filter: blur(4px);
  position: relative;
  padding-left: 2rem;
  transition: all 0.3s ease;
}

.user-name::before {
  content: "\F4DA";
  font-family: "bootstrap-icons";
  position: absolute;
  left: 0.7rem;
  font-size: 0.9rem;
  color: #ff9500;
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 149, 0, 0.2);
}

.logout-btn {
  background: transparent;
  border: 2px solid #ff9500;
  color: #ff9500;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #ff9500;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(255, 149, 0, 0.3);
}

/* Popup de signature */
.signature-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.signature-modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(3px);
}

.signature-modal-content {
  position: relative;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalAppear 0.3s ease-out;
  border: 1px solid rgba(255, 149, 0, 0.2);
}

@keyframes modalAppear {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.signature-modal-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #ff9500, #ffb347);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.signature-modal-header h3 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.signature-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: calc(85vh - 150px);
}

.document-preview {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  border: 1px dashed rgba(0, 0, 0, 0.1);
}

.document-name {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: #333;
}

.document-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.document-info i {
  color: #ff9500;
  font-size: 1.5rem;
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-title {
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.1rem;
  border-bottom: 2px solid rgba(255, 149, 0, 0.1);
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-group small {
  display: block;
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.8rem;
}

.dropzone {
  border: 2px dashed #ddd;
  border-radius: 0.5rem;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 120px;
  background-color: rgba(255, 255, 255, 0.5);
}

.dropzone.active {
  border-color: #ff9500;
  background-color: rgba(255, 149, 0, 0.05);
  transform: scale(1.02);
}

.dropzone.has-file {
  border-color: #28a745;
  background-color: rgba(40, 167, 69, 0.05);
}

.dropzone-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.dropzone-placeholder i {
  font-size: 2.5rem;
  color: #aaa;
}

.dropzone-text {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.main-text {
  font-weight: 600;
  color: #555;
}

.sub-text {
  font-size: 0.9rem;
  color: #888;
}

.dropzone-file {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.dropzone-file i {
  font-size: 2rem;
  color: #28a745;
}

.file-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.file-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #333;
  word-break: break-all;
}

.file-size {
  font-size: 0.8rem;
  color: #6c757d;
}

.remove-file {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-file:hover {
  background-color: rgba(220, 53, 69, 0.1);
  transform: scale(1.1);
}

.hidden-input {
  display: none;
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-container input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #777;
  cursor: pointer;
}

.signature-modal-footer {
  padding: 1.25rem 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.signature-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.signature-status.error {
  color: #dc3545;
}

.signature-status.success {
  color: #28a745;
}

.signature-status.pending {
  color: #6c757d;
}

.button-group {
  display: flex;
  gap: 1rem;
}

.btn-cancel {
  background: none;
  border: 1px solid #ddd;
  color: #555;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: #f0f0f0;
}

.btn-sign {
  background: linear-gradient(45deg, #ff9500, #ffb347);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-sign:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 149, 0, 0.3);
}

.btn-sign:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background: linear-gradient(45deg, #ccc, #ddd);
}

/* Contenu principal */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

/* Section de bienvenue */
.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--text-color, #333);
}

.underlined-text {
  position: relative;
  display: inline-block;
}

.underlined-text::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -10px;
  height: 4px;
  width: 100%;
  background: linear-gradient(90deg, #ff9500, #ffb347, #ff9500);
  background-size: 200% 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(255, 149, 0, 0.3);
  animation: gradientMove 3s ease infinite;
}

@keyframes gradientMove {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.highlight-text {
  background: linear-gradient(45deg, #ff9500, #ffb347);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-description {
  font-size: 1.1rem;
  color: var(--text-muted, #6c757d);
  max-width: 600px;
  margin: 0 auto;
}

/* Actions rapides */
.quick-actions {
  margin-bottom: 3rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid transparent;
  border-radius: 1rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  position: relative;
  /* Ombre identique à CollaboratorDashboard */
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.action-card:hover, .action-card.active {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.action-card.urgent {
  border-color: #dc3545;
  background: rgba(220, 53, 69, 0.05);
}

.action-card.urgent:hover {
  border-color: #dc3545;
  box-shadow: 0 10px 30px rgba(220, 53, 69, 0.2);
}

/* Hover/accent comme CollaboratorDashboard */
.action-card:not(.urgent):hover, .action-card.active {
  border-color: var(--accent-color, #ff9500);
  box-shadow: 0 10px 30px rgba(255, 149, 0, 0.15);
}

.action-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

/* Style par défaut (accent) comme dans CollaboratorDashboard */
.action-card .action-icon {
  background: rgba(6, 255, 165, 0.1);
  color: var(--accent-color, #06ffa5);
}

.action-card.urgent .action-icon {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.action-icon.warning {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.action-icon.success {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.action-icon.primary {
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
}

.action-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color, #333);
}

.action-description {
  font-size: 0.875rem;
  color: var(--text-muted, #6c757d);
}

.notification-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #dc3545;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  min-width: 1.5rem;
  text-align: center;
}

/* Statistiques */
.stats-section {
  margin-bottom: 3rem;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6c757d);
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

/* Même palette que CollaboratorDashboard */
.stat-icon.success {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.stat-icon.primary {
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
}

.stat-icon.warning {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

/* Section de contenu */
.content-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 1.25rem;
  padding: 2.5rem;
  box-shadow: 0 10px 30px rgba(255, 149, 0, 0.1);
  border: 1px solid rgba(255, 149, 0, 0.08);
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.content-title {
  font-size: 1.35rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 149, 0, 0.1);
  position: relative;
}

.content-title i {
  color: #ff9500;
  font-size: 1.5rem;
}

.content-title::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #ff9500, #ffb347, #ff9500);
  border-radius: 3px;
}

/* Listes de documents */
.documents-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.document-item {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.document-item.urgent {
  border-left: 4px solid #dc3545;
  background: rgba(220, 53, 69, 0.02);
}

.document-item:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 149, 0, 0.08);
  border-color: rgba(255, 149, 0, 0.12);
}

.document-item.urgent:hover {
  box-shadow: 0 8px 25px rgba(220, 53, 69, 0.1);
  border-color: #dc3545;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex: 1;
}

.doc-info i {
  font-size: 1.75rem;
  color: #ff9500;
  background: rgba(255, 149, 0, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.document-item:hover .doc-info i {
  background: #ff9500;
  color: white;
  transform: scale(1.05);
}

.document-item.urgent .doc-info i {
  color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
}

.document-item.urgent:hover .doc-info i {
  background: #dc3545;
  color: white;
}

.doc-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.doc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.doc-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-color, #333);
}

.urgent-tag {
  background: #dc3545;
  color: white;
  font-size: 0.625rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  text-transform: uppercase;
}

.doc-meta {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.doc-priority {
  margin-top: 0.25rem;
}

.time-elapsed {
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
  padding: 0.2rem 0.6rem;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 1rem;
}

.time-elapsed.urgent {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  font-weight: 500;
}

.signature-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #28a745;
  background: rgba(40, 167, 69, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  margin-top: 0.25rem;
  display: inline-flex;
}

.signer-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #ff9500;
  background: rgba(255, 149, 0, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  margin-top: 0.25rem;
  display: inline-flex;
}

.doc-status {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-badge {
  padding: 0.35rem 0.85rem;
  border-radius: 2rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.signed {
  background: rgba(40, 167, 69, 0.15);
  color: #155724;
}

.doc-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.btn-primary {
  background: linear-gradient(45deg, #ff9500, #ffb347);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 149, 0, 0.3);
}

.btn-icon {
  background: none;
  border: 1.5px solid #ff9500;
  color: #ff9500;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.btn-icon:hover {
  background: #ff9500;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 149, 0, 0.2);
}



/* État vide */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  border: 1px dashed rgba(255, 149, 0, 0.2);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: rgba(255, 149, 0, 0.3);
}

.empty-state p {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-color, #333);
}

.empty-subtitle {
  font-size: 0.95rem;
  opacity: 0.8;
}

/* Contenu par défaut */
.default-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.welcome-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.welcome-card .btn-primary {
  margin: 0 auto;
  display: inline-flex;
}

.welcome-icon {
  width: 5rem;
  height: 5rem;
  border-radius: 1rem;
  background: linear-gradient(45deg, #ff9500, #ffb347);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  margin: 0 auto 1.5rem;
}

.welcome-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 1rem;
}

.welcome-card p {
  color: var(--text-muted, #6c757d);
  margin-bottom: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    padding: 1rem 1.5rem;
  }
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  .logo-icon {
    font-size: 2rem;
  }
  .logo-text {
    font-size: 1.3rem;
  }
  .main-content {
    padding: 1rem;
  }
  .welcome-title {
    font-size: 2rem;
  }
  .actions-grid {
    grid-template-columns: 1fr;
  }
  .stats-container {
    grid-template-columns: 1fr;
  }
  .document-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .doc-actions {
    width: 100%;
    justify-content: flex-end;
  }
  .signature-modal-content {
    width: 95%;
  }
  .button-group {
    flex-direction: column;
    width: 100%;
  }
  .signature-modal-footer {
    flex-direction: column;
    gap: 1rem;
  }
  .signature-status {
    width: 100%;
    justify-content: center;
  }
}

/* Onglets documents à signer */
.pending-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.pending-tabs .tab-btn {
  background: rgba(255, 149, 0, 0.1);
  border: 1px solid rgba(255, 149, 0, 0.3);
  padding: 0.4rem 1rem;
  border-radius: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-color, #333);
}
.pending-tabs .tab-btn.active,
.pending-tabs .tab-btn:hover {
  background: #ff9500;
  color: #fff;
}

/* Cartes template en attente */
.template-cards-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.template-card-pending {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 149, 0, 0.2);
  border-radius: 1rem;
  padding: 1rem;
  width: 260px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(255, 149, 0, 0.05);
}
.template-card-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-color, #333);
}
.template-card-count {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.75rem;
}
.template-card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

/* Header documents template */
.template-docs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.template-docs-title {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(45deg, #ff9500, #ffb347);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-transform: capitalize;
}

.btn-secondary {
  background: none;
  border: 1.5px solid #ff9500;
  color: #ff9500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.btn-secondary:hover {
  background: #ff9500;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 149, 0, 0.25);
}

/* Styles pour la pagination et recherche */
.search-container {
  position: relative;
  margin-bottom: 1.5rem;
}

.search-input {
  padding: 10px 15px 10px 40px;
  border-radius: 25px;
  border: 1px solid var(--border-color, #ddd);
  background-color: var(--input-bg, white);
  color: var(--text-color, #333);
  min-width: 100%;
  transition: all 0.3s ease;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #ff9500;
  box-shadow: 0 0 0 2px rgba(255, 149, 0, 0.2);
}

.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary, #6c757d);
}

/* Styles pour la pagination */
.pagination-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
  padding: 30px;
  background-color: var(--card-bg, white);
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.pagination-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  text-align: center;
  color: var(--text-color, #333);
}

.pagination-info span:first-child {
  font-weight: 600;
  font-size: 16px;
}

.documents-count {
  font-size: 14px;
  color: var(--text-secondary, #6c757d);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 15px;
  border: 1px solid var(--border-color, #ddd);
  background-color: var(--card-bg, white);
  color: var(--text-color, #333);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  min-width: 44px;
  min-height: 44px;
  text-decoration: none;
  gap: 6px;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #ff9500;
  color: white;
  border-color: #ff9500;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 149, 0, 0.3);
}

.pagination-btn.active {
  background-color: #ff9500;
  color: white;
  border-color: #ff9500;
  font-weight: 600;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--light-bg, #f8f9fa);
  color: var(--text-secondary, #6c757d);
}

.pagination-btn:disabled:hover {
  transform: none;
  box-shadow: none;
  background-color: var(--light-bg, #f8f9fa);
  color: var(--text-secondary, #6c757d);
  border-color: var(--border-color, #ddd);
}

.pagination-btn.prev,
.pagination-btn.next {
  padding: 10px 20px;
  font-weight: 600;
}

.pagination-btn.page {
  width: 44px;
  height: 44px;
  padding: 0;
  border-radius: 50%;
}

.pagination-dots {
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: var(--text-secondary, #6c757d);
  font-weight: bold;
  font-size: 16px;
}

/* Responsive pour la pagination */
@media (max-width: 768px) {
  .pagination-container {
    margin-top: 30px;
    padding: 20px;
  }
  
  .pagination-controls {
    gap: 4px;
  }
  
  .pagination-btn {
    min-width: 40px;
    min-height: 40px;
    padding: 8px 12px;
    font-size: 13px;
  }
  
  .pagination-btn.page {
    width: 40px;
    height: 40px;
  }
  
  .pagination-btn.prev,
  .pagination-btn.next {
    padding: 8px 16px;
  }
  
  .search-input {
    min-width: 250px;
  }
}

@media (max-width: 480px) {
  .pagination-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
  }
  
  .search-input {
    min-width: 200px;
  }
}

/* Ajout cohésion SignSimpleSigner */
.sign-section {
  background: transparent;
  padding: 0;
  animation: fadeIn 0.5s ease-out;
}

.sign-section :deep(.sign-document-container) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* === STYLES POUR LES TEMPLATES === */

/* Section header avec bouton - comme CollaboratorDashboard */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

/* État de chargement */
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 149, 0, 0.2);
  border-radius: 50%;
  border-top-color: #ff9500;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-description {
  display: block;
  font-size: 0.95rem;
  opacity: 0.8;
  margin: 1rem 0 1.5rem;
}

/* Grille des templates */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 149, 0, 0.1);
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.template-card:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 149, 0, 0.15);
  border-color: rgba(255, 149, 0, 0.2);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.template-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(45deg, #ff9500, #ffb347);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.template-status {
  display: flex;
  align-items: center;
}

.template-badge {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  text-transform: uppercase;
}

.template-content {
  margin-bottom: 1.5rem;
}

.template-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 1rem;
  word-break: break-word;
}

.template-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted, #6c757d);
}

.meta-item i {
  color: #ff9500;
  width: 16px;
  text-align: center;
}

.template-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Boutons d'action template */
.template-actions .btn-icon {
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  width: 36px;
  height: 36px;
}

.template-actions .btn-icon.primary {
  background: rgba(58, 134, 255, 0.1);
  border-color: rgba(58, 134, 255, 0.15);
  color: var(--primary-color, #3a86ff);
}

.template-actions .btn-icon.primary:hover {
  background: var(--primary-color, #3a86ff);
  color: white;
}

.template-actions .btn-icon.success {
  background: rgba(40, 167, 69, 0.1);
  border-color: rgba(40, 167, 69, 0.15);
  color: #28a745;
}

.template-actions .btn-icon.success:hover {
  background: #28a745;
  color: white;
}

.template-actions .btn-icon.danger {
  background: rgba(220, 53, 69, 0.1);
  border-color: rgba(220, 53, 69, 0.15);
  color: #dc3545;
}

.template-actions .btn-icon.danger:hover {
  background: #dc3545;
  color: white;
}

/* === STYLES POUR LA MODALE DE SIGNATURE (inspiré de CollaboratorDashboard) === */

/* Modal overlay - Positionnement correct comme CollaboratorDashboard */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(33, 37, 41, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Modal de choix - Couleurs orange du SignerDashboard */
.choice-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(255, 149, 0, 0.15);
  border: 1px solid rgba(255, 149, 0, 0.1);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  overflow: hidden;
  position: relative;
}

.choice-modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #ff9500, #ffb347, #ff9500);
  background-size: 200% 100%;
  border-radius: 20px 20px 0 0;
  animation: gradientMove 3s ease infinite;
}

@keyframes gradientMove {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.choice-modal .modal-header {
  background: linear-gradient(135deg, #ff9500, #ffb347);
  color: white;
  padding: 1.25rem 2rem;
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.choice-modal .header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.choice-modal .modal-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  animation: pulse 2s infinite;
  flex-shrink: 0;
}

.choice-modal .modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.choice-modal .modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.choice-modal .modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.choice-modal .modal-body {
  padding: 2.5rem;
}

.choice-description {
  text-align: center;
  font-size: 1.1rem;
  color: var(--text-muted, #6c757d);
  margin-bottom: 2rem;
}

.choice-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.choice-option {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(255, 149, 0, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  text-align: left;
  position: relative;
  overflow: hidden;
}

.choice-option:hover {
  background: rgba(255, 255, 255, 1);
  border-color: #ff9500;
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(255, 149, 0, 0.2);
}

.choice-option .option-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  transition: all 0.3s ease;
}

.choice-option .option-icon.template {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.choice-option .option-icon.direct {
  background: rgba(58, 134, 255, 0.1);
  color: #3a86ff;
}

.choice-option:hover .option-icon {
  transform: scale(1.1) rotate(5deg);
}

.choice-option .option-content {
  flex: 1;
}

.choice-option .option-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin: 0 0 0.5rem 0;
}

.choice-option .option-description {
  font-size: 0.95rem;
  color: var(--text-muted, #6c757d);
  margin: 0;
}

.choice-option .option-arrow {
  font-size: 1.5rem;
  color: var(--text-muted, #6c757d);
  opacity: 0.5;
  transition: all 0.3s ease;
}

.choice-option:hover .option-arrow {
  opacity: 1;
  color: #ff9500;
  transform: translateX(5px);
}

/* Animation pour la modale */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Mode sombre */
:global(.dark-theme) .choice-modal {
  background: rgba(30, 41, 59, 0.95);
  border-color: rgba(255, 149, 0, 0.1);
}

:global(.dark-theme) .choice-option {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(255, 149, 0, 0.2);
}

:global(.dark-theme) .choice-option:hover {
  background: rgba(15, 23, 42, 1);
  border-color: #ff9500;
}

/* Responsive */
@media (max-width: 768px) {
  .choice-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .choice-modal .modal-header {
    padding: 1.5rem;
  }
  
  .choice-modal .modal-icon {
    width: 60px;
    height: 60px;
    font-size: 2rem;
  }
  
  .choice-modal .modal-title {
    font-size: 1.5rem;
  }
  
  .choice-modal .modal-body {
    padding: 1.5rem;
  }
  
  .choice-option {
    padding: 1rem;
  }
  
  .choice-option .option-icon {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
}

/* Section de création de template */
.create-template-section {
  background: transparent;
  padding: 0;
  box-shadow: none;
  border: none;
  overflow: visible;
  max-height: none;
}

.create-template-section :deep(.create-template-container) {
  max-height: none !important;
  overflow: visible !important;
}

.create-template-section :deep(.section-card) {
  max-height: none !important;
  overflow: visible !important;
}

/* Section de signature avec template */
.sign-with-template-section {
  background: transparent;
  padding: 0;
  box-shadow: none;
  border: none;
  overflow: visible;
  max-height: none;
}

.sign-with-template-section :deep(.sign-document-container) {
  max-height: none !important;
  overflow: visible !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* Responsive pour les templates et la modale */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .template-card {
    padding: 1.25rem;
  }
  
  .template-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  /* Modale responsive */
  .choice-modal .modal-header {
    padding: 1rem 1.5rem;
  }
  
  .choice-modal .modal-icon {
    width: 35px;
    height: 35px;
    font-size: 16px;
  }
  
  .choice-modal .modal-title {
    font-size: 1.1rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
      }
  }
/* 🆕 STYLES POUR LA MODAL D'ÉDITION DE TEMPLATE */

.edit-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  max-width: 90vw;
  max-height: 90vh;
  width: 800px;
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.edit-modal .modal-header {
  background: linear-gradient(135deg, #ff9500 0%, #ff6b35 100%);
  color: white;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-modal .modal-title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.edit-modal .modal-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.edit-modal .modal-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
}

.edit-modal .modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 35px;
  height: 35px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-modal .modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.edit-modal .modal-body {
  padding: 2rem;
  max-height: 60vh;
  overflow-y: auto;
}

.edit-modal .template-form {
  margin-bottom: 2rem;
}

.edit-modal .form-group {
  margin-bottom: 1.5rem;
}

.edit-modal .form-group label {
  display: block;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.edit-modal .form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(229, 231, 235, 0.6);
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
}

.edit-modal .form-control:focus {
  outline: none;
  border-color: #ff9500;
  box-shadow: 0 0 0 3px rgba(255, 149, 0, 0.1);
}

.edit-modal .qr-positioner-wrapper {
  border: 2px solid rgba(229, 231, 235, 0.6);
  border-radius: 12px;
  overflow: hidden;
}

.edit-modal .loading-edit-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-color);
}

.edit-modal .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 149, 0, 0.2);
  border-top: 4px solid #ff9500;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.edit-modal .edit-file-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #dc3545;
  text-align: center;
}

.edit-modal .edit-file-error i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.edit-modal .modal-footer {
  background: rgba(248, 249, 250, 0.8);
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid rgba(229, 231, 235, 0.6);
}

.edit-modal .btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-size: 1rem;
}

.edit-modal .btn-secondary {
  background: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.edit-modal .btn-secondary:hover {
  background: rgba(108, 117, 125, 0.2);
}

.edit-modal .btn-primary {
  background: linear-gradient(135deg, #ff9500 0%, #ff6b35 100%);
  color: white;
}

.edit-modal .btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(255, 149, 0, 0.3);
}

.edit-modal .btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.edit-modal .spin {
  animation: spin 1s linear infinite;
}

/* Responsive pour la modal d'édition */
@media (max-width: 768px) {
  .edit-modal {
    width: 95vw;
    max-height: 95vh;
  }
  
  .edit-modal .modal-header {
    padding: 1rem 1.5rem;
  }
  
  .edit-modal .modal-icon {
    width: 35px;
    height: 35px;
    font-size: 1rem;
  }
  
  .edit-modal .modal-title {
    font-size: 1.1rem;
  }
  
  .edit-modal .modal-body {
    padding: 1.5rem;
  }
  
  .edit-modal .modal-footer {
    padding: 1rem 1.5rem;
    flex-direction: column;
  }
  
  .edit-modal .btn {
    width: 100%;
  }
}

/* 🆕 STYLES POUR SIGNATURES ÉPHÉMÈRES DANS LA MODAL */

/* Section type de signature */
.signature-type-section {
  margin-bottom: 25px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 15px;
}

.signature-type-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.signature-type-option {
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(229, 231, 235, 0.6);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  backdrop-filter: blur(10px);
}

.signature-type-option:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.6);
}

.signature-type-option.selected {
  border-color: rgba(34, 197, 94, 0.8);
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(255, 255, 255, 0.9) 100%);
  box-shadow: 0 5px 15px rgba(34, 197, 94, 0.2);
}

.type-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.type-icon.permanent {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.type-icon.ephemeral {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.signature-type-option:hover .type-icon {
  transform: scale(1.05);
}

.type-content h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 5px 0;
  color: var(--text-color);
}

.type-content p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.9rem;
}

.type-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 3px;
}

/* Section configuration expiration */
.expiration-section {
  margin-bottom: 25px;
  padding: 20px;
  background: rgba(58, 134, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(58, 134, 255, 0.2);
}

.duration-presets {
  margin-bottom: 20px;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.preset-btn {
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-height: 90px;
}

.preset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.preset-btn.active {
  background: rgba(58, 134, 255, 0.1);
  border-color: var(--primary-color);
}

.preset-btn.custom {
  border-style: dashed;
}

.preset-icon {
  width: 35px;
  height: 35px;
  border-radius: 8px;
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  margin-bottom: 3px;
}

.preset-btn.custom .preset-icon {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.preset-label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.85rem;
}

.preset-desc {
  font-size: 0.7rem;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.2;
}

/* Sélecteur de date personnalisée */
.custom-date-selector {
  background: var(--bg-light);
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
}

.custom-date-selector label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.9rem;
}

.date-input {
  width: 100%;
  padding: 10px;
  border: 2px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.date-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(58, 134, 255, 0.1);
}

.custom-date-selector small {
  display: block;
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* Résumé de l'expiration */
.expiration-summary {
  background: rgba(58, 134, 255, 0.1);
  border: 1px solid rgba(58, 134, 255, 0.3);
  border-radius: 8px;
  padding: 12px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
}

.expiration-summary i {
  color: var(--primary-color);
  font-size: 1.1rem;
}

.expiration-summary span {
  color: var(--text-color);
  font-size: 0.9rem;
}

.expiration-summary strong {
  color: var(--primary-color);
  font-weight: 600;
}

/* =======================
   Styles – Section Édition de Template
   ======================= */
.edit-template-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
  position: relative;
}

.edit-template-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.edit-template-header .header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.edit-template-header .modal-icon {
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.edit-template-header .modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 1.35rem;
  color: var(--text-muted, #6c757d);
  cursor: pointer;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: var(--text-color, #333);
}

.edit-template-body {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.template-form .form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.template-form label {
  font-weight: 500;
}

.template-form .form-control {
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
}

.qr-positioner-wrapper {
  border: 1px dashed #ced4da;
  border-radius: 12px;
  padding: 1rem;
  background: #f9fafb;
}

.loading-edit-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 0;
  color: var(--text-muted, #6c757d);
}

.loading-edit-file .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top-color: var(--primary-color, #3a86ff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.edit-file-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem 0;
  color: #dc3545;
}

.edit-template-footer {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.edit-template-footer .btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
}

.edit-template-footer .btn.btn-primary {
  background: var(--primary-color, #3a86ff);
  border: none;
  color: #fff;
}

.edit-template-footer .btn.btn-primary[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-template-footer .btn.btn-secondary {
  background: #e9ecef;
  border: none;
  color: var(--text-color, #333);
}

.edit-template-footer .btn.btn-secondary:hover {
  background: #dee2e6;
}

@media (max-width: 768px) {
  .edit-template-section {
    padding: 1.25rem;
  }
  .edit-template-body {
    gap: 1.25rem;
  }
}

/* =================================
   STYLES POUR LA MODALE D'APERÇU
   ================================= */

/* Modal d'aperçu - Identique au CollaboratorDashboard */
.preview-modal {
  background-color: var(--bg-light, #ffffff);
  border-radius: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 1000px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  border: 1px solid var(--border-color, #e0e0e0);
}

/* En-tête de la modale d'aperçu */
.preview-modal .modal-header {
  background: linear-gradient(135deg, #ff9500, #ffb347);
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.preview-modal .modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 15px;
}

.preview-modal .modal-header i {
  font-size: 1.5rem;
}

.preview-modal .modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 12px;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.preview-modal .modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* Corps de la modale d'aperçu */
.preview-body {
  padding: 0;
  position: relative;
  overflow: hidden;
  flex: 1;
  background: var(--bg-light, #ffffff);
}

/* Contenu d'aperçu */
.loading-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-secondary, #6c757d);
}

.loading-preview .spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 149, 0, 0.2);
  border-top: 4px solid #ff9500;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background-color: #fff;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
  color: var(--text-secondary, #6c757d);
  padding: 30px;
}

.preview-error i {
  font-size: 4rem;
  color: #ff9500;
  margin-bottom: 20px;
}

.preview-error p {
  font-size: 1.1rem;
  margin-bottom: 20px;
  line-height: 1.5;
}

.preview-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

/* Animation de slide-in pour la modale */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive pour la modale d'aperçu */
@media (max-width: 768px) {
  .preview-modal {
    width: 95%;
    height: 90vh;
  }
  
  .preview-modal .modal-header {
    padding: 20px;
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .preview-modal .modal-header h3 {
    flex-direction: column;
    gap: 10px;
  }
}

/* =================================
   STYLES POUR LA MODALE D'APERÇU
   ================================= */

/* Modal d'aperçu - Identique au CollaboratorDashboard */
.preview-modal {
  background-color: var(--bg-light, #ffffff);
  border-radius: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 1000px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  border: 1px solid var(--border-color, #e0e0e0);
}

/* En-tête de la modale d'aperçu */
.preview-modal .modal-header {
  background: linear-gradient(135deg, #ff9500, #ffb347);
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.preview-modal .modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 15px;
}

.preview-modal .modal-header i {
  font-size: 1.5rem;
}

.preview-modal .modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 12px;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.preview-modal .modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* Corps de la modale d'aperçu */
.preview-body {
  padding: 0;
  position: relative;
  overflow: hidden;
  flex: 1;
  background: var(--bg-light, #ffffff);
}

/* Contenu d'aperçu */
.loading-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-secondary, #6c757d);
}

.loading-preview .spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 149, 0, 0.2);
  border-top: 4px solid #ff9500;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background-color: #fff;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
  color: var(--text-secondary, #6c757d);
  padding: 30px;
}

.preview-error i {
  font-size: 4rem;
  color: #ff9500;
  margin-bottom: 20px;
}

.preview-error p {
  font-size: 1.1rem;
  margin-bottom: 20px;
  line-height: 1.5;
}

.preview-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

/* Animation de slide-in pour la modale */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive pour la modale d'aperçu */
@media (max-width: 768px) {
  .preview-modal {
    width: 95%;
    height: 90vh;
  }
  
  .preview-modal .modal-header {
    padding: 20px;
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .preview-modal .modal-header h3 {
    flex-direction: column;
    gap: 10px;
  }
}

</style> 