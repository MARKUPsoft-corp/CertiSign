<template>
  <div class="sign-document-container">
    <div class="section-card">
      <div class="section-header">
        <h3 class="section-title">
          <i class="bi bi-lightning-charge"></i> Signature rapide
        </h3>
        <button @click="closeSignature" class="close-button">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
      <!-- Progression des étapes -->
      <div class="steps-progress">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          :class="['step', { 'active': currentStep >= index, 'completed': currentStep > index }]"
        >
          <div class="step-number">
            <span v-if="currentStep > index"><i class="bi bi-check"></i></span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ step.label }}</div>
        </div>
      </div>

      <!-- Contenu principal qui change selon l'étape courante -->
      <div class="step-content">
        <!-- 🆕 ÉTAPE 0: Choix du type de signature (pérenne ou éphémère) -->
        <div v-if="currentStep === 0" class="step-body">
          <div class="signature-type-selection">
            <div class="intro-banner">
              <i class="bi bi-lightning-charge"></i>
              <div>
                <h4>Type de signature</h4>
                <p>Choisissez le type de signature pour vos documents</p>
              </div>
            </div>

            <div class="signature-type-options">
              <!-- Option 1: Signature Pérenne -->
              <div class="signature-type-card" 
                   :class="{'selected': signatureType === 'permanent'}" 
                   @click="selectSignatureType('permanent')">
                <div class="type-icon permanent">
                  <i class="bi bi-shield-lock"></i>
                </div>
                <div class="type-content">
                  <h4 class="type-title">Signature Pérenne</h4>
                  <p class="type-description">Valide indéfiniment, comme le système actuel</p>
                  <ul class="type-features">
                    <li><i class="bi bi-check-circle"></i> Valable à vie</li>
                    <li><i class="bi bi-check-circle"></i> Sécurité maximale</li>
                    <li><i class="bi bi-check-circle"></i> Usage standard</li>
                  </ul>
                </div>
                <div class="type-badge recommended" v-if="signatureType === 'permanent'">
                  <i class="bi bi-star-fill"></i>
                  Sélectionné
                </div>
              </div>
              
              <!-- Option 2: Signature Éphémère -->
              <div class="signature-type-card" 
                   :class="{'selected': signatureType === 'ephemeral'}" 
                   @click="selectSignatureType('ephemeral')">
                <div class="type-icon ephemeral">
                  <i class="bi bi-clock-history"></i>
                </div>
                <div class="type-content">
                  <h4 class="type-title">Signature Éphémère</h4>
                  <p class="type-description">Valide pendant une période définie</p>
                  <ul class="type-features">
                    <li><i class="bi bi-check-circle"></i> Période configurable</li>
                    <li><i class="bi bi-check-circle"></i> Auto-expiration</li>
                    <li><i class="bi bi-check-circle"></i> Documents temporaires</li>
                  </ul>
                </div>
                <div class="type-badge new" v-if="signatureType === 'ephemeral'">
                  <i class="bi bi-star-fill"></i>
                  Sélectionné
                </div>
              </div>
            </div>

            <!-- Aperçu du choix -->
            <div class="selection-preview" v-if="signatureType">
              <div class="preview-content">
                <i class="bi" :class="signatureType === 'permanent' ? 'bi-shield-lock' : 'bi-clock-history'"></i>
                <div>
                  <strong>Type sélectionné :</strong> 
                  {{ signatureType === 'permanent' ? 'Signature Pérenne' : 'Signature Éphémère' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 🆕 ÉTAPE 1: Configuration de la période de validité (si éphémère) -->
        <div v-if="currentStep === 1 && signatureType === 'ephemeral'" class="step-body">
          <div class="expiration-configuration">
            <div class="intro-banner">
              <i class="bi bi-clock-history"></i>
              <div>
                <h4>Période de validité</h4>
                <p>Définissez combien de temps vos signatures resteront valides</p>
              </div>
            </div>

            <!-- Durées pré-définies -->
            <div class="duration-presets">
              <h5>Durées courantes</h5>
              <div class="presets-grid">
                <button v-for="preset in durationPresets" 
                        :key="preset.value"
                        :class="['preset-btn', {'selected': selectedDuration === preset.value}]"
                        @click="selectDuration(preset.value)">
                  <div class="preset-icon">
                    <i :class="preset.icon"></i>
                  </div>
                  <div class="preset-label">{{ preset.label }}</div>
                  <div class="preset-desc">{{ preset.description }}</div>
                </button>
                
                <!-- Option personnalisée -->
                <button :class="['preset-btn custom', {'selected': selectedDuration === 'custom'}]"
                        @click="selectDuration('custom')">
                  <div class="preset-icon">
                    <i class="bi bi-calendar-date"></i>
                  </div>
                  <div class="preset-label">Personnalisé</div>
                  <div class="preset-desc">Date au choix</div>
                </button>
              </div>
            </div>

            <!-- Configuration date personnalisée -->
            <div v-if="selectedDuration === 'custom'" class="custom-date-config">
              <h5>Date d'expiration personnalisée</h5>
              <div class="date-input-group">
                <label for="custom-date">Expire le :</label>
                <input type="datetime-local" 
                       id="custom-date"
                       v-model="customExpirationDate"
                       :min="minDateTime"
                       class="custom-date-input">
              </div>
            </div>

            <!-- Aperçu de l'expiration -->
            <div class="expiration-preview" v-if="expirationDate">
              <div class="preview-card">
                <div class="preview-header">
                  <i class="bi bi-calendar-check"></i>
                  <h5>Aperçu de l'expiration</h5>
                </div>
                <div class="preview-content">
                  <div class="expiration-info">
                    <div class="info-item">
                      <span class="label">Date d'expiration :</span>
                      <span class="value">{{ formatExpirationDisplay }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">Durée de validité :</span>
                      <span class="value">{{ durationDescription }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">Type de signature :</span>
                      <span class="value">Éphémère</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ÉTAPE 2: Sélection des documents à signer (ancienne étape 0) -->
        <div v-if="currentStep === 2 || (currentStep === 1 && signatureType === 'permanent')" class="step-body">
          <div class="template-info-banner">
            <i class="bi bi-files"></i>
            <div>
              <h4>Sélection des documents</h4>
              <p>Sélectionnez un ou plusieurs documents PDF à signer avec une signature 
                 <strong>{{ signatureType === 'permanent' ? 'pérenne' : 'éphémère' }}</strong>
                 <span v-if="signatureType === 'ephemeral'">
                   (expire {{ formatExpirationDisplay }})
                 </span>
              </p>
            </div>
          </div>

          <!-- Zone d'upload multiple -->
          <div class="upload-area multiple" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
            <i class="bi bi-cloud-arrow-up-fill"></i>
            <p>Déposez vos fichiers PDF ici ou cliquez pour sélectionner</p>
            <span class="upload-hint">Formats acceptés: .pdf (max 10MB par fichier) - Sélection multiple autorisée</span>
            <input type="file" ref="fileInput" accept=".pdf" multiple @change="handleFileSelection" class="file-input">
          </div>

          <!-- Liste des documents sélectionnés -->
          <div v-if="selectedFiles.length > 0" class="selected-documents-list">
            <h4>Documents sélectionnés ({{ selectedFiles.length }})</h4>
            <div class="documents-grid">
              <div v-for="(file, index) in selectedFiles" :key="index" class="document-card">
                <div class="document-header">
                  <div class="document-icon">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </div>
                  <button @click="removeDocument(index)" class="remove-btn" title="Supprimer ce document">
                    <i class="bi bi-x-circle-fill"></i>
                  </button>
                </div>
                <div class="document-info">
                  <div class="document-name" :title="file.name">{{ file.name }}</div>
                  <div class="document-size">{{ formatFileSize(file.size) }}</div>
                </div>
                <!-- Badge type de signature -->
                <div class="signature-type-badge" :class="signatureType">
                  <i class="bi" :class="signatureType === 'permanent' ? 'bi-shield-lock' : 'bi-clock-history'"></i>
                  {{ signatureType === 'permanent' ? 'Pérenne' : 'Éphémère' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ÉTAPE 3: Prévisualisation des documents (ancienne étape 1) -->
        <div v-if="currentStep === 3 || (currentStep === 2 && signatureType === 'permanent')" class="step-body">
          <div class="documents-summary">
            <h4>{{ selectedFiles.length }} document(s) sélectionné(s) pour la signature</h4>
            <p>Vous pouvez prévisualiser chaque document en cliquant sur les onglets ci-dessous.</p>
          </div>

          <!-- Onglets des documents -->
          <div class="documents-tabs">
            <div class="tabs-header">
              <button 
                v-for="(file, index) in selectedFiles" 
                :key="index"
                @click="setActiveDocument(index)"
                :class="['tab-button', { 'active': activeDocumentIndex === index }]"
              >
                <i class="bi bi-file-earmark-pdf"></i>
                <span class="tab-title">{{ truncateFileName(file.name, 20) }}</span>
                <button @click.stop="removeDocument(index)" class="tab-remove-btn" title="Supprimer">
                  <i class="bi bi-x"></i>
                </button>
              </button>
            </div>
            
            <!-- Contenu de l'onglet actif -->
            <div class="tab-content" v-if="selectedFiles[activeDocumentIndex]">
              <div class="document-info-header">
                <div class="document-icon">
                  <i class="bi bi-file-earmark-pdf"></i>
                </div>
                <div class="document-details">
                  <div class="document-name">{{ selectedFiles[activeDocumentIndex].name }}</div>
                  <div class="document-size">{{ formatFileSize(selectedFiles[activeDocumentIndex].size) }}</div>
                </div>
              </div>

              <!-- Prévisualisation PDF -->
              <div class="pdf-preview-container">
                <div v-if="!documentPreviews || !documentPreviews[activeDocumentIndex]" class="pdf-loading">
                  <i class="bi bi-arrow-repeat spinning"></i>
                  <p>Initialisation de la prévisualisation...</p>
                </div>
                <div v-else-if="documentPreviews[activeDocumentIndex]?.loading" class="pdf-loading">
                  <i class="bi bi-arrow-repeat spinning"></i>
                  <p>Chargement de la prévisualisation...</p>
                </div>
                <div v-else-if="documentPreviews[activeDocumentIndex]?.error" class="pdf-error">
                  <i class="bi bi-exclamation-triangle"></i>
                  <p>Impossible de charger la prévisualisation. {{ documentPreviews[activeDocumentIndex].error }}</p>
                </div>
                <iframe 
                  v-else-if="documentPreviews[activeDocumentIndex]?.url" 
                  class="pdf-preview" 
                  :src="documentPreviews[activeDocumentIndex].url"
                  width="100%"
                  height="600"
                  frameborder="0"
                ></iframe>
                <div v-else class="pdf-error">
                  <i class="bi bi-exclamation-triangle"></i>
                  <p>Aucune prévisualisation disponible pour ce document.</p>
                  <button @click="createDocumentPreviews" class="retry-btn">Réessayer</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 4: Positionnement du QR code et de la signature -->
        <div v-if="currentStep === 4" class="step-body">
          <div class="positioning-info-banner">
            <i class="bi bi-cursor"></i>
            <div>
              <h4>Positionnement individuel des éléments</h4>
              <p>Définissez la position du QR code et de votre signature sur chaque document. Utilisez les onglets ci-dessous pour naviguer entre vos documents et positionner les éléments individuellement.</p>
            </div>
          </div>

          <!-- Onglets pour chaque document -->
          <div class="positioning-tabs">
            <div class="tabs-header">
              <button 
                v-for="(file, index) in selectedFiles" 
                :key="index"
                @click="setActivePositioningDocument(index)"
                :class="['tab-button positioning-tab', { 
                  'active': activePositioningIndex === index,
                  'completed': documentPositions[index]?.completed
                }]"
              >
                <div class="tab-content">
                  <i class="bi bi-file-earmark-pdf"></i>
                  <span class="tab-title">{{ truncateFileName(file.name, 15) }}</span>
                  <div class="tab-status">
                    <i v-if="documentPositions[index]?.completed" class="bi bi-check-circle-fill" title="Positionnement terminé"></i>
                    <i v-else-if="documentPositions[index]?.hasPositions" class="bi bi-circle-half" title="Positionnement en cours"></i>
                    <i v-else class="bi bi-circle" title="À positionner"></i>
                  </div>
                </div>
              </button>
            </div>
            
            <!-- Contenu de l'onglet actif -->
            <div class="tab-content-positioning" v-if="selectedFiles[activePositioningIndex]">
              <div class="document-positioning-header">
                <div class="document-info">
                  <div class="document-icon">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </div>
                  <div class="document-details">
                    <div class="document-name">{{ selectedFiles[activePositioningIndex].name }}</div>
                    <div class="document-progress">
                      Document {{ activePositioningIndex + 1 }} sur {{ selectedFiles.length }}
                      <span v-if="documentPositions[activePositioningIndex]?.completed" class="status-completed">
                        <i class="bi bi-check-circle-fill"></i> Terminé
                      </span>
                      <span v-else class="status-pending">
                        <i class="bi bi-clock"></i> En attente
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- Boutons de navigation rapide -->
                <div class="document-navigation">
                  <button 
                    @click="previousPositioningDocument" 
                    :disabled="activePositioningIndex === 0"
                    class="nav-doc-btn"
                    title="Document précédent"
                  >
                    <i class="bi bi-chevron-left"></i>
                  </button>
                  <button 
                    @click="nextPositioningDocument" 
                    :disabled="activePositioningIndex === selectedFiles.length - 1"
                    class="nav-doc-btn"
                    title="Document suivant"
                  >
                    <i class="bi bi-chevron-right"></i>
                  </button>
                </div>
              </div>

              <!-- Intégration du composant QrPositioner pour le document actuel -->
              <QrPositioner
                :key="`positioner-${activePositioningIndex}`"
                :pdfFile="selectedFiles[activePositioningIndex]"
                :totalPages="documentTotalPages[activePositioningIndex] || 1"
                :initialQrPosition="documentPositions[activePositioningIndex]?.qr_position"
                :initialSignaturePosition="documentPositions[activePositioningIndex]?.signature"
                @position-confirmed="handleIndividualPositionConfirmed"
                @signature-uploaded="handleIndividualSignatureUploaded"
              />
              
              <!-- Boutons d'action pour ce document -->
              <div class="positioning-actions">
                <!-- Message informatif quand le document est terminé -->
                <div v-if="documentPositions[activePositioningIndex]?.completed" class="document-completed-info">
                  <i class="bi bi-check-circle-fill"></i>
                  <span>Positionnement confirmé pour ce document</span>
                </div>
                
                <!-- Message informatif pour le workflow -->
                <div v-else class="positioning-instructions">
                  <i class="bi bi-info-circle"></i>
                  <span>Positionnez les éléments puis cliquez sur "Aperçu final" → "Confirmer" pour valider automatiquement ce document</span>
                </div>
                
                <!-- Bouton pour éditer un document déjà confirmé -->
                <button 
                  v-if="documentPositions[activePositioningIndex]?.completed"
                  @click="editDocumentPositioning"
                  class="edit-positioning-btn"
                >
                  <i class="bi bi-pencil"></i>
                  Modifier le positionnement
                </button>
              </div>
            </div>
          </div>

          <!-- Résumé global du positionnement -->
          <div class="positioning-summary" v-if="selectedFiles.length > 1">
            <h5>Résumé du positionnement</h5>
            <div class="summary-grid">
              <div 
                v-for="(file, index) in selectedFiles" 
                :key="index"
                class="summary-item"
              >
                <div class="summary-icon">
                  <i v-if="documentPositions[index]?.completed" class="bi bi-check-circle-fill text-success"></i>
                  <i v-else-if="documentPositions[index]?.hasPositions" class="bi bi-circle-half text-warning"></i>
                  <i v-else class="bi bi-circle text-muted"></i>
                </div>
                <div class="summary-text">
                  <div class="summary-filename">{{ truncateFileName(file.name, 20) }}</div>
                  <div class="summary-status">
                    <span v-if="documentPositions[index]?.completed">Positionnement confirmé</span>
                    <span v-else-if="documentPositions[index]?.hasPositions">En cours de positionnement</span>
                    <span v-else>Non positionné</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 5: Saisie du certificat et du mot de passe -->
        <div v-if="currentStep === 5" class="step-body">
          <div class="certificate-info-banner">
            <i class="bi bi-shield-lock-fill"></i>
            <div>
              <h4>Certificat numérique</h4>
              <p>Pour signer les {{ selectedFiles.length }} documents avec une signature 
                 <strong>{{ signatureType === 'permanent' ? 'pérenne' : 'éphémère' }}</strong>
                 <span v-if="signatureType === 'ephemeral'">
                   (expire {{ formatExpirationDisplay }})
                 </span>, 
                 vous devez fournir un certificat PFX (.pfx) et son mot de passe.
              </p>
            </div>
          </div>

          <div class="certificate-form">
            <div class="form-group">
              <label>Certificat PFX</label>
              <div class="upload-area small" @click="triggerCertificateInput" @dragover.prevent @drop.prevent="handleCertificateDrop">
                <i class="bi bi-shield-fill"></i>
                <p v-if="!certificateFile">Déposez votre fichier .pfx ou cliquez pour sélectionner</p>
                <p v-else class="certificate-name">{{ certificateFile.name }}</p>
                <input type="file" ref="certificateInput" accept=".pfx" @change="handleCertificateSelection" class="file-input">
              </div>
            </div>

            <div class="form-group">
              <label>Mot de passe du certificat</label>
              <div class="password-input-container">
                <input 
                  :type="showPassword ? 'text' : 'password'"
                  v-model="certificatePassword"
                  class="password-input"
                  placeholder="Entrez le mot de passe du certificat"
                >
                <button @click="showPassword = !showPassword" type="button" class="toggle-password-btn">
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
            </div>

            <!-- Résumé de la signature à effectuer -->
            <div class="signature-summary">
              <h5>Résumé de la signature</h5>
              <div class="summary-details">
                <div class="summary-item">
                  <i class="bi bi-files"></i>
                  <span><strong>{{ selectedFiles.length }}</strong> document(s) à signer</span>
                </div>
                <div class="summary-item">
                  <i class="bi" :class="signatureType === 'permanent' ? 'bi-shield-lock' : 'bi-clock-history'"></i>
                  <span>Signature <strong>{{ signatureType === 'permanent' ? 'pérenne' : 'éphémère' }}</strong></span>
                </div>
                <div v-if="signatureType === 'ephemeral'" class="summary-item">
                  <i class="bi bi-calendar-check"></i>
                  <span>Expire le <strong>{{ formatExpirationDisplay }}</strong></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Étape 6: En cours de signature -->
        <div v-if="currentStep === 6" class="step-body signature-processing">
          <div v-if="signatureStatus === 'loading'">
            <div class="processing-animation">
              <i class="bi bi-shield-fill-check pulsing"></i>
              <div class="spinner-container">
                <div class="spinner"></div>
              </div>
            </div>
            <p class="processing-text">Signature des {{ selectedFiles.length }} documents en cours...</p>
            
            <!-- Progression détaillée pour chaque document -->
            <div class="documents-processing">
              <div 
                v-for="(file, index) in selectedFiles" 
                :key="index"
                :class="['document-processing-item', { 
                  'completed': completedDocuments.includes(index),
                  'current': currentProcessingDocument === index,
                  'pending': currentProcessingDocument < index
                }]"
              >
                <div class="processing-icon">
                  <i v-if="completedDocuments.includes(index)" class="bi bi-check-circle-fill"></i>
                  <i v-else-if="currentProcessingDocument === index" class="bi bi-arrow-repeat spinning"></i>
                  <i v-else class="bi bi-circle"></i>
                </div>
                <span class="document-name">{{ file.name }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="signatureStatus === 'error'" class="signature-error">
            <i class="bi bi-exclamation-circle"></i>
            <h4>Erreur lors de la signature</h4>
            <p>{{ signatureError }}</p>
          </div>
        </div>

        <!-- Étape 7: Téléchargement des documents signés -->
        <div v-if="currentStep === 7" class="step-body signature-complete">
          <div class="success-animation">
            <i class="bi bi-check-circle-fill"></i>
          </div>
          <h3>{{ selectedFiles.length }} document(s) signé(s) avec succès !</h3>
          <p>Tous vos documents ont été signés numériquement avec votre certificat.</p>
          
          <!-- Liste des documents signés -->
          <div class="signed-documents-list">
            <h4>Documents signés disponibles pour téléchargement</h4>
            <div class="signed-documents-grid">
              <div v-for="(signedDoc, index) in signedDocuments" :key="index" class="signed-document-card">
                <div class="signed-card-header">
                  <div class="document-icon large">
                    <i class="bi bi-file-earmark-check"></i>
                  </div>
                  <div class="document-status-badge">
                    <i class="bi bi-check-circle-fill"></i>
                    <span>Signé</span>
                  </div>
                </div>
                <div class="signed-card-body">
                  <div class="document-name" :title="signedDoc.name">
                    {{ truncateFileName(signedDoc.name, 35) }}
                  </div>
                  <div class="signature-date">
                    <i class="bi bi-calendar-check"></i>
                    {{ signatureDate }}
                  </div>
                  <div class="document-size-info">
                    <i class="bi bi-file-earmark"></i>
                    Document {{ index + 1 }} de {{ signedDocuments.length }}
                  </div>
                </div>
                <div class="signed-card-footer">
                  <a :href="signedDoc.url" :download="signedDoc.name" class="download-button">
                    <i class="bi bi-download"></i>
                    <span>Télécharger</span>
                  </a>
                </div>
              </div>
            </div>
            
            <!-- Bouton pour télécharger tous les documents -->
            <div class="download-all-section">
              <button @click="downloadAllDocuments" class="download-all-button">
                <i class="bi bi-download"></i>
                Télécharger tous les documents signés
              </button>
              <p class="download-note">Les documents signés contiennent une signature numérique et un QR code intégrés qui peuvent être vérifiés.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Boutons de navigation entre les étapes -->
      <div class="step-navigation">
        <button 
          v-if="currentStep > 0 && currentStep < 7" 
          @click="prevStep" 
          class="nav-button secondary"
        >
          <i class="bi bi-arrow-left"></i> Précédent
        </button>
        
        <div class="spacer" v-if="currentStep > 0"></div>
        
        <button 
          v-if="currentStep < 6" 
          @click="nextStep" 
          class="nav-button primary"
          :disabled="!canProceedToNextStep"
        >
          Suivant <i class="bi bi-arrow-right"></i>
        </button>
        
        <button 
          v-if="currentStep === 7" 
          @click="closeSignature" 
          class="nav-button primary"
        >
          Terminer <i class="bi bi-check"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits } from 'vue';
import QrPositioner from '@/components/QrPositioner.vue';

// Définir les émetteurs d'événements
const emit = defineEmits(['close']);

// Étapes du workflow de signature rapide
const steps = [
  { label: 'Type de signature' },
  { label: 'Configuration expiration' },
  { label: 'Sélection documents' },
  { label: 'Prévisualisation' },
  { label: 'Positionnement' },
  { label: 'Certificat' },
  { label: 'Signature' },
  { label: 'Téléchargement' }
];

// Étape courante
const currentStep = ref(0);

// 🆕 NOUVELLES VARIABLES POUR SIGNATURES ÉPHÉMÈRES
const signatureType = ref(''); // 'permanent' ou 'ephemeral'
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
    value: '1week', 
    label: '1 semaine', 
    description: 'Documents à court terme',
    hours: 168,
    icon: 'bi-calendar-week'
  },
  { 
    value: '1month', 
    label: '1 mois', 
    description: 'Durée standard recommandée',
    hours: 720,
    icon: 'bi-calendar-month'
  },
  { 
    value: '3months', 
    label: '3 mois', 
    description: 'Projets à moyen terme',
    hours: 2160,
    icon: 'bi-calendar-range'
  },
  { 
    value: '6months', 
    label: '6 mois', 
    description: 'Documents à long terme',
    hours: 4320,
    icon: 'bi-calendar2-range'
  },
  { 
    value: '1year', 
    label: '1 an', 
    description: 'Durée maximale recommandée',
    hours: 8760,
    icon: 'bi-calendar-year'
  }
];

