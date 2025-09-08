<template>
  <div class="collaborator-dashboard">
    <!-- Fond animé avec particules -->
    <div class="particles-container">
      <div v-for="i in 12" :key="i" class="particle" 
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
          <span class="role-badge collaborator top-right-of-logo">Collaborateur</span>
        </div>
        
        <div class="user-info">
          <div class="organization-info">
            <div class="org-name-wrapper">
              <span class="org-name">{{ organizationName }}</span>
              <span v-if="organizationStatus" 
                    class="status-badge org-status top-right-of-org-name" 
                    :class="`org-status-${organizationStatus?.toLowerCase()}`">
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
            <span class="underlined-text">Préparation de <span class="highlight-text">documents</span></span>
          </h2>
          <p class="welcome-description">
            Préparez et organisez les documents pour la signature électronique
          </p>
          
          <!-- Indicateur d'organisation active -->
          <div class="organization-filter-info">
            <i class="bi bi-filter-circle"></i>
            <span>Données filtrées pour l'organisation <strong>{{ organizationName }}</strong></span>
            <button @click="refreshData" class="refresh-btn" title="Actualiser les données">
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </section>

      <!-- Contenu normal du dashboard -->
      <div v-if="!showCreateTemplate && !showPrepareWithTemplate && activeSection !== 'prepare-document'">
      <!-- Statistiques -->
      <section class="stats-section">
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.thisWeek }}</div>
              <div class="stat-label">Cette semaine</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-calendar-week"></i>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ stats.thisMonth }}</div>
              <div class="stat-label">Ce mois-ci</div>
            </div>
            <div class="stat-icon accent">
              <i class="bi bi-calendar-month"></i>
            </div>
          </div>
          
          <button class="stat-card action-stat" @click="openPrepareDocument">
            <div class="stat-content">
              <div class="stat-value">
                <i class="bi bi-plus-circle"></i>
            </div>
              <div class="stat-label">Nouveau document</div>
            </div>
            <div class="stat-icon primary">
              <i class="bi bi-file-earmark-plus"></i>
          </div>
          </button>
        </div>
      </section>

      <!-- Actions rapides -->
      <section class="quick-actions">
        <div class="actions-grid">
          <button class="action-card" @click="activeSection = 'templates'" :class="{ 'active': activeSection === 'templates' }">
            <div class="action-icon accent">
              <i class="bi bi-file-earmark-richtext"></i>
            </div>
            <span class="action-title">Templates</span>
            <span class="action-description">{{ templates.length }} modèles disponibles</span>
          </button>
          <button class="action-card" @click="activeSection = 'drafts'" :class="{ 'active': activeSection === 'drafts' }">
            <div class="action-icon accent">
              <i class="bi bi-file-earmark-text"></i>
            </div>
            <span class="action-title">Brouillons</span>
            <span class="action-description">{{ drafts.length }} documents en préparation</span>
          </button>
          <button class="action-card" @click="activeSection = 'pending'" :class="{ 'active': activeSection === 'pending' }">
            <div class="action-icon warning">
              <i class="bi bi-hourglass-split"></i>
            </div>
            <span class="action-title">En attente</span>
            <span class="action-description">{{ pendingDocuments.length }} documents assignés</span>
          </button>
          <button class="action-card" @click="activeSection = 'completed'" :class="{ 'active': activeSection === 'completed' }">
            <div class="action-icon success">
              <i class="bi bi-file-check"></i>
            </div>
            <span class="action-title">Terminés</span>
            <span class="action-description">{{ completedDocuments.length }} documents signés</span>
          </button>
        </div>
      </section>

      <!-- Contenu dynamique selon la section active -->
      <section class="content-section" v-if="activeSection">
        <!-- Brouillons -->
        <div v-if="activeSection === 'drafts'" class="section-content">
          <div class="section-header">
            <h3 class="content-title">
              <i class="bi bi-file-earmark-text"></i>
              Documents en préparation
            </h3>
            <button class="btn-primary" @click="openPrepareDocument">
              <i class="bi bi-plus"></i>
              Nouveau document
            </button>
          </div>
          
          <div class="documents-list">
            <div v-for="doc in drafts" :key="doc.id" class="document-item">
              <div class="doc-info">
                <div class="action-icon accent">
                  <i class="bi bi-file-earmark-text"></i>
                </div>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.name }}</span>
                  <span class="doc-meta">Créé le {{ formatDate(doc.createdAt) }}</span>
                </div>
              </div>
              <div class="doc-status">
                <span class="status-badge draft">Brouillon</span>
                <div class="doc-actions">
                  <button class="btn-icon primary" title="Continuer l'édition" @click="continueEdit(doc)">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn-icon success" title="Assigner pour signature" @click="assignForSignature(doc)">
                    <i class="bi bi-person-check"></i>
                  </button>
                  <button class="btn-icon danger" title="Supprimer" @click="deleteDraft(doc)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-if="drafts.length === 0" class="empty-state">
              <i class="bi bi-file-earmark-plus"></i>
              <p>Aucun brouillon</p>
              <button class="btn-primary" @click="openPrepareDocument">
                Créer votre premier document
              </button>
            </div>
          </div>
        </div>

        <!-- Templates -->
        <div v-if="activeSection === 'templates'" class="section-content">
          <div class="section-header">
            <h3 class="content-title">
              <i class="bi bi-file-earmark-richtext"></i>
              Mes templates d'organisation
            </h3>
            <button class="btn-primary" @click="openNewTemplateModal">
              <i class="bi bi-plus"></i>
              Nouveau template
            </button>
          </div>
          
          <div v-if="loadingTemplates" class="loading-state">
            <div class="spinner"></div>
            <p>Chargement des templates...</p>
          </div>
          
          <div v-else-if="templates.length === 0" class="empty-state">
            <i class="bi bi-file-earmark-richtext"></i>
            <p>Aucun template créé</p>
            <span class="empty-description">
              Créez votre premier template pour accélérer la préparation de vos documents
            </span>
            <button class="btn-primary" @click="openNewTemplateModal">
              <i class="bi bi-plus"></i>
              Créer mon premier template
            </button>
          </div>
          
          <div v-else class="templates-grid">
            <div v-for="template in templates" :key="template.id" class="template-card">
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

        <!-- Documents en attente -->
        <div v-if="activeSection === 'pending'" class="section-content">
          <div class="section-header">
          <h3 class="content-title">
            <i class="bi bi-hourglass-split"></i>
            Documents en attente de signature
          </h3>
            <button class="btn-primary" @click="refreshData">
              <i class="bi bi-arrow-clockwise"></i>
              Actualiser
            </button>
          </div>
          
          <!-- Onglets pour séparer les documents en attente -->
          <div class="pending-tabs">
            <button class="tab-btn" :class="{ active: pendingTab === 'quick' }" @click="pendingTab = 'quick'">
              Préparation directe
            </button>
            <button class="tab-btn" :class="{ active: pendingTab === 'template' }" @click="pendingTab = 'template'">
              Avec template
            </button>
          </div>
          
          <div class="documents-list">
            <!-- Affichage pour l'onglet préparation directe -->
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

              <div v-for="doc in paginatedQuickDocuments" :key="doc.id" class="document-item">
                <div class="doc-info">
                  <div class="action-icon warning">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </div>
                  <div class="doc-details">
                    <span class="doc-name">{{ doc.name }}</span>
                    <span class="doc-meta">Assigné à {{ doc.assignedTo }} le {{ formatDate(doc.assignedAt) }}</span>
                  </div>
                </div>
                <div class="doc-status">
                  <div class="status-info">
                    <span class="time-elapsed">{{ getTimeElapsed(doc.assignedAt) }}</span>
                    <span class="status-badge pending">En attente</span>
                  </div>
                  <div class="doc-actions">
                    <button class="btn-icon" title="Voir détails" @click="viewPendingDocument(doc)">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn-icon danger" title="Supprimer" @click="deletePendingDocument(doc)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
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
                <i class="bi bi-hourglass-split"></i>
                <p v-if="searchQueryQuick">Aucun résultat trouvé pour "{{ searchQueryQuick }}"</p>
                <p v-else>Aucun document en attente</p>
              </div>
            </template>

            <!-- Affichage pour l'onglet template -->
            <template v-else>
              <!-- Vue cartes de template -->
              <div v-if="!selectedPendingTemplateId" class="template-cards-grid">
                <div v-for="tpl in pendingTemplateCards" :key="tpl.templateId" class="template-card-pending">
                  <h4 class="template-card-title">{{ tpl.templateName }}</h4>
                  <p class="template-card-count">{{ tpl.documents.length }} document(s) en attente</p>
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
                  <p>Aucun document en attente via template</p>
                </div>
              </div>
              <!-- Vue documents d'un template -->
              <div v-else>
                <div class="template-docs-header">
                  <h4 class="template-docs-title">{{ currentTemplateName }}</h4>
                  <button class="btn-secondary" @click="selectedPendingTemplateId = null">
                    Retour aux templates →
                  </button>
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

                <div v-for="doc in paginatedTemplateDocuments" :key="doc.id" class="document-item">
                  <div class="doc-info">
                    <div class="action-icon warning">
                      <i class="bi bi-file-earmark-pdf"></i>
                    </div>
                    <div class="doc-details">
                      <span class="doc-name">{{ doc.name }}</span>
                      <span class="doc-meta">Assigné à {{ doc.assignedTo }} le {{ formatDate(doc.assignedAt) }}</span>
                    </div>
                  </div>
                  <div class="doc-status">
                    <div class="status-info">
                      <span class="time-elapsed">{{ getTimeElapsed(doc.assignedAt) }}</span>
                      <span class="status-badge pending">En attente</span>
                    </div>
                    <div class="doc-actions">
                      <button class="btn-icon" title="Voir détails" @click="viewPendingDocument(doc)">
                        <i class="bi bi-eye"></i>
                      </button>
                      <button class="btn-icon danger" title="Supprimer" @click="deletePendingDocument(doc)">
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
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

        <!-- Documents terminés -->
        <div v-if="activeSection === 'completed'" class="section-content">
          <div class="section-header">
          <h3 class="content-title">
            <i class="bi bi-file-check"></i>
            Documents signés
          </h3>
            <button class="btn-primary" @click="refreshData">
              <i class="bi bi-arrow-clockwise"></i>
              Actualiser
            </button>
          </div>
          
          <!-- Onglets Quick / Template -->
          <div class="pending-tabs">
            <button class="tab-btn" :class="{ active: signedTab === 'quick' }" @click="signedTab = 'quick'">Signés directs</button>
            <button class="tab-btn" :class="{ active: signedTab === 'template' }" @click="signedTab = 'template'">Avec template</button>
          </div>

          <!-- Onglet QUICK -->
          <template v-if="signedTab === 'quick'">
            <!-- Barre de recherche -->
            <div class="search-container">
              <input type="text" v-model="searchQuerySignedQuick" class="search-input" placeholder="Rechercher un document..." @input="filterSignedQuickDocuments">
              <i class="bi bi-search search-icon"></i>
            </div>

            <div v-for="doc in paginatedSignedQuickDocuments" :key="doc.id" class="document-item">
              <div class="doc-info">
                <div class="action-icon success"><i class="bi bi-file-check"></i></div>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.name }}</span>
                  <span class="doc-meta">Signé par {{ doc.signedBy }} le {{ formatDate(doc.signedAt) }}</span>
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
              <i class="bi bi-file-check"></i>
              <p v-if="searchQuerySignedQuick">Aucun résultat trouvé pour "{{ searchQuerySignedQuick }}"</p>
              <p v-else>Aucun document signé</p>
            </div>
          </template>

          <!-- Onglet TEMPLATE -->
          <template v-else>
            <!-- Cartes de templates -->
            <div v-if="!selectedSignedTemplateId" class="template-cards-grid">
              <div v-for="tpl in signedTemplateCards" :key="tpl.templateId" class="template-card-pending">
                <h4 class="template-card-title">{{ tpl.templateName }}</h4>
                <p class="template-card-count">{{ tpl.documents.length }} document(s)</p>
                <div class="template-card-actions">
                  <button class="btn-icon" @click="previewTemplateById(tpl.templateId)" title="Aperçu template"><i class="bi bi-eye"></i></button>
                  <button class="btn-icon primary" @click="selectedSignedTemplateId = tpl.templateId" title="Voir documents"><i class="bi bi-list"></i></button>
                </div>
              </div>
              <div v-if="signedTemplateCards.length === 0" class="empty-state"><i class="bi bi-file-check"></i><p>Aucun document signé via template</p></div>
            </div>

            <!-- Liste d'un template -->
            <div v-else>
              <div class="template-docs-header">
                <h4 class="template-docs-title">{{ currentSignedTemplateDocs[0]?.templateName || 'Template' }}</h4>
                <button class="btn-secondary" @click="selectedSignedTemplateId = null">Retour aux templates →</button>
              </div>

              <!-- Recherche template -->
              <div class="search-container">
                <input type="text" v-model="searchQuerySignedTemplate" class="search-input" placeholder="Rechercher un document..." @input="filterSignedTemplateDocuments">
                <i class="bi bi-search search-icon"></i>
              </div>

              <div v-for="doc in paginatedSignedTemplateDocuments" :key="doc.id" class="document-item">
                <div class="doc-info">
                  <div class="action-icon success"><i class="bi bi-file-check"></i></div>
                  <div class="doc-details">
                    <span class="doc-name">{{ doc.name }}</span>
                    <span class="doc-meta">Signé par {{ doc.signedBy }} le {{ formatDate(doc.signedAt) }}</span>
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

              <div v-if="filteredSignedTemplateDocuments.length === 0" class="empty-state"><i class="bi bi-file-check"></i><p v-if="searchQuerySignedTemplate">Aucun résultat trouvé pour "{{ searchQuerySignedTemplate }}"</p><p v-else>Aucun document pour ce template</p></div>
            </div>
          </template>
        </div>

        <!-- Section de préparation de document -->
        <div v-if="activeSection === 'prepare-document'" class="section-content prepare-section">
          <PrepareDocument @close="closePrepareSection" @documentPrepared="onDocumentPreparedAndClose"/>
        </div>

        <!-- Section de création de template -->
        <div v-if="showCreateTemplate" class="section-content create-template-section">
          <CreateTemplate @close="closeCreateTemplate" @template-created="onTemplateCreated"/>
        </div>
        
      </section>

      <!-- Section par défaut si aucune section active -->
      <section v-if="!activeSection" class="default-content">
        <div class="welcome-card">
          <div class="welcome-icon">
            <i class="bi bi-person-workspace"></i>
          </div>
          <h3>Bienvenue dans votre espace de travail</h3>
          <p>Gérez vos documents et suivez leur progression de signature</p>
          <button class="btn-primary" @click="openPrepareDocument">
            <i class="bi bi-file-earmark-plus"></i>
            Commencer maintenant
          </button>
        </div>
      </section>
          </div>
          
      <!-- Section de préparation de document -->
      <div v-if="activeSection === 'prepare-document'" class="section-content prepare-section">
        <PrepareDocument @close="closePrepareSection" @documentPrepared="onDocumentPreparedAndClose"/>
              </div>
              
      <!-- Section de préparation de documents avec template -->
      <div v-if="showPrepareWithTemplate" class="section-content prepare-with-template-section">
        <PrepareDocumentWithTemplate 
          :preselectedTemplate="selectedTemplate"
          @close="closePrepareWithTemplate" 
          @documentPrepared="onDocumentPreparedWithTemplate"
          @create-template="openCreateTemplateFromPrepare"
        />
      </div>
      
      <!-- Section de création de template -->
      <div v-if="showCreateTemplate" class="section-content create-template-section">
        <CreateTemplate @close="closeCreateTemplate" @template-created="onTemplateCreated"/>
                </div>
    </main>

    <!-- Modal d'aperçu de template -->
    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="preview-modal">
        <div class="modal-header">
          <div class="modal-title-section">
            <div class="modal-icon">
              <i class="bi bi-eye"></i>
            </div>
            <h3 class="modal-title">Aperçu du template : {{ selectedTemplate?.name }}</h3>
          </div>
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

    <!-- Modal de confirmation de suppression -->
    <div v-if="showDeleteConfirmModal" class="modal-overlay" @click.self="closeDeleteConfirmModal">
      <div class="confirm-modal">
        <div class="modal-header">
          <div class="modal-title-section">
            <div class="modal-icon danger">
              <i class="bi bi-exclamation-triangle"></i>
            </div>
            <h3 class="modal-title">Confirmer la suppression</h3>
          </div>
          <button class="modal-close" @click="closeDeleteConfirmModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Êtes-vous sûr de vouloir supprimer le template <strong>{{ selectedTemplate?.name }}</strong> ?</p>
          <p class="text-danger">Cette action est irréversible et supprimera définitivement ce modèle.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline-secondary" @click="closeDeleteConfirmModal" :disabled="isDeleting">Annuler</button>
          <button class="btn btn-danger" @click="deleteTemplateConfirmed" :disabled="isDeleting">
            <span v-if="isDeleting"><i class="bi bi-hourglass-split spin"></i> Suppression...</span>
            <span v-else><i class="bi bi-trash"></i> Supprimer</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de choix de préparation -->
    <div v-if="showPrepareChoice" class="modal-overlay" @click.self="closePrepareChoice">
      <div class="choice-modal">
          <div class="modal-header">
          <div class="modal-title-section">
            <div class="modal-icon">
              <i class="bi bi-file-earmark-plus"></i>
            </div>
            <h3 class="modal-title">Préparer un nouveau document</h3>
          </div>
          <button class="modal-close" @click="closePrepareChoice">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          
          <div class="modal-body">
          <p class="choice-description">Comment souhaitez-vous préparer votre document ?</p>
          
          <div class="choice-options">
            <button class="choice-option" @click="selectTemplatePreparation">
              <div class="option-icon template">
                <i class="bi bi-file-earmark-richtext"></i>
              </div>
              <div class="option-content">
                <h4 class="option-title">Utiliser un template</h4>
                <p class="option-description">Préparez rapidement avec un modèle existant</p>
              </div>
              <div class="option-arrow">
                <i class="bi bi-chevron-right"></i>
              </div>
              </button>
            
            <button class="choice-option" @click="selectDirectPreparation" :disabled="isProcessingChoice">
              <div class="option-icon direct">
                <i class="bi bi-file-earmark"></i>
            </div>
              <div class="option-content">
                <h4 class="option-title">Préparation directe</h4>
                <p class="option-description">Créez et configurez un nouveau document</p>
          </div>
              <div class="option-arrow">
                <i class="bi bi-chevron-right"></i>
        </div>
            </button>
      </div>
        </div>
      </div>
    </div>



  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import AuthService from '@/services/AuthService';
