<template>
  <div class="home-container">
    <!-- Fond animé avec particules flottantes -->
    <div class="particles-container">
      <div v-for="i in 20" :key="i" class="particle" 
        :class="{ 'particle-primary': i % 3 === 0, 'particle-accent': i % 3 === 1, 'particle-light': i % 3 === 2 }"
        :style="{
          top: particlePositions[(i-1) % particlePositions.length].top,
          left: particlePositions[(i-1) % particlePositions.length].left,
          width: particlePositions[(i-1) % particlePositions.length].size + 'px',
          height: particlePositions[(i-1) % particlePositions.length].size + 'px',
          animationDuration: particlePositions[(i-1) % particlePositions.length].duration + 's',
          animationDelay: particlePositions[(i-1) % particlePositions.length].delay + 's'
        }">
      </div>
    </div>

    <!-- En-tête avec logo et navigation -->
    <header class="header">
      <div class="logo-container">
        <img src="@/assets/doc.png" alt="Doc@uthANTIC Logo" class="header-logo-img">
        <h1 class="logo-text">
          <span class="text-green">Doc</span>
          <span class="text-red">@uth</span>
          <span class="text-yellow">ANTIC</span>
        </h1>
      </div>
      <nav class="nav-menu" :class="{ 'active': isMenuOpen }">
        <div class="mobile-menu-close" @click="toggleMenu">
          <i class="bi bi-x-lg"></i>
        </div>
        <ul>
          <li><a href="#features" class="nav-link" @click="closeMenuIfMobile">Fonctionnalités</a></li>
          <li><a href="#about" class="nav-link" @click="closeMenuIfMobile">À propos</a></li>
          <li><a href="#contact" class="nav-link" @click="closeMenuIfMobile">Contact</a></li>
          <li>
            <ThemeToggler class="theme-toggler" />
          </li>
          <li>
            <LanguageSelector class="language-selector" />
          </li>
          <li>
            <router-link to="/login" class="login-btn">
              <i class="bi bi-box-arrow-in-right"></i> Connexion
            </router-link>
          </li>
        </ul>
      </nav>
      <div class="mobile-menu-toggle" @click="toggleMenu">
        <i class="bi" :class="isMenuOpen ? 'bi-x-lg' : 'bi-list'"></i>
      </div>
    </header>

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- Section de présentation principale -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">
            <span class="highlight-text">Sécurisez vos documents TEST</span>
            <br>avec des signatures électroniques
          </h1>
          <p class="hero-description">
            Doc@uthANTIC est une solution de signature électronique professionnelle et sécurisée qui vous permet
            de signer et de vérifier vos documents importants en toute confiance.
          </p>
          <div class="hero-actions">
            <router-link to="/login" class="btn btn-primary btn-lg pulse-animation">
              <i class="bi bi-shield-check me-2"></i>Commencer maintenant
            </router-link>
            <a href="#features" class="btn btn-outline-primary btn-lg ms-3">
              <i class="bi bi-info-circle me-2"></i>En savoir plus
            </a>
          </div>
        </div>
        <div class="hero-image">
          <img src="@/assets/images/secure-document.svg" alt="Document sécurisé" class="floating-animation">
        </div>
      </section>

      <!-- Section statistiques -->
      <section class="stats-section">
        <div class="stats-container" data-stagger>
          <div class="stat-card" data-animate="fade-in-up">
            <div class="stat-value"><span class="counter">10,000+</span></div>
            <div class="stat-label">Documents signés</div>
          </div>
          <div class="stat-card" data-animate="fade-in-up">
            <div class="stat-value"><span class="counter">1,000+</span></div>
            <div class="stat-label">Utilisateurs actifs</div>
          </div>
          <div class="stat-card" data-animate="fade-in-up">
            <div class="stat-value"><span class="counter">99.9%</span></div>
            <div class="stat-label">Disponibilité</div>
          </div>
          <div class="stat-card" data-animate="fade-in-up">
            <div class="stat-value"><span class="counter">100%</span></div>
            <div class="stat-label">Conformité légale</div>
          </div>
        </div>
      </section>

      <!-- Section des fonctionnalités -->
      <section id="features" class="features-section">
        <h2 class="section-title" data-animate="fade-in-up">
          <span class="line-decoration"></span>
          Nos Fonctionnalités
          <span class="line-decoration"></span>
        </h2>
        <div class="feature-cards" data-stagger>
          <div class="feature-card" v-for="(feature, index) in features" :key="index" data-animate="zoom-in">
            <div class="feature-icon" :class="feature.iconClass">
              <i :class="feature.icon"></i>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </div>
      </section>

      <!-- Section "Comment ça marche" -->
      <section class="how-it-works">
        <h2 class="section-title" data-animate="fade-in-up">
          <span class="line-decoration"></span>
          Comment ça marche
          <span class="line-decoration"></span>
        </h2>
        <div class="steps-container" data-stagger>
          <div class="step-item" v-for="(step, index) in steps" :key="index" data-animate="fade-in-left">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h3 class="step-title">{{ step.title }}</h3>
              <p class="step-description">{{ step.description }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Section de sécurité -->
      <section id="about" class="security-section" data-animate="fade-in-up">
        <div class="security-container">
          <div class="security-image" data-animate="fade-in-right">
            <div class="security-shape"></div>
            <div class="security-icon">
              <i class="bi bi-shield-check"></i>
            </div>
          </div>
          <div class="security-content" data-animate="fade-in-left">
            <h2 class="security-title">Sécurité de niveau entreprise</h2>
            <p class="security-description">
              Chez Doc@uthANTIC, nous prenons la sécurité de vos documents très au sérieux. Notre plateforme utilise 
              un chiffrement de bout en bout, une authentification à deux facteurs et des certificats numériques conformes 
              aux normes internationales pour garantir l'intégrité de vos signatures.
            </p>
            <ul class="security-features">
              <li><i class="bi bi-check-circle-fill"></i> Chiffrement de bout en bout</li>
              <li><i class="bi bi-check-circle-fill"></i> Authentification à deux facteurs</li>
              <li><i class="bi bi-check-circle-fill"></i> Conformité à la Loi n°2010/021</li>
              <li><i class="bi bi-check-circle-fill"></i> Audits de sécurité réguliers</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Section de témoignages -->
      <section class="testimonials">
        <h2 class="section-title" data-animate="fade-in-up">
          <span class="line-decoration"></span>
          Témoignages
          <span class="line-decoration"></span>
        </h2>
        <div class="testimonial-slider" data-stagger>
          <div class="testimonial-card" v-for="(testimonial, index) in testimonials" :key="index" data-animate="fade-in-up">
            <div class="testimonial-content">
              <p class="testimonial-text">"{{ testimonial.text }}"</p>
              <div class="testimonial-author">
                <div class="testimonial-author-avatar">
                  <i class="bi bi-person-circle"></i>
                </div>
                <div class="testimonial-author-info">
                  <h4 class="testimonial-author-name">{{ testimonial.name }}</h4>
                  <p class="testimonial-author-title">{{ testimonial.title }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Foire aux questions -->
      <section id="contact" class="faq-section">
        <h2 class="section-title" data-animate="fade-in-up">
          <span class="line-decoration"></span>
          Questions fréquentes
          <span class="line-decoration"></span>
        </h2>
        <div class="faq-container" data-stagger>
          <div class="faq-item" data-animate="fade-in-up">
            <div class="faq-question">
              <h3>Comment fonctionne la signature électronique ?</h3>
              <span class="faq-icon"><i class="bi bi-plus"></i></span>
            </div>
            <div class="faq-answer">
              <p>La signature électronique utilise des certificats numériques pour créer une empreinte numérique unique 
                qui lie le signataire au document. Cette empreinte est cryptographiquement sécurisée et permet de vérifier 
                l'authenticité et l'intégrité du document.</p>
            </div>
          </div>
          <div class="faq-item" data-animate="fade-in-up">
            <div class="faq-question">
              <h3>Les signatures électroniques sont-elles légalement valides ?</h3>
              <span class="faq-icon"><i class="bi bi-plus"></i></span>
            </div>
            <div class="faq-answer">
              <p>Oui, les signatures électroniques sont légalement valides dans la plupart des pays. EAu cameroun elle est régit par la Loi n°2010/021 du 21 Décembre 2010.</p>
            </div>
          </div>
          <div class="faq-item" data-animate="fade-in-up">
            <div class="faq-question">
              <h3>Comment obtenir un certificat numérique ?</h3>
              <span class="faq-icon"><i class="bi bi-plus"></i></span>
            </div>
            <div class="faq-answer">
              <p>Vous pouvez obtenir un certificat numérique auprès de l'Agence National des Technologies de l'Information et de la Communication (ANTIC),
                plus précisément auprès de son organe spécialisé le Centre National de Cryptographie et de Certification Electronique situé à la Poste centrale. 
                Doc@uthANTIC vous accompagne dans ce processus et vous aide à choisir le certificat adapté à vos besoins.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Section d'appel à l'action -->
      <section class="cta-section" data-animate="fade-in-up">
        <div class="cta-content">
          <h2 class="cta-title">Prêt à sécuriser vos documents ?</h2>
          <p class="cta-description">
            Rejoignez des milliers d'utilisateurs qui font confiance à Doc@uthANTIC pour leurs signatures électroniques.
          </p>
          <router-link to="/login" class="btn btn-primary btn-lg cta-button focus-glow">
            <i class="bi bi-shield-check me-2"></i>Commencer maintenant
          </router-link>
        </div>
      </section>
    </main>

    <!-- Pied de page -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand" data-animate="fade-in-left">
          <div class="footer-logo">
            <img src="@/assets/doc.png" alt="Doc@uthANTIC Logo" class="footer-logo-img">
            <div class="footer-logo-text">
              <span class="text-green">Doc</span>
              <span class="text-red">@uth</span>
              <span class="text-yellow">ANTIC</span>
            </div>
          </div>
          <p class="footer-tagline">La solution de signature électronique de confiance</p>
        </div>
        <div class="footer-links" data-stagger>
          <div class="footer-links-column" data-animate="fade-in-up">
            <h4>Produit</h4>
            <ul>
              <li><a href="#features">Fonctionnalités</a></li>
              <li><a href="#">Tarifs</a></li>
              <li><a href="#">FAQ</a></li>
            </ul>
          </div>
          <div class="footer-links-column" data-animate="fade-in-up">
            <h4>Ressources</h4>
            <ul>
              <li><a href="#">Documentation</a></li>
              <li><a href="#">Tutoriels</a></li>
              <li><a href="#">Blog</a></li>
            </ul>
          </div>
          <div class="footer-links-column" data-animate="fade-in-up">
            <h4>Société</h4>
            <ul>
              <li><a href="#about">À propos</a></li>
              <li><a href="#contact">Contact</a></li>
              <li><a href="#">Carrières</a></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2025 Doc@uthANTIC. Tous droits réservés.</p>
        <div class="footer-social">
          <a href="#" class="social-icon"><i class="bi bi-facebook"></i></a>
          <a href="#" class="social-icon"><i class="bi bi-twitter"></i></a>
          <a href="#" class="social-icon"><i class="bi bi-linkedin"></i></a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ThemeToggler from '@/components/ThemeToggler.vue';
import LanguageSelector from '@/components/LanguageSelector.vue';
import { initScrollAnimations, setupStaggeredAnimations } from '@/assets/js/scrollAnimations.js';

// État du menu mobile
const isMenuOpen = ref(false);

// Fonction pour basculer le menu mobile
const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value;
  
  // Bloquer le défilement quand le menu est ouvert
  if (isMenuOpen.value) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = 'auto';
  }
};

