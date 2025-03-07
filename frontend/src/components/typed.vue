<template>
  <!-- Conteneur principal contenant le texte animé -->
  <div class="container">
    <!-- Élément span qui sera utilisé pour afficher le texte animé -->
    <span ref="typedText"></span>
  </div>
</template>

<script setup>
// Importation des fonctions nécessaires de Vue.js
import { onMounted, ref } from "vue"; 
// Importation de la bibliothèque Typed.js pour l'effet d'écriture
import Typed from "typed.js";

// Déclaration d'une référence pour le texte animé
const typedText = ref(null);

// Exécuter le script lorsque le composant est monté
onMounted(() => {
  // Création d'une nouvelle instance de Typed.js et application à l'élément "typedText"
  new Typed(typedText.value, {
    strings: ["Signez En Un Clic"], // Texte qui sera affiché avec l'effet d'écriture
    typeSpeed: 230,  // Vitesse d'apparition des lettres (en millisecondes)
    backSpeed: 50,   // Vitesse de suppression des lettres (en millisecondes)
    showCursor: true, // Afficher un curseur clignotant "|" après le texte
    cursorChar: "|",  // Personnalisation du curseur
    loop: true       // Répéter l'animation à l'infini
  });
});
</script>

<style scoped>
/* Style du conteneur principal */
.container {
  font-family: 'Courier New', Courier, monospace; /* Police d'écriture façon machine à écrire */
  color: rgb(112, 105, 105); /* Couleur du texte en gris */
  font-weight: 700; /* Texte en gras */
  font-size: 24px; /* Taille du texte */
  text-align: center; /* Centrer le texte horizontalement */
  margin-top: 50px; /* Ajouter un espace en haut pour mieux positionner le texte */
}
</style>