import PrepareDocument from '@/views/PrepareDocument.vue';
import CreateTemplate from '@/views/CreateTemplate.vue';
import PrepareDocumentWithTemplate from '@/views/PrepareDocumentWithTemplate.vue';
import TemplateService from '@/services/TemplateService.js';
import QrPositioner from '@/components/QrPositioner.vue';

const router = useRouter();

// État réactif
const activeSection = ref('');
const userName = ref('');
const organizationName = ref('');
const organizationStatus = ref('');

// État pour l'affichage des modales
const showPrepareChoice = ref(false);
const isProcessingChoice = ref(false); // Protection contre les clics multiples

// Variables pour les templates
const templates = ref([]);
const loadingTemplates = ref(false);
const showCreateTemplate = ref(false);
const showPrepareWithTemplate = ref(false);
const showDeleteConfirmModal = ref(false);
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

// Variables pour la suppression
const isDeleting = ref(false);

// Computed properties
const canUpdateTemplate = computed(() => {
  return editingTemplate.value.name && 
         editingTemplate.value.file && 
         editingTemplate.value.qrPositions;
});

// Statistiques
const stats = {
  thisWeek: ref(5),
  thisMonth: ref(18),
  avgTime: ref('2j')
};

// Documents brouillons
const drafts = ref([]);

