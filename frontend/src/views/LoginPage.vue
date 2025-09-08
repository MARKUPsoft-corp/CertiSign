<template>
  <div class="login-page" :class="{'admin-theme': selectedRole === 'admin', 'superadmin-theme': selectedRole === 'superadmin'}">
    <!-- Modale des informations de l'organisation (redesigned) -->
    <div v-if="showOrgModal" class="org-modal-overlay">
      <div class="org-modal" :class="{'admin-theme': selectedRole === 'admin', 'superadmin-theme': selectedRole === 'superadmin'}">
        <div class="org-modal-header">
          <div class="org-modal-icon">
            <i class="fas fa-building"></i>
          </div>
          <div class="org-modal-titles">
            <h2>Configuration de votre organisation</h2>
            <p>Ces informations sont nécessaires pour finaliser votre compte administrateur</p>
          </div>
        </div>
        
        <div class="org-modal-content">
          <div class="org-modal-info">
            <div class="info-badge">
              <i class="fas fa-info-circle"></i>
              <span>Les champs marqués d'un astérisque (*) sont obligatoires</span>
            </div>
          </div>
          
          <form @submit.prevent="submitOrgInfo" class="org-form">
            <div class="form-group">
              <label for="orgName">Nom de l'organisation*</label>
              <div class="input-with-icon">
                <i class="fas fa-building"></i>
                <input 
                  type="text" 
                  id="orgName" 
                  v-model="orgInfo.name" 
                  required 
                  placeholder="Nom de votre organisation"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="orgRegistration">Numéro d'immatriculation*</label>
              <div class="input-with-icon">
                <i class="fas fa-id-card"></i>
                <input 
                  type="text" 
                  id="orgRegistration" 
                  v-model="orgInfo.registration_number" 
                  required 
                  placeholder="SIREN/SIRET ou autre numéro d'immatriculation"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="orgEmail">Email de contact*</label>
              <div class="input-with-icon">
                <i class="fas fa-envelope"></i>
                <input 
                  type="email" 
                  id="orgEmail" 
                  v-model="orgInfo.email" 
                  required 
                  placeholder="Email de contact de l'organisation"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="orgAddress">Adresse</label>
              <div class="input-with-icon textarea-container">
                <i class="fas fa-map-marker-alt"></i>
                <textarea 
                  id="orgAddress" 
                  v-model="orgInfo.address" 
                  placeholder="Adresse complète de l'organisation"
                ></textarea>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn-cancel" @click="cancelOrgInfo">
                <i class="fas fa-times"></i>
                <span>Annuler</span>
              </button>
              <button type="submit" class="btn-submit" :disabled="orgSubmitting">
                <template v-if="!orgSubmitting">
                  <i class="fas fa-check"></i>
                  <span>Soumettre</span>
                </template>
                <div v-else class="button-spinner"></div>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- Fond d'écran animé avec particules -->
    <div class="particles-background">
      <div v-for="(particle, index) in 50" :key="index" class="particle"></div>
    </div>
    
    <!-- Conteneur principal pour centrer le contenu de connexion -->
    <div class="container main-container">
      <div class="login-card">
        <!-- Bouton de retour stratégiquement placé -->
        <div class="strategic-back-button">
            <router-link to="/" class="back-button">
            <i class="fas fa-arrow-left"></i> Retour à l'accueil
            </router-link>
        </div>
        
        <!-- Connexion sécurisée en cours d'initialisation -->
        <div v-if="initializingSecureConnection" class="two-column-secure-layout">
          <!-- Colonne gauche pour la bannière -->
          <div class="banner-column animated fadeInUp">
            <div class="banner-container fullheight">
              <img src="@/assets/banniere.jpeg" alt="Bannière Doc@uthANTIC" class="banner-image">
            </div>
          </div>
          
          <!-- Colonne droite pour le message de chargement -->
          <div class="message-column">
            <div class="secure-connection-loader">
              <div class="spinner"></div>
              <p class="loader-text animated fadeIn">Initialisation de la connexion sécurisée...</p>
        </div>
      </div>
        </div>
        
        <!-- Échec de connexion sécurisée -->
        <div v-if="!initializingSecureConnection && !secureConnectionEstablished" class="two-column-secure-layout">
          <!-- Colonne gauche pour la bannière -->
          <div class="banner-column animated fadeInUp">
            <div class="banner-container fullheight">
              <img src="@/assets/banniere.jpeg" alt="Bannière Doc@uthANTIC" class="banner-image">
            </div>
        </div>

          <!-- Colonne droite pour le message d'erreur -->
          <div class="message-column">
            <div class="connection-error-container">
              <div class="error-icon-large"><i class="fas fa-exclamation-circle"></i></div>
              <h3>Erreur de connexion sécurisée</h3>
              <p>Impossible d'établir une connexion sécurisée avec le serveur.</p>
              <button class="retry-button" @click="retryConnection">
                <i class="fas fa-redo"></i> Réessayer
              </button>
            </div>
          </div>
        </div>

        <!-- Contenu principal (3 colonnes) quand la connexion sécurisée est établie -->
        <div v-if="!initializingSecureConnection && secureConnectionEstablished" class="three-column-layout">
          <!-- Colonne gauche pour la bannière uniquement -->
          <div class="left-column animated fadeInUp">
            <!-- Bannière à gauche qui s'affiche même pendant l'initialisation -->
            <div class="banner-container fullheight">
              <img src="@/assets/banniere.jpeg" alt="Bannière CertiSign" class="banner-image">
            </div>
            </div>
            
          <!-- Colonne centrale pour le certificat et mot de passe -->
          <div class="center-column animated fadeInUp">
            <!-- Titre de connexion stylisé -->
            <div class="header-text text-center">
              <h1 class="highlighted-title animated fadeIn">AUTHENTIFICATION</h1>
              <TypedText />
            </div>

            <!-- Sélecteur d'organisation -->
            <div class="organization-selector-container">
              <label class="organization-selector-label">Votre organisation</label>
              <div class="custom-select">
                <!-- En-tête du sélecteur -->
                <div class="select-selected" @click="toggleDropdown">
                  <div class="select-icon">
                    <i class="fas fa-building"></i>
                  </div>
                  <span v-if="selectedOrganization">{{ selectedOrganization.name }}</span>
                  <span v-else>Aucune organisation</span>
                  <i class="fas fa-chevron-down dropdown-arrow" :class="{'active': dropdownOpen}"></i>
                </div>
                
                <!-- Liste des organisations -->
                <div v-if="dropdownOpen" class="org-selector-full">
                  <!-- Barre de recherche d'organisation -->
                  <div class="org-search-container">
                    <div class="org-search-input-wrapper">
                      <i class="fas fa-search"></i>
                      <input 
                        type="text" 
                        class="org-search-input" 
                        placeholder="Rechercher une organisation..." 
                        v-model="orgSearchQuery"
                        @input="filterOrganizations"
                      />
                      <i v-if="orgSearchQuery" @click="clearSearch" class="fas fa-times clear-search"></i>
                    </div>
                  </div>
                  
                  <!-- Option Aucune organisation -->
                  <div class="org-list">
                    <div 
                      class="select-item special-item" 
                      :class="{'same-as-selected': !selectedOrganization}" 
                      @click="selectOrganization(null)">
                      <i class="fas fa-user"></i>
                      <span>Aucune organisation</span>
                    </div>
                    
                    <!-- Message si aucun résultat -->
                    <div v-if="filteredOrganizations.length === 0 && !loadingOrganizations" class="no-results-message">
                      <i class="fas fa-info-circle"></i>
                      <span>Aucune organisation ne correspond à votre recherche</span>
                    </div>
                    
                    <!-- Liste des organisations filtrées -->
                    <div 
                      v-for="org in filteredOrganizations" 
                      :key="org.id"
                      class="select-item" 
                      :class="{'same-as-selected': selectedOrganization && selectedOrganization.id === org.id}" 
                      @click="selectOrganization(org)">
                      <i class="fas fa-building"></i>
                      <span>{{ org.name }}</span>
                    </div>
                  </div>
                  
                  <!-- Information sur le total d'organisations -->
                  <div class="org-count-info">
                    <span>{{ filteredOrganizations.length }} organisation(s) sur {{ organizations.length }} au total</span>
                  </div>
                </div>
              </div>
              <!-- Message de chargement ou d'erreur -->
              <div v-if="loadingOrganizations" class="loading-message">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Chargement des organisations...</span>
              </div>
              <div v-if="organizationsError" class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <span>{{ organizationsError }}</span>
              </div>
            </div>
            
            <!-- Formulaire de certificat et mot de passe -->
            <div class="upload-section">
            <!-- Carte cliquable pour soumettre le certificat -->
            <div class="upload-card" @click="triggerFileInput">
              <div class="upload-icon-container">
                <i class="fas fa-upload upload-icon animated pulse"></i>
              </div>
              <h3 class="upload-title">Votre Certificat</h3>
              <p class="upload-text">{{ fileName ? fileName : "Soumettre son certificat" }}</p>
            </div>
            
            <!-- Input fichier caché -->
            <input type="file" ref="fileInput" @change="handleFileUpload" accept=".pfx" class="d-none" />

            <!-- Message d'erreur si fichier invalide -->
            <p v-if="invalidFile" class="error-message animated shake">Veuillez entrer un fichier valide.</p>

            <!-- Box pour le mot de passe, visible uniquement pour un fichier PFX -->
            <div v-if="showPasswordBox" class="password-container animated fadeIn">
              <div class="password-box">
                <div class="password-input-group">
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  class="password-input"
                  placeholder="Entrez votre mot de passe"
                  required
                />
                <span class="toggle-password" @click="togglePasswordVisibility">
                    <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </span>
              </div>
                <button class="submit-button" @click="submitForm">
                  <span v-if="!isLoading">Soumettre</span>
                  <div v-else class="button-spinner"></div>
                </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Colonne droite pour les statuts et messages -->
          <div class="right-column">
            <div class="status-content">
              <!-- Indicateur de progression du traitement -->
              <div v-if="isLoading && !isError" class="progress-container animated fadeIn">
                <div class="progress-step" :class="{ 'complete': processingStep >= 1 }">
                  <div class="step-circle">1</div>
                  <div class="step-label">Lecture du certificat</div>
                </div>
                <div class="progress-step" :class="{ 'complete': processingStep >= 2 }">
                  <div class="step-circle">2</div>
                  <div class="step-label">Chiffrement des données</div>
                </div>
                <div class="progress-step" :class="{ 'complete': processingStep >= 3 }">
                  <div class="step-circle">3</div>
                  <div class="step-label">Envoi au serveur</div>
                </div>
                <div class="progress-step" :class="{ 'complete': processingStep >= 4 }">
                  <div class="step-circle">4</div>
                  <div class="step-label">Vérification du certificat</div>
                </div>
                <p class="progress-message">{{ progressMessage }}</p>
              </div>
              
              <!-- Image d'illustration quand aucun traitement n'est en cours -->
              <div v-if="!isLoading && !isError && !isSuccess && !isExpired && !isRevoked" class="illustration-container">
                <img src="@/assets/images/secure-document.svg" alt="Document sécurisé" class="secure-document-image">
                <p class="illustration-text">Sélectionnez votre certificat pour commencer</p>
              </div>
              
              <!-- Message de succès -->
              <div v-if="isSuccess" class="success-container animated fadeIn">
                <div class="success-icon"><i class="fas fa-check-circle"></i></div>
                <h3>{{ successTitle }}</h3>
                <p>{{ successMessage }}</p>
              </div>

              <!-- Message d'erreur pour certificat invalide -->
              <div v-if="isError" class="error-container animated fadeIn">
                <div class="error-icon"><i class="fas fa-exclamation-circle"></i></div>
                <h3>{{ errorTitle }}</h3>
                <p>{{ errorMessage }}</p>
                <button v-if="isTimeout" @click="retrySubmit" class="retry-button">
                  <i class="fas fa-redo"></i> Réessayer
                </button>
              </div>

              <!-- Message d'erreur pour certificat expiré -->
              <div v-if="isExpired" class="error-container animated fadeIn">
                <div class="error-icon"><i class="fas fa-calendar-times"></i></div>
                <h3>Certificat expiré</h3>
                <p>{{ errorMessage || "Le certificat a dépassé sa date de validité. Impossible de créer un compte." }}</p>
              </div>

              <!-- Message d'erreur pour certificat révoqué -->
              <div v-if="isRevoked" class="error-container animated fadeIn">
                <div class="error-icon"><i class="fas fa-ban"></i></div>
                <h3>Certificat révoqué</h3>
                <p>{{ errorMessage || "Le certificat est révoqué. Impossible de créer un compte." }}</p>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import TypedText from '@/components/TypedText.vue';
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import userService from "@/services/UserService.js";

