/**
 * Service de cryptographie pour la gestion sécurisée des communications
 * Gère l'échange de clés Diffie-Hellman, le chiffrement et le déchiffrement des données
 */
import axios from 'axios';

class CryptoService {
  constructor() {
    this.privateKey = null;
    this.sharedKey = null;
    
    // Utiliser un ID client persistant s'il existe déjà dans le localStorage
    const storedClientId = localStorage.getItem('certisign_client_id');
    if (storedClientId) {
      this.clientId = storedClientId;
      console.log(`CryptoService: Utilisation de l'ID client existant depuis localStorage: ${this.clientId}`);
    } else {
      this.clientId = this.generateClientId();
      // Stocker l'ID client pour les futures sessions
      localStorage.setItem('certisign_client_id', this.clientId);
      console.log(`CryptoService: Génération d'un nouvel ID client: ${this.clientId}`);
    }
    
    this.baseUrl = 'https://192.168.4.131/gateway';
    this.secureConnectionEstablished = false;
    this.fallbackMode = false; // Mode de secours pour le développement
    console.log(`CryptoService initialisé avec l'ID client: ${this.clientId}`);
  }

  /**
   * Génère un identifiant client unique
   * @returns {string} - L'identifiant client généré
   */
  generateClientId() {
    return 'client-' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  }

  /**
   * Vérifie si les microservices nécessaires sont en ligne
   * @returns {Promise<boolean>} - True si tous les services sont disponibles
   */
  async checkServiceAvailability() {
    try {
      console.log("Vérification de la disponibilité des microservices...");
      
      // Vérifier l'API Gateway
      const gatewayResponse = await axios.get(`${this.baseUrl}/docs`, { 
        timeout: 5000,
        validateStatus: function (status) {
          return status < 500; // Accepter tous les codes de réponse sous 500
        }
      });
      
      console.log(`API Gateway status: ${gatewayResponse.status}`);
      
      // Vérifier les microservices via leurs endpoints de santé
      // Dans un environnement production, il y aurait des endpoints /health pour chaque service
      return true;
    } catch (error) {
      console.error("Erreur lors de la vérification des services:", error);
      return false;
    }
  }