// Documents en attente
const pendingDocuments = ref([]);

// Documents terminés
const completedDocuments = ref([]);

// Positions des particules
const particlePositions = Array.from({ length: 12 }, () => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 6 + 3,
  duration: Math.random() * 25 + 20,
  delay: Math.random() * 8
}));

// Méthodes
function formatDate(date) {
  return new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  }).format(date);
}

function getTimeElapsed(date) {
  const now = new Date();
  const diff = now - date;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60));
    return `${hours}h`;
  }
  return `${days}j`;
}

function openPrepareDocument() {
  showPrepareChoice.value = true;
}

function closePrepareChoice() {
  showPrepareChoice.value = false;
}

function selectTemplatePreparation() {
  closePrepareChoice();
  // Ouvrir directement la vue de préparation avec template
  showPrepareWithTemplate.value = true;
}

function selectDirectPreparation() {
  console.log('selectDirectPreparation appelée', activeSection.value);
  
  // Éviter les appels multiples
  if (activeSection.value === 'prepare-document' || isProcessingChoice.value) {
    console.log('Section déjà active ou en cours de traitement, ignoring...');
    return;
  }
  
  // Marquer comme en cours de traitement
  isProcessingChoice.value = true;
  
  // Fermer la modal de choix
  closePrepareChoice();
  
  // Afficher la section de préparation directe
  activeSection.value = 'prepare-document';
  console.log('Section activeSection définie à:', activeSection.value);
  
  // Réinitialiser le flag après un délai
  setTimeout(() => {
    isProcessingChoice.value = false;
  }, 1000);
}

function closePrepareSection() {
  // Fermer la section de préparation et revenir à la vue par défaut
  activeSection.value = '';
}

function onDocumentPreparedAndClose(document) {
  // Appeler la fonction existante pour gérer le document
  onDocumentPrepared(document);
  // Fermer la section de préparation
  closePrepareSection();
  // Optionnel : afficher la section des documents en attente
  activeSection.value = 'pending';
}

async function fetchDocuments() {
  try {
    // Récupérer l'ID de l'utilisateur connecté
    const user = AuthService.getCurrentUser();
    if (!user || !user.id) {
      console.error('Utilisateur non connecté ou ID manquant');
      return;
    }

    // Récupérer l'ID de l'organisation actuelle
    const organizationId = user?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }

    // Appel direct à l'API Django
    const token = localStorage.getItem('token');
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        organization_id: organizationId  // Utiliser l'ID de l'organisation pour être cohérent
      }
    };

    // Utiliser l'endpoint by_collaborator qui retourne les documents par statut
    const response = await axios.get(`https://ppd.camgovca.cm/api/documents/qr-positions/by_collaborator/`, config);
    
    if (response.data) {
      // Maintenant que le filtrage se fait automatiquement côté backend avec organization_id,
      // nous n'avons plus besoin de filtrer côté frontend
      // Mettre à jour les documents brouillons
      if (response.data.drafts) {
        drafts.value = response.data.drafts.map(doc => ({
          id: doc.id,
          name: doc.document_name,
          createdAt: new Date(doc.created_at),
          status: 'draft'
        }));
      }
      
      // Mettre à jour les documents en attente
      if (response.data.pending) {
        pendingDocuments.value = response.data.pending.map(doc => ({
          id: doc.id,
          name: doc.document_name,
          assignedAt: new Date(doc.created_at),
          assignedTo: doc.collaborator_username || 'En attente de signature',
          status: 'pending',
          isTemplate: !!(doc.metadata && doc.metadata.template_used),
          templateId: doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_id : null,
          templateName: doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_name : null
        }));
      }
      
      // Mettre à jour les documents complétés
      if (response.data.completed) {
        completedDocuments.value = response.data.completed.map(doc => ({
          id: doc.id,
          name: doc.document_name,
          signedAt: new Date(doc.updated_at),
          signedBy: doc.organization_name || 'Signataire',
          status: 'completed',
          isTemplate: !!(doc.metadata && doc.metadata.template_used),
          templateId: doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_id : null,
          templateName: doc.metadata && doc.metadata.template_used ? doc.metadata.template_used.template_name : null
        }));
      }
      
      // Mettre à jour les statistiques en fonction des documents filtrés
      stats.thisWeek.value = response.data.stats?.this_week || 0;
      stats.thisMonth.value = response.data.stats?.this_month || 0;
      stats.avgTime.value = response.data.stats?.avg_time || '1j';
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des documents:', error);
  }
}

function onDocumentPrepared(document) {
  console.log('Document(s) préparé(s):', document);
  
  // Gérer les documents multiples ou un seul document
  const documents = document.documents || [document];
  
  documents.forEach(doc => {
    // Si le document est un brouillon, l'ajouter à la liste des brouillons
    if (doc.status === 'draft' || document.status === 'draft') {
      drafts.value.unshift({
        id: doc.id || doc.document_id,
        name: doc.name || doc.title,
        createdAt: new Date(),
        status: 'draft'
      });
    } 
    // Sinon, l'ajouter à la liste des documents en attente
    else if (doc.status === 'pending_signature' || document.status === 'pending_signature') {
      pendingDocuments.value.unshift({
        id: doc.id || doc.document_id,
        name: doc.name || doc.title,
        assignedAt: new Date(),
        status: 'pending',
        assignedTo: 'En attente de signature'
      });
    }
  });
  
  // Actualiser les données
  fetchDocuments();
}

function continueEdit(doc) {
  console.log('Continuer l\'édition de:', doc.name);
  
  // Récupérer l'ID de l'organisation actuelle
  const user = AuthService.getCurrentUser();
  const organizationId = user?.organization?.id;
  
  if (!organizationId) {
    console.error('ID d\'organisation manquant');
    return;
  }
  
  // Rediriger vers la page d'édition avec l'ID du document et l'ID de l'organisation
  router.push({
    name: 'edit-document',
    params: { id: doc.id },
    query: { organization_id: organizationId }
  });
}

function assignForSignature(doc) {
  console.log('Assigner pour signature:', doc.name);
  
  // Récupérer l'ID de l'organisation actuelle
  const user = AuthService.getCurrentUser();
  const organizationId = user?.organization?.id;
  
  if (!organizationId) {
    console.error('ID d\'organisation manquant');
    return;
  }
  
  // Rediriger vers la page d'assignation avec l'ID du document et l'ID de l'organisation
  router.push({
    name: 'assign-document',
    params: { id: doc.id },
    query: { organization_id: organizationId }
  });
}

async function deleteDraft(doc) {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce brouillon ?')) {
    try {
      // Récupérer l'ID de l'organisation actuelle
      const user = AuthService.getCurrentUser();
      const organizationId = user?.organization?.id;
      
      if (!organizationId) {
        console.error('ID d\'organisation manquant');
        return;
      }
      
      // Appel à l'API pour supprimer le document
      const token = localStorage.getItem('token');
      await axios.delete(`https://ppd.camgovca.cm/api/documents/qr-positions/${doc.id}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          organization_id: organizationId
        }
      });
      
      // Supprimer le document de la liste des brouillons
      const index = drafts.value.findIndex(d => d.id === doc.id);
      if (index > -1) {
        drafts.value.splice(index, 1);
      }
    } catch (error) {
      console.error('Erreur lors de la suppression du brouillon:', error);
    }
  }
}

async function deletePendingDocument(doc) {
  console.log('Supprimer le document en attente:', doc.name);
  
  try {
    // Récupérer l'ID de l'organisation actuelle
    const user = AuthService.getCurrentUser();
    const organizationId = user?.organization?.id;
    
    if (!organizationId) {
      console.error('ID d\'organisation manquant');
      return;
    }
    
    // Appel à l'API pour supprimer le document
    const token = localStorage.getItem('token');
    await axios.delete(`https://ppd.camgovca.cm/api/documents/qr-positions/${doc.id}/`, 
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    // Supprimer le document de la liste locale
    pendingDocuments.value = pendingDocuments.value.filter(d => d.id !== doc.id);
    
    alert('Document supprimé avec succès.');
  } catch (error) {
    console.error('Erreur lors de la suppression du document:', error);
    alert('Erreur lors de la suppression du document.');
  }
}

function logout() {
  AuthService.logout();
  router.push('/login');
}

function refreshData() {
  fetchDocuments();
}

// Fonctions pour la gestion des templates
function openNewTemplateModal() {
  console.log('Ouverture de la vue de création de template');
  showCreateTemplate.value = true;
}

function closeCreateTemplate() {
  console.log('Fermeture de la vue de création de template');
  showCreateTemplate.value = false;
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
    hasSignature: templateData.hasSignature
  };
  
  templates.value.unshift(newTemplateForList);
  
  // Fermer la vue de création
  closeCreateTemplate();
  
  // Passer à la section templates pour voir le nouveau template
  activeSection.value = 'templates';
  
  // Optionnel: afficher un message de succès
  console.log('Template ajouté à la liste avec succès');
}