// Références pour le fichier et le mot de passe
const fileInput = ref(null);
const fileName = ref("");
const password = ref("");
const showPassword = ref(false);
const showPasswordBox = ref(false); 
const invalidFile = ref(false);
const selectedFile = ref(null); 
const isLoading = ref(false); 
const isSuccess = ref(false); 
const isError = ref(false); 
const isExpired = ref(false); 
const isRevoked = ref(false);
const isTimeout = ref(false);

// Variables pour la modale d'organisation
const showOrgModal = ref(false);
const orgSubmitting = ref(false);
const orgInfo = ref({
  name: '',
  registration_number: '',
  address: '',
  email: ''
});
// Variables pour stocker temporairement les informations du certificat
const tempCertificateData = ref(null);

// Variable pour le rôle sélectionné (pour les thèmes CSS)
const selectedRole = ref('user'); // Par défaut: 'user', peut être 'admin' ou 'superadmin'

// Variables pour messages de statut
const errorTitle = ref("Certificat invalide"); 
const errorMessage = ref("Certificat invalide ou mot de passe incorrect."); 
const successTitle = ref("Certificat validé"); 
const successMessage = ref("Vous allez être redirigé..."); 
const processingStep = ref(0); 
const progressMessage = ref("Traitement en cours..."); 

// Sélecteur d'organisation
const selectedOrganization = ref(null); // Par défaut: pas d'organisation
const organizations = ref([]); // Liste complète des organisations
const filteredOrganizations = ref([]); // Liste filtrée des organisations (pour la recherche)
const orgSearchQuery = ref(''); // Terme de recherche d'organisation
const loadingOrganizations = ref(false); // État de chargement
const organizationsError = ref(''); // Message d'erreur
const dropdownOpen = ref(false); // État ouvert/fermé du dropdown

// Fonction pour récupérer la liste des organisations
async function fetchOrganizations() {
  loadingOrganizations.value = true;
  organizationsError.value = '';
  
  try {
    const data = await userService.getOrganizations();
    organizations.value = data || [];
    // Initialiser également les organisations filtrées avec la liste complète
    filteredOrganizations.value = [...organizations.value];
    console.log('Organisations récupérées:', organizations.value);
  } catch (error) {
    console.error('Erreur lors de la récupération des organisations:', error);
    organizationsError.value = 'Impossible de charger la liste des organisations';
  } finally {
    loadingOrganizations.value = false;
  }
}

// Fonction pour sélectionner une organisation
function selectOrganization(org) {
  selectedOrganization.value = org;
  dropdownOpen.value = false; // Ferme le dropdown après sélection
}

// Fonction pour filtrer les organisations selon la recherche
function filterOrganizations() {
  if (!orgSearchQuery.value.trim()) {
    // Si la recherche est vide, afficher toutes les organisations
    filteredOrganizations.value = [...organizations.value];
    return;
  }
  
  // Filtre sensible à la casse pour correspondre à n'importe quelle partie du nom
  const searchTerm = orgSearchQuery.value.toLowerCase().trim();
  filteredOrganizations.value = organizations.value.filter(org => 
    org.name.toLowerCase().includes(searchTerm)
  );
}

// Fonction pour effacer la recherche
function clearSearch() {
  orgSearchQuery.value = '';
  filterOrganizations();
}

// Fonction pour basculer l'état du dropdown
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value;
}

// Fermer le dropdown si clic à l'extérieur
function closeDropdown(event) {
  if (!event.target.closest('.custom-select')) {
    dropdownOpen.value = false;
  }
}

// Variables pour la gestion de la connexion sécurisée
const initializingSecureConnection = ref(true);
const secureConnectionEstablished = ref(false);
const clientId = ref('');
const privateKey = ref(null);
const sharedKey = ref(null);

// Router pour rediriger après succès
const router = useRouter();

// À l'initialisation du composant, établir une connexion sécurisée et charger les organisations
onMounted(async () => {
  try {
    // Établir la connexion sécurisée
    await initSecureConnection();
    
    // Démarrer l'animation des particules
    animateParticles();
    
    // Ajouter l'écouteur de clic pour fermer le dropdown
    document.addEventListener('click', closeDropdown);
    
    // Récupérer la liste des organisations
    await fetchOrganizations();
  } catch (error) {
    console.error("Erreur lors de l'initialisation du composant:", error);
    initializingSecureConnection.value = false;
    secureConnectionEstablished.value = false;
  }
});

// Fonction pour convertir un ArrayBuffer en chaîne Base64
function arrayBufferToBase64(buffer) {
  const binary = String.fromCharCode.apply(null, new Uint8Array(buffer));
  return window.btoa(binary);
}