// Date minimum pour le sélecteur (maintenant + 1 heure)
const minDateTime = computed(() => {
  const now = new Date();
  now.setHours(now.getHours() + 1);
  return now.toISOString().slice(0, 16);
});

// Date d'expiration calculée
const expirationDate = computed(() => {
  if (signatureType.value !== 'ephemeral') return null;
  
  if (selectedDuration.value === 'custom') {
    return customExpirationDate.value ? new Date(customExpirationDate.value) : null;
  } else {
    const preset = durationPresets.find(p => p.value === selectedDuration.value);
    if (preset) {
      const expiration = new Date();
      expiration.setHours(expiration.getHours() + preset.hours);
      return expiration;
    }
  }
  return null;
});

// Affichage formaté de la date d'expiration
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

// Références aux éléments DOM
const fileInput = ref(null);
const certificateInput = ref(null);

// État des documents
const selectedFiles = ref([]);
const certificateFile = ref(null);
const certificatePassword = ref('');
const showPassword = ref(false);

// Gestion des onglets de prévisualisation
const activeDocumentIndex = ref(0);
const documentPreviews = ref([]);
const documentTotalPages = ref({});
const referenceDocumentIndex = ref(0);

// État de la signature
const signatureStatus = ref(null); // 'loading', 'error', 'success'
const signatureError = ref(null);
const currentProcessingDocument = ref(-1);
const completedDocuments = ref([]);