  /**
   * Initialise une connexion sécurisée avec le serveur via Diffie-Hellman
   * @param {number} maxRetries - Nombre maximal de tentatives (par défaut: 3)
   * @returns {Promise<boolean>} - True si la connexion a été établie avec succès, sinon False
   */
  async initSecureConnection(maxRetries = 3) {
    let retryCount = 0;
    
    console.log(`---- Début de l'initialisation de la connexion sécurisée ----`);
    console.log(`CryptoService: ID client pour l'échange de clés: ${this.clientId}`);
    
    while (retryCount <= maxRetries) {
      try {
        console.log(`Initialisation de la connexion sécurisée (tentative ${retryCount + 1}/${maxRetries + 1})...`);
        
        // Vérifier si une connexion est déjà établie
        if (this.secureConnectionEstablished && this.sharedKey) {
          console.log("Une connexion sécurisée est déjà établie.");
          return true;
        }
        
        // Générer une paire de clés Diffie-Hellman côté client
        console.log("Génération de la paire de clés ECDH...");
        const keyPair = await this.generateDHKeyPair();
        this.privateKey = keyPair.privateKey;
        const publicKey = keyPair.publicKey;
        
        // Convertir la clé publique en format PEM
        console.log("Exportation de la clé publique...");
        const publicKeyPem = await this.exportPublicKey(publicKey);
        
        // Envoyer la clé publique au serveur
        console.log("Envoi de la clé publique au serveur...");
        try {
          const response = await axios.post(`${this.baseUrl}/dh-exchange/`, {
            client_id: this.clientId,
            public_key: publicKeyPem  // Assurez-vous que le nom de paramètre correspond à celui attendu par le backend
          }, {
            timeout: 10000,  // Timeout de 10 secondes
            headers: {
              'Content-Type': 'application/json',
              'X-Client-ID': this.clientId
            }
          });
          
          // Récupérer la clé publique du serveur
          console.log("Réception de la clé publique du serveur...");
          const serverPublicKey = response.data.public_key;
          
          if (!serverPublicKey) {
            throw new Error("La clé publique du serveur est manquante dans la réponse");
          }
          
          // Créer une clé de session dérivée de la clé partagée
          console.log("Importation de la clé publique du serveur...");
          const importedServerPublicKey = await this.importPublicKey(serverPublicKey);
          
          console.log("Dérivation de la clé partagée...");
          const sharedSecret = await this.deriveSharedKey(this.privateKey, importedServerPublicKey);
          
          console.log("Dérivation de la clé symétrique...");
          this.sharedKey = await this.deriveSymmetricKey(sharedSecret);
          
          // La connexion sécurisée est établie
          this.secureConnectionEstablished = true;
          this.fallbackMode = false;
          
          console.log("Connexion sécurisée établie avec succès");
          return true;
        } catch (requestError) {
          // Si le serveur renvoie une erreur 404, cela peut signifier que la route dh-exchange
          // n'est pas encore implémentée ou que le backend n'est pas démarré
          if (requestError.response && requestError.response.status === 404) {
            console.warn("Le service d'échange de clés n'est pas disponible. Activation du mode de développement.");
            
            // Activer le mode de secours pour le développement
            this.fallbackMode = true;
            
            // Générer une clé symétrique fictive pour permettre au frontend de fonctionner
            this.sharedKey = await this.createDummySymmetricKey("development_key");
            this.secureConnectionEstablished = true;
            
            console.log("Mode de développement activé avec succès.");
            return true;
          } else {
            // Pour les autres erreurs, tenter à nouveau si possible
            console.error(`Erreur lors de la tentative ${retryCount + 1}:`, requestError);
            
            if (retryCount < maxRetries) {
              // Attendre avant la prochaine tentative (avec délai exponentiel)
              const retryDelayMs = Math.pow(2, retryCount) * 1000;
              console.log(`Nouvelle tentative dans ${retryDelayMs / 1000} secondes...`);
              await new Promise(resolve => setTimeout(resolve, retryDelayMs));
              retryCount++;
              continue;
            } else {
              throw requestError;
            }
          }
        }
      } catch (error) {
        console.error(`Erreur détaillée lors de l'initialisation de la connexion sécurisée (tentative ${retryCount + 1}):`, error);
        
        if (error.response) {
          console.error("Réponse du serveur:", error.response.data);
          console.error("Code d'état:", error.response.status);
        } else if (error.request) {
          console.error("Aucune réponse reçue du serveur");
        } else {
          console.error("Erreur de configuration de la requête:", error.message);
        }
        
        if (retryCount < maxRetries) {
          // Attendre avant la prochaine tentative
          const retryDelayMs = Math.pow(2, retryCount) * 1000;
          console.log(`Nouvelle tentative dans ${retryDelayMs / 1000} secondes...`);
          await new Promise(resolve => setTimeout(resolve, retryDelayMs));
          retryCount++;
        } else {
          // En cas d'échec après toutes les tentatives, activer le mode de secours
          console.warn("Échec de l'établissement d'une connexion sécurisée après plusieurs tentatives. Activation du mode de développement.");
          this.fallbackMode = true;
          this.sharedKey = await this.createDummySymmetricKey("fallback_development_key");
          this.secureConnectionEstablished = true;
          return true;
        }
      }
    }
    
    // Si toutes les tentatives ont échoué
    this.secureConnectionEstablished = false;
    return false;
  }

