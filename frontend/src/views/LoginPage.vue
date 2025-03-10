<template>
  <div>
    <!-- Barre de navigation -->
    <navbar />
  </div>

  <!-- Conteneur principal pour centrer le contenu de connexion -->
  <div class="container d-flex justify-content-center align-items-center min-vh-100">
    
    <!-- Conteneur de connexion -->
    <div class="row border rounded-5 p-3 bg-white shadow box-area">
      
    <!-- Partie gauche : Image seule -->
    <div class="col-md-6 d-flex align-items-center justify-content-center left-box rounded-5 overflow-hidden h-75">
      <img src="@/assets/banniere.jpeg" class="img-fluid w-15 h-100 object-fit-cover" alt="Background Image" />
    </div>


      <!-- Partie droite : Formulaire de connexion -->
      <div class="col-md-6 d-flex flex-column justify-content-center align-items-center right-box">
        
        <!-- Titre de connexion stylisé -->
        <div class="header-text text-center mb-4">
          <h1 class="gradient-text">CONNEXION</h1>
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
        
        <!-- Modal Bootstrap pour le mot de passe du certificat -->
        <div class="modal fade" id="fileModal" tabindex="-1" aria-labelledby="fileModalLabel" aria-hidden="true">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="fileModalLabel">Mot de passe du certificat</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <input type="password" class="form-control" id="password" placeholder="Entrez votre mot de passe" required />
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                <button type="submit" form="passwordForm" class="btn btn-primary">Valider</button>
              </div>
            </div>
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
import { Modal } from "bootstrap";

// Référence pour l'input fichier
const fileInput = ref(null);
const fileName = ref("");

// Fonction pour ouvrir le sélecteur de fichier
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// Fonction pour gérer la sélection du fichier
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    fileName.value = file.name; // Affiche le nom du fichier
    
    // Affiche la modale après sélection du fichier
    const modal = new Modal(document.getElementById("fileModal"));
    modal.show();
  }
};
</script>

<style>
/* Style global du body */
body {
  font-family: 'Poppins', sans-serif;
  background-color: #ececec;
}

/* Conteneur principal */
.box-area {
  max-width: 1000px;
  width: 100%;
}

/* Partie droite */
.right-box {
  padding: 40px;
}

/* Partie gauche */
.left-box {
  background: whitesmoke;
  padding: 30px;
  text-align: center;
}

/* Style du titre "CONNEXION" */
.gradient-text {
  background: linear-gradient(90deg, #070707, #000000);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.5rem;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

/* Effet de survol sur la carte */
.custom-card {
  transition: all 0.3s ease;
  cursor: pointer;
  width: 80%;
}
.custom-card:hover {
  filter: brightness(0.9);
  transform: scale(0.95);
}

/* Responsive Design */
@media (max-width: 768px) {
  .box-area {
    flex-direction: column;
    height: auto;
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