// Fermer le menu si on est sur mobile et qu'on clique sur un lien
const closeMenuIfMobile = () => {
  if (window.innerWidth <= 992) {
    isMenuOpen.value = false;
    document.body.style.overflow = 'auto';
  }
};

// Données pour les fonctionnalités
const features = [
  {
    title: 'Signature Électronique',
    description: 'Signez vos documents électroniquement avec la même valeur juridique qu\'une signature manuscrite.',
    icon: 'bi bi-pen-fill',
    iconClass: 'icon-primary'
  },
  {
    title: 'Vérification de Signature',
    description: 'Vérifiez facilement l\'authenticité et l\'intégrité des documents signés.',
    icon: 'bi bi-check-circle-fill',
    iconClass: 'icon-accent'
  },
  {
    title: 'Sécurité de Niveau Bancaire',
    description: 'Protégez vos documents avec un chiffrement de niveau bancaire et une authentification forte.',
    icon: 'bi bi-shield-lock-fill',
    iconClass: 'icon-primary-dark'
  },
  {
    title: 'Gestion des Documents',
    description: 'Gérez facilement tous vos documents signés dans un tableau de bord intuitif.',
    icon: 'bi bi-folder-fill',
    iconClass: 'icon-primary'
  },
  {
    title: 'Conformité Légale',
    description: 'Conforme à la Loi n°2010/021, assurant la validité juridique de vos signatures.',
    icon: 'bi bi-file-earmark-check-fill',
    iconClass: 'icon-accent'
  },
  {
    title: 'Accessibilité',
    description: 'Accédez à vos documents et signez où que vous soyez, à tout moment.',
    icon: 'bi bi-laptop-fill',
    iconClass: 'icon-primary-dark'
  }
];