// Fonction pour afficher l'aperçu d'un template
async function previewTemplate(template) {
  try {
    selectedTemplate.value = template;
    showPreviewModal.value = true;
    loadingPreview.value = true;
    
    // Vérifier d'abord si le template a un preview_document
    if (!template.preview_document) {
      console.warn('Template sans aperçu:', template);
      previewUrl.value = null;
      return;
    }
    
    // Utiliser directement l'URL de l'endpoint preview_document
    // Django gère l'authentification via les cookies de session
    const previewUrlValue = TemplateService.getPreviewUrl(template.id);
    previewUrl.value = previewUrlValue;
    
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
    
    // Récupérer les détails complets du template depuis l'API
    const templateDetails = await TemplateService.getTemplate(template.id);
    
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
        } : null
      },
      signatureImage: null,
      generatedPdfFile: null,
      generatedPdfBlob: null,
      generatedPdfDataUrl: null
    };
    
    // Ouvrir la modale d'édition
    showEditModal.value = true;
  } catch (error) {
    console.error('Erreur lors de la récupération des détails du template:', error);
    alert('Une erreur est survenue lors de la récupération des détails du template.');
  } finally {
    loadingEditFile.value = false;
  }
}

// Fonction pour fermer la modal d'édition
function closeEditModal() {
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
    
    // Mettre à jour le template dans la liste locale
    const index = templates.value.findIndex(t => t.id === editingTemplate.value.id);
    if (index !== -1) {
      templates.value[index] = {
        ...templates.value[index],
        name: templateData.name,
        qrSize: templateData.qr_size,
        pageApplication: templateData.page_application,
      };
    }
    
    // Afficher un message de succès
    alert('Template mis à jour avec succès !');
    
    // Fermer la modale
    closeEditModal();
    
  } catch (error) {
    console.error('Erreur lors de la mise à jour du template:', error);
    alert('Une erreur est survenue lors de la mise à jour du template.');
  } finally {
    isUpdating.value = false;
  }
}

function useTemplate(template) {
  console.log('Utilisation du template:', template.name);
  // Sélectionner le template et ouvrir la vue de préparation avec template
  selectedTemplate.value = template;
  showPrepareWithTemplate.value = true;
}

function confirmDeleteTemplate(template) {
  console.log('Confirmation de suppression du template:', template.name);
  selectedTemplate.value = template;
  showDeleteConfirmModal.value = true;
}

// Fonction pour fermer la modal de suppression
function closeDeleteConfirmModal() {
  showDeleteConfirmModal.value = false;
  selectedTemplate.value = null;
}

// Fonction pour effectuer la suppression une fois confirmée
async function deleteTemplateConfirmed() {
  if (!selectedTemplate.value) return;
  
  try {
    isDeleting.value = true;
    await TemplateService.deleteTemplate(selectedTemplate.value.id);
    
    // Supprimer le template de la liste locale
    templates.value = templates.value.filter(t => t.id !== selectedTemplate.value.id);
    
    // Fermer la modale de confirmation
    closeDeleteConfirmModal();
    
    // Afficher un message de succès
    alert('Template supprimé avec succès !');
  } catch (error) {
    console.error('Erreur lors de la suppression du template:', error);
    alert('Une erreur est survenue lors de la suppression du template.');
  } finally {
    isDeleting.value = false;
  }
}

function getQrSizeLabel(size) {
  switch(size) {
    case 'small': return 'Petit';
    case 'medium': return 'Moyen';
    case 'large': return 'Grand';
    default: return 'Moyen';
  }
}

async function loadTemplates() {
  try {
    loadingTemplates.value = true;
    console.log('Chargement des templates depuis l\'API...');
    
    // Appel à l'API pour récupérer les templates
    const response = await TemplateService.getTemplates(organizationName.value);
    console.log('Réponse API templates:', response);
    
    // Transformer les données de l'API pour le format local
    templates.value = response.results.map(template => ({
      id: template.id,
      name: template.name,
      createdAt: new Date(template.created_at),
      pageApplication: template.page_application,
      qrSize: template.qr_size,
      hasSignature: !!template.signature_image,
      preview_document: template.preview_document
    }));
    
    console.log('Templates chargés:', templates.value.length);
    
  } catch (error) {
    console.error('Erreur lors du chargement des templates:', error);
    // En cas d'erreur, ne pas afficher d'erreur brutale, juste loguer
    templates.value = [];
  } finally {
    loadingTemplates.value = false;
  }
}

// Initialisation
onMounted(() => {
  document.title = 'Collaborateur - Doc@uthANTIC';
  
  // Fonction pour charger les données de l'utilisateur et des documents
  function loadUserAndDocuments() {
    const user = AuthService.getCurrentUser();
    if (user) {
      userName.value = user.username || 'Utilisateur';
      
      if (user.organization && typeof user.organization === 'object') {
        organizationName.value = user.organization.name || 'Organisation Inconnue';
        organizationStatus.value = user.organization.status || 'inconnu';
      } else {
        organizationName.value = user.organization || 'Mon Organisation';
        organizationStatus.value = 'N/A';
      }
      
      // Récupérer les documents
      fetchDocuments();
      
      // Charger les templates
      loadTemplates();
    } else {
      router.push('/login');
    }
  }
  
  // Chargement initial des données
  loadUserAndDocuments();
  
  // Ajouter un écouteur d'événement pour détecter les changements d'organisation
  window.addEventListener('organization-changed', () => {
    console.log('Changement d\'organisation détecté. Actualisation des données...');
    loadUserAndDocuments();
  });
  
  // Nettoyage de l'écouteur lors de la destruction du composant
  return () => {
    window.removeEventListener('organization-changed', loadUserAndDocuments);
  };
});

async function viewPendingDocument(doc) {
  console.log('Voir détails du document en attente:', doc.name);
  
  try {
    // Récupérer le token d'authentification
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Token d\'authentification manquant');
    }
    
    // Appeler l'API pour récupérer les détails du document
    const response = await axios.get(`https://ppd.camgovca.cm/api/documents/qr-positions/${doc.id}/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('Réponse API:', response.data);
    
    // Utiliser les endpoints SFTP de téléchargement
    if (response.data && response.data.generated_pdf_url) {
      // Le PDF généré existe, utiliser l'endpoint de téléchargement SFTP
      console.log('PDF généré trouvé, téléchargement via SFTP:', response.data.generated_pdf_url);
      
      // Créer un lien de téléchargement temporaire
      const downloadLink = document.createElement('a');
      downloadLink.href = response.data.generated_pdf_url;
      downloadLink.download = `document_${doc.id}_generated.pdf`;
      downloadLink.target = '_blank';
      
      // Ajouter le token d'authentification
      downloadLink.setAttribute('data-token', token);
      
      // Déclencher le téléchargement
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      
    } else if (response.data && response.data.document_file_url) {
      // Fallback: utiliser le document original via SFTP
      console.log('Utilisation du document original via SFTP:', response.data.document_file_url);
      
      const downloadLink = document.createElement('a');
      downloadLink.href = response.data.document_file_url;
      downloadLink.download = `document_${doc.id}_original.pdf`;
      downloadLink.target = '_blank';
      downloadLink.setAttribute('data-token', token);
      
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      
    } else {
      // Aucune URL de téléchargement disponible
      console.warn('Aucune URL de téléchargement trouvée dans la réponse:', response.data);
      
      // Afficher un message informatif
      alert('Ce document n\'a pas encore de fichier PDF généré. Veuillez attendre que le processus de génération soit terminé.');
    }
    
  } catch (error) {
    console.error('Erreur lors de la récupération du PDF:', error);
    
    if (error.response?.status === 404) {
      alert('Document non trouvé ou fichier non disponible.');
    } else if (error.response?.status === 403) {
      alert('Accès refusé. Vérifiez vos permissions.');
    } else {
    alert(error.response?.data?.detail || error.message || 'Erreur lors du chargement du document');
    }
  }
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

    // Étape 1: Interroger DocumentSignature pour récupérer le document signé
    const signatureUrl = `https://ppd.camgovca.cm/api/documents/signatures/?document_id=${doc.id}&organization_id=${organizationId}`;
    
    const signatureResponse = await axios.get(signatureUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    console.log('Réponse DocumentSignature:', signatureResponse.data);

    if (!signatureResponse.data.results || signatureResponse.data.results.length === 0) {
      throw new Error('Aucune signature trouvée pour ce document');
    }

    // Prendre la première signature trouvée
    const signature = signatureResponse.data.results[0];
    
    // Étape 2: Télécharger le document signé
    const downloadUrl = `https://ppd.camgovca.cm/api/documents/signatures/${signature.document_id}/download/`;
    
    const response = await axios.get(downloadUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
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

function closePrepareWithTemplate() {
  showPrepareWithTemplate.value = false;
}

function onDocumentPreparedWithTemplate(result) {
  console.log('Documents préparés avec template:', result);
  
  // Fermer la modal
  closePrepareWithTemplate();
  
  // Traiter le résultat selon le type (draft ou submission)
  if (result.type === 'draft') {
    // Ajouter aux brouillons
    for (let i = 0; i < result.count; i++) {
      drafts.value.unshift({
        id: Date.now() + i,
        name: `Document avec ${result.template} - Brouillon.pdf`,
        createdAt: new Date(),
        status: 'draft'
      });
    }
    
    // Afficher la section des brouillons
    activeSection.value = 'drafts';
  } else {
    // Ajouter aux documents en attente
    for (let i = 0; i < result.count; i++) {
      pendingDocuments.value.unshift({
        id: Date.now() + i,
        name: `Document avec ${result.template}.pdf`,
        assignedAt: new Date(),
        assignedTo: 'En attente de signature',
        status: 'pending'
      });
    }
    
    // Afficher la section des documents en attente
    activeSection.value = 'pending';
  }
  
  // Actualiser les données
  fetchDocuments();
}

function openCreateTemplateFromPrepare() {
  // Fermer la vue de préparation
  closePrepareWithTemplate();
  // Ouvrir la création de template
  openNewTemplateModal();
}

const pendingTab = ref('quick');
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

// Fonction utilitaire : apercevoir un template à partir de son ID
function previewTemplateById(tplId) {
  const tpl = templates.value.find(t => t.id === tplId);
  if (tpl) {
    previewTemplate(tpl);
  } else {
    console.warn("Template introuvable pour l'ID", tplId);
  }
}

watch(pendingTab, (newVal) => {
  if (newVal !== 'template') {
    selectedPendingTemplateId.value = null;
  }
});

const currentTemplateName = computed(() => {
  const doc = currentTemplateDocs.value[0];
  return doc ? (doc.templateName || `Template ${doc.templateId}`) : '';
});

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
    return doc.name.toLowerCase().includes(query) ||
           (doc.assignedTo && doc.assignedTo.toLowerCase().includes(query));
  });
  
  // Réinitialiser à la première page après un filtrage
  currentPageQuick.value = 1;
}

