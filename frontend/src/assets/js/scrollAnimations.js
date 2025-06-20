/**
 * Gestion des animations au défilement (scroll animations)
 * Utilise l'API Intersection Observer pour détecter quand les éléments entrent dans le viewport
 */

// Options pour l'Intersection Observer
const observerOptions = {
  root: null, // viewport est utilisé comme zone d'observation
  rootMargin: '0px', // pas de marge
  threshold: 0.15 // 15% de l'élément doit être visible
};

// Fonction pour initialiser les animations au défilement
export function initScrollAnimations() {
  // Sélectionner tous les éléments avec l'attribut data-animate
  const animatedElements = document.querySelectorAll('[data-animate]');
  
  if (animatedElements.length === 0) return;
  
  // Créer l'observateur
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      // Si l'élément est visible
      if (entry.isIntersecting) {
        // Récupérer le type d'animation
        const animationType = entry.target.dataset.animate;
        // Ajouter la classe d'animation
        entry.target.classList.add('animated', animationType);
        // Arrêter d'observer cet élément
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  // Observer chaque élément
  animatedElements.forEach(element => {
    // Ajouter une classe pour cacher l'élément initialement
    element.classList.add('animate-hidden');
    // Observer l'élément
    observer.observe(element);
  });
}

// Fonction pour ajouter un délai d'animation aux éléments enfants
export function setupStaggeredAnimations() {
  // Sélectionner tous les éléments avec attribut data-stagger
  const staggerContainers = document.querySelectorAll('[data-stagger]');
  
  staggerContainers.forEach(container => {
    // Sélectionner les enfants directs qui doivent être animés
    const children = container.querySelectorAll(':scope > [data-animate]');
    
    // Ajouter un délai croissant à chaque enfant
    children.forEach((child, index) => {
      const delay = index * 0.1; // 100ms entre chaque élément
      child.style.animationDelay = `${delay}s`;
    });
  });
} 