// Données pour les étapes
const steps = [
  {
    title: 'Créez votre compte',
    description: 'Inscrivez-vous avec votre certificat numérique pour commencer à utiliser Doc@uthANTIC.'
  },
  {
    title: 'Importez vos documents',
    description: 'Téléchargez facilement vos documents PDF à signer.'
  },
  {
    title: 'Signez électroniquement',
    description: 'Appliquez votre signature électronique sécurisée aux documents.'
  },
  {
    title: 'Partagez et vérifiez',
    description: 'Partagez vos documents signés et permettez à d\'autres de vérifier leur authenticité.'
  }
];

// Données pour les témoignages
const testimonials = [
  {
    text: 'Doc@uthANTIC a transformé notre processus de signature de contrats. Nous économisons des heures chaque semaine !',
    name: 'KAMENI Marthin',
    title: 'Directrice des Opérations, ABC Corp'
  },
  {
    text: 'L\'interface est intuitive et la sécurité est au rendez-vous. Exactement ce dont notre cabinet avait besoin.',
    name: 'MVONDO Edouard',
    title: 'Avocat, Cabinet MVONDO & Associés'
  },
  {
    text: 'Nous utilisons Doc@uthANTIC quotidiennement pour tous nos documents officiels. Le service client est exceptionnel.',
    name: 'YAKAM Isabelle',
    title: 'Notaire'
  }
];

