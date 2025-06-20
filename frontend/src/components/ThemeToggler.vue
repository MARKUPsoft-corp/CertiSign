<template>
  <div class="theme-switch-wrapper">
    <span class="theme-icon light-icon" :class="{ 'active': !darkMode }">
      <i class="bi bi-brightness-high-fill"></i>
    </span>
    <label class="theme-switch" for="theme-checkbox">
      <input type="checkbox" id="theme-checkbox" v-model="darkMode" @change="toggleTheme">
      <span class="slider">
        <span class="slider-icon">
          <i :class="darkMode ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill'"></i>
        </span>
      </span>
    </label>
    <span class="theme-icon dark-icon" :class="{ 'active': darkMode }">
      <i class="bi bi-moon-stars-fill"></i>
    </span>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// État pour suivre le mode sombre
const darkMode = ref(false);

// Fonction pour basculer le thème
const toggleTheme = () => {
  if (darkMode.value) {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
  }
};

// Initialiser le thème lors du chargement du composant
onMounted(() => {
  // Récupérer le thème stocké ou utiliser la préférence du navigateur
  const savedTheme = localStorage.getItem('theme');
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  
  if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme.matches)) {
    darkMode.value = true;
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    darkMode.value = false;
    document.documentElement.removeAttribute('data-theme');
  }
});
</script>

<style scoped>
.theme-switch-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-icon {
  font-size: 0.9rem;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  opacity: 0.5;
}

.theme-icon.active {
  opacity: 1;
  transform: scale(1.2);
}

.light-icon.active {
  color: #FFB100;
}

.dark-icon.active {
  color: #6C63FF;
}

.theme-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
  margin: 0;
}

.theme-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
  overflow: hidden;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
  z-index: 2;
}

input:checked + .slider {
  background-color: #2E3440;
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.slider-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  text-align: center;
  z-index: 1;
  font-size: 0.9rem;
  color: var(--text-light);
  display: flex;
  justify-content: space-between;
  padding: 0 6px;
}

[data-theme="dark"] .slider {
  background-color: #3B4252;
}

[data-theme="dark"] .theme-icon {
  color: var(--text-secondary);
}
</style> 