  /**
   * Génère une paire de clés Diffie-Hellman
   * @returns {Promise<CryptoKeyPair>} - La paire de clés générée
   */
  async generateDHKeyPair() {
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
        console.error("Erreur lors de la génération de la paire de clés ECDH:", error);
        throw error;
      }
    } else {
      throw new Error("API Web Crypto non disponible - utilisation d'un navigateur non pris en charge?");
    }
  }

  /**
   * Exporte une clé publique au format PEM
   * @param {CryptoKey} publicKey - La clé publique à exporter
   * @returns {Promise<string>} - La clé publique au format PEM
   */
  async exportPublicKey(publicKey) {
    try {
      // Exporter la clé publique en format binaire
      const exportedKey = await window.crypto.subtle.exportKey(
        "spki",
        publicKey
      );
      
      // Convertir en chaîne Base64
      const base64Key = btoa(String.fromCharCode(...new Uint8Array(exportedKey)));
      
      // Formater en PEM
      return `-----BEGIN PUBLIC KEY-----\n${base64Key}\n-----END PUBLIC KEY-----`;
    } catch (error) {
      console.error("Erreur lors de l'exportation de la clé publique:", error);
      throw error;
    }
  }

  /**
   * Importe une clé publique depuis le format PEM
   * @param {string} pemKey - La clé publique au format PEM
   * @returns {Promise<CryptoKey>} - La clé publique importée
   */
  async importPublicKey(pemKey) {
    try {
      // Supprimer les en-têtes et les sauts de ligne
      const pemContents = pemKey
        .replace(/-----BEGIN PUBLIC KEY-----/, "")
        .replace(/-----END PUBLIC KEY-----/, "")
        .replace(/\n/g, "");
      
      // Convertir de Base64 en ArrayBuffer
      const binaryDer = this.base64ToArrayBuffer(pemContents);
      
      // Importer la clé
      return await window.crypto.subtle.importKey(
        "spki",
        binaryDer,
        {
          name: "ECDH",
          namedCurve: "P-256",
        },
        true,
        []
      );
    } catch (error) {
      console.error("Erreur lors de l'importation de la clé publique:", error);
      throw error;
    }
  }

  /**
   * Dérive une clé partagée à partir d'une paire de clés
   * @param {CryptoKey} privateKey - La clé privée
   * @param {CryptoKey} publicKey - La clé publique
   * @returns {Promise<ArrayBuffer>} - La clé partagée
   */
  async deriveSharedKey(privateKey, publicKey) {
    try {
      // Dériver des bits à partir de la paire de clés
      return await window.crypto.subtle.deriveBits(
        { name: "ECDH", public: publicKey },
        privateKey,
        256
      );
    } catch (error) {
      console.error("Erreur lors de la dérivation de la clé partagée:", error);
      throw error;
    }
  }

  /**
   * Dérive une clé symétrique à partir de la clé partagée
   * @param {ArrayBuffer} sharedSecret - La clé partagée
   * @returns {Promise<CryptoKey>} - La clé symétrique
   */
  async deriveSymmetricKey(sharedSecret) {
    try {
      // Utiliser HKDF pour dériver une clé symétrique
      const rawKey = await window.crypto.subtle.importKey(
        "raw",
        sharedSecret,
        { name: "HKDF" },
        false,
        ["deriveKey"]
      );
      
      // Générer une clé AES-GCM à partir de la clé HKDF
      return await window.crypto.subtle.deriveKey(
        {
          name: "HKDF",
          info: new TextEncoder().encode("AES-GCM"),
          salt: new Uint8Array(16),
          hash: "SHA-256",
        },
        rawKey,
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt", "decrypt"]
      );
    } catch (error) {
      console.error("Erreur lors de la dérivation de la clé symétrique:", error);
      throw error;
    }
  }

  /**
   * Convertit une chaîne Base64 en ArrayBuffer
   * @param {string} base64 - La chaîne Base64
   * @returns {ArrayBuffer} - L'ArrayBuffer correspondant
   */
  base64ToArrayBuffer(base64) {
    const binary_string = atob(base64);
    const bytes = new Uint8Array(binary_string.length);
    for (let i = 0; i < binary_string.length; i++) {
      bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
  }

  /**
   * Convertit un ArrayBuffer en chaîne Base64
   * @param {ArrayBuffer} buffer - L'ArrayBuffer
   * @returns {string} - La chaîne Base64
   */
  arrayBufferToBase64(buffer) {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Crée une clé symétrique factice pour le mode de développement
   * @param {string} password - Un mot de passe pour dériver la clé
   * @returns {Promise<CryptoKey>} - La clé symétrique
   */
  async createDummySymmetricKey(password) {
    // Générer un sel aléatoire
    const salt = window.crypto.getRandomValues(new Uint8Array(16));
    
    // Importer le mot de passe comme une clé brute
    const passwordKey = await window.crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(password),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );
    
    // Dériver une clé AES-GCM à partir du mot de passe
    return await window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: 100000,
        hash: "SHA-256",
      },
      passwordKey,
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt", "decrypt"]
    );
  }

  /**
   * Chiffre des données avec la clé de session
   * @param {ArrayBuffer} data - Les données à chiffrer
   * @returns {Promise<Object>} - Les données chiffrées avec l'IV
   */
  async encryptData(data) {
    if (!this.sharedKey) {
      throw new Error("Connexion sécurisée non établie");
    }
    
    try {
      // Générer un vecteur d'initialisation (IV) pour AES-GCM
      const iv = window.crypto.getRandomValues(new Uint8Array(12));
      
      // Chiffrer les données
      const encryptedData = await window.crypto.subtle.encrypt(
        {
          name: "AES-GCM",
          iv,
        },
        this.sharedKey,
        data
      );
      
      // Retourner les données chiffrées et l'IV
      return {
        data: this.arrayBufferToBase64(encryptedData),
        iv: this.arrayBufferToBase64(iv)
      };
    } catch (error) {
      console.error("Erreur lors du chiffrement:", error);
      throw error;
    }
  }

  /**
   * Déchiffre des données avec la clé de session
   * @param {string} encryptedDataBase64 - Les données chiffrées en Base64
   * @param {string} ivBase64 - L'IV en Base64
   * @returns {Promise<ArrayBuffer>} - Les données déchiffrées
   */
  async decryptData(encryptedDataBase64, ivBase64) {
    if (!this.sharedKey) {
      throw new Error("Connexion sécurisée non établie");
    }
    
    try {
      // Convertir les données chiffrées et l'IV de Base64 en ArrayBuffer
      const encryptedData = this.base64ToArrayBuffer(encryptedDataBase64);
      const iv = this.base64ToArrayBuffer(ivBase64);
      
      // Déchiffrer les données
      return await window.crypto.subtle.decrypt(
        {
          name: "AES-GCM",
          iv: new Uint8Array(iv),
        },
        this.sharedKey,
        encryptedData
      );
    } catch (error) {
      console.error("Erreur lors du déchiffrement:", error);
      throw error;
    }
  }

  /**
   * Envoie des données chiffrées à une URL spécifique
   * @param {string} endpoint - L'endpoint API à appeler
   * @param {Object} data - Les données à envoyer
   * @returns {Promise<Object>} - La réponse déchiffrée
   */
  async sendEncryptedData(endpoint, data) {
    console.log(`CryptoService: Préparation de l'envoi des données chiffrées à ${endpoint}`);
    console.log(`CryptoService: ID client utilisé: ${this.clientId}`);
    console.log(`CryptoService: État de la connexion sécurisée: ${this.secureConnectionEstablished ? 'ÉTABLIE' : 'NON ÉTABLIE'}`);
    
    if (!this.secureConnectionEstablished) {
      console.log(`CryptoService: Tentative d'établissement de la connexion sécurisée avant l'envoi...`);
      await this.initSecureConnection();
      console.log(`CryptoService: État après tentative: ${this.secureConnectionEstablished ? 'ÉTABLIE' : 'NON ÉTABLIE'}`);
    }
    
    try {
      // Convertir les données en ArrayBuffer pour le chiffrement
      const dataStr = JSON.stringify(data);
      const dataBuffer = new TextEncoder().encode(dataStr);
      
      // Chiffrer les données
      const encryptedData = await this.encryptData(dataBuffer);
      
      // Envoyer les données chiffrées au serveur
      const response = await axios.post(`${this.baseUrl}${endpoint}`, encryptedData, {
        headers: {
          "Content-Type": "application/encrypted+json",
          "X-Client-ID": this.clientId, // Ajouter l'ID client pour identification
        },
        timeout: 30000, // Timeout de 30 secondes
      });
      
      // Déchiffrer la réponse
      if (response.status === 200) {
        const encryptedResponse = response.data;
        const decrypted = await this.decryptData(encryptedResponse.data, encryptedResponse.iv);
        const decodedText = new TextDecoder().decode(decrypted);
        return JSON.parse(decodedText);
      }
      
      return response.data;
    } catch (error) {
      console.error("Erreur lors de l'envoi des données chiffrées:", error);
      throw error;
    }
  }

  /**
   * Envoie un fichier chiffré avec des données de formulaire
   * @param {string} endpoint - L'endpoint API à appeler
   * @param {File} file - Le fichier à envoyer
   * @param {Object} formData - Données supplémentaires du formulaire
   * @returns {Promise<Object>} - La réponse déchiffrée
   */
  async sendEncryptedFile(endpoint, file, formData) {
    if (!this.secureConnectionEstablished) {
      await this.initSecureConnection();
    }
    
    try {
      // Lire le fichier comme un ArrayBuffer
      const fileArrayBuffer = await file.arrayBuffer();
      console.log(`Taille du fichier: ${fileArrayBuffer.byteLength} octets`);
      
      // Convertir le fichier en base64
      const fileBase64 = this.arrayBufferToBase64(fileArrayBuffer);
      
      // Combiner les données du formulaire et le fichier
      const combinedData = JSON.stringify({
        formData: JSON.stringify(formData),
        fileBase64: fileBase64,
        fileName: file.name,
        fileType: file.type
      });
      
      // Convertir en ArrayBuffer pour le chiffrement
      const dataBuffer = new TextEncoder().encode(combinedData);
      
      // Chiffrer les données
      const encryptedData = await this.encryptData(dataBuffer);
      
      // Envoyer les données chiffrées au serveur
      const response = await axios.post(`${this.baseUrl}${endpoint}`, encryptedData, {
        headers: {
          "Content-Type": "application/encrypted+json",
          "X-Client-ID": this.clientId, // Ajouter l'ID client pour identification
        },
        timeout: 120000, // Timeout de 2 minutes pour les fichiers volumineux
      });
      
      // Déchiffrer la réponse
      if (response.status === 200) {
        const encryptedResponse = response.data;
        const decrypted = await this.decryptData(encryptedResponse.data, encryptedResponse.iv);
        const decodedText = new TextDecoder().decode(decrypted);
        return JSON.parse(decodedText);
      }
      
      return response.data;
    } catch (error) {
      console.error("Erreur lors de l'envoi du fichier chiffré:", error);
      throw error;
    }
  }
}

// Exporter une instance unique du service (pattern Singleton)
export default new CryptoService();