// Informations sur les documents signés
const signedDocuments = ref([]);
const signatureDate = ref('');

// Image de signature uploadée
const uploadedSignatureImage = ref(null);

// État de positionnement pour chaque document
const documentPositions = ref({});
const activePositioningIndex = ref(0);

// 🆕 MÉTHODES POUR SIGNATURES ÉPHÉMÈRES
function selectSignatureType(type) {
  signatureType.value = type;
  console.log('Type de signature sélectionné:', type);
}

function selectDuration(duration) {
  selectedDuration.value = duration;
  console.log('Durée sélectionnée:', duration);
  
  // Réinitialiser la date personnalisée si on sélectionne un preset
  if (duration !== 'custom') {
    customExpirationDate.value = '';
  }
}

// Propriété calculée pour contrôler la progression des étapes
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 0) {
    // Étape 0: Un type de signature doit être sélectionné
    return signatureType.value !== '';
  } else if (currentStep.value === 1 && signatureType.value === 'ephemeral') {
    // Étape 1: Configuration expiration pour signatures éphémères
    if (selectedDuration.value === 'custom') {
      return customExpirationDate.value !== '' && expirationDate.value > new Date();
    }
    return selectedDuration.value !== '';
  } else if (currentStep.value === 2 || (currentStep.value === 1 && signatureType.value === 'permanent')) {
    // Étape sélection documents: Au moins un fichier PDF doit être sélectionné
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 3 || (currentStep.value === 2 && signatureType.value === 'permanent')) {
    // Étape prévisualisation: Les prévisualisations doivent être chargées
    return selectedFiles.value.length > 0;
  } else if (currentStep.value === 4 || (currentStep.value === 3 && signatureType.value === 'permanent')) {
    // Étape positionnement: Tous les documents doivent avoir leurs positions confirmées
    return selectedFiles.value.every((_, index) => 
      documentPositions.value[index]?.completed === true
    );
  } else if (currentStep.value === 5 || (currentStep.value === 4 && signatureType.value === 'permanent')) {
    // Étape certificat: Le certificat et le mot de passe doivent être fournis
    return certificateFile.value !== null && certificatePassword.value.trim() !== '';
  }
  
  return true;
});