// Positionnement aléatoire des particules
const particlePositions = Array.from({ length: 20 }, () => ({
  top: `${Math.random() * 100}%`,
  left: `${Math.random() * 100}%`,
  size: Math.random() * 10 + 5,
  duration: Math.random() * 15 + 10,
  delay: Math.random() * 5
}));

// Initialisation au chargement de la page
onMounted(() => {
  document.title = "Doc@uthANTIC - Solution de Signature Électronique";
  
  // Initialiser les animations au défilement
  initScrollAnimations();
  setupStaggeredAnimations();
  
  // Animation du texte de la bannière
  const heroTitle = document.querySelector('.hero-title');
  if (heroTitle) {
    heroTitle.classList.add('text-focus-in');
  }
  
  // Animation des particules
  animateParticles();
});

// Fonction pour animer les particules
function animateParticles() {
  const particles = document.querySelectorAll('.particle');
  particles.forEach((particle, index) => {
    const position = particlePositions[index % particlePositions.length];
    particle.style.top = position.top;
    particle.style.left = position.left;
    particle.style.width = `${position.size}px`;
    particle.style.height = `${position.size}px`;
    particle.style.animationDuration = `${position.duration}s`;
    particle.style.animationDelay = `${position.delay}s`;
  });
}
</script>

<style scoped>
/* Importation des animations */
@import '@/assets/css/animations.css';

/* Styles généraux */
.home-container {
  min-height: 100vh;
  position: relative;
  background-color: var(--bg-color);
  color: var(--text-color);
  overflow-x: hidden;
}

/* Animation de particules */
.particles-container {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  opacity: 0.3;
  animation: float 20s infinite linear;
  box-shadow: 0 0 10px 2px rgba(46, 139, 87, 0.2);
}

.particle-primary {
  background-color: var(--primary-color);
}

.particle-accent {
  background-color: var(--accent-color);
}

.particle-light {
  background-color: var(--primary-light);
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.5;
  }
  90% {
    opacity: 0.5;
  }
  100% {
    transform: translateY(-100vh) translateX(100vw) rotate(360deg);
    opacity: 0;
  }
}

/* Styles d'en-tête */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background-color: var(--bg-light);
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: 10;
  animation: slideInDown 0.8s forwards;
}

.logo-container {
  display: flex;
  align-items: center;
  z-index: 11;
}

.header-logo-img {
  width: 50px;
  height: auto;
  margin-right: 10px;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  font-family: "Motoya Maru Std-w6", Arial, sans-serif;
}

.text-green {
  color: #00a651; /* Brighter green */
}

.text-red {
  color: #e74c3c;
}

.text-yellow {
  color: #f1c40f;
}

.nav-menu ul {
  display: flex;
  list-style-type: none;
  margin: 0;
  padding: 0;
  gap: 20px;
  align-items: center;
}