// Fonction pour convertir une chaîne Base64 en ArrayBuffer
function base64ToArrayBuffer(base64) {
  const binary = window.atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

// Fonction pour animer les particules
function animateParticles() {
  const particles = document.querySelectorAll('.particle');
  
  particles.forEach(particle => {
    // Position aléatoire
    const posX = Math.random() * 100;
    const posY = Math.random() * 100;
    particle.style.left = `${posX}%`;
    particle.style.top = `${posY}%`;
    
    // Taille aléatoire
    const size = Math.random() * 10 + 5;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    
    // Animation
    particle.style.animationDuration = `${Math.random() * 20 + 10}s`;
    particle.style.animationDelay = `${Math.random() * 5}s`;
  });
}

// Fonction pour initialiser la connexion sécurisée avec Diffie-Hellman
async function initSecureConnection() {
  try {
    console.log("Initialisation de la connexion sécurisée...");
    
    // Générer un ID client unique
    clientId.value = generateClientId();
    console.log("ID client généré:", clientId.value);
    
    // Générer une paire de clés Diffie-Hellman côté client
    console.log("Génération de la paire de clés ECDH...");
    const keyPair = await generateDHKeyPair();
    privateKey.value = keyPair.privateKey;
    const publicKey = keyPair.publicKey;
    
    // Convertir la clé publique en format PEM
    console.log("Exportation de la clé publique...");
    const publicKeyPem = await exportPublicKey(publicKey);
    
    // Envoyer la clé publique au serveur
    console.log("Envoi de la clé publique au serveur...");
    console.log("Client ID:", clientId.value);
    console.log("Public key format:", typeof publicKeyPem);
    console.log("Public key length:", publicKeyPem.length);
    console.log("Public key preview:", publicKeyPem.substring(0, 60) + "...");
    console.log("Request payload:", JSON.stringify({
      client_id: clientId.value,
      public_key: publicKeyPem
    }).substring(0, 100) + "...");
    
    try {
      const response = await axios.post("/gateway/dh-exchange/", {
        client_id: clientId.value,
        public_key: publicKeyPem
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log("Response received:", response.status, response.data);
      
      // Récupérer la clé publique du serveur
      console.log("Réception de la clé publique du serveur...");
      const serverPublicKeyPem = response.data.public_key;
    
    // Importer la clé publique du serveur
    console.log("Importation de la clé publique du serveur...");
    const serverPublicKey = await importPublicKey(serverPublicKeyPem);
    
    // Calculer la clé partagée
    console.log("Calcul de la clé partagée...");
    const rawSharedKey = await deriveSharedKey(privateKey.value, serverPublicKey);
    
    // Dériver une clé symétrique à partir de la clé partagée
    console.log("Dérivation de la clé symétrique...");
    sharedKey.value = await deriveSymmetricKey(rawSharedKey);
    
    // La connexion sécurisée est établie
    secureConnectionEstablished.value = true;
    initializingSecureConnection.value = false;
    
    console.log("Connexion sécurisée établie avec succès");
    
    // Test de la clé 
    const testData = new TextEncoder().encode("test_de_chiffrement");
    const encrypted = await encryptWithSessionKey(testData);
    console.log("Test de chiffrement réussi:", encrypted);
    } catch (axiosError) {
      console.error("Erreur lors de la requête au serveur:", axiosError);
      if (axiosError.response) {
        console.error("Réponse du serveur:", axiosError.response.data);
        console.error("Code d'état:", axiosError.response.status);
      }
      throw axiosError;
    }
  } catch (error) {
    console.error("Erreur détaillée lors de l'initialisation de la connexion sécurisée:", error);
    
    if (error.response) {
      console.error("Réponse du serveur:", error.response.data);
      console.error("Code d'état:", error.response.status);
    } else if (error.request) {
      console.error("Aucune réponse reçue du serveur");
    } else {
      console.error("Erreur de configuration de la requête:", error.message);
    }
    
    secureConnectionEstablished.value = false;
    initializingSecureConnection.value = false;
    throw error;
  }
}

// Fonction pour générer un ID client unique
function generateClientId() {
  return 'client-' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// Fonction pour générer une paire de clés Diffie-Hellman
async function generateDHKeyPair() {
  // Utiliser l'API Web Crypto si disponible
  if (window.crypto && window.crypto.subtle) {
    try {
      // Générer les paramètres Diffie-Hellman
      const keyPair = await window.crypto.subtle.generateKey(
        {
          name: "ECDH",
          namedCurve: "P-256",
        },
        true,
        ["deriveKey", "deriveBits"]
      );
      
      return keyPair;
    } catch (error) {
      console.error("Erreur lors de la génération de la paire de clés:", error);
      throw error;
    }
  } else {
    // Fallback pour les navigateurs qui ne supportent pas l'API Web Crypto
    throw new Error("L'API Web Crypto n'est pas disponible dans ce navigateur.");
  }
}

// Fonction pour exporter une clé publique au format PEM
async function exportPublicKey(publicKey) {
  // Exporter la clé publique au format brut
  const exported = await window.crypto.subtle.exportKey("spki", publicKey);
  
  // Convertir la clé exportée en base64
  const exportedAsBase64 = arrayBufferToBase64(exported);
  
  // Formater en PEM
  return `-----BEGIN PUBLIC KEY-----\n${exportedAsBase64}\n-----END PUBLIC KEY-----`;
}

// Fonction pour importer une clé publique depuis le format PEM
async function importPublicKey(pemKey) {
  // Supprimer les en-têtes et les sauts de ligne
  const pemContents = pemKey
    .replace("-----BEGIN PUBLIC KEY-----", "")
    .replace("-----END PUBLIC KEY-----", "")
    .replace(/\n/g, "");
  
  // Convertir de base64 en tableau d'octets
  const binaryDer = base64ToArrayBuffer(pemContents);
  
  // Importer la clé
  return window.crypto.subtle.importKey(
    "spki",
    binaryDer,
    {
      name: "ECDH",
      namedCurve: "P-256",
    },
    false,
    []
  );
}

// Fonction pour dériver la clé partagée
async function deriveSharedKey(privateKey, publicKey) {
  // Dériver la clé partagée
  return window.crypto.subtle.deriveBits(
    {
      name: "ECDH",
      public: publicKey,
    },
    privateKey,
    256
  );
}

// Fonction pour dériver une clé symétrique à partir de la clé partagée
async function deriveSymmetricKey(sharedSecret) {
  // Dériver une clé AES à partir de la clé partagée
  return window.crypto.subtle.deriveKey(
    {
      name: "HKDF",
      hash: "SHA-256",
      salt: new Uint8Array(0),
      info: new TextEncoder().encode("handshake data"),
    },
    await window.crypto.subtle.importKey(
      "raw",
      sharedSecret,
      { name: "HKDF" },
      false,
      ["deriveKey"]
    ),
    {
      name: "AES-GCM",
      length: 256,
    },
    true,
    ["encrypt", "decrypt"]
  );
}

// Fonction pour chiffrer des données avec la clé de session
async function encryptWithSessionKey(data) {
  console.log("Démarrage du chiffrement...");
  // Générer un vecteur d'initialisation aléatoire
  const iv = window.crypto.getRandomValues(new Uint8Array(12)); // Pour GCM, 12 octets est optimal
  console.log("IV généré:", iv);
  
  // Chiffrer les données
  console.log("Chiffrement avec AES-GCM...");
  try {
    const encrypted = await window.crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv,
        tagLength: 128 // Taille du tag d'authentification en bits
      },
      sharedKey.value,
      data
    );
    
    console.log("Données chiffrées avec succès, taille:", encrypted.byteLength);
    
    // Retourner le résultat chiffré et l'IV
    return {
      iv: arrayBufferToBase64(iv),
      encrypted_data: arrayBufferToBase64(encrypted),
      client_id: clientId.value
    };
  } catch (error) {
    console.error("Erreur lors du chiffrement:", error);
    throw error;
  }
}

// Fonction pour ouvrir le sélecteur de fichier
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// Fonction pour gérer la sélection du fichier avec vérification du type
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  
  // Vérification de la taille du fichier
  const fileSizeInMB = file.size / (1024 * 1024);
  console.log(`Taille du fichier: ${fileSizeInMB.toFixed(2)} Mo`);
  
  // Rejeter les fichiers trop volumineux (plus de 10 Mo)
  if (fileSizeInMB > 10) {
      invalidFile.value = true;
    fileName.value = "Fichier trop volumineux (max 10 Mo)";
      showPasswordBox.value = false;
    selectedFile.value = null; // Réinitialiser le fichier sélectionné
    return;
  }
  
  if (file && file.name.endsWith('.pfx')) {
      fileName.value = file.name;
    showPasswordBox.value = true;
    invalidFile.value = false;
    selectedFile.value = file; // Stocker le fichier sélectionné
  } else {
    fileName.value = "";
    showPasswordBox.value = false;
    invalidFile.value = true;
    selectedFile.value = null; // Réinitialiser le fichier sélectionné
  }
};

// Fonction pour afficher/masquer le mot de passe
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

// Fonction pour annuler la saisie des informations d'organisation
function cancelOrgInfo() {
  showOrgModal.value = false;
  // Réinitialiser les informations d'organisation
  orgInfo.value = {
    name: '',
    registration_number: '',
    address: '',
    email: ''
  };
  // Réinitialiser les états
  isLoading.value = false;
  isError.value = false;
}

// Fonction pour soumettre les informations de l'organisation
async function submitOrgInfo() {
  if (!orgInfo.value.name || !orgInfo.value.registration_number || !orgInfo.value.email) {
    // Validation basique
    isError.value = true;
    errorTitle.value = "Données incomplètes";
    errorMessage.value = "Veuillez remplir tous les champs obligatoires (nom, numéro d'immatriculation et email).";
    return;
  }
  
  // Validation de format d'email basique
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(orgInfo.value.email)) {
    isError.value = true;
    errorTitle.value = "Format d'email invalide";
    errorMessage.value = "Veuillez entrer une adresse email valide.";
    return;
  }
  
  orgSubmitting.value = true;
  
  try {
    // Vérifier que nous avons bien les données temporaires du certificat
    if (!tempCertificateData.value) {
      throw new Error("Données de certificat manquantes");
    }
    
    // Préparer les données à envoyer (certificat + infos organisation)
    const completeData = {
      ...tempCertificateData.value,
      organization: orgInfo.value
    };
    
    // Importer le service utilisateur
    const UserService = (await import('@/services/UserService')).default;
    
    // Envoyer la requête pour créer/vérifier l'organisation et l'administrateur
    const response = await UserService.authenticateOrgAdmin(completeData);
    
    // Masquer la modale
    showOrgModal.value = false;
    
    // Vérifier le statut de l'organisation
    if (response.org_status === 'pending') {
      // Afficher le message d'attente sans redirection
      isSuccess.value = true;
      successTitle.value = "Organisation en attente de validation";
      successMessage.value = "Votre demande d'accès a été enregistrée avec succès. Un super administrateur doit maintenant valider votre organisation avant que vous puissiez vous connecter. Vous serez notifié par email dès que votre accès sera activé.";
      
      // Sauvegarder uniquement les informations nécessaires
      if (response.certificate_info) {
        localStorage.setItem('certificateInfo', JSON.stringify(response.certificate_info));
      }
      
      // Ne pas rediriger l'utilisateur
    } else {
      // Comportement normal pour les organisations actives
      isSuccess.value = true;
      successTitle.value = "Bienvenue";
      successMessage.value = response.message || "Vous allez être redirigé vers votre espace d'administration...";
      
      // Sauvegarder les informations du certificat et de l'organisation
      if (response.certificate_info) {
        localStorage.setItem('certificateInfo', JSON.stringify(response.certificate_info));
      }
      if (response.organization) {
        localStorage.setItem('organizationInfo', JSON.stringify(response.organization));
      }
      localStorage.setItem('isAdmin', true);
      
      // Rediriger vers le dashboard d'administration d'organisation
      setTimeout(() => {
        router.push(getDashboardByRole('admin'));
      }, 2000);
    }
    
  } catch (error) {
    console.error("Erreur lors de la soumission des informations d'organisation:", error);
    isError.value = true;
    errorTitle.value = "Erreur";
    errorMessage.value = error.message || "Une erreur s'est produite lors de la vérification de votre organisation.";
  } finally {
    orgSubmitting.value = false;
  }
}