function filterTemplateDocuments() {
  const query = searchQueryTemplate.value.toLowerCase();
  
  filteredTemplateDocuments.value = currentTemplateDocs.value.filter(doc => {
    return doc.name.toLowerCase().includes(query) ||
           (doc.assignedTo && doc.assignedTo.toLowerCase().includes(query));
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
watch(pendingQuickDocuments, () => { filterQuickDocuments(); }, { immediate: true });

watch(currentTemplateDocs, () => { filterTemplateDocuments(); }, { immediate: true });

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
const signedQuickDocuments = computed(() => completedDocuments.value.filter(doc => !doc.isTemplate));
const signedTemplateDocuments = computed(() => completedDocuments.value.filter(doc => doc.isTemplate));

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

// Recherche & pagination
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
    return doc.name.toLowerCase().includes(query) || (doc.signedBy && doc.signedBy.toLowerCase().includes(query));
  });
  currentPageSignedQuick.value = 1;
}

function filterSignedTemplateDocuments() {
  const query = searchQuerySignedTemplate.value.toLowerCase();
  filteredSignedTemplateDocuments.value = currentSignedTemplateDocs.value.filter(doc => {
    return doc.name.toLowerCase().includes(query) || (doc.signedBy && doc.signedBy.toLowerCase().includes(query));
  });
  currentPageSignedTemplate.value = 1;
}

// Pagination Quick
function goToPageSignedQuick(page) {
  if (page >= 1 && page <= totalPagesSignedQuick.value) currentPageSignedQuick.value = page;
}
function previousPageSignedQuick() { if (currentPageSignedQuick.value > 1) currentPageSignedQuick.value--; }
function nextPageSignedQuick() { if (currentPageSignedQuick.value < totalPagesSignedQuick.value) currentPageSignedQuick.value++; }

// Pagination Template
function goToPageSignedTemplate(page) {
  if (page >= 1 && page <= totalPagesSignedTemplate.value) currentPageSignedTemplate.value = page;
}
function previousPageSignedTemplate() { if (currentPageSignedTemplate.value > 1) currentPageSignedTemplate.value--; }
function nextPageSignedTemplate() { if (currentPageSignedTemplate.value < totalPagesSignedTemplate.value) currentPageSignedTemplate.value++; }

// Watchers
watch(signedQuickDocuments, () => { filterSignedQuickDocuments(); }, { immediate: true });
watch(currentSignedTemplateDocs, () => { filterSignedTemplateDocuments(); }, { immediate: true });
watch(signedTab, () => {
  currentPageSignedQuick.value = 1;
  currentPageSignedTemplate.value = 1;
});
watch(selectedSignedTemplateId, () => {
  searchQuerySignedTemplate.value = '';
  currentPageSignedTemplate.value = 1;
});
// === Fin gestion documents signés ===

watch(signedTab, () => {
  currentPageSignedQuick.value = 1;
  currentPageSignedTemplate.value = 1;
  // Réinitialiser le template sélectionné si on quitte l'onglet template
  if (signedTab.value !== 'template') {
    selectedSignedTemplateId.value = null;
  }
});
</script>

<style scoped>
/* Styles généraux */
.collaborator-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, 
    var(--bg-color, #f8f9fa) 0%, 
    rgba(6, 255, 165, 0.05) 50%, 
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
  opacity: 0.15;
  animation: float 25s infinite linear;
  background: var(--accent-color, #06ffa5);
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.2;
  }
  90% {
    opacity: 0.2;
  }
  100% {
    transform: translateY(-100vh) translateX(50px) rotate(360deg);
    opacity: 0;
  }
}

/* En-tête */
.dashboard-header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(6, 255, 165, 0.2);
  padding: 1.25rem 2.5rem;
  position: relative; /* le header défile maintenant avec la page */
  top: auto;
  z-index: initial;
  box-shadow: 0 2px 15px rgba(6, 255, 165, 0.1);
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

.role-badge.collaborator.top-right-of-logo {
  position: relative;
  top: 0;
  right: 0;
  font-size: 0.8rem;
  padding: 0.25rem 0.55rem;
  line-height: 1.1;
  border-radius: 0.75rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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
  color: var(--accent-color, #06ffa5);
  font-size: 1.9rem;
  line-height: 1.2;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.05);
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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
  box-shadow: 0 2px 10px rgba(6, 255, 165, 0.12);
  border: 1px solid rgba(6, 255, 165, 0.15);
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
  color: var(--accent-color, #06ffa5);
}

.user-name:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.2);
}