// Méthodes de navigation entre les étapes
function nextStep() {
  console.log('nextStep appelée, currentStep:', currentStep.value, 'signatureType:', signatureType.value);
  
  if (!canProceedToNextStep.value) {
    console.log('Impossible de passer à l\'étape suivante');
    return;
  }
  
  // Logique spéciale pour le workflow éphémère vs permanent
  if (currentStep.value === 0) {
    // Depuis l'étape de choix du type
    if (signatureType.value === 'permanent') {
      // Skip l'étape de configuration et aller directement à la sélection
      currentStep.value = 2;
      console.log('Signature permanente: saut vers sélection documents (étape 2)');
    } else {
      // Aller à la configuration expiration
      currentStep.value = 1;
      console.log('Signature éphémère: vers configuration expiration (étape 1)');
    }
  } else if (currentStep.value === 1 && signatureType.value === 'ephemeral') {
    // Depuis la configuration expiration vers sélection documents
    currentStep.value = 2;
    console.log('Configuration finie: vers sélection documents (étape 2)');
  } else if (currentStep.value < steps.length - 1) {
    // Navigation normale pour les autres étapes
    currentStep.value++;
    console.log('Navigation normale vers étape:', currentStep.value);
  }
  
  // Actions spécifiques selon l'étape atteinte
  if (currentStep.value === 3 || (currentStep.value === 2 && signatureType.value === 'permanent')) {
    // Arrivée à l'étape de prévisualisation
    console.log('Création des prévisualisations pour', selectedFiles.value.length, 'documents');
    createDocumentPreviews();
     } else if (currentStep.value === 6) {
     // Arrivée à l'étape de signature
     console.log('Démarrage du processus de signature');
     startSigningProcess();
   }
}

function prevStep() {
  if (currentStep.value > 0) {
    // Logique spéciale pour revenir en arrière avec les signatures éphémères
    if (currentStep.value === 2 && signatureType.value === 'permanent') {
      // Si on est à la sélection et type permanent, revenir au choix du type
      currentStep.value = 0;
    } else if (currentStep.value === 2 && signatureType.value === 'ephemeral') {
      // Si on est à la sélection et type éphémère, revenir à la configuration
      currentStep.value = 1;
    } else {
      // Navigation normale
      currentStep.value--;
    }
  }
}

// Méthodes de manipulation des fichiers
function triggerFileInput() {
  fileInput.value.click();
}

function triggerCertificateInput() {
  certificateInput.value.click();
}

function handleFileSelection(event) {
  const files = Array.from(event.target.files);
  addFiles(files);
}

function handleFileDrop(event) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer.files);
  addFiles(files);
}

function addFiles(files) {
  const pdfFiles = files.filter(file => file.type === 'application/pdf' && file.size <= 10 * 1024 * 1024);
  
  pdfFiles.forEach(file => {
    // Vérifier si le fichier n'est pas déjà dans la liste
    const exists = selectedFiles.value.some(existingFile => 
      existingFile.name === file.name && existingFile.size === file.size
    );
    
    if (!exists) {
      selectedFiles.value.push(file);
    }
  });
  
  // Si c'est le premier fichier ajouté, le définir comme onglet actif
  if (activeDocumentIndex.value >= selectedFiles.value.length) {
    activeDocumentIndex.value = selectedFiles.value.length - 1;
  }
}

function removeDocument(index) {
  selectedFiles.value.splice(index, 1);
  documentPreviews.value.splice(index, 1);
  delete documentTotalPages.value[index];
  
  // Ajuster l'index de l'onglet actif
  if (activeDocumentIndex.value >= selectedFiles.value.length) {
    activeDocumentIndex.value = Math.max(0, selectedFiles.value.length - 1);
  }
  
  // Ajuster l'index du document de référence
  if (referenceDocumentIndex.value >= selectedFiles.value.length) {
    referenceDocumentIndex.value = Math.max(0, selectedFiles.value.length - 1);
  }
}

function setActiveDocument(index) {
  activeDocumentIndex.value = index;
}

function truncateFileName(fileName, maxLength) {
  if (fileName.length <= maxLength) return fileName;
  const extension = fileName.split('.').pop();
  const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
  const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4);
  return `${truncatedName}...${extension}`;
}

function handleCertificateSelection(event) {
  const file = event.target.files[0];
  if (file && file.name.toLowerCase().endsWith('.pfx')) {
    certificateFile.value = file;
  }
}

function handleCertificateDrop(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file && file.name.toLowerCase().endsWith('.pfx')) {
    certificateFile.value = file;
  }
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

// Créer les prévisualisations pour tous les documents
function createDocumentPreviews() {
  console.log('Création des prévisualisations pour', selectedFiles.value.length, 'documents');
  
  documentPreviews.value = selectedFiles.value.map((file, index) => {
    const preview = {
      loading: true,
      error: null,
      url: null
    };
    
    console.log(`Création prévisualisation pour ${file.name} (index ${index})`);
    
    // Créer l'URL de prévisualisation immédiatement
    try {
      const fileUrl = URL.createObjectURL(file);
      preview.url = fileUrl;
      preview.loading = false;
      console.log(`URL créée pour ${file.name}:`, fileUrl);
    } catch (error) {
      console.error(`Erreur création URL pour ${file.name}:`, error);
      preview.error = 'Erreur de chargement';
      preview.loading = false;
    }
    
    return preview;
  });
  
  console.log('Prévisualisations créées:', documentPreviews.value);
}