.nav-link {
  color: var(--text-color);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 8px 15px;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.nav-link:before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background-color: var(--primary-color);
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.nav-link:hover {
  color: var(--primary-color);
}

.nav-link:hover:before {
  width: 80%;
}

.theme-toggler {
  margin: 0 15px;
}

.login-btn {
  background-color: var(--primary-color);
  color: var(--text-light);
  padding: 10px 20px;
  border-radius: 30px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  z-index: 1;
  border: none;
  cursor: pointer;
}

/* Menu mobile */
.mobile-menu-toggle {
  display: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: var(--text-color);
  z-index: 11;
  transition: all 0.3s ease;
}

.mobile-menu-close {
  display: none;
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 1.8rem;
  cursor: pointer;
  color: var(--text-color);
  transition: all 0.3s ease;
}

/* Responsive styles for header */
@media (max-width: 992px) {
  .header {
    padding: 15px 30px;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .mobile-menu-close {
    display: block;
  }
  
  .nav-menu {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    background-color: var(--bg-light);
    box-shadow: var(--shadow-lg);
    transition: right 0.3s ease;
    z-index: 1000;
    padding: 80px 20px 20px;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
  
  .nav-menu.active {
    right: 0;
  }
  
  .nav-menu ul {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .nav-link {
    width: 100%;
    display: block;
    padding: 12px 15px;
  }
  
  .dropdown {
    width: 100%;
  }
  
  .login-btn {
    width: 100%;
    justify-content: center;
  }
  
  .dropdown-menu {
    position: static;
    display: none;
    width: 100%;
    margin-top: 10px;
    box-shadow: none;
    border: 1px solid var(--border-color);
  }
  
  .dropdown:hover .dropdown-menu,
  .dropdown:focus .dropdown-menu,
  .dropdown:active .dropdown-menu {
    display: block;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 12px 20px;
  }
  
  .logo-container {
    flex-direction: row;
    align-items: center;
  }
  
  .header-logo-img {
    width: 45px;
  }
  
  .logo-text {
    font-size: 1.5rem;
  }
  
  .footer-logo-img {
    width: 40px;
  }
  
  .footer-logo-text {
    font-size: 1.3rem;
  }
}

@media (max-width: 576px) {
  .header-logo-img {
    width: 40px;
  }
  
  .logo-text {
    font-size: 1.3rem;
  }
  
  .footer-logo-img {
    width: 35px;
  }
  
  .footer-logo-text {
    font-size: 1.2rem;
  }
  
  .badge-cert i {
    font-size: 1rem;
  }
}

/* Section héros */
.hero-section {
  display: flex;
  padding: 60px 40px;
  min-height: 70vh;
  position: relative;
  z-index: 1;
  align-items: center;
  justify-content: space-between;
}

.hero-content {
  flex: 1;
  max-width: 600px;
  animation: fadeInLeft 1s forwards;
}

.hero-title {
  font-size: 3.5rem;
  margin-bottom: 20px;
  line-height: 1.2;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.text-focus-in {
  animation: textFocusIn 1s cubic-bezier(0.550, 0.085, 0.680, 0.530) both;
}

@keyframes textFocusIn {
  0% {
    filter: blur(12px);
    opacity: 0;
  }
  100% {
    filter: blur(0);
    opacity: 1;
  }
}

.highlight-text {
  color: var(--primary-color);
  font-weight: 800;
  position: relative;
  background: linear-gradient(120deg, var(--primary-color), var(--accent-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.highlight-text::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  border-radius: 3px;
  animation: lineExpand 1.5s forwards;
  animation-delay: 0.5s;
}

@keyframes lineExpand {
  0% {
    width: 0;
  }
  100% {
    width: 100%;
  }
}

.hero-description {
  font-size: 1.2rem;
  margin-bottom: 40px;
  color: var(--text-secondary);
  line-height: 1.6;
  animation: fadeIn 1s forwards;
  animation-delay: 0.3s;
  opacity: 0;
}

.hero-actions {
  display: flex;
  gap: 15px;
  animation: fadeIn 1s forwards;
  animation-delay: 0.6s;
  opacity: 0;
}

.pulse-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(46, 139, 87, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(46, 139, 87, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(46, 139, 87, 0);
  }
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  animation: fadeInRight 1s forwards;
  animation-delay: 0.3s;
  opacity: 0;
}

.hero-image img {
  max-width: 100%;
  max-height: 400px;
  filter: drop-shadow(0 10px 15px rgba(2, 119, 47, 0.15));
}

.floating-animation {
  animation: floating 6s ease-in-out infinite;
}

@keyframes floating {
  0% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(2deg);
  }
  100% {
    transform: translateY(0px) rotate(0deg);
  }
}

/* Sections */
.features-section, .how-it-works, .testimonials, .cta-section {
  padding: 80px 40px;
  position: relative;
  z-index: 1;
}

.section-title {
  text-align: center;
  font-size: 2.2rem;
  margin-bottom: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-weight: 700;
}

.line-decoration {
  display: inline-block;
  height: 2px;
  width: 60px;
  background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
  margin: 0 15px;
}

/* Features */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.feature-card {
  background-color: var(--card-bg);
  border-radius: 12px;
  padding: 30px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  border: 2px solid transparent;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-light);
}

.feature-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 2rem;
  color: white;
  transition: all 0.3s ease;
}

.icon-primary {
  background-color: var(--primary-color);
}

.icon-accent {
  background-color: var(--accent-color);
}

.icon-primary-dark {
  background-color: var(--primary-dark);
}

.feature-card:hover .feature-icon {
  transform: scale(1.1) rotate(10deg);
}

.feature-title {
  font-size: 1.5rem;
  margin-bottom: 15px;
  font-weight: 600;
  color: var(--primary-color);
}

.feature-description {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Steps section */
.steps-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.steps-container:before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 32px;
  width: 4px;
  background: linear-gradient(to bottom, var(--primary-color), var(--accent-color));
  border-radius: 2px;
}

.step-item {
  display: flex;
  margin-bottom: 40px;
  position: relative;
}

.step-number {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 700;
  margin-right: 25px;
  z-index: 1;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.step-item:hover .step-number {
  transform: scale(1.1);
  background-color: var(--accent-color);
}

.step-content {
  flex: 1;
  background-color: var(--card-bg);
  border-radius: 12px;
  padding: 25px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.step-item:hover .step-content {
  transform: translateX(10px);
  box-shadow: var(--shadow-md);
}

.step-title {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: var(--primary-color);
  font-weight: 600;
}

.step-description {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Testimonials */
.testimonial-slider {
  display: flex;
  overflow-x: auto;
  padding: 20px 0;
  gap: 30px;
  scroll-snap-type: x mandatory;
  scrollbar-width: none; /* Firefox */
}

.testimonial-slider::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.testimonial-card {
  min-width: 300px;
  max-width: 350px;
  border-radius: 12px;
  background-color: var(--card-bg);
  box-shadow: var(--shadow-md);
  padding: 30px;
  scroll-snap-align: start;
  transition: all 0.3s ease;
  border-left: 4px solid var(--primary-color);
  flex: 1;
}

.testimonial-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: var(--shadow-lg);
}

.testimonial-text {
  font-style: italic;
  margin-bottom: 20px;
  position: relative;
  padding-left: 25px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.testimonial-text:before {
  content: '"';
  position: absolute;
  left: 0;
  top: -10px;
  font-size: 3rem;
  color: var(--primary-light);
  font-family: Georgia, serif;
  line-height: 1;
}

.testimonial-author {
  display: flex;
  align-items: center;
}

.testimonial-author-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 1.5rem;
  color: white;
}

.testimonial-author-name {
  font-weight: 600;
  margin: 0;
  color: var(--primary-color);
}

.testimonial-author-title {
  font-size: 0.9rem;
  margin: 0;
  color: var(--text-secondary);
}

/* CTA Section */
.cta-section {
  background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
  color: white;
  text-align: center;
  border-radius: 20px;
  margin: 40px;
  padding: 60px;
  box-shadow: var(--shadow-lg);
}

.cta-title {
  font-size: 2.5rem;
  margin-bottom: 20px;
  font-weight: 700;
}

.cta-description {
  max-width: 600px;
  margin: 0 auto 30px;
  font-size: 1.2rem;
  opacity: 0.9;
}

.cta-button {
  background-color: white;
  color: var(--primary-dark) !important;
  border: none;
  padding: 15px 30px;
  font-size: 1.1rem;
  border-radius: 30px;
  transition: all 0.3s ease;
}

.cta-button:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  background-color: white !important;
}

/* Footer */
.footer {
  background-color: var(--bg-light);
  color: var(--text-color);
  padding: 60px 40px 20px;
  margin-top: 60px;
  position: relative;
  z-index: 1;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;
  flex-wrap: wrap;
  gap: 40px;
}

.footer-brand {
  flex: 1;
  min-width: 250px;
}

.footer-logo {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 15px;
  color: var(--primary-color);
}

.footer-logo-img {
  width: 50px;
  height: auto;
  margin-right: 10px;
}

.footer-logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  font-family: "Motoya Maru Std-w6", Arial, sans-serif;
}

.footer-tagline {
  color: var(--text-secondary);
  margin-bottom: 20px;
  max-width: 300px;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 60px;
}

.footer-links-column h4 {
  font-size: 1.2rem;
  margin-bottom: 20px;
  position: relative;
  display: inline-block;
}

.footer-links-column h4:after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 30px;
  height: 3px;
  background-color: var(--primary-color);
}

.footer-links-column ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links-column ul li {
  margin-bottom: 10px;
}

.footer-links-column a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-block;
}

.footer-links-column a:hover {
  color: var(--primary-color);
  transform: translateX(5px);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
  flex-wrap: wrap;
  gap: 20px;
}

.footer-social {
  display: flex;
  gap: 15px;
}

.social-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--bg-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  transition: all 0.3s ease;
}

.social-icon:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-5px);
}