// Fonction pour soumettre le formulaire
async function submitForm() {
  // Si un fichier est sélectionné et que le mot de passe est saisi
  if (!selectedFile.value || !password.value) {
    // Simple validation côté client
    isError.value = true;
    errorTitle.value = "Données incomplètes";
    errorMessage.value = "Veuillez sélectionner un certificat et saisir votre mot de passe.";
    return;
  }
  
  // Nettoyer le cache et les cookies avant l'authentification
  clearCacheAndCookies();
  
  // Mettre à jour le statut et réinitialiser les valeurs
  isLoading.value = true;
  isSuccess.value = false;
  isError.value = false;
  isTimeout.value = false;
  isExpired.value = false;
  isRevoked.value = false;
  processingStep.value = 1;
  progressMessage.value = "Lecture du certificat en cours...";
  
  try {
    // Lire le fichier PFX avec FileReader
    const fileReader = new FileReader();
    
    const certificatePromise = new Promise((resolve, reject) => {
      fileReader.onload = function() {
        resolve(this.result);
      };
      
      fileReader.onerror = function() {
        reject(new Error("Erreur lors de la lecture du fichier"));
      };
    });
    
    fileReader.readAsArrayBuffer(selectedFile.value);
    
    // Attendre que le fichier soit lu
    const pfxData = await certificatePromise;
    
    // Mettre à jour le statut
    processingStep.value = 2;
    progressMessage.value = "Chiffrement des données en cours...";
    
    // Convertir le certificat en Base64
    const pfxBase64 = arrayBufferToBase64(pfxData);
    
    // Préparer les données à envoyer
    const authData = {
      certificate: pfxBase64,
      password: password.value,
      organization_id: selectedOrganization.value ? selectedOrganization.value.id : 'none',
      filename: fileName.value
    };
    
    // Mettre à jour le statut
    processingStep.value = 3;
    progressMessage.value = "Envoi au serveur en cours...";
    
    // Importer UserService
    const UserService = (await import('@/services/UserService')).default;
    
    // Pour la compatibilité avec le flux existant, vérifier si nous traitons un admin
    // Dans le nouveau système, c'est le backend qui détermine le rôle
    const isAdminFlow = false; // Désactivé dans le nouveau flux
    if (isAdminFlow) {
      try {
        // Pour un admin, on fait d'abord une vérification du certificat seulement
        const verifyResponse = await UserService.verifyAdminCertificate(authData);
        
        // Mettre à jour le statut
        processingStep.value = 4;
        progressMessage.value = "Vérification du certificat...";
        
        // Logs de débogage
        console.log('Réponse de vérification du certificat admin:', verifyResponse);
        
        // Réinitialiser les variables d'état
        isLoading.value = false;
        
        // Si le certificat est valide, vérifier s'il s'agit d'un admin existant ou d'un nouveau
        if (verifyResponse.valid) {
          // Stocker temporairement les données du certificat
          tempCertificateData.value = authData;
          
          // Vérifier si c'est un administrateur existant (avec exists: true)
          if (verifyResponse.exists) {
            console.log('Administrateur existant, connexion directe sans modale');
            
            // Si l'administrateur existe déjà et a une organisation associée, nous pouvons
            // procéder directement à l'authentification complète sans afficher la modale
            if (verifyResponse.organization) {
              // Les données de l'organisation et de l'utilisateur sont déjà présentes dans la réponse
              // Nous pouvons simuler une connexion réussie
              processAuthResponse({
                status: 'active',
                org_status: verifyResponse.organization.status || 'active',
                message: `Bienvenue, ${verifyResponse.user?.first_name || 'Administrateur'}. Vous êtes connecté en tant qu'administrateur de ${verifyResponse.organization.name}.`,
                user_id: verifyResponse.user?.id,
                username: verifyResponse.user?.username,
                email: verifyResponse.user?.email,
                role: 'admin',
                organization: verifyResponse.organization,
                certificate_info: {
                  serial: authData.serial_number || '',
                  subject_dn: '',
                  common_name: '',
                  expiry_date: '',
                  filename: authData.filename
                }
              });
              return;
            }
          }
          
          // Pour un nouvel administrateur ou un admin sans organisation, pré-remplir les champs si disponibles
          if (verifyResponse.organization) {
            orgInfo.value = {
              name: verifyResponse.organization.name || '',
              registration_number: verifyResponse.organization.registration_number || '',
              address: verifyResponse.organization.address || ''
            };
          }
          
          // Afficher la modale pour les nouveaux administrateurs ou ceux sans organisation
          showOrgModal.value = true;
          return;
        } else {
          // Le certificat est invalide ou l'utilisateur n'est pas autorisé
          isError.value = true;
          errorTitle.value = verifyResponse.errorTitle || "Certificat invalide";
          errorMessage.value = verifyResponse.errorMessage || "Certificat invalide ou non autorisé.";
          return;
        }
      } catch (error) {
        console.error("Erreur lors de la vérification du certificat admin:", error);
        isLoading.value = false;
        isError.value = true;
        errorTitle.value = "Erreur lors de la vérification";
        errorMessage.value = error.message || "Une erreur s'est produite lors de la vérification du certificat.";
        return;
      }
    } else {
      try {
        // Préparer les données avec l'organisation sélectionnée
        const orgAuthData = {
          ...authData,
          organization_id: selectedOrganization.value ? selectedOrganization.value.id : 'none'
        };
        
        console.log('Tentative d\'authentification avec organisation:', orgAuthData.organization_id);
        
        // Utiliser le nouveau service d'authentification avec organisation
        const response = await userService.authenticateWithOrganization(orgAuthData);
        
        // Mettre à jour le statut
        processingStep.value = 4;
        progressMessage.value = "Vérification du certificat...";
        
        // Logs de débogage pour l'inspection de la réponse complète
        console.log('Réponse complète de l\'authentification:', response);
        console.log('Statut de la réponse:', response.status);
        console.log('Message de la réponse:', response.message);
        
        // Réinitialiser toutes les variables d'état
        isLoading.value = false;
        isSuccess.value = false;
        isError.value = false;
        isExpired.value = false;
        isRevoked.value = false;
        
        // Traiter la réponse selon le statut du compte ou du certificat
        processAuthResponse(response);
      } catch (error) {
        console.error("Erreur lors de l'authentification:", error);
        isLoading.value = false;
        isError.value = true;
        errorTitle.value = "Erreur lors de l'authentification";
        errorMessage.value = error.message || "Une erreur s'est produite lors de l'authentification.";
      }
    }
  } catch (error) {
    console.error("Erreur lors du traitement du certificat:", error);
    isLoading.value = false;
    isError.value = true;
    errorTitle.value = "Erreur";
    errorMessage.value = error.message || "Une erreur s'est produite lors du traitement du certificat.";
    
    if (error.message && error.message.includes('timeout')) {
      isTimeout.value = true;
    }
  }
}