// Gérer la confirmation de position depuis QrPositioner
function handleIndividualPositionConfirmed(positionData) {
  console.log('Positions confirmées pour le document', activePositioningIndex.value, ':', positionData);
  
  // Stocker les positions pour le document actuel
  if (!documentPositions.value[activePositioningIndex.value]) {
    documentPositions.value[activePositioningIndex.value] = {};
  }
  
  documentPositions.value[activePositioningIndex.value].qr_position = positionData.qr;
  
  if (positionData.signature) {
    documentPositions.value[activePositioningIndex.value].signature = {
      image: uploadedSignatureImage.value,
      positions: positionData.signature.positions,
      size: positionData.signature.size  // Ajouter la taille de signature
    };
  }
  
  // Marquer que ce document a des positions définies
  documentPositions.value[activePositioningIndex.value].hasPositions = true;
  
  // **NOUVEAU** : Marquer automatiquement le document comme terminé
  documentPositions.value[activePositioningIndex.value].completed = true;
  
  console.log('Document', activePositioningIndex.value, 'automatiquement marqué comme terminé après confirmation des positions');
  console.log('Paramètres de position stockés pour le document', activePositioningIndex.value, ':', documentPositions.value[activePositioningIndex.value]);
  
  // Passer automatiquement au document suivant s'il y en a un non terminé
  const nextIncomplete = selectedFiles.value.findIndex((_, index) => 
    index > activePositioningIndex.value && !documentPositions.value[index]?.completed
  );
  
  if (nextIncomplete !== -1) {
    console.log('Passage automatique au document suivant non terminé:', nextIncomplete);
    activePositioningIndex.value = nextIncomplete;
  } else {
    console.log('Tous les documents suivants sont terminés ou il n\'y en a plus');
  }
}

// Gérer l'upload de signature depuis QrPositioner
function handleIndividualSignatureUploaded(signatureFile) {
  console.log('Signature uploadée pour le document', activePositioningIndex.value, ':', signatureFile);
  
  // Convertir le fichier en base64
  const reader = new FileReader();
  reader.onloadend = function() {
    uploadedSignatureImage.value = reader.result;
    console.log('Signature convertie en base64');
  };
  reader.readAsDataURL(signatureFile);
}

// Lancer le processus de signature pour tous les documents
async function startSigningProcess() {
  console.log('Démarrage du processus de signature');
  console.log('Démarrage du processus de signature pour', selectedFiles.value.length, 'documents');
  
  signatureStatus.value = 'loading';
  currentProcessingDocument.value = 0;
  completedDocuments.value = [];
  signedDocuments.value = [];
  signatureError.value = '';
  
  try {
    // Obtenir les informations de l'utilisateur connecté
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    console.log('Informations utilisateur:', userInfo);
    
    // Signer chaque document séquentiellement
    for (let i = 0; i < selectedFiles.value.length; i++) {
      currentProcessingDocument.value = i;
      console.log(`Signature du document ${i + 1}/${selectedFiles.value.length}: ${selectedFiles.value[i].name}`);
      
      const file = selectedFiles.value[i];
      
      // Debug - vérifier les paramètres de position pour ce document spécifique
      const documentPosition = documentPositions.value[i];
      console.log(`Paramètres de position pour le document ${i} (${file.name}):`, documentPosition);
      
      // Extraire les positions QR pour ce document spécifique
      let qrX = 85; // valeur par défaut
      let qrY = 90; // valeur par défaut
      
      if (documentPosition?.qr_position?.positions) {
        // Vérifier si positions est un objet avec des clés numériques
        if (typeof documentPosition.qr_position.positions === 'object' && 
            !Array.isArray(documentPosition.qr_position.positions)) {
          
          console.log('Positions QR sous format objet, extraction de la première position');
          const firstPageKey = Object.keys(documentPosition.qr_position.positions)[0];
          if (firstPageKey && documentPosition.qr_position.positions[firstPageKey]) {
            const firstPosition = documentPosition.qr_position.positions[firstPageKey];
            qrX = firstPosition.x || 85;
            qrY = firstPosition.y || 90;
            console.log(`Position QR extraite de la page ${firstPageKey}: x=${qrX}, y=${qrY}`);
          }
        } else if (Array.isArray(documentPosition.qr_position.positions) && 
                   documentPosition.qr_position.positions.length > 0) {
          
          console.log('Positions QR sous format tableau, extraction de la première position');
          const firstPosition = documentPosition.qr_position.positions[0];
          qrX = firstPosition.x || 85;
          qrY = firstPosition.y || 90;
          console.log(`Position QR extraite du tableau: x=${qrX}, y=${qrY}`);
        }
      } else if (documentPosition?.qr_position?.x && documentPosition?.qr_position?.y) {
        // Position unique
        qrX = documentPosition.qr_position.x;
        qrY = documentPosition.qr_position.y;
        console.log(`Position QR unique: x=${qrX}, y=${qrY}`);
      }
      
      // Créer les métadonnées utilisateur avec les paramètres de position pour ce document
      const userMetadata = {
        user_id: userInfo.id || '',
        username: userInfo.username || '',
        email: userInfo.email || '',
        full_name: userInfo.fullName || '',
        organization: userInfo.organization || '',
        organization_id: userInfo.organizationId || '',
        signer_role: userInfo.position || userInfo.role || '',
        jwt_token: localStorage.getItem('jwtToken') || '',
        qr_position: {
          x: qrX,
          y: qrY,
          size: documentPosition?.qr_position?.size || 'medium',
          pages: documentPosition?.qr_position?.pages || 'all',
          positions: documentPosition?.qr_position?.positions || [],
          mode: documentPosition?.qr_position?.mode || 'all'
        },
        signature_position: null
      };
      
      console.log('Métadonnées QR position préparées pour le document', i, ':', {
        qr_position: userMetadata.qr_position
      });
      
      // Ajouter les informations de signature si disponibles pour ce document
      if (documentPosition?.signature && documentPosition?.signature?.image) {
        let signatureImage = documentPosition.signature.image;
        
        console.log('DEBUG SIGNATURE IMAGE - État initial pour document', i, ':', {
          'image_exists': !!signatureImage,
          'image_type': typeof signatureImage,
          'image_length': signatureImage?.length || 0,
          'image_starts_with_data': signatureImage?.startsWith('data:image'),
          'image_preview': signatureImage?.substring(0, 100) + '...'
        });
        
        // S'assurer que l'image est au bon format
        if (signatureImage && !signatureImage.startsWith('data:image')) {
          console.warn('Format d\'image incorrect, tentative de correction');
          let imageType = 'png';
          if (signatureImage.startsWith('/9j/')) {
            imageType = 'jpeg';
          }
          signatureImage = `data:image/${imageType};base64,${signatureImage}`;
          console.log('Image corrigée:', signatureImage.substring(0, 100) + '...');
        }
        
        // Convertir les positions de signature en format attendu par le microservice
        let signaturePositions = [];
        console.log('DEBUG SIGNATURE POSITIONS - Positions brutes pour document', i, ':', documentPosition.signature.positions);
        
        if (documentPosition.signature.positions) {
          if (typeof documentPosition.signature.positions === 'object' && 
              !Array.isArray(documentPosition.signature.positions)) {
            
            console.log('Conversion des positions de signature du format objet au format tableau');
            Object.entries(documentPosition.signature.positions).forEach(([pageKey, position]) => {
              if (pageKey === 'default') {
                // Pour les positions par défaut (mode "all"), envoyer une seule position avec page: "all"
                console.log('Mode "all" détecté, envoi d\'une position avec page: "all"');
                
                const convertedPosition = {
                  page: "all",
                  x: position.x,
                  y: position.y,
                  width: 20,
                  height: 10
                };
                signaturePositions.push(convertedPosition);
                
                console.log('Position avec mode "all" générée');
              } else {
                // Positions individuelles par page
                const pageNumber = parseInt(pageKey);
                
                // Vérifier que pageNumber est valide
                if (!isNaN(pageNumber)) {
                  const convertedPosition = {
                    page: pageNumber,
                    x: position.x,
                    y: position.y,
                    width: 20,
                    height: 10
                  };
                  signaturePositions.push(convertedPosition);
                  console.log(`Position signature page ${pageNumber}:`, convertedPosition);
                }
              }
            });
          } else if (Array.isArray(documentPosition.signature.positions)) {
            signaturePositions = documentPosition.signature.positions;
            console.log('Positions signature déjà en format tableau:', signaturePositions);
          }
        }
        
        userMetadata.signature_position = {
          positions: signaturePositions,
          signature_image: signatureImage,
          signature_size: documentPosition.signature?.size || 50  // Ajouter la taille de signature
        };
        
        console.log('DEBUG SIGNATURE FINAL - Données finales pour document', i, ':', {
          'positions_count': userMetadata.signature_position.positions?.length || 0,
          'image_disponible': !!userMetadata.signature_position.signature_image,
          'image_final_format': userMetadata.signature_position.signature_image?.startsWith('data:image'),
          'positions_detail': userMetadata.signature_position.positions
        });
      }
      
      // Créer un FormData pour l'envoi au microservice
      const formData = new FormData();
      formData.append('document', file);
      formData.append('certificate', certificateFile.value);
      formData.append('password', certificatePassword.value);
      formData.append('metadata', JSON.stringify(userMetadata));
      
      // 🆕 AJOUTER LES DONNÉES D'EXPIRATION POUR SIGNATURES ÉPHÉMÈRES
      if (signatureType.value === 'ephemeral' && expirationDate.value) {
        formData.append('expires_at', expirationDate.value.toISOString());
        console.log('Signature éphémère configurée, expiration:', expirationDate.value.toISOString());
      } else {
        console.log('Signature pérenne configurée (pas d\'expiration)');
      }
      
      if (userInfo.id) {
        formData.append('owner_id', userInfo.id);
      }
      
      // Gestion organisation
      const orgId = userInfo.organizationId || (userInfo.organization && userInfo.organization.id);
      const orgName = userInfo.organizationName || (userInfo.organization && userInfo.organization.name);
      
      if (orgId) formData.append('organization_id', orgId);
      if (orgName) formData.append('organization_name', orgName);
      
      console.log('Envoi de la requête de signature pour:', file.name);
      
      // URL de l'API gateway
      const apiUrl = 'https://ppd.camgovca.cm/sign/sign';
      
      // Appel à l'API gateway
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage;
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || 'Erreur inconnue';
        } catch {
          errorMessage = errorText || 'Erreur de communication avec le serveur';
        }
        throw new Error(`Erreur lors de la signature de ${file.name}: ${errorMessage}`);
      }
      
      // Récupérer le document signé
      const blob = await response.blob();
      console.log('Document signé reçu pour:', file.name, 'Taille:', blob.size);
      
      const signedDocUrl = URL.createObjectURL(blob);
      
      // Ajouter le document signé à la liste
      signedDocuments.value.push({
        name: file.name.replace('.pdf', '_signed.pdf'),
        url: signedDocUrl,
        originalIndex: i
      });
      
      // Marquer ce document comme terminé
      completedDocuments.value.push(i);
      console.log(`Document ${i + 1} signé avec succès`);
    }
    
    // Tous les documents sont signés
    signatureDate.value = new Date().toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    console.log('Tous les documents ont été signés avec succès');
    
    // Passer à l'étape de téléchargement
    currentStep.value = 7;
    signatureStatus.value = 'success';
    
  } catch (error) {
    console.error('Erreur lors de la signature:', error);
    signatureStatus.value = 'error';
    signatureError.value = error.message || 'Une erreur est survenue lors de la signature des documents.';
  }
}

