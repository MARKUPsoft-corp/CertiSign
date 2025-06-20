<template>
  <div class="language-selector">
    <div class="language-icon">
      <i class="bi bi-globe"></i>
    </div>
    <select ref="languageSelect" class="language-select" @change="changeLanguage">
      <option value="fr">Français</option>
      <option value="en">English</option>
    </select>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

const languageSelect = ref(null);

// Fonction pour changer la langue via l'URL de Google Translate
const changeLanguage = (event) => {
  const lang = event.target.value;
  localStorage.setItem('certiSignLanguage', lang);
  
  if (lang === 'fr') {
    // Retour à la langue d'origine - supprimer tous les cookies
    const cookieDomains = ['', '.' + window.location.hostname, window.location.hostname];
    
    cookieDomains.forEach(domain => {
      const cookiePaths = ['/', '/home'];
      cookiePaths.forEach(path => {
        document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${path}${domain ? `; domain=${domain}` : ''}`;
      });
    });
    
    // Recharger la page pour réinitialiser
    window.location.reload();
  } else {
    // Définir le cookie pour la traduction avec une date d'expiration longue (1 an)
    const transCookie = '/fr/' + lang;
    const expirationDate = new Date();
    expirationDate.setFullYear(expirationDate.getFullYear() + 1);
    
    // Définir le cookie sur tous les domaines et chemins possibles
    const cookieDomains = ['', '.' + window.location.hostname, window.location.hostname];
    
    cookieDomains.forEach(domain => {
      const cookieValue = `googtrans=${transCookie}; expires=${expirationDate.toUTCString()}; path=/${domain ? `; domain=${domain}` : ''}`;
      document.cookie = cookieValue;
    });
    
    // Forcer la présence du cookie en le vérifiant et en le réappliquant si nécessaire
    setTimeout(() => {
      if (document.cookie.indexOf('googtrans') === -1) {
        cookieDomains.forEach(domain => {
          document.cookie = `googtrans=${transCookie}; path=/${domain ? `; domain=${domain}` : ''}`;
        });
      }
    }, 100);
    
    // Si le script Google n'est pas encore chargé, le charger
    if (!window.google || !window.google.translate) {
      loadGoogleTranslateScript();
    } else {
      // Recharger la page pour appliquer la traduction
      window.location.reload();
    }
  }
};

// Fonction pour charger le script de Google Translate
const loadGoogleTranslateScript = () => {
  if (document.getElementById('google-translate-script')) return;
  
  const script = document.createElement('script');
  script.id = 'google-translate-script';
  script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
  script.async = true;
  script.defer = true;
  
  // Initialiser Google Translate en mode automatique
  window.googleTranslateElementInit = function() {
    new window.google.translate.TranslateElement({
      pageLanguage: 'fr',
      includedLanguages: 'en,fr',
      autoDisplay: false,
      layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE
    }, 'google_translate_element');
    
    // Masquer les éléments de l'interface de Google Translate
    hideTranslateBar();
  };
  
  document.head.appendChild(script);
};

// Fonction pour masquer la barre de notification de Google Translate
const hideTranslateBar = () => {
  // Créer une feuille de style pour masquer les éléments de Google Translate
  if (!document.getElementById('google-translate-style')) {
    const style = document.createElement('style');
    style.id = 'google-translate-style';
    style.innerHTML = `
      .goog-te-banner-frame { display: none !important; }
      .goog-te-menu-value { text-decoration: none !important; }
      body { position: static !important; top: 0 !important; }
      .goog-tooltip, .goog-tooltip:hover { display: none !important; }
      .goog-text-highlight { background-color: transparent !important; box-shadow: none !important; }
    `;
    document.head.appendChild(style);
  }
};

// Fonction pour vérifier et définir les cookies de traduction au démarrage
const setInitialLanguage = () => {
  const savedLang = localStorage.getItem('certiSignLanguage');
  
  // Si une langue est sauvegardée et ce n'est pas le français
  if (savedLang && savedLang !== 'fr') {
    // Définir le cookie pour la traduction avec une date d'expiration longue (1 an)
    const transCookie = '/fr/' + savedLang;
    const expirationDate = new Date();
    expirationDate.setFullYear(expirationDate.getFullYear() + 1);
    
    // Définir le cookie sur tous les domaines et chemins possibles
    const cookieDomains = ['', '.' + window.location.hostname, window.location.hostname];
    const cookiePaths = ['/', '/home'];
    
    cookieDomains.forEach(domain => {
      cookiePaths.forEach(path => {
        const cookieValue = `googtrans=${transCookie}; expires=${expirationDate.toUTCString()}; path=${path}${domain ? `; domain=${domain}` : ''}`;
        document.cookie = cookieValue;
      });
    });
    
    return true; // Indique qu'une traduction est nécessaire
  }
  
  return false; // Pas besoin de traduction
};

// Vérifier si un cookie de traduction est déjà présent
const hasTranslationCookie = () => {
  return document.cookie.indexOf('googtrans') > -1;
};

// Au montage du composant
onMounted(() => {
  // Créer un élément caché pour Google Translate
  if (!document.getElementById('google_translate_element')) {
    const translateElement = document.createElement('div');
    translateElement.id = 'google_translate_element';
    translateElement.style.display = 'none';
    document.body.appendChild(translateElement);
  }
  
  // Appliquer la langue sauvegardée au sélecteur
  const savedLang = localStorage.getItem('certiSignLanguage');
  if (savedLang && languageSelect.value) {
    languageSelect.value.value = savedLang;
  }
  
  // Vérifier si nous avons besoin de charger le script de traduction
  const needsTranslation = setInitialLanguage() || hasTranslationCookie();
  if (needsTranslation) {
    loadGoogleTranslateScript();
  }
  
  // Masquer la barre de notification de Google Translate
  hideTranslateBar();
  
  // Observer les changements dans le DOM pour masquer la barre de notification
  const observer = new MutationObserver(() => {
    hideTranslateBar();
  });
  
  observer.observe(document.body, { 
    childList: true, 
    subtree: true
  });
});
</script>

<style scoped>
.language-selector {
  margin: 0 15px;
  position: relative;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
  border-radius: 12px;
  padding: 5px 10px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.18);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.language-selector:hover {
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.language-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  color: var(--primary-color, #3498db);
  font-size: 1.2rem;
}

.language-select {
  padding: 6px 30px 6px 10px;
  border-radius: 8px;
  border: none;
  color: var(--text-color, #333);
  background-color: transparent;
  font-family: 'Poppins', sans-serif;
  font-size: 14px;
  font-weight: 500;
  outline: none;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  transition: all 0.3s ease;
  min-width: 110px;
}

.language-select:focus {
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.25);
}

.language-select:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Styles pour le mode sombre */
[data-theme="dark"] .language-selector {
  background: linear-gradient(135deg, rgba(30,30,30,0.5), rgba(20,20,20,0.5));
  border: 1px solid rgba(80,80,80,0.3);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

[data-theme="dark"] .language-icon {
  color: var(--primary-color, #60a5fa);
}

[data-theme="dark"] .language-select {
  color: var(--text-color, #fff);
}

[data-theme="dark"] .language-select:focus {
  box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.25);
}

[data-theme="dark"] .language-select:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

/* Styles pour les options du sélecteur */
.language-select option {
  background-color: var(--bg-color, #fff);
  color: var(--text-color, #333);
  padding: 8px;
}

[data-theme="dark"] .language-select option {
  background-color: var(--bg-color, #222);
  color: var(--text-color, #fff);
}
</style>

<style>
/* Styles pour masquer les éléments de Google Translate */
#google_translate_temp {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  width: 0 !important;
  overflow: hidden !important;
}
</style>
