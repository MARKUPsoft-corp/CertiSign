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
      <section class="stats-section" v-if="activeSection !== 'sign-simple'">
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
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">Total signé</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-file-earmark-check"></i>
            </div>
          </div>
          <button class="stat-card action-stat" @click="activeSection = 'sign-simple'">
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
      <section class="quick-actions" v-if="activeSection !== 'sign-simple'">
        <div class="actions-grid">
          <div class="action-card urgent" v-if="urgentDocuments.length > 0">
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
          <button class="action-card" @click="activeSection = 'signed'" :class="{ 'active': activeSection === 'signed' }">
            <div class="action-icon success">
              <i class="bi bi-file-earmark-check"></i>
            </div>
            <span class="action-title">Signés</span>
            <span class="action-description">{{ signedDocuments.length }} documents signés</span>
          </button>
          <button class="action-card" @click="activeSection = 'history'" :class="{ 'active': activeSection === 'history' }">
            <div class="action-icon primary">
              <i class="bi bi-clock-history"></i>
            </div>
            <span class="action-title">Historique</span>
            <span class="action-description">Voir toutes les signatures</span>
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
            <!-- Onglets Quick / Template -->
            <div class="pending-tabs">
              <button class="tab-btn" :class="{ active: signedTab === 'quick' }" @click="signedTab = 'quick'">Signés directs</button>
              <button class="tab-btn" :class="{ active: signedTab === 'template' }" @click="signedTab = 'template'">Avec template</button>
              <button class="tab-btn" :class="{ active: signedTab === 'self' }" @click="signedTab = 'self'">Self</button>
            </div>

            <!-- Onglet QUICK -->
            <template v-if="signedTab === 'quick'">
              <!-- Recherche -->
              <div class="search-container">
                <input type="text" v-model="searchQuerySignedQuick" class="search-input" placeholder="Rechercher un document..." @input="filterSignedQuickDocuments">
                <i class="bi bi-search search-icon"></i>
              </div>

              <div v-for="doc in paginatedSignedQuickDocuments" :key="doc.id" class="document-item">
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

              <!-- Pagination quick -->
              <div v-if="totalPagesSignedQuick > 1" class="pagination-container">
                <div class="pagination-info">
                  <span>Page {{ currentPageSignedQuick }} sur {{ totalPagesSignedQuick }}</span>
                  <span class="documents-count">({{ filteredSignedQuickDocuments.length }} documents au total)</span>
                </div>
                <div class="pagination-controls">
                  <button class="pagination-btn prev" :disabled="currentPageSignedQuick === 1" @click="previousPageSignedQuick"><i class="bi bi-chevron-left"></i> Précédent</button>
                  <button v-if="visiblePagesSignedQuick[0] > 1" class="pagination-btn page" @click="goToPageSignedQuick(1)">1</button>
                  <span v-if="visiblePagesSignedQuick[0] > 2" class="pagination-dots">...</span>
                  <button v-for="page in visiblePagesSignedQuick" :key="page" class="pagination-btn page" :class="{ 'active': page === currentPageSignedQuick }" @click="goToPageSignedQuick(page)">{{ page }}</button>
                  <span v-if="visiblePagesSignedQuick[visiblePagesSignedQuick.length - 1] < totalPagesSignedQuick - 1" class="pagination-dots">...</span>
                  <button v-if="visiblePagesSignedQuick[visiblePagesSignedQuick.length - 1] < totalPagesSignedQuick" class="pagination-btn page" @click="goToPageSignedQuick(totalPagesSignedQuick)">{{ totalPagesSignedQuick }}</button>
                  <button class="pagination-btn next" :disabled="currentPageSignedQuick === totalPagesSignedQuick" @click="nextPageSignedQuick">Suivant <i class="bi bi-chevron-right"></i></button>
                </div>
              </div>

              <div v-if="filteredSignedQuickDocuments.length === 0" class="empty-state">
                <i class="bi bi-file-earmark"></i>
                <p v-if="searchQuerySignedQuick">Aucun résultat trouvé pour "{{ searchQuerySignedQuick }}"</p>
                <p v-else>Aucun document signé</p>
              </div>
            </template>

            <!-- Onglet TEMPLATE -->
            <template v-else-if="signedTab === 'template'">
              <!-- Cartes templates -->
              <div v-if="!selectedSignedTemplateId" class="template-cards-grid">
                <div v-for="tpl in signedTemplateCards" :key="tpl.templateId" class="template-card-pending">
                  <h4 class="template-card-title">{{ tpl.templateName }}</h4>
                  <p class="template-card-count">{{ tpl.documents.length }} document(s)</p>
                  <div class="template-card-actions">
                    <button class="btn-icon" @click="previewTemplateById(tpl.templateId)" title="Aperçu template"><i class="bi bi-eye"></i></button>
                    <button class="btn-icon primary" @click="selectedSignedTemplateId = tpl.templateId" title="Voir documents"><i class="bi bi-list"></i></button>
                  </div>
                </div>
                <div v-if="signedTemplateCards.length === 0" class="empty-state"><i class="bi bi-file-earmark"></i><p>Aucun document signé via template</p></div>
              </div>

              <!-- Liste d'un template -->
              <div v-else>
                <div class="template-docs-header">
                  <h4 class="template-docs-title">{{ currentSignedTemplateDocs[0]?.templateName || 'Template' }}</h4>
                  <button class="btn-secondary" @click="selectedSignedTemplateId = null">Retour aux templates →</button>
                </div>

                <!-- Recherche -->
                <div class="search-container">
                  <input type="text" v-model="searchQuerySignedTemplate" class="search-input" placeholder="Rechercher un document..." @input="filterSignedTemplateDocuments">
                  <i class="bi bi-search search-icon"></i>
                </div>

                <div v-for="doc in paginatedSignedTemplateDocuments" :key="doc.id" class="document-item">
                  <div class="doc-info">
                    <i class="bi bi-file-earmark-check"></i>
                    <div class="doc-details">
                      <span class="doc-name">{{ doc.document_name || doc.name || 'Document sans nom' }}</span>
                      <span class="doc-meta">Signé le {{ formatDate(doc.signedAt || doc.updated_at) }}</span>
                    </div>
                  </div>
                  <div class="doc-status">
                    <span class="status-badge signed">Signé</span>
                    <div class="doc-actions">
                      <button class="btn-icon" title="Télécharger" @click="downloadSignedDocument(doc)"><i class="bi bi-download"></i></button>
                    </div>
                  </div>
                </div>

                <!-- Pagination template -->
                <div v-if="totalPagesSignedTemplate > 1" class="pagination-container">
                  <div class="pagination-info">
                    <span>Page {{ currentPageSignedTemplate }} sur {{ totalPagesSignedTemplate }}</span>
                    <span class="documents-count">({{ filteredSignedTemplateDocuments.length }} documents au total)</span>
                  </div>
                  <div class="pagination-controls">
                    <button class="pagination-btn prev" :disabled="currentPageSignedTemplate === 1" @click="previousPageSignedTemplate"><i class="bi bi-chevron-left"></i> Précédent</button>
                    <button v-if="visiblePagesSignedTemplate[0] > 1" class="pagination-btn page" @click="goToPageSignedTemplate(1)">1</button>
                    <span v-if="visiblePagesSignedTemplate[0] > 2" class="pagination-dots">...</span>
                    <button v-for="page in visiblePagesSignedTemplate" :key="page" class="pagination-btn page" :class="{ 'active': page === currentPageSignedTemplate }" @click="goToPageSignedTemplate(page)">{{ page }}</button>
                    <span v-if="visiblePagesSignedTemplate[visiblePagesSignedTemplate.length - 1] < totalPagesSignedTemplate - 1" class="pagination-dots">...</span>
                    <button v-if="visiblePagesSignedTemplate[visiblePagesSignedTemplate.length - 1] < totalPagesSignedTemplate" class="pagination-btn page" @click="goToPageSignedTemplate(totalPagesSignedTemplate)">{{ totalPagesSignedTemplate }}</button>
                    <button class="pagination-btn next" :disabled="currentPageSignedTemplate === totalPagesSignedTemplate" @click="nextPageSignedTemplate">Suivant <i class="bi bi-chevron-right"></i></button>
                  </div>
                </div>

                <div v-if="filteredSignedTemplateDocuments.length === 0" class="empty-state"><i class="bi bi-file-earmark"></i><p v-if="searchQuerySignedTemplate">Aucun résultat trouvé pour "{{ searchQuerySignedTemplate }}"</p><p v-else>Aucun document pour ce template</p></div>
              </div>
            </template>

            <!-- Onglet SELF -->
            <template v-else-if="signedTab === 'self'">
              <!-- Cartes templates -->
              <div v-if="!selectedSignedTemplateId" class="template-cards-grid">
                <div v-for="tpl in signedSelfDocumentsCards" :key="tpl.templateId" class="template-card-pending">
                  <h4 class="template-card-title">{{ tpl.templateName }}</h4>
                  <p class="template-card-count">{{ tpl.documents.length }} document(s)</p>
                  <div class="template-card-actions">
                    <button class="btn-icon" @click="previewTemplateById(tpl.templateId)" title="Aperçu template"><i class="bi bi-eye"></i></button>
                    <button class="btn-icon primary" @click="selectedSignedTemplateId = tpl.templateId" title="Voir documents"><i class="bi bi-list"></i></button>
                  </div>
                </div>
                <div v-if="signedSelfDocumentsCards.length === 0" class="empty-state"><i class="bi bi-file-earmark"></i><p>Aucun document signé par le signataire</p></div>
              </div>

              <!-- Liste d'un template -->
              <div v-else>
                <div class="template-docs-header">
                  <h4 class="template-docs-title">{{ currentSignedSelfDocuments[0]?.templateName || 'Template' }}</h4>
                  <button class="btn-secondary" @click="selectedSignedTemplateId = null">Retour aux templates →</button>
                </div>

                <!-- Recherche -->
                <div class="search-container">
                  <input type="text" v-model="searchQuerySignedSelf" class="search-input" placeholder="Rechercher un document..." @input="filterSignedSelfDocuments">
                  <i class="bi bi-search search-icon"></i>
                </div>

                <div v-for="doc in paginatedSignedSelfDocuments" :key="doc.id" class="document-item">
                  <div class="doc-info">
                    <i class="bi bi-file-earmark-check"></i>
                    <div class="doc-details">
                      <span class="doc-name">{{ doc.document_name || doc.name || 'Document sans nom' }}</span>
                      <span class="doc-meta">Signé le {{ formatDate(doc.signedAt || doc.updated_at) }}</span>
                    </div>
                  </div>
                  <div class="doc-status">
                    <span class="status-badge signed">Signé</span>
                    <div class="doc-actions">
                      <button class="btn-icon" title="Télécharger" @click="downloadSignedDocument(doc)"><i class="bi bi-download"></i></button>
                    </div>
                  </div>
                </div>

                <!-- Pagination self -->
                <div v-if="totalPagesSignedSelf > 1" class="pagination-container">
                  <div class="pagination-info">
                    <span>Page {{ currentPageSignedSelf }} sur {{ totalPagesSignedSelf }}</span>
                    <span class="documents-count">({{ filteredSignedSelfDocuments.length }} documents au total)</span>
                  </div>
                  <div class="pagination-controls">
                    <button class="pagination-btn prev" :disabled="currentPageSignedSelf === 1" @click="previousPageSignedSelf"><i class="bi bi-chevron-left"></i> Précédent</button>
                    <button v-if="visiblePagesSignedSelf[0] > 1" class="pagination-btn page" @click="goToPageSignedSelf(1)">1</button>
                    <span v-if="visiblePagesSignedSelf[0] > 2" class="pagination-dots">...</span>
                    <button v-for="page in visiblePagesSignedSelf" :key="page" class="pagination-btn page" :class="{ 'active': page === currentPageSignedSelf }" @click="goToPageSignedSelf(page)">{{ page }}</button>
                    <span v-if="visiblePagesSignedSelf[visiblePagesSignedSelf.length - 1] < totalPagesSignedSelf - 1" class="pagination-dots">...</span>
                    <button v-if="visiblePagesSignedSelf[visiblePagesSignedSelf.length - 1] < totalPagesSignedSelf" class="pagination-btn page" @click="goToPageSignedSelf(totalPagesSignedSelf)">{{ totalPagesSignedSelf }}</button>
                    <button class="pagination-btn next" :disabled="currentPageSignedSelf === totalPagesSignedSelf" @click="nextPageSignedSelf">Suivant <i class="bi bi-chevron-right"></i></button>
                  </div>
                </div>

                <div v-if="filteredSignedSelfDocuments.length === 0" class="empty-state"><i class="bi bi-file-earmark"></i><p v-if="searchQuerySignedSelf">Aucun résultat trouvé pour "{{ searchQuerySignedSelf }}"</p><p v-else>Aucun document pour ce template</p></div>
              </div>
            </template>
          </div>
        </div>

        <!-- Historique -->
        <div v-if="activeSection === 'history'" class="section-content">
          <h3 class="content-title">
            <i class="bi bi-clock-history"></i>
            Historique des signatures
          </h3>
          
          <div class="history-timeline">
            <div v-for="entry in signatureHistory" :key="entry.id" class="timeline-item">
              <div class="timeline-marker" :class="entry.status">
                <i class="bi" :class="getStatusIcon(entry.status)"></i>
              </div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-title">{{ entry.action }}</span>
                  <span class="timeline-date">{{ formatDateTime(entry.timestamp) }}</span>
                </div>
                <div class="timeline-details">
                  <span class="document-name">{{ entry.documentName }}</span>
                  <span class="timeline-description">{{ entry.description }}</span>
                </div>
              </div>
            </div>
            <div v-if="signatureHistory.length === 0" class="empty-state">
              <i class="bi bi-clock"></i>
              <p>Aucun historique disponible</p>
            </div>
          </div>
        </div>

        <!-- Signature directe par le signataire -->
        <div v-if="activeSection === 'sign-simple'" class="section-content sign-section">
          <SignSimpleSigner @close="activeSection = ''" :organization-name="organizationName" />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import AuthService from '@/services/AuthService';