// Télécharger tous les documents signés
function downloadAllDocuments() {
  signedDocuments.value.forEach(doc => {
    const link = document.createElement('a');
    link.href = doc.url;
    link.download = doc.name;
    link.click();
  });
}

// Méthode pour fermer le composant
function closeSignature() {
  // Nettoyer les ressources
  documentPreviews.value.forEach(preview => {
    if (preview.url) {
      URL.revokeObjectURL(preview.url);
    }
  });
  
  signedDocuments.value.forEach(doc => {
    if (doc.url) {
      URL.revokeObjectURL(doc.url);
    }
  });
  
  emit('close');
}

function setActivePositioningDocument(index) {
  activePositioningIndex.value = index;
  console.log('Document de positionnement actif:', index);
}

function previousPositioningDocument() {
  if (activePositioningIndex.value > 0) {
    activePositioningIndex.value--;
  }
}

function nextPositioningDocument() {
  if (activePositioningIndex.value < selectedFiles.value.length - 1) {
    activePositioningIndex.value++;
  }
}

// Permettre la modification du positionnement d'un document terminé
function editDocumentPositioning() {
  if (documentPositions.value[activePositioningIndex.value]) {
    documentPositions.value[activePositioningIndex.value].completed = false;
    console.log('Mode édition activé pour le document', activePositioningIndex.value);
  }
}



</script>

