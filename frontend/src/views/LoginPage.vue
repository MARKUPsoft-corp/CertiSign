<template>
  <div>
    <!-- Barre de navigation -->
    <navbar />

    <!-- Conteneur principal pour centrer le contenu de connexion -->
    <div class="container d-flex justify-content-center align-items-center min-vh-100">
      <div class="row border rounded-5 p-3 bg-white shadow box-area">
        
        <!-- Partie gauche : Image pleine largeur et hauteur avec bords arrondis -->
        <div class="col-md-6 d-flex align-items-center justify-content-center left-box rounded-5 overflow-hidden">
          <img src="@/assets/banniere.jpeg" class="img-fluid w-100 h-100 object-fit-contain rounded-5" alt="Background Image" />
        </div>

        <!-- Partie droite : Formulaire de connexion avec effets CSS -->
        <div class="col-md-6 right-box">
          
          <!-- Titre de connexion stylisé -->
          <div class="header-text text-center mb-4">
            <h1 class="highlighted-title">CONNEXION</h1>
            <typed />
          </div>

          <!-- Carte cliquable pour soumettre le certificat -->
          <div class="card mb-5 custom-card text-center" @click="triggerFileInput">
            <img src="@/assets/upload.png" class="card-img-top mx-auto" style="width: 50px;" alt="Upload" />
            <div class="card-body">
              <h3 class="card-title">Votre Certificat</h3>
              <p class="card-text">{{ fileName ? fileName : "Soumettre son certificat" }}</p>
            </div>
          </div>
          
          <!-- Input fichier caché -->
          <input type="file" ref="fileInput" @change="handleFileUpload" accept=".pfx" class="d-none" />

          <!-- Message d'erreur si fichier invalide -->
          <p v-if="invalidFile" class="text-danger">Veuillez entrer un fichier valide.</p>

          <!-- Box pour le mot de passe, visible uniquement pour un fichier PFX -->
          <div v-if="showPasswordBox" class="password-box-container">
            <div class="password-box">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="form-control"
                placeholder="Entrez votre mot de passe"
                required
              />
              <span class="toggle-password" @click="togglePasswordVisibility">
                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </span>
              <button class="btn btn-success mt-3" @click="submitForm">Soumettre</button>
            </div>
          </div>

          <!-- Indicateur de chargement -->
          <div v-if="isLoading" class="spinner-border text-primary mt-3" role="status">
            <span class="visually-hidden">Chargement...</span>
          </div>

          <!-- Message de succès -->
          <div v-if="isSuccess" class="alert alert-success mt-3 text-center">
            <strong>Votre certificat est valide !</strong><br>Votre compte a été créé.
          </div>

          <!-- Message d'erreur pour certificat invalide -->
          <div v-if="isError" class="alert alert-danger mt-3 text-center">
            <strong>Certificat invalide ou mot de passe incorrect.</strong>
          </div>

          <!-- Message d'erreur pour certificat expiré -->
          <div v-if="isExpired" class="alert alert-danger mt-3 text-center">
            <strong>Le certificat est expiré.</strong>
          </div>

          <!-- Message d'erreur pour certificat révoqué -->
          <div v-if="isRevoked" class="alert alert-danger mt-3 text-center">
            <strong>Le certificat est révoqué. Votre compte ne peut pas être créé.</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import navbar from "@/components/navbar.vue";
import typed from "@/components/typed.vue";
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

// Références pour le fichier et le mot de passe
const fileInput = ref(null);
const fileName = ref("");
const password = ref("");
const showPasswordBox = ref(false); // Affichage de la box pour le mot de passe
const showPassword = ref(false); // Déclaration de la variable showPassword
const isLoading = ref(false); // Indicateur de chargement
const isSuccess = ref(false); // Indicateur de succès
const isError = ref(false); // Indicateur d'erreur pour certificat invalide
const isExpired = ref(false); // Indicateur de certificat expiré
const isRevoked = ref(false); // Indicateur de certificat révoqué
const invalidFile = ref(false); // Indicateur pour fichier invalide