// Fonction utilitaire pour obtenir la route du dashboard selon le rôle
function getDashboardByRole(role) {
  switch(role) {
    case 'admin':
      return { name: 'admin-dashboard' };
    case 'collaborator':
      return { name: 'collaborator-dashboard' };
    case 'signer':
      return { name: 'signer-dashboard' };
    case 'user':
    case 'superadmin':
    default:
      return { name: 'new-dashboard' };
  }
}

// Fonction pour nettoyer le cache et les cookies avant l'authentification
function clearCacheAndCookies() {
  console.log('Nettoyage du cache et des cookies avant authentification...');
  
  // Supprimer les données du localStorage
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('certificateInfo');
  localStorage.removeItem('isAdmin');
  localStorage.removeItem('isCollaborator');
  localStorage.removeItem('isSigner');
  localStorage.removeItem('organizationInfo');
  
  // Supprimer les cookies CSRF et de session
  document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  document.cookie = 'sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  
  console.log('Cache et cookies nettoyés');
}

// Fonction pour traiter la réponse d'authentification
function processAuthResponse(response) {
  try {
    if (response && response.status) {
      switch(response.status) {
        case 'pending':
          isSuccess.value = true;
          successTitle.value = "En attente de validation";
          successMessage.value = response.message || "Votre compte a été créé et est en attente de validation par un administrateur.";
          break;
          
        case 'error':
          // Nouvel état pour gérer le cas où un utilisateur essaie de se connecter en tant qu'admin
          isError.value = true;
          errorTitle.value = "Accès refusé";
          errorMessage.value = response.message || "Vous n'avez pas les droits nécessaires pour accéder à cette section.";
          break;

        case 'mismatch':
          // Gérer le cas de non-correspondance entre le certificat et l'organisation sélectionnée
          isError.value = true;
          errorTitle.value = "Organisation non correspondante";
          errorMessage.value = response.message || "L'organisation sélectionnée ne correspond pas à votre certificat.";
          
          // Si une organisation suggérée est fournie, la proposer à l'utilisateur
          if (response.suggested_organization) {
            setTimeout(() => {
              // Proposer de sélectionner l'organisation suggérée
              if (confirm(`${response.message}\n\nVoulez-vous sélectionner l'organisation ${response.suggested_organization.name} ?`)) {
                // Trouver l'organisation suggérée dans la liste
                const suggestedOrg = organizations.value.find(org => org.id === response.suggested_organization.id);
                if (suggestedOrg) {
                  selectedOrganization.value = suggestedOrg;
                  // Redéclencher la soumission du formulaire
                  submitForm();
                }
              }
            }, 500); // Délai court pour permettre à l'interface de se mettre à jour d'abord
          }
          break;
          
        case 'active':
          isSuccess.value = true;
          successTitle.value = "Bienvenue";
          successMessage.value = response.message || "Vous allez être redirigé vers votre espace personnel...";
          // Sauvegarder les informations du certificat et rediriger
          localStorage.setItem('certificateInfo', JSON.stringify(response.certificate_info));
          
          // Stocker les informations de rôle
          if (response.role === 'admin') {
            localStorage.setItem('isAdmin', 'true');
          } else if (response.role === 'collaborator') {
            localStorage.setItem('isCollaborator', 'true');
          } else if (response.role === 'signer') {
            localStorage.setItem('isSigner', 'true');
          }
          
          // IMPORTANT: S'assurer que les informations d'authentification sont correctement enregistrées
          console.log('Enregistrement des informations d\'authentification');
          if (response.token) {
            console.log('Token JWT reçu, enregistrement dans localStorage');
            localStorage.setItem('token', response.token);
            // Créer un objet utilisateur complet avec toutes les informations disponibles
            const userData = {
              id: response.user_id,
              role: response.role,
              username: response.username || '',
              email: response.email || '',
              organization: response.organization || null
            };
            localStorage.setItem('user', JSON.stringify(userData));
            console.log('Informations utilisateur enregistrées:', userData);
            
            // Initialiser le service d'authentification pour configurer l'intercepteur
            // Utilisons une référence directe au service au lieu d'une importation dynamique
            import('@/services/AuthService').then(module => {
              const AuthService = module.default;
              AuthService.token = response.token;
              AuthService.user = userData;
              AuthService.setupAxiosInterceptors();
              console.log('Service d\'authentification configuré');
            }).catch(error => {
              console.error('Erreur lors de l\'initialisation du service d\'authentification:', error);
            });
          } else {
            console.warn('Aucun token JWT reçu dans la réponse');
          }
          
          // Rediriger vers le dashboard approprié selon le rôle
          setTimeout(() => {
            console.log('Redirection vers le tableau de bord selon le rôle:', response.role);
            router.push(getDashboardByRole(response.role));
          }, 500); // Délai réduit pour une meilleure expérience utilisateur
          break;
          
        case 'rejected':
          isError.value = true;
          errorTitle.value = "Compte rejeté";
          errorMessage.value = response.message || "Votre demande de création de compte a été rejetée par l'administrateur.";
          break;
          
        case 'approved':
          isSuccess.value = true;
          successTitle.value = "Compte approuvé";
          successMessage.value = response.message || "Votre compte a été approuvé. Vous allez être redirigé vers votre espace personnel...";
          // Sauvegarder les informations du certificat et rediriger
          if (response.certificate_info) {
            localStorage.setItem('certificateInfo', JSON.stringify(response.certificate_info));
          }
          
          // Stocker les informations de rôle
          if (response.role === 'admin') {
            localStorage.setItem('isAdmin', 'true');
          } else if (response.role === 'collaborator') {
            localStorage.setItem('isCollaborator', 'true');
          } else if (response.role === 'signer') {
            localStorage.setItem('isSigner', 'true');
          }
          
          // S'assurer que les informations d'authentification sont correctement enregistrées
          console.log('Enregistrement des informations d\'authentification (cas approved)');
          if (response.token) {
            console.log('Token JWT reçu, enregistrement dans localStorage');
            localStorage.setItem('token', response.token);
            // Créer un objet utilisateur complet avec toutes les informations disponibles
            const userData = {
              id: response.user_id,
              role: response.role,
              username: response.username || '',
              email: response.email || '',
              organization: response.organization || null
            };
            localStorage.setItem('user', JSON.stringify(userData));
            console.log('Informations utilisateur enregistrées:', userData);
            
            // Initialiser le service d'authentification pour configurer l'intercepteur
            // Utilisons une référence directe au service au lieu d'une importation dynamique
            import('@/services/AuthService').then(module => {
              const AuthService = module.default;
              AuthService.token = response.token;
              AuthService.user = userData;
              AuthService.setupAxiosInterceptors();
              console.log('Service d\'authentification configuré');
            }).catch(error => {
              console.error('Erreur lors de l\'initialisation du service d\'authentification:', error);
            });
          } else {
            console.warn('Aucun token JWT reçu dans la réponse');
          }
          
          // Rediriger vers le dashboard approprié selon le rôle
          setTimeout(() => {
            console.log('Redirection vers le tableau de bord selon le rôle:', response.role);
            router.push(getDashboardByRole(response.role));
          }, 500); // Délai réduit pour une meilleure expérience utilisateur
          break;
          
        case 'revoked':
          isRevoked.value = true;
          errorMessage.value = response.message || "Le certificat est révoqué. Impossible de créer un compte.";
          break;
          
        case 'expired':
          isExpired.value = true;
          errorMessage.value = response.message || "Le certificat a dépassé sa date de validité. Impossible de créer un compte.";
          break;
          
        default:
          isError.value = true;
          errorTitle.value = "Statut inattendu";
          errorMessage.value = response.message || "Une erreur inattendue s'est produite. Veuillez réessayer.";
          break;
      }
    } else {
      throw new Error('Réponse invalide du serveur');
    }
  } catch (error) {
    console.error('Erreur lors de l\'authentification:', error);
    isLoading.value = false;
    isError.value = true;
    errorTitle.value = "Erreur d'authentification";
    errorMessage.value = error.message || "Une erreur s'est produite lors de l'authentification. Veuillez réessayer.";
    
    // Détecter si l'erreur est un timeout
    if (error.message && error.message.includes('timeout')) {
      isTimeout.value = true;
    }
  } finally {
    isLoading.value = false;
  }
}