<style scoped>
.sign-document-container {
  background-color: var(--bg-color, #f8f9fa);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 100%;
  animation: fade-in 0.3s ease-in-out;
}

/* Progression des étapes */
.steps-progress {
  display: flex;
  justify-content: space-between;
  margin: 25px 0;
  position: relative;
}

.steps-progress::before {
  content: '';
  position: absolute;
  top: 14px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--border-color, rgba(0, 0, 0, 0.1));
  z-index: 1;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
  flex: 1;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: var(--bg-secondary, #e9ecef);
  color: var(--text-muted, #6c757d);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background-color: var(--primary-color, #3a86ff);
  color: white;
  box-shadow: 0 2px 8px rgba(58, 134, 255, 0.3);
}

.step.completed .step-number {
  background-color: var(--success-color, #28a745);
  color: white;
}

.step-label {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  font-weight: 500;
  text-align: center;
}

.step.active .step-label {
  color: var(--primary-color, #3a86ff);
  font-weight: 600;
}

.step.completed .step-label {
  color: var(--success-color, #28a745);
}

/* Contenu des étapes */
.step-content {
  min-height: 400px;
  padding: 0 10px;
}

.step-body {
  animation: fade-in 0.3s ease-in-out;
}

/* Zone d'upload */
.upload-area {
  border: 2px dashed var(--border-color, #dee2e6);
  border-radius: 10px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: var(--bg-light, #f8f9fa);
  margin-bottom: 20px;
}

.upload-area.multiple {
  background: linear-gradient(135deg, rgba(58, 134, 255, 0.03), rgba(0, 123, 255, 0.01));
  border-color: rgba(58, 134, 255, 0.3);
}

.upload-area:hover {
  border-color: var(--primary-color, #3a86ff);
  background-color: rgba(58, 134, 255, 0.05);
}

.upload-area i {
  font-size: 3rem;
  color: var(--primary-color, #3a86ff);
  margin-bottom: 15px;
  display: block;
}

.upload-area p {
  margin: 0 0 10px;
  font-size: 1.1rem;
  color: var(--text-color, #333);
}

.upload-hint {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.file-input {
  display: none;
}

/* Styles pour la grille des documents */
.selected-documents-list {
  margin-top: 25px;
}

.selected-documents-list h4 {
  margin-bottom: 15px;
  color: var(--text-color, #333);
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 15px;
}

.document-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  padding: 15px;
  position: relative;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.document-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.document-icon {
  font-size: 2rem;
  color: #dc3545;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #dc3545;
  font-size: 1.2rem;
  padding: 0;
  transition: all 0.2s;
}

.remove-btn:hover {
  transform: scale(1.1);
}

.document-info {
  text-align: left;
}

.document-name {
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-size {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

/* Styles pour les onglets */
.documents-tabs {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.tabs-header {
  display: flex;
  background: #f8f9fa;
  overflow-x: auto;
  border-bottom: 2px solid #e9ecef;
}

.tab-button {
  background: none;
  border: none;
  padding: 12px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted, #6c757d);
  font-weight: 500;
  transition: all 0.2s;
  position: relative;
  min-width: 150px;
  justify-content: center;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background: rgba(0, 0, 0, 0.02);
  color: var(--text-color, #333);
}

.tab-button.active {
  color: var(--primary-color, #3a86ff);
  background: white;
  border-bottom-color: var(--primary-color, #3a86ff);
}

.tab-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 120px;
}

.tab-remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #dc3545;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
  font-size: 0.8rem;
}

.tab-remove-btn:hover {
  background: rgba(220, 53, 69, 0.1);
}

.tab-content {
  padding: 20px;
}

.document-info-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.document-details {
  flex: 1;
}

.document-details .document-name {
  font-size: 1.1rem;
  margin-bottom: 5px;
}

/* Prévisualisation PDF */
.pdf-preview-container {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
  min-height: 600px;
  position: relative;
}

.pdf-preview {
  width: 100%;
  height: 600px;
  border: none;
  background: white;
}

.pdf-loading,
.pdf-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 600px;
  color: var(--text-muted, #6c757d);
}

.pdf-loading i,
.pdf-error i {
  font-size: 3rem;
  margin-bottom: 15px;
}

.pdf-error i {
  color: var(--danger, #dc3545);
}

/* Styles pour le positionnement */
.positioning-info-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 152, 0, 0.05));
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.positioning-info-banner i {
  font-size: 2.5rem;
  color: #ff9800;
}

.positioning-info-banner h4 {
  margin: 0 0 5px;
  color: var(--text-color, #333);
  font-size: 1.2rem;
}

.positioning-info-banner p {
  margin: 0;
  color: var(--text-muted, #6c757d);
  line-height: 1.4;
}

.reference-document-selector {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.reference-document-selector label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-color, #333);
}

.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: var(--text-color, #333);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.form-select:hover {
  border-color: var(--primary-color, #3a86ff);
}

.form-select:focus {
  outline: none;
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 0 0 3px rgba(58, 134, 255, 0.1);
}

/* Certificat et mot de passe */
.certificate-info-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  background: linear-gradient(135deg, rgba(108, 117, 125, 0.1), rgba(73, 80, 87, 0.05));
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  border: 1px solid rgba(108, 117, 125, 0.2);
}

.certificate-info-banner i {
  font-size: 2.5rem;
  color: #6c757d;
}

.certificate-form {
  max-width: 500px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-color, #333);
}

.upload-area.small {
  padding: 20px;
  margin-bottom: 0;
}

.certificate-name {
  color: var(--success-color, #28a745);
  font-weight: 600;
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  width: 100%;
  padding: 10px 40px 10px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.2s;
}

.password-input:focus {
  outline: none;
  border-color: var(--primary-color, #3a86ff);
  box-shadow: 0 0 0 3px rgba(58, 134, 255, 0.1);
}

.toggle-password-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted, #6c757d);
  padding: 8px;
  transition: all 0.2s;
}

.toggle-password-btn:hover {
  color: var(--primary-color, #3a86ff);
}

/* Signature en cours */
.signature-processing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
}

.processing-animation {
  position: relative;
  margin-bottom: 30px;
}

.processing-animation i {
  font-size: 4rem;
  color: var(--primary-color, #3a86ff);
}

.pulsing {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

.spinner-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.spinner {
  width: 80px;
  height: 80px;
  border: 4px solid rgba(58, 134, 255, 0.1);
  border-top-color: var(--primary-color, #3a86ff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.processing-text {
  font-size: 1.1rem;
  color: var(--text-color, #333);
  margin-bottom: 30px;
}

/* Progression des documents */
.documents-processing {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.document-processing-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  margin-bottom: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.document-processing-item.current {
  background: linear-gradient(135deg, rgba(58, 134, 255, 0.1), rgba(0, 123, 255, 0.05));
  border: 1px solid rgba(58, 134, 255, 0.3);
}

.document-processing-item.completed {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(32, 201, 151, 0.05));
  border: 1px solid rgba(40, 167, 69, 0.3);
}

.processing-icon i {
  font-size: 1.2rem;
}

.document-processing-item.pending .processing-icon i {
  color: #dee2e6;
}

.document-processing-item.current .processing-icon i {
  color: var(--primary-color, #3a86ff);
}

.document-processing-item.completed .processing-icon i {
  color: var(--success-color, #28a745);
}

/* Erreur de signature */
.signature-error {
  text-align: center;
  padding: 40px;
}

.signature-error i {
  font-size: 3rem;
  color: var(--danger, #dc3545);
  margin-bottom: 20px;
}

.signature-error h4 {
  color: var(--danger, #dc3545);
  margin-bottom: 15px;
}

.signature-error p {
  color: var(--text-muted, #6c757d);
  line-height: 1.5;
}

/* Signature complète */
.signature-complete {
  text-align: center;
  padding: 40px 20px;
}

.success-animation {
  margin-bottom: 30px;
}

.success-animation i {
  font-size: 4rem;
  color: var(--success-color, #28a745);
  animation: success-bounce 0.6s ease-out;
}

@keyframes success-bounce {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.signature-complete h3 {
  color: var(--success-color, #28a745);
  margin-bottom: 15px;
}

.signature-complete p {
  color: var(--text-muted, #6c757d);
  margin-bottom: 30px;
}

/* Documents signés */
.signed-documents-list {
  margin-top: 30px;
  text-align: left;
}

.signed-documents-list h4 {
  text-align: center;
  margin-bottom: 25px;
  color: var(--text-color, #333);
}

.signed-documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.signed-document-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 350px;
}

.signed-document-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.signed-card-header {
  background: linear-gradient(135deg, var(--success-color, #28a745), #20c997);
  color: white;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.signed-card-header::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 15px solid transparent;
  border-right: 15px solid transparent;
  border-top: 10px solid #20c997;
}

.signed-document-card .document-icon.large {
  font-size: 3rem;
  color: white;
  margin: 0;
}

.document-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.signed-card-body {
  padding: 30px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.signed-document-card .document-name {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-color, #333);
  line-height: 1.4;
  margin: 0;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.signature-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  margin: 0;
}

.document-size-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-muted, #6c757d);
  font-style: italic;
}

.signed-card-footer {
  padding: 0 30px 30px 30px;
  margin-top: auto;
}

.download-button {
  background: linear-gradient(135deg, var(--primary-color, #3a86ff), #007bff);
  color: white;
  text-decoration: none;
  padding: 18px 30px;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(58, 134, 255, 0.3);
  width: 100%;
}

.download-button:hover {
  background: linear-gradient(135deg, var(--primary-dark, #2970cf), #0056b3);
  color: white;
  text-decoration: none;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 134, 255, 0.4);
}

.download-button i {
  font-size: 1.1rem;
}

.download-all-section {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
}

.download-all-button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 10px;
}

.download-all-button:hover {
  background-color: #218838;
  transform: translateY(-1px);
}

.download-note {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
  margin: 0;
}

/* Navigation */
.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #e9ecef;
  margin-top: 30px;
}

.nav-button {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.nav-button.primary {
  background-color: var(--primary-color, #3a86ff);
  color: white;
}

.nav-button.primary:hover:not(:disabled) {
  background-color: var(--primary-hover, #2969d6);
  transform: translateY(-1px);
}

.nav-button.secondary {
  background-color: #6c757d;
  color: white;
}

.nav-button.secondary:hover {
  background-color: #5a6268;
  transform: translateY(-1px);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spacer {
  flex: 1;
}

/* Section card et header */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  height: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-color, #333);
  margin: 0;
}

.section-title i {
  color: #ff9800;
}

.close-button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted, #6c757d);
  font-size: 1.2rem;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--text-color, #333);
}

/* Banner d'information */
.template-info-banner,
.positioning-info-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 193, 7, 0.05));
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.template-info-banner i,
.positioning-info-banner i {
  font-size: 2.5rem;
  color: #ff9800;
}

.template-info-banner h4,
.positioning-info-banner h4 {
  margin: 0 0 5px;
  color: var(--text-color, #333);
  font-size: 1.2rem;
}

.template-info-banner p,
.positioning-info-banner p {
  margin: 0;
  color: var(--text-muted, #6c757d);
  line-height: 1.4;
}

/* Onglets de positionnement */
.positioning-tabs {
  margin-bottom: 30px;
}

.positioning-tab {
  position: relative;
  min-width: 200px;
  border-radius: 12px 12px 0 0 !important;
  border-bottom: none !important;
}

.positioning-tab.completed {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(139, 195, 74, 0.05));
  border-color: rgba(76, 175, 80, 0.3);
}

.positioning-tab .tab-content {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.positioning-tab .tab-title {
  flex: 1;
  text-align: left;
  font-weight: 500;
}

.positioning-tab .tab-status {
  flex-shrink: 0;
}

.positioning-tab .tab-status i {
  font-size: 1rem;
}

.positioning-tab .tab-status .bi-check-circle-fill {
  color: #4caf50;
}

.positioning-tab .tab-status .bi-circle-half {
  color: #ff9800;
}

.positioning-tab .tab-status .bi-circle {
  color: #bbb;
}

/* Contenu de l'onglet de positionnement */
.tab-content-positioning {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 0 12px 12px 12px;
  padding: 25px;
  min-height: 600px;
}

.document-positioning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.document-positioning-header .document-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.document-positioning-header .document-icon {
  font-size: 2rem;
  color: #dc3545;
}

.document-positioning-header .document-details {
  flex: 1;
}

.document-positioning-header .document-name {
  font-weight: 600;
  color: var(--text-color, #333);
  margin-bottom: 5px;
}

.document-positioning-header .document-progress {
  font-size: 0.9rem;
  color: var(--text-muted, #6c757d);
  display: flex;
  align-items: center;
  gap: 10px;
}

.document-positioning-header .status-completed {
  color: #4caf50;
  font-weight: 500;
}

.document-positioning-header .status-pending {
  color: #ff9800;
  font-weight: 500;
}

.document-navigation {
  display: flex;
  gap: 8px;
}

.nav-doc-btn {
  padding: 8px 12px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-color, #333);
  transition: all 0.2s;
  font-size: 1.1rem;
}

.nav-doc-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.nav-doc-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Actions de positionnement */
.positioning-actions {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.document-completed-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(139, 195, 74, 0.05));
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 8px;
  color: #2e7d32;
  font-weight: 500;
}

.document-completed-info i {
  font-size: 1.2rem;
  color: #4caf50;
}

.positioning-instructions {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 15px 20px;
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1), rgba(100, 181, 246, 0.05));
  border: 1px solid rgba(33, 150, 243, 0.3);
  border-radius: 8px;
  color: #1565c0;
  font-weight: 500;
  text-align: center;
  max-width: 600px;
}

.positioning-instructions i {
  font-size: 1.2rem;
  color: #2196f3;
  flex-shrink: 0;
  margin-top: 2px;
}

.positioning-instructions span {
  line-height: 1.4;
}

.confirm-positioning-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #4caf50, #66bb6a);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.confirm-positioning-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #43a047, #5cb85c);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.confirm-positioning-btn:disabled {
  background: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.edit-positioning-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #ff9800, #ffa726);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.edit-positioning-btn:hover {
  background: linear-gradient(135deg, #f57c00, #ff9800);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4);
}

/* Résumé du positionnement */
.positioning-summary {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-top: 25px;
}

.positioning-summary h5 {
  margin: 0 0 15px;
  color: var(--text-color, #333);
  font-weight: 600;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.summary-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.summary-text {
  flex: 1;
}

.summary-filename {
  font-weight: 500;
  color: var(--text-color, #333);
  margin-bottom: 2px;
}

.summary-status {
  font-size: 0.85rem;
  color: var(--text-muted, #6c757d);
}

.text-success {
  color: #4caf50 !important;
}

.text-warning {
  color: #ff9800 !important;
}

.text-muted {
  color: #6c757d !important;
}

/* Animations */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.spinning {
  animation: spin 1.5s linear infinite;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: var(--primary-color, #3a86ff);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.retry-btn:hover {
  background-color: var(--primary-hover, #2969d6);
  transform: translateY(-1px);
}

/* Responsive styles */
@media (max-width: 768px) {
  .steps-progress {
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .steps-progress::before {
    display: none;
  }
  
  .step {
    width: 30%;
    margin-bottom: 10px;
  }
  
  .step-navigation {
    flex-direction: column;
    gap: 10px;
  }
  
  .nav-button {
    width: 100%;
  }
  
  .spacer {
    display: none;
  }
  
  .pdf-preview-container {
    height: 300px;
  }
  
  .documents-grid {
    grid-template-columns: 1fr;
  }
  
  .tabs-header {
    flex-direction: column;
  }
  
  .tab-button {
    min-width: auto;
    width: 100%;
    justify-content: space-between;
  }
  
  .signed-documents-grid {
    grid-template-columns: 1fr;
  }
  
  .signed-document-card {
    flex-direction: column;
    text-align: center;
  }
  
  .document-processing-item {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
}

@media (max-width: 576px) {
  .template-info-banner,
  .positioning-info-banner,
  .certificate-info-banner {
    flex-direction: column;
    text-align: center;
  }
  
  .section-title {
    font-size: 1.1rem;
  }
}

@media (max-width: 1200px) {
  .signed-documents-grid {
    grid-template-columns: 1fr;
    gap: 25px;
  }
}

@media (max-width: 480px) {
  .signed-document-card {
    min-height: 280px;
  }
  
  .signed-card-header .document-icon.large {
    font-size: 2.2rem;
  }
  
  .document-status-badge {
    font-size: 0.75rem;
    padding: 4px 8px;
  }
}

/* 🆕 STYLES POUR SIGNATURES ÉPHÉMÈRES */

/* Sélection du type de signature */
.signature-type-selection {
  padding: 20px 0;
}

.intro-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  color: white;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.intro-banner i {
  font-size: 2.5rem;
  opacity: 0.9;
}

.intro-banner h4 {
  margin: 0 0 5px 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.intro-banner p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
}

.signature-type-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.signature-type-card {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
  position: relative;
  overflow: hidden;
}

.signature-type-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.signature-type-card.selected {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(58, 134, 255, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%);
  box-shadow: 0 10px 25px rgba(58, 134, 255, 0.15);
}

.type-icon {
  width: 70px;
  height: 70px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.type-icon.permanent {
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
}

.type-icon.ephemeral {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.signature-type-card:hover .type-icon {
  transform: scale(1.1) rotate(5deg);
}

.type-content h4 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: var(--text-color);
}

.type-content p {
  color: var(--text-secondary);
  margin: 0 0 15px 0;
  font-size: 0.95rem;
  line-height: 1.5;
}

.type-features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.type-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.type-features li i {
  color: var(--primary-color);
  font-size: 0.8rem;
}

.type-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
}

.type-badge.recommended {
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
}

.type-badge.new {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.selection-preview {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 15px 20px;
  margin-top: 20px;
}

.preview-content {
  display: flex;
  align-items: center;
  gap: 15px;
  color: var(--text-color);
}

.preview-content i {
  font-size: 1.5rem;
  color: var(--primary-color);
}

/* Configuration de l'expiration */
.expiration-configuration {
  padding: 20px 0;
}

.duration-presets h5 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: var(--text-color);
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.preset-btn {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 20px 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.preset-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.preset-btn.selected {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(58, 134, 255, 0.1), rgba(255, 255, 255, 0.9));
  box-shadow: 0 8px 20px rgba(58, 134, 255, 0.15);
}

.preset-btn.custom.selected {
  border-color: #ff9800;
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1), rgba(255, 255, 255, 0.9));
}

.preset-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary-color), #4c63d2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.preset-btn.custom .preset-icon {
  background: linear-gradient(135deg, #ff9800, #f57c00);
}

.preset-label {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.95rem;
}

.preset-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.3;
}

/* Configuration date personnalisée */
.custom-date-config {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.custom-date-config h5 {
  margin: 0 0 15px 0;
  color: var(--text-color);
  font-weight: 600;
}

.date-input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.date-input-group label {
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.9rem;
}

.custom-date-input {
  padding: 12px 15px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  background: var(--input-bg);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.custom-date-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(58, 134, 255, 0.1);
}

/* Aperçu de l'expiration */
.expiration-preview {
  margin-top: 25px;
}

.preview-card {
  background: linear-gradient(135deg, #e3f2fd, #f8f9ff);
  border: 1px solid rgba(58, 134, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
}

.preview-header {
  background: var(--primary-color);
  color: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-header h5 {
  margin: 0;
  font-weight: 600;
}

.preview-header i {
  font-size: 1.2rem;
}

.preview-content {
  padding: 20px;
}

.expiration-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  font-weight: 500;
  color: var(--text-secondary);
}

.info-item .value {
  font-weight: 600;
  color: var(--text-color);
}

/* Badge type de signature sur les documents */
.signature-type-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(5px);
}

.signature-type-badge.permanent {
  background: rgba(76, 175, 80, 0.9);
  color: white;
}

.signature-type-badge.ephemeral {
  background: rgba(255, 152, 0, 0.9);
  color: white;
}

.signature-type-badge i {
  font-size: 0.6rem;
}

/* Résumé de signature dans l'étape certificat */
.signature-summary {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  margin-top: 25px;
}

.signature-summary h5 {
  margin: 0 0 15px 0;
  color: var(--text-color);
  font-weight: 600;
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-color);
}

.summary-item i {
  color: var(--primary-color);
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .signature-type-options {
    grid-template-columns: 1fr;
  }
  
  .presets-grid {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
  
  .preset-btn {
    padding: 15px 10px;
  }
  
  .preset-icon {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
}
</style> 