/* Animations supplémentaires */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInDown {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes tada {
  0% {transform: scale(1);}
  10%, 20% {transform: scale(0.9) rotate(-3deg);}
  30%, 50%, 70%, 90% {transform: scale(1.1) rotate(3deg);}
  40%, 60%, 80% {transform: scale(1.1) rotate(-3deg);}
  100% {transform: scale(1) rotate(0);}
}

/* Responsive design */
@media (max-width: 992px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
  }
  
  .hero-content {
    max-width: 100%;
    margin-bottom: 40px;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .steps-container:before {
    left: 35px;
  }
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    padding: 20px;
  }
  
  .nav-menu ul {
    margin-top: 20px;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .hero-title {
    font-size: 2.2rem;
  }
  
  .hero-image img {
    max-height: 300px;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
  }
  
  .step-number {
    width: 50px;
    height: 50px;
    font-size: 1.4rem;
  }
  
  .cta-section {
    margin: 20px;
    padding: 40px 20px;
  }
  
  .cta-title {
    font-size: 2rem;
  }
}

/* Ajustements pour le mode sombre */
[data-theme="dark"] .highlight-text::after {
  background: linear-gradient(90deg, var(--primary-color), var(--accent-light));
}

[data-theme="dark"] .feature-card {
  background-color: rgba(52, 58, 64, 0.8);
}

[data-theme="dark"] .step-content {
  background-color: rgba(52, 58, 64, 0.8);
}

[data-theme="dark"] .testimonial-card {
  background-color: rgba(52, 58, 64, 0.8);
}

/* Stats Section */
.stats-section {
  padding: 40px;
  margin: 0 40px;
  background-color: var(--card-bg);
  border-radius: 15px;
  box-shadow: var(--shadow-md);
  position: relative;
  z-index: 2;
  margin-top: -50px;
}

.stats-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  gap: 20px;
}