// Fonction pour réessayer la soumission
const retrySubmit = () => {
  submitForm();
};

// Fonction pour réessayer la connexion
const retryConnection = async () => {
  console.log("Tentative de reconnexion...");
  initializingSecureConnection.value = true;
  try {
    await initSecureConnection();
  } catch (error) {
    console.error("Erreur lors de la nouvelle tentative de connexion:", error);
    initializingSecureConnection.value = false;
    secureConnectionEstablished.value = false;
  }
};

/* Fonction temporairement désactivée car non utilisée
async function simulateProcessingSteps() {
  processingStep.value = 1;
  progressMessage.value = "Lecture du certificat...";
  await new Promise(resolve => setTimeout(resolve, 800));
  
  processingStep.value = 2;
  progressMessage.value = "Chiffrement des données...";
  await new Promise(resolve => setTimeout(resolve, 800));
  
  processingStep.value = 3;
  progressMessage.value = "Envoi au serveur...";
  await new Promise(resolve => setTimeout(resolve, 800));
  
  processingStep.value = 4;
  progressMessage.value = "Vérification du certificat...";
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return true;
}*/

</script>

<style scoped>
/* Styles pour la modale d'organisation - Redesigned */
.org-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.org-modal {
  background-color: #fff;
  width: 600px;
  max-width: 95%;
  max-height: 90vh; /* Pour éviter qu'elle ne dépasse l'écran */
  border-radius: 16px;
  overflow: auto; /* Pour permettre le défilement si la modale est trop grande */
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(0, 0, 0, 0.05);
  position: relative;
  animation: modalSlideUp 0.5s cubic-bezier(0.19, 1, 0.22, 1);
  transform: translateY(0);
  opacity: 1;
  
  /* Support des écrans moyens */
  @media (max-width: 768px) {
    width: 90%;
    max-height: 85vh;
  }
  
  /* Support des petits écrans */
  @media (max-width: 480px) {
    width: 95%;
    max-height: 90vh;
    border-radius: 12px;
  }
}

