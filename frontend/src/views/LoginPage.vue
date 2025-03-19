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
          <input type="file" ref="fileInput" @change="handleFileUpload" accept=".pdf,.jpg,.png" class="d-none" />
          
          <!-- Box pour le mot de passe -->
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
              <button class="btn btn-success mt-3" @click="validatePassword">Soumettre</button>
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

// Références pour le fichier et le mot de passe
const fileInput = ref(null);
const fileName = ref("");
const password = ref("");
const showPasswordBox = ref(false); // Affichage de la box pour le mot de passe
const showPassword = ref(false); // Déclaration de la variable showPassword
const isLoading = ref(false); // Indicateur de chargement
const isSuccess = ref(false); // Indicateur de succès

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
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      alert('Veuillez télécharger un fichier PDF, JPG ou PNG');
      return;
    }
    fileName.value = file.name;
    showPasswordBox.value = true; // Afficher la box pour le mot de passe
  }
};

// Fonction pour afficher/masquer le mot de passe
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

// Fonction de validation du mot de passe
const validatePassword = () => {
  console.log("Mot de passe entré :", password.value);

  // Affichage du cercle de chargement
  isLoading.value = true;

  // Simuler un délai de traitement (remplacer avec votre logique)
  setTimeout(() => {
    // Logique de validation de certificat ici

    // Si le certificat est valide
    isLoading.value = false;
    isSuccess.value = true;

    // Attendre quelques secondes avant la redirection
    setTimeout(() => {
      isSuccess.value = false;
      // Redirection vers une autre page après succès
      router.push('/success-page'); // Remplacer par la route souhaitée
    }, 2000);
  }, 3000); // Temps de chargement simulé
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

.toggle-password {
  position: absolute;
  right: 10px;
  top: 10px;
  cursor: pointer;
  font-size: 1.2rem;
}

.spinner-border {
  display: block;
  margin: 0 auto;
}

.alert {
  text-align: center;
}

@media (max-width: 768px) {
  .box-area {
    max-width: 90%;
  }
  .left-box, .right-box {
    width: 100%;
    padding: 20px;
  }
  .custom-card {
    width: 100%;
  }
}
</style>