.stat-card {
  flex: 1;
  min-width: 180px;
  text-align: center;
  padding: 20px;
  border-radius: 10px;
  transition: all 0.3s ease;
  background-color: transparent;
}

.stat-card:hover {
  background-color: var(--bg-dark);
  transform: translateY(-5px);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--primary-color);
  position: relative;
  display: inline-block;
}

.stat-value:after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background-color: var(--accent-color);
  border-radius: 3px;
}

.stat-label {
  font-size: 1rem;
  color: var(--text-secondary);
}

.counter {
  display: inline-block;
  animation: countUp 2s ease-out forwards;
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Security Section */
.security-section {
  padding: 80px 40px;
}

.security-container {
  display: flex;
  align-items: center;
  gap: 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.security-image {
  flex: 1;
  position: relative;
  height: 350px;
}

.security-shape {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  animation: morphShape 8s infinite alternate ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 0;
}

@keyframes morphShape {
  0% {
    border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  }
  25% {
    border-radius: 58% 42% 75% 25% / 76% 46% 54% 24%;
  }
  50% {
    border-radius: 50% 50% 33% 67% / 55% 27% 73% 45%;
  }
  75% {
    border-radius: 33% 67% 58% 42% / 63% 68% 32% 37%;
  }
  100% {
    border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  }
}

.security-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  font-size: 7rem;
  color: rgba(255, 255, 255, 0.8);
  animation: pulse 3s infinite;
}

.security-content {
  flex: 1;
  max-width: 600px;
}

.security-title {
  font-size: 2.2rem;
  margin-bottom: 20px;
  color: var(--primary-color);
  font-weight: 700;
}

.security-description {
  margin-bottom: 30px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.security-features {
  list-style: none;
  padding: 0;
  margin: 0;
}

.security-features li {
  margin-bottom: 15px;
  padding-left: 30px;
  position: relative;
  color: var(--text-secondary);
}

.security-features li i {
  position: absolute;
  left: 0;
  top: 2px;
  color: var(--primary-color);
}

/* FAQ Section */
.faq-section {
  padding: 80px 40px;
}

.faq-container {
  max-width: 800px;
  margin: 0 auto;
}

.faq-item {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  background-color: var(--card-bg);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.faq-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-3px);
}

.faq-question {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.faq-question h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-color);
  flex: 1;
}

