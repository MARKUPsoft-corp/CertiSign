<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import '@/assets/css/theme.css';

// Initialiser le thème lors du chargement de l'application
onMounted(() => {
  // Récupérer le thème stocké ou utiliser la préférence du navigateur
  const savedTheme = localStorage.getItem('theme');
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  
  if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme.matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
});
</script>

<style>
/* Styles globaux pour l'application */
body {
  margin: 0;
  padding: 0;
  font-family: 'Roboto', 'Segoe UI', sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-container {
  flex: 1;
  padding: 20px;
}

/* Icônes personnalisées pour CertiSign */
.certisign-icon {
  color: var(--primary-color);
}

/* Amélioration des transitions pour toute l'interface */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>