/* Thémes de couleur pour les différents rôles selon la charte graphique */
.org-modal.admin-theme .org-modal-header {
  background: linear-gradient(135deg, #ffc107, #e0a800); /* Jaune pour admin */
  color: #212529; /* Texte noir pour contraste */
}

.org-modal.superadmin-theme .org-modal-header {
  background: linear-gradient(135deg, #8e44ad, #2c3e50);
}

.org-modal-header {
  background: linear-gradient(135deg, #ffc107, #e0a800); /* Jaune par défaut */
  color: #212529; /* Texte noir pour contraste */
  padding: 25px 30px;
  display: flex;
  align-items: center;
  gap: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.org-modal-icon {
  font-size: 2.5rem;
  height: 60px;
  width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.1); /* Fond sombre pour contraste avec jaune */
  border-radius: 50%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  animation: pulse 2s infinite;
  
  /* Responsive */
  @media (max-width: 768px) {
    font-size: 2rem;
    height: 50px;
    width: 50px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.75rem;
    height: 45px;
    width: 45px;
  }
}

.org-modal-titles h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.org-modal-titles p {
  margin: 0;
  font-size: 0.95rem;
  opacity: 0.9;
  max-width: 380px;
}

.org-modal-content {
  padding: 30px;
  
  /* Responsive */
  @media (max-width: 768px) {
    padding: 20px;
  }
  
  @media (max-width: 480px) {
    padding: 15px;
  }
}

.org-modal-info {
  margin-bottom: 25px;
}

.info-badge {
  background-color: rgba(52, 152, 219, 0.1);
  border-left: 4px solid #3498db;
  padding: 15px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  color: #2c3e50;
}

.info-badge i {
  color: #3498db;
  font-size: 1.2rem;
}

.org-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  margin-bottom: 5px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-icon i {
  position: absolute;
  left: 15px;
  color: #7f8c8d;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.input-with-icon input, .input-with-icon textarea {
  width: 100%;
  padding: 14px 15px 14px 45px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.input-with-icon input:focus, .input-with-icon textarea:focus {
  border-color: #ffc107; /* Jaune selon la charte */
  box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.25);
  outline: none;
}

.input-with-icon:focus-within i {
  color: #ffc107; /* Jaune selon la charte */
}

.textarea-container {
  align-items: flex-start;
}

.textarea-container i {
  top: 15px;
}

.input-with-icon textarea {
  min-height: 120px;
  resize: vertical;
  padding-top: 14px;
  line-height: 1.6;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
  gap: 15px;
}

.btn-cancel, .btn-submit {
  padding: 12px 22px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.btn-cancel {
  background-color: #f1f2f6;
  color: #2d3436;
}

.btn-cancel:hover {
  background-color: #e2e2e2;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-submit {
  background-color: #ffc107; /* Jaune selon la charte */
  color: #212529; /* Texte noir pour contraste */
}

.btn-submit:hover {
  background-color: #e0a800; /* Jaune plus foncé au survol */
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-submit:disabled {
  background-color: #95a5a6;
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

/* Animations personnalisées */
@keyframes modalSlideUp {
  0% {
    transform: translateY(50px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(-30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
/* Style global */
.login-page {
  font-family: 'Poppins', sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(120deg, #f8f9fa, #e9ecef);
  color: #333;
  position: relative;
  overflow: hidden;
}

/* Layout à trois colonnes */
.three-column-layout {
  display: flex;
  gap: 1.5rem;
  align-items: stretch;
  min-height: 450px;
  margin-bottom: 1rem;
}

.left-column, .center-column, .right-column {
  display: flex;
  flex-direction: column;
}

.left-column {
  flex: 1.1;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 0;
}

.center-column {
  flex: 1;
  justify-content: flex-start;
}

.right-column {
  flex: 1;
  min-height: 400px;
}

/* Layout à deux colonnes pour les états de connexion */
.two-column-secure-layout {
  display: flex;
  gap: 1.5rem;
  align-items: stretch;
  min-height: 350px;
  margin-bottom: 1rem;
}

.banner-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0;
}

.message-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* Bannière à pleine hauteur pour l'état non connecté */
.banner-container.fullheight {
  width: 100%;
  height: 100%;
  min-height: 300px;
  max-height: none;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  margin: 0;
}

/* Styles améliorés pour la bannière */
.banner-container {
  width: 100%;
  height: 100%;
  max-height: 600px;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  margin: 0;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: contain; /* Changé de 'cover' à 'contain' pour éviter le rognage tout en maximisant la taille */
  object-position: center; /* Centrer l'image */
  display: block;
  border-radius: 8px;
}

/* Upload section styles */
.upload-section {
  width: 100%;
  padding: 1rem 0;
}

/* Layout à deux colonnes (ancien style à conserver pour compatibilité) */
.two-column-layout {
  display: none; /* Masquer l'ancien layout */
}

/* Responsive design for three columns */
@media (max-width: 992px) {
  .three-column-layout {
    flex-direction: column;
    min-height: auto;
    gap: 1.5rem;
  }
  
  .left-column, .center-column, .right-column {
    width: 100%;
    flex: auto;
  }
  
  .banner-container {
    max-height: 250px;
    margin-bottom: 1.5rem;
  }
  
  .right-column {
    min-height: 300px;
  }
}

/* Animation de fond avec particules */
.particles-background {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 0;
}

.particle {
  position: absolute;
  background-color: #007b3c;
  opacity: 0.1;
  border-radius: 50%;
  width: 10px;
  height: 10px;
  animation: float 20s infinite linear;
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
  }
  25% {
    transform: translateY(-30px) translateX(30px) rotate(90deg);
  }
  50% {
    transform: translateY(0) translateX(50px) rotate(180deg);
  }
  75% {
    transform: translateY(30px) translateX(30px) rotate(270deg);
  }
  100% {
    transform: translateY(0) translateX(0) rotate(360deg);
  }
}

/* Header styles */
.header {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 15px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.site-title {
  margin: 0;
  color: #007b3c;
  font-size: 1.8rem;
  font-weight: 700;
}

.back-button {
  display: inline-flex;
  align-items: center;
  color: #2c3e50;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s;
}

.back-button:hover {
  color: #007b3c;
}

.back-button i {
  margin-right: 8px;
}

/* Containers */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.main-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 0;
  z-index: 1;
}

/* Login card */
.login-card {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 1200px;
  padding: 2rem;
  margin: 0 auto;
  position: relative;
  z-index: 2;
  transition: transform 0.3s, box-shadow 0.3s;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

/* Header text */
.header-text {
  text-align: center;
  margin-bottom: 1rem;
}

.highlighted-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #007b3c;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  position: relative;
  display: inline-block;
}

.highlighted-title::after {
  content: '';
  display: block;
  width: 60%;
  height: 4px;
  background: linear-gradient(90deg, #007b3c, transparent);
  margin: 0.5rem auto 0;
  border-radius: 2px;
}

/* Secure connection loading */
.secure-connection-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(0, 123, 60, 0.2);
  border-radius: 50%;
  border-top-color: #007b3c;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loader-text {
  font-size: 1rem;
  color: #6c757d;
}

/* Upload card styling */
.upload-card {
  background-color: #ffffff;
  border: 2px dashed #4caf50;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 1.5rem;
}

.upload-card:hover {
  border-color: #007b3c;
  transform: scale(1.02);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.upload-icon-container {
  width: 60px;
  height: 60px;
  background-color: rgba(76, 175, 80, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.upload-icon {
  font-size: 2rem;
  color: #007b3c;
}

.upload-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.upload-text {
  font-size: 1rem;
  color: #6c757d;
  margin-bottom: 0;
}

/* Password container */
.password-container {
  max-width: 100%;
  margin: 0.5rem 0 0;
}

.password-box {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.password-input-group {
  position: relative;
  margin-bottom: 1.5rem;
}

.password-input {
  width: 100%;
  padding: 1rem 3rem 1rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.password-input:focus {
  outline: none;
  border-color: #007b3c;
}

.toggle-password {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 1.2rem;
  color: #6c757d;
  transition: color 0.3s;
}

.toggle-password:hover {
  color: #007b3c;
}

.submit-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(45deg, #007b3c, #4caf50);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 123, 60, 0.3);
}

.button-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

/* Message containers */
.success-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  border-radius: 10px;
  margin: 1.5rem 0;
  text-align: center;
}

.success-container {
  background-color: rgba(40, 167, 69, 0.1);
  border: 1px solid rgba(40, 167, 69, 0.2);
}

.error-container {
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.2);
}

.success-icon,
.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.success-icon {
  color: #28a745;
}

.error-icon {
  color: #dc3545;
}

.success-container h3,
.error-container h3 {
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.success-container p,
.error-container p {
  color: #6c757d;
  margin-bottom: 0;
}

.error-message {
  color: #dc3545;
  text-align: center;
  margin-top: 1rem;
  font-weight: 500;
}

/* Illustration container */
.illustration-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 1rem;
  text-align: center;
}

.secure-document-image {
  width: 150px;
  height: auto;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.illustration-text {
  color: #6c757d;
  font-style: italic;
}

/* Animations */
.animated {
  animation-duration: 1s;
  animation-fill-mode: both;
}

.fadeIn {
  animation-name: fadeIn;
}

.fadeInUp {
  animation-name: fadeInUp;
}

.pulse {
  animation: pulse 2s infinite;
}

.shake {
  animation: shake 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate3d(0, 30px, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* Responsive design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
  }
  
  .login-card {
    padding: 1.5rem;
  }
  
  .highlighted-title {
    font-size: 2rem;
  }
  
  .upload-icon-container {
    width: 60px;
    height: 60px;
  }
  
  .upload-icon {
    font-size: 2rem;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .footer-links a {
    margin: 0 0.75rem;
  }
  
  .two-column-layout {
    flex-direction: column;
    min-height: auto;
    gap: 1rem;
  }
  
  .left-column, .right-column {
    width: 100%;
  }
  
  .right-column {
    min-height: 300px;
  }
  
  .banner-container {
    height: 120px;
    margin-bottom: 1rem;
  }
  
  .password-container {
    margin-bottom: 1rem;
  }
  
  .status-content {
    padding: 1rem;
  }
  
  .right-column .success-container,
  .right-column .error-container {
    position: relative;
    margin: 0;
  }
  
  .login-card {
    padding: 1.5rem;
  }
}

/* Dark mode styles - amélioré pour fonctionner correctement */
:global(.dark-mode) .login-page {
  background: linear-gradient(120deg, #1a1a1a, #2c3e50);
  color: #f8f9fa;
}

:global(.dark-mode) .header {
  background-color: rgba(28, 28, 28, 0.9);
}

:global(.dark-mode) .login-card {
  background-color: #263545;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  color: #f8f9fa;
}

:global(.dark-mode) .upload-card {
  background-color: #2c3e50;
  border-color: #4caf50;
  color: #f8f9fa;
}

:global(.dark-mode) .password-box {
  background-color: #2c3e50;
  color: #f8f9fa;
}

:global(.dark-mode) .password-input {
  background-color: #1e2a38;
  color: #ffffff;
  border-color: #4a6572;
}

:global(.dark-mode) .status-content {
  background-color: #263545;
  color: #f8f9fa;
}

:global(.dark-mode) .connection-error-container {
  background-color: rgba(40, 40, 40, 0.95);
  color: #f8f9fa;
}

:global(.dark-mode) .progress-message,
:global(.dark-mode) .illustration-text,
:global(.dark-mode) .upload-text,
:global(.dark-mode) .loader-text {
  color: #adb5bd;
}

:global(.dark-mode) .site-title,
:global(.dark-mode) .upload-title,
:global(.dark-mode) .back-button,
:global(.dark-mode) .highlighted-title {
  color: #f8f9fa;
}

/* Élément caché avec la classe d-none */
.d-none {
  display: none;
}

/* Centering text */
.text-center {
  text-align: center;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.retry-button:hover {
  background-color: #007b3c;
}

/* Styles pour l'indicateur de progression */
.progress-container {
  margin: 0;
  padding: 1rem;
  background-color: transparent;
  border-radius: 0;
  box-shadow: none;
}

.progress-step {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.progress-step.complete {
  opacity: 1;
}

.step-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #6c757d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-weight: bold;
  transition: background-color 0.3s;
}

.progress-step.complete .step-circle {
  background-color: #007b3c;
}

.step-label {
  font-size: 1rem;
}

.progress-message {
  margin-top: 1rem;
  font-style: italic;
  color: #6c757d;
}

/* Status content container */
.status-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  min-height: 100%;
  overflow: hidden;
  position: relative;
}

/* Connection error container */
.connection-error-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  background-color: rgba(240, 240, 240, 0.95);
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  margin: 0;
  max-width: none;
}

.error-icon-large {
  font-size: 4rem;
  color: #dc3545;
  margin-bottom: 1.5rem;
  animation: pulse 2s infinite;
}

/* Success and error containers in right column */
.right-column .success-container,
.right-column .error-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  z-index: 5;
  margin: 0;
  padding: 1rem;
  border: none;
  box-shadow: none;
}

.success-container {
  background-color: rgba(40, 167, 69, 0.1);
  border-radius: 10px;
}

.error-container {
  background-color: rgba(220, 53, 69, 0.1);
  border-radius: 10px;
}

.progress-container {
  margin: 0;
  padding: 1rem;
  background-color: transparent;
  border-radius: 0;
  box-shadow: none;
}

/* Ajustement de la login card pour la nouvelle mise en page */
.login-card {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 1200px;
  padding: 2rem;
  margin: 0 auto;
  position: relative;
  z-index: 2;
  transition: transform 0.3s, box-shadow 0.3s;
}

/* Ajuster l'espacement et la taille dans les colonnes */
.center-column .header-text {
  margin-bottom: 1rem;
}

.status-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
  min-height: 100%;
  overflow: hidden;
  position: relative;
}

/* Styles pour le support mobile */
@media (max-width: 768px) {
  .login-card {
    padding: 1rem;
  }
  
  .three-column-layout {
    flex-direction: column;
    min-height: auto;
    gap: 1rem;
  }
  
  .banner-container {
    max-height: 180px;
    margin-bottom: 1rem;
  }
  
  .three-column-layout .banner-container {
    min-height: 180px;
  }
  
  .two-column-secure-layout .banner-container.fullheight {
    min-height: 180px;
  }
}

/* Ajustement spécifique pour la bannière dans une mise en page à trois colonnes */
.three-column-layout .banner-container {
  width: 100%;
  min-height: 400px;
  margin: 0;
}

/* Responsive design for two columns */
@media (max-width: 992px) {
  .two-column-secure-layout {
    flex-direction: column;
    min-height: auto;
    gap: 1.5rem;
  }
  
  .banner-column, .message-column {
    width: 100%;
    flex: auto;
  }
  
  .banner-container.fullheight {
    min-height: 200px;
    max-height: 250px; /* Limiter la hauteur en responsive */
    margin-bottom: 1rem;
  }
  
  .connection-error-container {
    margin-top: 1rem;
    padding: 1.5rem;
  }
}

/* Pour les grands écrans, assurer que la bannière est bien visible */
@media (min-width: 1200px) {
  .three-column-layout .banner-container {
    min-height: 450px;
  }
  
  .left-column {
    flex: 1.2; /* Augmenté un peu plus pour les grands écrans */
  }
}

/* Bouton de retour stratégique */
.strategic-back-button {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.strategic-back-button .back-button {
  display: inline-flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.85);
  color: #007b3c;
  text-decoration: none;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.strategic-back-button .back-button:hover {
  background-color: #007b3c;
  color: white;
  box-shadow: 0 5px 12px rgba(0, 123, 60, 0.3);
  transform: translateY(-2px);
}

.strategic-back-button .back-button i {
  margin-right: 8px;
}

/* Dark mode ajustement pour le bouton de retour */
:global(.dark-mode) .strategic-back-button .back-button {
  background-color: rgba(40, 40, 40, 0.85);
  color: #4caf50;
}

:global(.dark-mode) .strategic-back-button .back-button:hover {
  background-color: #4caf50;
  color: #1a1a1a;
}

/* Responsive pour le bouton retour stratégique */
@media (max-width: 768px) {
  .strategic-back-button {
    top: 1rem;
    left: 1rem;
  }
  
  .strategic-back-button .back-button {
    font-size: 0.9rem;
    padding: 0.4rem 0.8rem;
  }
}

/* Styles améliorés pour le titre du sélecteur */
.organization-selector-label {
  display: block;
  margin-bottom: 0.8rem;
  font-weight: 600;
  color: var(--text-color);
  text-align: center;
  font-size: 0.95rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  position: relative;
  padding-bottom: 0.5rem;
}

.organization-selector-label::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
  border-radius: 2px;
}

.organization-selector-container {
  margin: 1.5rem 0;
  width: 100%;
}

/* Styles pour les messages de chargement et d'erreur */
.loading-message, .error-message {
  margin-top: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
}

.loading-message {
  background-color: rgba(33, 150, 243, 0.1);
  color: #2196F3;
}

.error-message {
  background-color: rgba(244, 67, 54, 0.1);
  color: #F44336;
}

.loading-message i, .error-message i {
  margin-right: 0.5rem;
}

/* Styles améliorés pour la liste déroulante */
.custom-select {
  position: relative;
  width: 100%;
  z-index: 100;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.select-selected {
  background-color: #ffffff;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 0.85rem 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  font-weight: 500;
  color: #333;
}

.select-selected:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.select-icon {
  margin-right: 0.75rem;
  width: 24px;
  display: flex;
  justify-content: center;
  font-size: 1.1rem;
}

/* Nouveau sélecteur d'organisations */
.org-selector-full {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: #ffffff;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  animation: fadeInDropdown 0.3s ease forwards;
  max-height: 75vh; /* Hauteur maximale à 75% de la hauteur de la fenêtre */
  display: flex;
  flex-direction: column;
}

/* Conteneur de recherche */
.org-search-container {
  padding: 10px;
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.org-search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.org-search-input-wrapper i {
  position: absolute;
  left: 12px;
  color: #6c757d;
}

.org-search-input-wrapper .clear-search {
  left: auto;
  right: 12px;
  cursor: pointer;
  color: #adb5bd;
}

.org-search-input-wrapper .clear-search:hover {
  color: #6c757d;
}

.org-search-input {
  width: 100%;
  padding: 10px 35px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.org-search-input:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

/* Liste des organisations */
.org-list {
  overflow-y: auto;
  flex-grow: 1;
  max-height: calc(75vh - 120px); /* Hauteur ajustée pour tenir compte des autres éléments */
  scrollbar-width: thin; /* Pour Firefox */
  scrollbar-color: rgba(0, 0, 0, 0.3) transparent; /* Pour Firefox */
}

/* Style pour la barre de défilement - pour Chrome, Edge, Safari */
.org-list::-webkit-scrollbar {
  width: 6px;
}

.org-list::-webkit-scrollbar-track {
  background: transparent;
}

.org-list::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}

.org-list::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.5);
}

/* Message aucun résultat */
.no-results-message {
  padding: 15px;
  text-align: center;
  color: #6c757d;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.no-results-message i {
  font-size: 24px;
  color: #6c757d;
}

/* Compteur d'organisations */
.org-count-info {
  padding: 10px;
  font-size: 12px;
  text-align: center;
  background-color: #f8f9fa;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  color: #6c757d;
}

/* Style spécial pour l'option "Aucune organisation" */
.special-item {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

/* Style pour la barre de défilement - pour Chrome, Edge, Safari */
.select-items::-webkit-scrollbar {
  width: 6px;
}

.select-items::-webkit-scrollbar-track {
  background: transparent;
}

.select-items::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
}

.select-items::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.5);
}

@keyframes fadeInDropdown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.select-item {
  padding: 0.85rem 1.2rem;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  border-left: 3px solid transparent;
  background-color: #ffffff;
  color: #333;
}

/* Effet de survol amélioré pour tous les éléments de la liste */
.select-item:hover {
  background-color: rgba(76, 175, 80, 0.08); /* Fond légèrement vert */
  border-left-color: #4CAF50; /* Bordure gauche verte */
  transform: translateX(5px); /* Léger décalage vers la droite */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); /* Ombre subtile */
  color: #2c3e50; /* Texte plus foncé */
}

.select-item:hover i {
  color: #4CAF50; /* Icône qui devient verte */
  transform: scale(1.2); /* Icône légèrement agrandie */
}

.select-item i {
  width: 24px;
  display: flex;
  justify-content: center;
  margin-right: 0.75rem;
  font-size: 1.1rem;
  color: rgba(0, 0, 0, 0.5);
  transition: all 0.3s;
}

.select-item span {
  font-weight: 500;
}

/* Effets de survol par rôle */
.select-item:nth-child(1):hover {
  background-color: rgba(76, 175, 80, 0.1);
  border-left-color: #4CAF50;
}

.select-item:nth-child(1):hover i {
  color: #4CAF50;
}

.select-item:nth-child(2):hover {
  background-color: rgba(255, 193, 7, 0.1);
  border-left-color: #FFC107;
}

.select-item:nth-child(2):hover i {
  color: #FFC107;
}

.select-item:nth-child(3):hover {
  background-color: rgba(244, 67, 54, 0.1);
  border-left-color: #F44336;
}

.select-item:nth-child(3):hover i {
  color: #F44336;
}

.select-item:hover {
  transform: translateX(5px);
}

.select-hide {
  display: none;
}

.dropdown-arrow {
  transition: transform 0.3s ease;
  font-size: 0.9rem;
  color: rgba(0, 0, 0, 0.4);
}

.dropdown-arrow.active {
  transform: rotate(180deg);
}

/* Style pour le mode sombre */
[data-theme="dark"] .select-selected,
[data-theme="dark"] .select-items,
[data-theme="dark"] .select-item {
  background-color: #2d3748;
  color: #e2e8f0;
  border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .select-item i {
  color: rgba(255, 255, 255, 0.6);
}

/* Styles spécifiques pour chaque thème */
/* User theme - vert */
.select-selected {
  border-left: 3px solid #4CAF50;
}

.select-item.same-as-selected {
  background-color: rgba(76, 175, 80, 0.08);
  border-left-color: #4CAF50;
}

.select-item.same-as-selected i {
  color: #4CAF50;
}

/* Admin theme - jaune */
.admin-theme .select-selected {
  border-left: 3px solid #FFC107;
}

.admin-theme .select-item.same-as-selected {
  background-color: rgba(255, 193, 7, 0.08);
  border-left-color: #FFC107;
}

.admin-theme .select-item.same-as-selected i {
  color: #FFC107;
}

/* SuperAdmin theme - rouge */
.superadmin-theme .select-selected {
  border-left: 3px solid #F44336;
}

.superadmin-theme .select-item.same-as-selected {
  background-color: rgba(244, 67, 54, 0.08);
  border-left-color: #F44336;
}

.superadmin-theme .select-item.same-as-selected i {
  color: #F44336;
}

/* Responsive design */
@media (max-width: 768px) {
  .role-selector {
    flex-direction: column;
  }
  
  .select-item {
    width: 100%;
  }
}

/* Thèmes de couleur */
/* Thème Admin (jaune foncé) */
.admin-theme .upload-icon,
.admin-theme .highlighted-title,
.admin-theme .secure-connection-loader,
.admin-theme .success-icon,
.admin-theme .progress-step.complete .step-circle {
  color: #FFC107 !important;
  border-color: #FFC107 !important;
}

.admin-theme .progress-step.complete .step-circle {
  background-color: rgba(255, 193, 7, 0.1) !important;
}

.admin-theme .submit-button,
.admin-theme .retry-button {
  background-color: #FFC107 !important;
}

.admin-theme .upload-card:hover {
  border-color: #FFC107 !important;
  box-shadow: 0 0 15px rgba(255, 193, 7, 0.2) !important;
}

/* Thème SuperAdmin (rouge) */
.superadmin-theme .upload-icon,
.superadmin-theme .highlighted-title,
.superadmin-theme .secure-connection-loader,
.superadmin-theme .success-icon,
.superadmin-theme .progress-step.complete .step-circle {
  color: #F44336 !important;
  border-color: #F44336 !important;
}

.superadmin-theme .progress-step.complete .step-circle {
  background-color: rgba(244, 67, 54, 0.1) !important;
}

.superadmin-theme .submit-button,
.superadmin-theme .retry-button {
  background-color: #F44336 !important;
}

.superadmin-theme .upload-card:hover {
  border-color: #F44336 !important;
  box-shadow: 0 0 15px rgba(244, 67, 54, 0.2) !important;
}
</style> 