.logout-btn {
  background: transparent;
  border: 2px solid var(--accent-color, #06ffa5);
  color: var(--accent-color, #06ffa5);
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: var(--accent-color, #06ffa5);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(6, 255, 165, 0.3);
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
  background: linear-gradient(90deg, var(--accent-color, #06ffa5), #39ffb4, var(--accent-color, #06ffa5));
  background-size: 200% 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(6, 255, 165, 0.3);
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
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
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

/* Indicateur d'organisation active */
.organization-filter-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: rgba(6, 255, 165, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  margin: 1.5rem auto 0;
  max-width: 80%;
  font-size: 0.9rem;
  color: var(--text-color, #333);
  border: 1px dashed rgba(6, 255, 165, 0.3);
}

.organization-filter-info i {
  color: var(--accent-color, #06ffa5);
  font-size: 1.1rem;
}

.organization-filter-info strong {
  color: var(--accent-color, #06ffa5);
  font-weight: 700;
}

.refresh-btn {
  background: transparent;
  border: none;
  color: var(--accent-color, #06ffa5);
  cursor: pointer;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.5rem;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background-color: rgba(6, 255, 165, 0.2);
  transform: rotate(180deg);
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
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.action-card:hover, .action-card.active {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.action-card.primary:hover {
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 10px 30px rgba(58, 134, 255, 0.2);
}

.action-card:not(.primary):hover, .action-card.active {
  border-color: var(--accent-color, #06ffa5);
  box-shadow: 0 10px 30px rgba(6, 255, 165, 0.15);
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

.action-card .action-icon {
  background: rgba(6, 255, 165, 0.1);
  color: var(--accent-color, #06ffa5);
}

.action-card.primary .action-icon {
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
}

.action-icon.accent {
  background: rgba(6, 255, 165, 0.1);
  color: var(--accent-color, #06ffa5);
}

.action-icon.warning {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.action-icon.success {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
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

.stat-icon.primary {
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
}

.stat-icon.accent {
  background: rgba(6, 255, 165, 0.1);
  color: var(--accent-color, #06ffa5);
}

.stat-icon.warning {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.stat-card.action-stat {
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.stat-card.action-stat:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(58, 134, 255, 0.2);
  border-color: var(--primary-color, #3a86ff);
  background: rgba(255, 255, 255, 1);
}

.stat-card.action-stat .stat-value {
  color: var(--primary-color, #3a86ff);
  font-size: 2.5rem;
}

.stat-card.action-stat .stat-label {
  color: var(--primary-color, #3a86ff);
  font-weight: 600;
}

.stat-card.action-stat .stat-icon {
  transform: scale(1.1);
}

/* Section de contenu */
.content-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 1.25rem;
  padding: 2.5rem;
  box-shadow: 0 10px 30px rgba(6, 255, 165, 0.1);
  border: 1px solid rgba(6, 255, 165, 0.08);
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
  position: relative;
}

.section-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-color, #06ffa5), #39ffb4, var(--accent-color, #06ffa5));
  border-radius: 3px;
}

.content-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-color, #333);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.content-title i {
  color: var(--accent-color, #06ffa5);
  font-size: 1.5rem;
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

.document-item:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(6, 255, 165, 0.08);
  border-color: rgba(6, 255, 165, 0.12);
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.doc-info i {
  font-size: 1.75rem;
  color: var(--accent-color, #06ffa5);
  background: rgba(6, 255, 165, 0.1);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.document-item:hover .doc-info i {
  background: var(--accent-color, #06ffa5);
  color: white;
  transform: scale(1.05);
}

.doc-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.doc-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--text-color, #333);
  margin-bottom: 0;
}

.doc-meta {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.doc-status {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.status-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.time-elapsed {
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
  background: rgba(0, 0, 0, 0.05);
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
}

.status-badge {
  padding: 0.35rem 0.85rem;
  border-radius: 2rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-badge.draft {
  background: rgba(73, 80, 87, 0.15);
  color: #495057;
}

.status-badge.pending {
  background: rgba(255, 193, 7, 0.15);
  color: #856404;
}

.status-badge.signed {
  background: rgba(40, 167, 69, 0.15);
  color: #155724;
}

.doc-actions {
  display: flex;
  gap: 0.75rem;
}

/* Boutons */
.btn-primary {
  background: var(--accent-color, #06ffa5);
  color: white;
  box-shadow: 0 4px 15px rgba(6, 255, 165, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(6, 255, 165, 0.4);
  background: #05e394;
}

.empty-state .btn-primary {
  margin: 1.5rem auto 0;
}

.btn-icon {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 0.6rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  backdrop-filter: blur(10px);
}

.btn-icon.primary {
  background: rgba(58, 134, 255, 0.1);
  border-color: rgba(58, 134, 255, 0.15);
  color: var(--primary-color, #3a86ff);
}

.btn-icon.primary:hover {
  background: var(--primary-color, #3a86ff);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(58, 134, 255, 0.3);
}

.btn-icon.success {
  background: rgba(40, 167, 69, 0.1);
  border-color: rgba(40, 167, 69, 0.15);
  color: #28a745;
}

.btn-icon.success:hover {
  background: #28a745;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.btn-icon.danger {
  background: rgba(220, 53, 69, 0.1);
  border-color: rgba(220, 53, 69, 0.15);
  color: #dc3545;
}

.btn-icon.danger:hover {
  background: #dc3545;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.btn-icon.warning {
  background: rgba(255, 193, 7, 0.1);
  border-color: rgba(255, 193, 7, 0.15);
  color: #ffc107;
}

.btn-icon.warning:hover {
  background: #ffc107;
  color: #212529;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.3);
}

.btn-icon:not(.primary):not(.success):not(.danger):not(.warning) {
  background: rgba(6, 255, 165, 0.1);
  border-color: rgba(6, 255, 165, 0.15);
  color: var(--accent-color, #06ffa5);
}

.btn-icon:not(.primary):not(.success):not(.danger):not(.warning):hover {
  background: var(--accent-color, #06ffa5);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(6, 255, 165, 0.3);
}

/* État vide */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  border: 1px dashed rgba(6, 255, 165, 0.2);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: rgba(6, 255, 165, 0.3);
}

.empty-state p {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  color: var(--text-color, #333);
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
  background: rgba(6, 255, 165, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: var(--accent-color, #06ffa5);
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
  .header-content {
    flex-direction: column;
    gap: 1rem;
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
  
  .doc-status {
    width: 100%;
    justify-content: space-between;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

/* Modal overlay */
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

/* Modal de choix de préparation */
.preparation-choice-modal .modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 60px rgba(6, 255, 165, 0.15);
  border: 1px solid rgba(6, 255, 165, 0.1);
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slide-up 0.4s ease;
  position: relative;
}

.preparation-choice-modal .modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--accent-color, #06ffa5), #39ffb4, var(--accent-color, #06ffa5));
  background-size: 200% 100%;
  border-radius: 1.25rem 1.25rem 0 0;
  animation: gradientMove 3s ease infinite;
}

.preparation-choice-modal .modal-header {
  padding: 2.5rem 2.5rem 1.5rem;
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: linear-gradient(135deg, 
    rgba(0, 166, 81, 0.95), 
    rgba(76, 175, 80, 0.95)
  );
  backdrop-filter: blur(10px);
  z-index: 100;
  box-shadow: 0 4px 20px rgba(6, 255, 165, 0.2);
}

.preparation-choice-modal .modal-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 2.5rem;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #00a651, #4CAF50);
  border-radius: 3px;
}

.preparation-choice-modal .modal-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.preparation-choice-modal .modal-title i {
  color: #00a651;
  font-size: 2rem;
  background: rgba(0, 166, 81, 0.2);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 166, 81, 0.3);
}

.preparation-choice-modal .close-button {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  font-size: 1.2rem;
  color: white;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.preparation-choice-modal .close-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

.preparation-choice-modal .modal-body {
  padding: 2.5rem;
}

.choice-description {
  font-size: 1.2rem;
  color: var(--text-muted, #6c757d);
  text-align: center;
  margin-bottom: 3rem;
  line-height: 1.6;
}

.preparation-options {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preparation-option {
  display: flex;
  align-items: center;
  padding: 2rem;
  border: 2px solid rgba(6, 255, 165, 0.1);
  border-radius: 1.25rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.preparation-option::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(6, 255, 165, 0.05), transparent);
  transition: left 0.5s ease;
}

.preparation-option:hover::before {
  left: 100%;
}

.preparation-option:hover {
  border-color: var(--accent-color, #06ffa5);
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(6, 255, 165, 0.15);
}

.option-icon {
  width: 5rem;
  height: 5rem;
  border-radius: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  margin-right: 2rem;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.option-icon::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(45deg);
  transition: all 0.3s ease;
  opacity: 0;
}

.preparation-option:hover .option-icon::after {
  opacity: 1;
  animation: shimmer 0.6s ease;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.option-icon.template {
  background: linear-gradient(45deg, #e91e63, #ff5722);
  box-shadow: 0 8px 25px rgba(233, 30, 99, 0.3);
}

.option-icon.direct {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5));
  box-shadow: 0 8px 25px rgba(58, 134, 255, 0.3);
}

.option-content {
  flex: 1;
}

.option-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin-bottom: 0.75rem;
  position: relative;
}

.option-description {
  color: var(--text-muted, #6c757d);
  margin-bottom: 1.5rem;
  line-height: 1.6;
  font-size: 1rem;
}

.option-features {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.95rem;
  color: var(--text-muted, #6c757d);
  background: rgba(6, 255, 165, 0.08);
  padding: 0.5rem 1rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(6, 255, 165, 0.15);
  transition: all 0.2s ease;
}

.preparation-option:hover .feature {
  background: rgba(6, 255, 165, 0.12);
  border-color: rgba(6, 255, 165, 0.25);
  transform: translateY(-1px);
}

.feature i {
  color: #28a745;
  font-size: 0.9rem;
  background: rgba(40, 167, 69, 0.1);
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.option-arrow {
  font-size: 2rem;
  color: var(--accent-color, #06ffa5);
  margin-left: 1.5rem;
  transition: all 0.3s ease;
  opacity: 0.6;
}

.preparation-option:hover .option-arrow {
  opacity: 1;
  transform: translateX(8px);
}

/* Modal de template */
.template-preparation-modal .modal-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 60px rgba(6, 255, 165, 0.15);
  border: 1px solid rgba(6, 255, 165, 0.1);
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slide-up 0.4s ease;
  position: relative;
}

.template-preparation-modal .modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #e91e63, #ff5722, #e91e63);
  background-size: 200% 100%;
  border-radius: 1.25rem 1.25rem 0 0;
  animation: gradientMove 3s ease infinite;
}

.template-preparation-modal .modal-content.large {
  max-width: 1200px;
}

.template-preparation-modal .modal-header {
  padding: 2.5rem 2.5rem 1.5rem;
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: linear-gradient(135deg, 
    rgba(0, 166, 81, 0.95), 
    rgba(76, 175, 80, 0.95)
  );
  backdrop-filter: blur(10px);
  z-index: 100;
  box-shadow: 0 4px 20px rgba(6, 255, 165, 0.2);
}

.template-preparation-modal .modal-header::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 2.5rem;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #00a651, #4CAF50);
  border-radius: 3px;
}

.template-preparation-modal .modal-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.template-preparation-modal .modal-title i {
  color: #00a651;
  font-size: 2rem;
  background: rgba(0, 166, 81, 0.2);
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 166, 81, 0.3);
}

.template-preparation-modal .close-button {
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  font-size: 1.2rem;
  color: white;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.template-preparation-modal .close-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
}

.template-preparation-modal .modal-body {
  padding: 2.5rem;
}

.template-description {
  font-size: 1.2rem;
  color: var(--text-muted, #6c757d);
  text-align: center;
  margin-bottom: 3rem;
  line-height: 1.6;
}

.coming-soon {
  text-align: center;
  padding: 4rem 3rem;
  background: linear-gradient(135deg, 
    rgba(6, 255, 165, 0.08), 
    rgba(58, 134, 255, 0.05), 
    rgba(233, 30, 99, 0.05)
  );
  border-radius: 1.25rem;
  border: 2px dashed rgba(6, 255, 165, 0.2);
  position: relative;
  overflow: hidden;
}

.coming-soon::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(6, 255, 165, 0.05), transparent);
  animation: rotate 10s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.coming-soon i {
  font-size: 5rem;
  color: var(--accent-color, #06ffa5);
  margin-bottom: 2rem;
  opacity: 0.8;
  position: relative;
  z-index: 1;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
}

.coming-soon h4 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

.coming-soon p {
  color: var(--text-muted, #6c757d);
  margin-bottom: 2.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.coming-soon .btn-primary {
  background: linear-gradient(45deg, var(--primary-color, #3a86ff), var(--accent-color, #06ffa5));
  border: none;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 2rem;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  box-shadow: 0 8px 25px rgba(58, 134, 255, 0.3);
}

.coming-soon .btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(58, 134, 255, 0.4);
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive pour les modales */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 1rem;
  }
  
  .preparation-choice-modal .modal-content,
  .template-preparation-modal .modal-content {
    max-width: 100%;
  }
  
  .preparation-options {
    gap: 1.5rem;
  }
  
  .preparation-option {
    flex-direction: column;
    text-align: center;
    padding: 2rem 1.5rem;
  }
  
  .option-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .option-arrow {
    display: none;
  }
  
  .option-features {
    justify-content: center;
  }
}

/* Styles pour les templates */
.action-icon.template {
  background: linear-gradient(45deg, #e91e63, #ff5722);
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.template-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(6, 255, 165, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.template-card:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(6, 255, 165, 0.15);
  border-color: var(--accent-color, #06ffa5);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(233, 30, 99, 0.1);
  color: #e91e63;
  font-size: 1.5rem;
}

.template-status {
  background: rgba(233, 30, 99, 0.1);
  color: #e91e63;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 600;
}

.template-content {
  flex: 1;
}

.template-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 0.75rem;
  line-height: 1.3;
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
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.meta-item i {
  color: var(--accent-color, #06ffa5);
  width: 16px;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.empty-description {
  display: block;
  font-size: 0.95rem;
  color: var(--text-muted, #6c757d);
  margin-bottom: 1.5rem;
  line-height: 1.4;
}

/* États de chargement et spinners */
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  border: 1px dashed rgba(6, 255, 165, 0.2);
}

.loading-state .spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(6, 255, 165, 0.2);
  border-radius: 50%;
  border-top-color: var(--accent-color, #06ffa5);
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

.loading-state p {
  font-size: 1.2rem;
  font-weight: 500;
  color: var(--text-color, #333);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted, #6c757d);
  background: rgba(255, 255, 255, 0.5);
  border-radius: 1rem;
  border: 1px dashed rgba(6, 255, 165, 0.2);
}

.error-state i {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: rgba(6, 255, 165, 0.3);
}

.error-state p {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  color: var(--text-color, #333);
}

/* Responsive pour templates */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .template-actions {
    justify-content: center;
  }
}

/* Styles pour la modale de création de template */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
  animation: fadeIn 0.3s ease-out;
}

.template-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(6, 255, 165, 0.2);
  animation: modalIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.modal-header {
  padding: 2rem 2.5rem 1.5rem;
  border-bottom: 1px solid rgba(6, 255, 165, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(6, 255, 165, 0.05), rgba(58, 134, 255, 0.05));
}

.modal-title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.modal-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(45deg, #e91e63, #ff5722);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin: 0;
}

.modal-close {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-muted, #6c757d);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.2rem;
}

.modal-close:hover {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  transform: scale(1.1);
}

.modal-body {
  padding: 2rem 2.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.template-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-color, #333);
  font-size: 0.95rem;
}

.form-label i {
  color: var(--accent-color, #06ffa5);
  font-size: 1.1rem;
}

.form-input {
  padding: 1rem 1.25rem;
  border: 2px solid rgba(6, 255, 165, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: var(--accent-color, #06ffa5);
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 0 0 4px rgba(6, 255, 165, 0.1);
}

.form-input.error {
  border-color: #dc3545;
  background: rgba(220, 53, 69, 0.05);
}

.error-message {
  color: #dc3545;
  font-size: 0.85rem;
  font-weight: 500;
}

.file-upload-area {
  border: 2px dashed rgba(6, 255, 165, 0.3);
  border-radius: 12px;
  padding: 2rem;
  background: rgba(6, 255, 165, 0.02);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.file-upload-area:hover {
  border-color: var(--accent-color, #06ffa5);
  background: rgba(6, 255, 165, 0.05);
}

.file-input {
  display: none;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  background: rgba(6, 255, 165, 0.1);
  color: var(--accent-color, #06ffa5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.upload-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color, #333);
}

.upload-subtitle {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
}

.file-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  padding: 1rem;
  border: 1px solid rgba(6, 255, 165, 0.2);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-info i {
  font-size: 1.5rem;
}

.file-name {
  font-weight: 600;
  color: var(--text-color, #333);
}

.file-size {
  color: var(--text-muted, #6c757d);
  font-size: 0.9rem;
}

.remove-file {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.remove-file:hover {
  background: rgba(220, 53, 69, 0.1);
  transform: scale(1.1);
}

.section-divider {
  position: relative;
  text-align: center;
  margin: 1rem 0;
}

.section-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(6, 255, 165, 0.3), transparent);
}

.divider-text {
  background: rgba(255, 255, 255, 0.9);
  padding: 0 1rem;
  font-weight: 600;
  color: var(--text-color, #333);
  font-size: 0.9rem;
}

.qr-positioner-container {
  border: 1px solid rgba(6, 255, 165, 0.2);
  border-radius: 12px;
  background: rgba(6, 255, 165, 0.02);
  padding: 2rem;
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
  padding: 2rem;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.qr-placeholder p {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color, #333);
  margin: 0;
}

.qr-placeholder small {
  color: var(--text-muted, #6c757d);
}

.modal-footer {
  padding: 1.5rem 2.5rem 2rem;
  border-top: 1px solid rgba(6, 255, 165, 0.1);
  background: rgba(6, 255, 165, 0.02);
}

.footer-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-secondary, .btn-primary {
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-size: 0.95rem;
}

.btn-secondary {
  background: rgba(108, 117, 125, 0.1);
  color: var(--text-muted, #6c757d);
  border: 1px solid rgba(108, 117, 125, 0.2);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(108, 117, 125, 0.2);
  transform: translateY(-2px);
}

.btn-primary {
  background: var(--accent-color, #06ffa5);
  color: white;
  box-shadow: 0 4px 15px rgba(6, 255, 165, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(6, 255, 165, 0.4);
  background: #05e394;
}

.btn-primary:disabled, .btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Responsive pour la modale */
@media (max-width: 768px) {
  .template-modal {
    margin: 1rem;
    max-width: calc(100% - 2rem);
  }
  
  .modal-header {
    padding: 1.5rem 2rem 1rem;
  }
  
  .modal-body {
    padding: 1.5rem 2rem;
  }
  
  .modal-footer {
    padding: 1rem 2rem 1.5rem;
  }
  
  .footer-actions {
    flex-direction: column;
  }
  
  .btn-secondary, .btn-primary {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .modal-header {
    padding: 1rem 1.5rem 0.75rem;
  }
  
  .modal-body {
    padding: 1rem 1.5rem;
  }
  
  .modal-footer {
    padding: 0.75rem 1.5rem 1rem;
  }
  
  .upload-placeholder {
    padding: 1rem;
  }
  
  .upload-icon {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
}

/* Styles pour la modale de choix */
.choice-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 600px;
  animation: modalIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
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
  border: 2px solid rgba(6, 255, 165, 0.1);
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
  border-color: var(--accent-color, #06ffa5);
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(6, 255, 165, 0.2);
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
  background: rgba(6, 255, 165, 0.1);
  color: var(--accent-color, #06ffa5);
}

.choice-option .option-icon.direct {
  background: rgba(58, 134, 255, 0.1);
  color: var(--primary-color, #3a86ff);
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
  color: var(--accent-color, #06ffa5);
  transform: translateX(5px);
}

@media (max-width: 768px) {
  .choice-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .choice-option {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .choice-option .option-arrow {
    transform: rotate(90deg);
  }
  
  .choice-option:hover .option-arrow {
    transform: rotate(90deg) translateY(5px);
  }
}

/* Styles pour la modale de préparation de document */
.prepare-document-overlay {
  z-index: 10001;
}

.prepare-document-overlay .prepare-document-container {
  width: 95%;
  max-width: 1200px;
  max-height: 90vh;
  margin: 2rem auto;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

@media (max-width: 768px) {
  .choice-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .choice-option {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .choice-option .option-arrow {
    transform: rotate(90deg);
  }
  
  .choice-option:hover .option-arrow {
    transform: rotate(90deg) translateY(5px);
  }
}

/* Styles pour la section de préparation de document */
.prepare-section {
  padding: 0;
  background: transparent;
  box-shadow: none;
  border: none;
}

.prepare-section .prepare-document-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(6, 255, 165, 0.1);
  border: 1px solid rgba(6, 255, 165, 0.08);
  transition: all 0.3s ease;
}

.prepare-section .section-card {
  background: transparent;
  box-shadow: none;
  padding: 0;
}

@media (max-width: 768px) {
  .prepare-section .prepare-document-container {
    padding: 1.5rem;
  }
}

/* Styles pour la section de préparation intégrée - SUPPRESSION DE L'EFFET MODAL */
.prepare-section {
  background: transparent;
  padding: 0;
  margin: 0;
  width: 100%;
  animation: fadeIn 0.5s ease-out;
}

/* Forcer le composant PrepareDocument à s'afficher comme une section normale */
.prepare-section :deep(.prepare-document-container) {
  background: transparent !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  margin: 0 !important;
  max-height: none !important;
  overflow-y: visible !important;
  padding: 0 !important;
  border: none !important;
  position: static !important;
  width: 100% !important;
  max-width: 100% !important;
}

/* Forcer les sections internes à avoir un style normal */
.prepare-section :deep(.section-card) {
  background: var(--card-bg) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
  padding: 24px !important;
  margin-bottom: 20px !important;
  border: 1px solid var(--border-color) !important;
}

/* Styles pour l'en-tête de la section de préparation */
.prepare-section :deep(.modal-header) {
  background: transparent !important;
  border: none !important;
  padding: 0 0 20px 0 !important;
  position: static !important;
  backdrop-filter: none !important;
  box-shadow: none !important;
}

.prepare-section :deep(.modal-title) {
  color: var(--text-color) !important;
  font-size: 1.5rem !important;
  text-shadow: none !important;
}

/* Supprimer l'icône de fermeture qui n'est plus nécessaire */
.prepare-section :deep(.modal-close) {
  display: none !important;
}

/* Styles pour le contenu principal */
.prepare-section :deep(.modal-body) {
  padding: 0 !important;
  max-height: none !important;
  overflow-y: visible !important;
}

/* Ajustements pour les formulaires et zones de contenu */
.prepare-section :deep(.upload-area),
.prepare-section :deep(.file-upload-zone) {
  background: var(--bg-light) !important;
  border: 2px dashed var(--border-color) !important;
  border-radius: 12px !important;
}

/* Ajustements pour les boutons */
.prepare-section :deep(.btn-primary) {
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

.prepare-section :deep(.btn-secondary) {
  background-color: var(--secondary-color) !important;
  border-color: var(--border-color) !important;
}

/* Styles pour la section de création de template - Cohérent avec prepare-section */
.create-template-section {
  background: transparent;
  padding: 0;
  margin: 0;
  width: 100%;
  animation: fadeIn 0.5s ease-out;
}

/* Forcer le composant CreateTemplate à s'afficher comme une section normale */
.create-template-section :deep(.create-template-container) {
  background: transparent !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  margin: 0 !important;
  max-height: none !important;
  overflow-y: visible !important;
  padding: 0 !important;
  border: none !important;
  position: static !important;
  width: 100% !important;
  max-width: 100% !important;
}

/* Forcer les sections internes à avoir un style normal */
.create-template-section :deep(.section-card) {
  background: var(--card-bg) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
  padding: 24px !important;
  margin-bottom: 20px !important;
  border: 1px solid var(--border-color) !important;
}

/* Styles pour l'en-tête de la section de création */
.create-template-section :deep(.section-header) {
  background: var(--card-bg) !important;
  border: 1px solid var(--border-color) !important;
  padding: 24px 32px !important;
  margin-bottom: 24px !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}

/* Ajustements pour les formulaires et zones de contenu */
.create-template-section :deep(.upload-area),
.create-template-section :deep(.file-upload-area) {
  background: var(--bg-light) !important;
  border: 2px dashed var(--border-color) !important;
  border-radius: 16px !important;
}

.create-template-section :deep(.upload-area:hover) {
  border-color: var(--primary-color) !important;
  background: rgba(var(--primary-color-rgb), 0.02) !important;
}

/* Ajustements pour les boutons */
.create-template-section :deep(.btn-primary) {
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

.create-template-section :deep(.btn-secondary) {
  background-color: var(--bg-light) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

/* QrPositioner dans CreateTemplate */
.create-template-section :deep(.qr-positioner-container) {
  background: var(--bg-light) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 12px !important;
  padding: 20px !important;
}

/* Animation d'entrée pour la création de template */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* =================================
   STYLES POUR LES MODALES DE TEMPLATES
   ================================= */

/* Modal overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  overflow-y: auto;
  padding: 20px;
  animation: modalOverlayIn 0.3s ease-out;
}

/* Modal d'aperçu */
.preview-modal {
  background-color: var(--bg-light);
  border-radius: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 1000px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

/* Modal d'édition */
.edit-modal {
  background-color: var(--bg-light);
  border-radius: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

/* Modal de confirmation */
.confirm-modal {
  background-color: var(--bg-light);
  border-radius: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

/* En-têtes de modales */
.modal-header {
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  color: white;
  padding: 25px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  border-bottom: 1px solid var(--border-color);
}

.modal-title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.modal-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.modal-icon.danger {
  background: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.modal-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.modal-close {
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

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* Corps de modales */
.modal-body {
  padding: 30px;
  flex: 1;
  overflow-y: auto;
  background: var(--bg-light);
}

.preview-body {
  padding: 0;
  position: relative;
  overflow: hidden;
}

/* Contenu d'aperçu */
.loading-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-secondary);
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
  color: var(--danger-color);
}

.preview-error i {
  font-size: 3rem;
  margin-bottom: 20px;
}

/* Formulaire de template */
.template-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-color);
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
  color: var(--text-color);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-color-rgb), 0.1);
}

/* États de chargement et d'erreur pour l'édition */
.loading-edit-file,
.edit-file-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-secondary);
  text-align: center;
}

.edit-file-error {
  color: var(--danger-color);
}

.edit-file-error i {
  font-size: 3rem;
  margin-bottom: 20px;
}

/* QR Positioner dans la modale d'édition */
.qr-positioner-wrapper {
  margin-top: 20px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

/* Spinner */
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(var(--primary-color-rgb), 0.3);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

/* Pied de modale */
.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: var(--bg-dark);
}

/* Boutons de modale */
.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 120px;
  justify-content: center;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(var(--primary-color-rgb), 0.3);
}

.btn-secondary {
  background: var(--bg-light);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--hover-bg);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn-outline-secondary {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-outline-secondary:hover:not(:disabled) {
  background: var(--bg-light);
  border-color: var(--text-secondary);
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(220, 53, 69, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Texte de danger */
.text-danger {
  color: var(--danger-color);
  font-size: 0.9rem;
  margin-top: 10px;
}

/* Animations */
@keyframes modalOverlayIn {
  from {
    opacity: 0;
    backdrop-filter: blur(0px);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(3px);
  }
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Animation pour les icônes de chargement */
.spin {
  display: inline-block;
  animation: spin 1s linear infinite;
}

/* Responsive design */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
  }
  
  .preview-modal,
  .edit-modal {
    width: 95%;
    height: 90vh;
  }
  
  .confirm-modal {
    width: 95%;
  }
  
  .modal-header {
    padding: 20px;
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .modal-title-section {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    padding: 15px 20px;
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}

/* Mode sombre */
:global(.dark-theme) .preview-modal,
:global(.dark-theme) .edit-modal,
:global(.dark-theme) .confirm-modal {
  background-color: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(10px);
}

:global(.dark-theme) .form-control {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:global(.dark-theme) .form-control:focus {
  border-color: var(--primary-color);
  background: rgba(30, 41, 59, 0.9);
}

.pending-tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
.pending-tabs .tab-btn {
  background: rgba(6, 255, 165, 0.1);
  border: 1px solid rgba(6, 255, 165, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-color, #333);
}
.pending-tabs .tab-btn.active,
.pending-tabs .tab-btn:hover {
  background: var(--accent-color, #06ffa5);
  color: #fff;
}

/* Cartes template en attente */
.template-cards-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.template-card-pending {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 0.75rem;
  padding: 1rem;
  width: 260px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.template-card-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.template-card-count {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.75rem;
}
.template-card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-secondary {
  background: rgba(0,0,0,0.05);
  border: 1px solid rgba(0,0,0,0.1);
  color: var(--text-color, #333);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s ease;
}
.btn-secondary:hover {
  background: rgba(0,0,0,0.08);
}

.template-docs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.template-docs-title {
  font-size: 1.35rem;
  font-weight: 700;
  background: linear-gradient(45deg, var(--accent-color, #06ffa5), #39ffb4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-transform: capitalize;
  letter-spacing: 0.3px;
}

.template-docs-button {
  background: var(--accent-color, #06ffa5);
  color: white;
  border: none;
  border-radius: 5px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.template-docs-button:hover {
  background: var(--primary-color, #3a86ff);
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
  border-color: var(--accent-color, #06ffa5);
  box-shadow: 0 0 0 2px rgba(6, 255, 165, 0.2);
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
  background-color: var(--accent-color, #06ffa5);
  color: white;
  border-color: var(--accent-color, #06ffa5);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(6, 255, 165, 0.3);
}

.pagination-btn.active {
  background-color: var(--accent-color, #06ffa5);
  color: white;
  border-color: var(--accent-color, #06ffa5);
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

/* Styles pour les actions de l'aperçu */
.preview-actions {
  margin-top: 1rem;
  text-align: center;
}

.preview-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
  text-decoration: none;
  border: none;
  cursor: pointer;
}

.preview-actions .btn-primary {
  background: var(--accent-color, #06ffa5);
  color: white;
}

.preview-actions .btn-primary:hover {
  background: var(--primary-color, #3a86ff);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 255, 165, 0.3);
}

.preview-error {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary, #6c757d);
}

.preview-error i {
  font-size: 3rem;
  color: var(--warning-color, #ffc107);
  margin-bottom: 1rem;
}

.preview-error p {
  margin-bottom: 1rem;
  line-height: 1.6;
}
</style> 