.faq-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
}

.faq-item:hover .faq-icon {
  background-color: var(--primary-color);
  transform: rotate(45deg);
}

.faq-answer {
  padding: 0 20px 20px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Ajout d'un élément décoratif */
.decorative-element {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--primary-light) 0%, transparent 70%);
  opacity: 0.2;
  z-index: 0;
}

.decorative-top-right {
  top: -150px;
  right: -150px;
}

.decorative-bottom-left {
  bottom: -150px;
  left: -150px;
}

/* Responsive pour les nouvelles sections */
@media (max-width: 992px) {
  .security-container {
    flex-direction: column;
    text-align: center;
  }
  
  .security-content {
    max-width: 100%;
  }
  
  .security-features li {
    text-align: left;
  }
  
  .stats-container {
    flex-direction: column;
    align-items: center;
  }
  
  .stat-card {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .stats-section {
    margin: 0 20px;
    margin-top: -30px;
  }
  
  .security-shape {
    width: 200px;
    height: 200px;
  }
  
  .security-icon {
    font-size: 5rem;
  }
  
  .security-title {
    font-size: 1.8rem;
  }
}

@media (max-width: 576px) {
  .faq-question h3 {
    font-size: 1rem;
  }
}

/* Animation pour les FAQ */
.faq-item:hover .faq-answer {
  animation: fadeIn 0.5s forwards;
}

/* Animation pour le compteur de statistiques */
@keyframes countUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Styles pour le menu déroulant */
.dropdown {
  position: relative;
  display: inline-block;
}

/* Style du bouton de connexion modifié pour être un lien direct */
.login-btn {
  display: flex;
  align-items: center;
  cursor: pointer;
  text-decoration: none;
  background-color: var(--primary-color);
  color: var(--text-light);
  padding: 10px 20px;
  border-radius: 30px;
  font-weight: 600;
  transition: all 0.3s ease;
  gap: 8px;
  position: relative;
  overflow: hidden;
  z-index: 1;
  border: none;
}

.login-btn:hover {
  background-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.dropdown-toggle::after {
  content: '';
  display: inline-block;
  margin-left: 0.5em;
  vertical-align: middle;
  border-top: 0.3em solid;
  border-right: 0.3em solid transparent;
  border-left: 0.3em solid transparent;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 1000;
  display: none;
  min-width: 10rem;
  padding: 0.5rem 0;
  margin: 0.125rem 0 0;
  font-size: 0.9rem;
  color: #212529;
  text-align: left;
  list-style: none;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 0.25rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.5rem 1.5rem;
  clear: both;
  font-weight: 400;
  color: #212529;
  text-align: inherit;
  white-space: nowrap;
  background-color: transparent;
  border: 0;
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s;
}

.dropdown-item i {
  margin-right: 0.5rem;
}

.dropdown-item:hover, .dropdown-item:focus {
  color: var(--primary-color);
  text-decoration: none;
  background-color: #f8f9fa;
}

/* Dark mode pour dropdown */
:root.dark-mode .dropdown-menu {
  background-color: #2c3e50;
  border-color: rgba(255, 255, 255, 0.15);
}

:root.dark-mode .dropdown-item {
  color: #f8f9fa;
}

:root.dark-mode .dropdown-item:hover,
:root.dark-mode .dropdown-item:focus {
  color: var(--accent-color);
  background-color: #1a252f;
}

.main-content {
  padding: 10px;
  position: relative;
  z-index: 1;
  max-width: 1750px;
  margin: 0 auto;
}

@media (max-width: 992px) {
  .main-content {
    padding: 30px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px;
  }
}

@media (max-width: 576px) {
  .main-content {
    padding: 15px;
  }
}
</style>