import axios from 'axios';
import TemplateService from '@/services/TemplateService.js';
import SignSimpleSigner from '@/views/SignSimpleSigner.vue';

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

// Historique des signatures
const signatureHistory = ref([
  {
    id: 1,
    action: 'Document signé',
    documentName: 'Convention collective 2024.pdf',
    description: 'Signature électronique appliquée avec succès',
    timestamp: new Date('2024-01-11T14:30:00'),
    status: 'signed'
  },
  {
    id: 2,
    action: 'Document reçu',
    documentName: 'Rapport annuel 2023.pdf',
    description: 'Assigné pour signature par Jean Dupont',
    timestamp: new Date('2024-01-12T09:15:00'),
    status: 'received'
  },
  {
    id: 3,
    action: 'Document signé',
    documentName: 'Accord de partenariat.pdf',
    description: 'Signature électronique appliquée avec succès',
    timestamp: new Date('2024-01-10T16:45:00'),
    status: 'signed'
  }
]);

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

// eslint-disable-next-line no-unused-vars
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

function formatDateTime(dateStr) {
  if (!dateStr) return 'Date inconnue';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return 'Date invalide';
    }
    
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
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

function getStatusIcon(status) {
  const icons = {
    'signed': 'bi-file-earmark-check',
    'received': 'bi-file-earmark-plus',
    'pending': 'bi-hourglass-split'
  };
  return icons[status] || 'bi-circle';
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
      x: isNaN(xPosition) ? 85 : xPosition, // Position X par défaut à 85% si invalide
      y: isNaN(yPosition) ? 10 : yPosition, // Position Y par défaut à 10% si invalide
      size: qrSize,
      pages: pagesValue,
      positions: positions,
      mode: positionMode
    };
    
    console.log('Informations de positionnement du QR code formatées:', qrPosition);

    // ========== RÉCUPÉRATION DES INFORMATIONS DE SIGNATURE ==========
    // Récupérer et formater les informations de signature depuis DocumentQRPosition
    let signaturePosition = null;
    
    // Vérifier si le document a des informations de signature
    if (documentDetails.signature_image || documentDetails.signature_positions) {
      console.log('Informations de signature trouvées dans le document:', {
        has_image: !!documentDetails.signature_image,
        has_positions: !!documentDetails.signature_positions,
        signature_size: documentDetails.signature_size
      });
      
      // Construire l'objet signature_position au format attendu par le microservice
      signaturePosition = {};
      
      // Ajouter l'image de signature si disponible
      if (documentDetails.signature_image) {
        // L'image est stockée comme un fichier dans le backend Django
        // On doit la récupérer et la convertir en base64 pour le microservice
        try {
          let imageUrl = documentDetails.signature_image;
          // Construire l'URL absolue si nécessaire
          if (imageUrl.startsWith('/')) {
            imageUrl = `https://ppd.camgovca.cm${imageUrl}`;
          } else if (!imageUrl.startsWith('https')) {
            imageUrl = `https://ppd.camgovca.cm/${imageUrl}`;
          }
          
          console.log('Récupération de l\'image de signature depuis:', imageUrl);
          
          // Télécharger l'image de signature
          const imageResponse = await axios.get(imageUrl, {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            responseType: 'blob'
          });
          
          // Convertir l'image en base64
          const imageBlob = imageResponse.data;
          const imageBase64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.readAsDataURL(imageBlob);
          });
          
          signaturePosition.signature_image = imageBase64;
          console.log('Image de signature convertie en base64:', imageBase64.substring(0, 50) + '...');
          
        } catch (imageError) {
          console.error('Erreur lors de la récupération de l\'image de signature:', imageError);
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
    
    // Vérifier si le document a une URL de fichier
    if (!documentDetails.document_file) {
      throw new Error('Aucun fichier disponible pour ce document');
    }
    
    // Construire l'URL absolue du document
    let fileUrl = documentDetails.document_file;
    // Si l'URL commence par un slash, on le traite comme un chemin relatif au backend
    if (fileUrl.startsWith('/')) {
      fileUrl = `https://ppd.camgovca.cm${fileUrl}`;
    } else if (!fileUrl.startsWith('https')) {
      // Si l'URL ne commence pas par https, on ajoute le préfixe
      fileUrl = `https://ppd.camgovca.cm/${fileUrl}`;
    }
    
    console.log('Récupération du document à l\'URL:', fileUrl);
    
    // Télécharger le document à partir de son URL
    const response = await axios.get(fileUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      responseType: 'blob'
    });
    
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
  
  // Si le document a une URL de fichier, ouvrir dans un nouvel onglet
  if (doc.document_file) {
    try {
      // Construire l'URL absolue correcte sans double slash
      let fileUrl = doc.document_file;
      
      // Si l'URL commence par un slash, on le traite comme un chemin relatif au backend
      if (fileUrl.startsWith('/')) {
        fileUrl = `https://ppd.camgovca.cm${fileUrl}`;
      } else if (!fileUrl.startsWith('https')) {
        // Si l'URL ne commence pas par https, on ajoute le préfixe
        fileUrl = `https://ppd.camgovca.cm/${fileUrl}`;
      }
      
      // Ajouter l'ID de l'organisation comme paramètre de requête
      const currentUser = AuthService.getCurrentUser();
      const organizationId = currentUser?.organization?.id;
      
      if (organizationId) {
        // Ajouter l'ID de l'organisation comme paramètre de requête
        const separator = fileUrl.includes('?') ? '&' : '?';
        fileUrl += `${separator}organization_id=${organizationId}`;
      }
      
      console.log('Ouverture du document à l\'URL:', fileUrl);
      window.open(fileUrl, '_blank');
    } catch (error) {
      console.error('Erreur lors de l\'ouverture du document:', error);
      alert('Impossible d\'ouvrir le document. Veuillez réessayer plus tard.');
    }
  } else {
    console.error('Aucun fichier disponible pour ce document');
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

    // Récupérer les documents signés depuis l'API DocumentSignature
    const response = await axios.get('https://ppd.camgovca.cm/api/documents/signatures/', config);
    if (response.data && response.data.results) {
      signedDocuments.value = response.data.results.map(doc => {
        // Extraction robuste des informations de template
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
          templateName: tplName,
          self_prepared: (doc.prepare_mode === 'self') || (doc.metadata && doc.metadata.prepare_mode === 'self') || false
        };
      });
      
      console.log('Documents signés récupérés depuis DocumentSignature:', signedDocuments.value);
    }
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
    const blob = await TemplateService.downloadPreview(tplId);
    openBlobInNewTab(blob);
  } catch (err) {
    console.warn('Aperçu indisponible, essai avec le document original...', err);
    try {
      const blob = await TemplateService.downloadOriginal(tplId);
      openBlobInNewTab(blob);
    } catch (e) {
      console.error('Erreur de prévisualisation template', e);
      alert('Impossible de prévisualiser ce template');
    }
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
const signedTab = ref('quick'); // 'quick' | 'template' | 'self'
const signedQuickDocuments = computed(() => signedDocuments.value.filter(doc => !doc.isTemplate && !doc.self_prepared));
const signedTemplateDocuments = computed(() => signedDocuments.value.filter(doc =>  doc.isTemplate));
const signedSelfDocuments = computed(() => signedDocuments.value.filter(doc => doc.self_prepared));

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
const searchQuerySignedSelf = ref('');
const currentPageSignedQuick = ref(1);
const currentPageSignedTemplate = ref(1);
const currentPageSignedSelf = ref(1);

const filteredSignedQuickDocuments = ref([]);
const filteredSignedTemplateDocuments = ref([]);
const filteredSignedSelfDocuments = ref([]);

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

const paginatedSignedSelfDocuments = computed(() => {
  const start = (currentPageSignedSelf.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredSignedSelfDocuments.value.slice(start, end);
});

const totalPagesSignedSelf = computed(() => Math.ceil(filteredSignedSelfDocuments.value.length / itemsPerPage));

const visiblePagesSignedSelf = computed(() => {
  const pages = [];
  const total = totalPagesSignedSelf.value;
  const current = currentPageSignedSelf.value;
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

function filterSignedSelfDocuments() {
  const query = searchQuerySignedSelf.value.toLowerCase();
  filteredSignedSelfDocuments.value = signedSelfDocuments.value.filter(doc => {
    return (doc.document_name && doc.document_name.toLowerCase().includes(query)) ||
           (doc.signedBy && doc.signedBy.toLowerCase().includes(query));
  });
  currentPageSignedSelf.value = 1;
}

// Pagination helpers
function goToPageSignedQuick(page) { if (page >= 1 && page <= totalPagesSignedQuick.value) currentPageSignedQuick.value = page; }
function previousPageSignedQuick() { if (currentPageSignedQuick.value > 1) currentPageSignedQuick.value--; }
function nextPageSignedQuick() { if (currentPageSignedQuick.value < totalPagesSignedQuick.value) currentPageSignedQuick.value++; }

function goToPageSignedTemplate(page) { if (page >= 1 && page <= totalPagesSignedTemplate.value) currentPageSignedTemplate.value = page; }
function previousPageSignedTemplate() { if (currentPageSignedTemplate.value > 1) currentPageSignedTemplate.value--; }
function nextPageSignedTemplate() { if (currentPageSignedTemplate.value < totalPagesSignedTemplate.value) currentPageSignedTemplate.value++; }

function goToPageSignedSelf(page) { if (page >= 1 && page <= totalPagesSignedSelf.value) currentPageSignedSelf.value = page; }
function previousPageSignedSelf() { if (currentPageSignedSelf.value > 1) currentPageSignedSelf.value--; }
function nextPageSignedSelf() { if (currentPageSignedSelf.value < totalPagesSignedSelf.value) currentPageSignedSelf.value++; }

// Watchers
watch(signedQuickDocuments, () => { filterSignedQuickDocuments(); }, { immediate: true });
watch(currentSignedTemplateDocs, () => { filterSignedTemplateDocuments(); }, { immediate: true });
watch(signedSelfDocuments, () => { filterSignedSelfDocuments(); }, { immediate: true });
watch(signedTab, () => {
  currentPageSignedQuick.value = 1;
  currentPageSignedTemplate.value = 1;
  currentPageSignedSelf.value = 1;
  if (signedTab.value !== 'template') selectedSignedTemplateId.value = null;
});
watch(selectedSignedTemplateId, () => {
  searchQuerySignedTemplate.value = '';
  currentPageSignedTemplate.value = 1;
});
watch(searchQuerySignedSelf, () => {
  filterSignedSelfDocuments();
  currentPageSignedSelf.value = 1;
});
// === Fin gestion documents signés ===

// Placeholder pour éviter undefined si logique future d'agrégation par template
const signedSelfDocumentsCards = ref([]);
const currentSignedSelfDocuments = ref([]);
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
  position: sticky;
  top: 0;
  z-index: 100;
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

.action-card:not(.urgent):hover, .action-card.active {
  border-color: #ff9500;
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

/* Historique timeline */
.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.timeline-item {
  display: flex;
  gap: 1.25rem;
  align-items: flex-start;
}

.timeline-marker {
  width: 3rem;
  height: 3rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.timeline-item:hover .timeline-marker {
  transform: scale(1.05);
}

.timeline-marker.signed {
  background: linear-gradient(45deg, #28a745, #5bc85a);
}

.timeline-marker.received {
  background: linear-gradient(45deg, #ff9500, #ffb347);
}

.timeline-marker.pending {
  background: linear-gradient(45deg, #6c757d, #adb5bd);
}

.timeline-content {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 1rem;
  padding: 1.5rem;
  flex: 1;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.timeline-item:hover .timeline-content {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 149, 0, 0.08);
  border-color: rgba(255, 149, 0, 0.12);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.timeline-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-color, #333);
}

.timeline-date {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.timeline-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.document-name {
  font-weight: 500;
  color: var(--text-color, #333);
  font-size: 0.95rem;
}

.timeline-description {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
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
  .timeline-item {
    flex-direction: column;
    gap: 0.5rem;
  }
  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
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
</style> 