// Router pour rediriger après succès
const router = useRouter();

// Fonction pour ouvrir le sélecteur de fichier
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// Fonction pour gérer la sélection du fichier avec vérification du type
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const validType = file.name.endsWith(".pfx");
    if (!validType) {
      invalidFile.value = true;
      showPasswordBox.value = false;
      fileName.value = "";
    } else {
      invalidFile.value = false;
      fileName.value = file.name;
      showPasswordBox.value = true; // Afficher la box pour le mot de passe
    }
  }
};

// Fonction pour afficher/masquer le mot de passe
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

// Fonction pour soumettre le formulaire
const submitForm = async () => {
  if (!password.value) {
    return;
  }

  // Affichage du cercle de chargement
  isLoading.value = true;

  try {
    // Crée un FormData avec le fichier et le mot de passe
    const formData = new FormData();
    const file = fileInput.value.files[0];
    formData.append("file", file);
    formData.append("password", password.value);

    // Requête HTTP à l'API Gateway
    const response = await axios.post("http://localhost:8000/gateway/cert_info/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    // Si réponse du microservice valide
    isLoading.value = false;

    if (response.status === 200) {
      const data = response.data;
      // Vérification des clés dans la réponse JSON
      if (data.status === "expiré") {
        isExpired.value = true;
        isSuccess.value = false;
        isRevoked.value = false;
      } else if (data.revocation_status_crl === "révoqué") {
        isRevoked.value = true;
        isSuccess.value = false;
        isExpired.value = false;
      } else {
        isSuccess.value = true;
        isExpired.value = false;
        isRevoked.value = false;
        // Redirection vers la page de succès
        setTimeout(() => {
          router.push("/success-page");
        }, 2000);
      }
    } else {
      // Si erreur 400 ou autre
      isError.value = true;
      isSuccess.value = false;
      isExpired.value = false;
      isRevoked.value = false;
      isLoading.value = false;
    }
    console.log("Réponse du microservice :", response.data);
  } catch (error) {
    console.error("Erreur lors de la soumission du formulaire :", error);
    isLoading.value = false;
    isError.value = true;
  }
};
</script>

<style scoped>
/* Style global */
body {
  font-family: 'Poppins', sans-serif;
  background-color: #ececec;
  margin: 0;
  padding: 0;
}

/* Conteneur principal étiré en hauteur */
.box-area {
  max-width: 1200px;
  width: 90%;
  height: 100%;
  border-radius: 15px;
  overflow: hidden;
}

/* Partie gauche : Image responsive */
.left-box {
  padding: 0;
  height: 100%;
  overflow: hidden;
}

/* Partie droite avec effets CSS */
.right-box {
  padding: 40px;
  background: linear-gradient(135deg, rgba(240, 253, 244, 0.3), rgba(255, 255, 255, 0.3)); /* léger dégradé vert */
  color: #000; /* texte en noir */
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.right-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

/* Style du titre dans la partie droite */
.header-text h1 {
  font-size: 3rem; /* Taille augmentée */
  font-weight: bold;
  margin-bottom: 20px;
  color: #007b3c; /* Vert pour mettre en valeur */
  text-transform: uppercase; /* Titre en majuscules */
}

/* Style de la carte avec bordure en dégradé vert */
.custom-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  width: 80%;
  border: 2px solid transparent;
  border-radius: 15px;
  background: linear-gradient(white, white) padding-box,
              linear-gradient(45deg, #4CAF50, #2E8B57) border-box; /* Bordure dégradée verte */
}
.custom-card:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

/* Container pour la box du mot de passe, avec centrage */
.password-box-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.password-box {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Ajout d'une icône pour la visibilité du mot de passe */
.toggle-password {
  position: absolute;
  right: 20px;
  top: 10px;
  cursor: pointer;
  font-size: 1.25rem;
  color: #007b3c;
}

/* Animation de chargement */
.spinner-border {
  margin-top: 20px;
}
</style>
