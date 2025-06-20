/* 
  le fichier index.js dans le dossier router sert à  configurer le Vue Router pour gérer la navigation entre 
  les différentes vues de l'application. C'est ici qu'on définis les routes et où on crées l'instance 
  du routeur. 
*/

import { createRouter, createWebHistory } from 'vue-router'; //ici, on importe deux fonctions depuis le module vue-router. 
//createwebhistory permet de créer un mode de navigation basé sur l'historique de l'URL du navigateur, ce qui signifie qu'il utilise les chemins d'URL propres (sans #).
import LoginPage from '@/views/LoginPage.vue'; //Ici, on importes le composant LoginPage.vue situé dans le répertoire @/views. Le symbole @ fait référence au dossier src du projet, ce qui est un raccourci couramment utilisé dans Vue.js pour accéder facilement aux fichiers.
import HomePage from '@/views/HomePage.vue'; // pareil ici pour la HomePage
import SignDocument from '@/views/SignDocument.vue'; // Import de la page de signature
import NewDashboard from '@/views/NewDashboard.vue'; // Import du tableau de bord principal

// Import des nouveaux tableaux de bord organisationnels
import AdminDashboard from '@/views/AdminDashboard.vue'; // Administrateur d'organisation
import CollaboratorDashboard from '@/views/CollaboratorDashboard.vue'; // Collaborateur
import SignerDashboard from '@/views/SignerDashboard.vue'; // Signataire

import UserHistory from '@/views/UserHistory.vue'; // Import de la page d'historique d'activités

// Import du service d'authentification pour les gardes de navigation
import AuthService from '@/services/AuthService';

/* 
  const routes = [...] crée un tableau routes qui définit la configuration des routes pour l'application. 
  Chaque objet dans ce tableau représente une route de l'application.
*/
const routes = [
  {
    path: '/login',
    name: 'LoginPage', 
    component: LoginPage,
    meta: {
      requiresAuth: false,
      title: 'Connexion - CertiSign'
    }
  },
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: {
      requiresAuth: false,
      title: 'Accueil - CertiSign'
    }
  },
  
  {
    path: '/new-dashboard',
    name: 'new-dashboard',
    component: NewDashboard,
    meta: {
      requiresAuth: true,
      title: 'Tableau de bord - CertiSign'
    }
  },
  
  // Tableaux de bord organisationnels
  {
    path: '/admin-dashboard',
    name: 'admin-dashboard',
    component: AdminDashboard,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Administration d\'organisation - CertiSign'
    }
  },
  
  {
    path: '/collaborator-dashboard',
    name: 'collaborator-dashboard',
    component: CollaboratorDashboard,
    meta: {
      requiresAuth: true,
      requiresCollaborator: true,
      title: 'Préparation de documents - CertiSign'
    }
  },
  
  {
    path: '/signer-dashboard',
    name: 'signer-dashboard',
    component: SignerDashboard,
    meta: {
      requiresAuth: true,
      requiresSigner: true,
      title: 'Signature de documents - CertiSign'
    }
  },
  
  {
    path: '/user-history',
    name: 'user-history',
    component: UserHistory,
    meta: {
      requiresAuth: true,
      title: 'Historique des activités - CertiSign'
    }
  },

  {
    path: '/sign',
    name: 'sign-document',
    component: SignDocument,
    meta: {
      requiresAuth: true,
      title: 'Signer un document - CertiSign'
    }
  },
  
  
  {
    path: '/my-documents',
    name: 'my-documents',
    component: () => import('@/views/MyDocuments.vue'),
    meta: {
      requiresAuth: true,
      title: 'Mes Documents - CertiSign'
    }
  },
  
  // Route de redirection par défaut
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

 /*
  on crée une instance du routeur avec la fonction createRouter
  on passe la constante routes définie précédement qui contient toutes les informations des routes de l'application
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Fonction helper pour déterminer le dashboard selon le rôle
function getDashboardByRole(role) {
  switch (role) {
    case 'admin':
      return '/admin-dashboard';
    case 'collaborator':
      return '/collaborator-dashboard';
    case 'signer':
      return '/signer-dashboard';
    case 'superadmin':
      return '/new-dashboard'; // Super admin utilise le dashboard principal
    default:
      return '/new-dashboard'; // Utilisateurs simples
  }
}

// Garde de navigation pour la protection des routes
router.beforeEach(async (to, from, next) => {
  console.log(`Navigation de ${from.fullPath} vers ${to.fullPath}`);
  // Définir le titre de la page
  document.title = to.meta.title || 'CertiSign - Sécurité des signatures numériques';
  
  // Afficher les informations d'authentification actuelles pour débogage
  console.log('Auth dans le routeur:', {
    isAuthenticated: AuthService.isAuthenticated(),
    token: localStorage.getItem('token') ? 'Présent' : 'Absent',
    user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null
  });
  
  // Vérifier si la route nécessite une authentification
  if (to.matched.some(record => record.meta.requiresAuth)) {
    console.log('Route protégée, vérification de l\'authentification');
    // Vérifier si l'utilisateur est connecté
    if (!AuthService.isAuthenticated()) {
      console.warn('Utilisateur non authentifié, redirection vers login');
      // Rediriger vers la page de connexion
      return next({ 
        path: '/login', 
        query: { redirect: to.fullPath } // Sauvegarder la destination initiale
      });
    }
    
    // Vérifier si le token est valide
    try {
      console.log('Vérification de la validité du token JWT...');
      const isValid = await AuthService.validateToken();
      if (!isValid) {
        // Token invalide, déconnecter l'utilisateur et rediriger
        console.warn('Token invalide, déconnexion et redirection vers login');
        AuthService.logout();
        return next({ 
          path: '/login', 
          query: { redirect: to.fullPath }
        });
      }
      console.log('Token valide, vérification des permissions...');
    } catch (error) {
      console.error('Erreur lors de la validation du token:', error);
      return next({ path: '/login' });
    }
    
    const currentUser = AuthService.getCurrentUser();
    
    // Vérifier les permissions spécifiques (admin d'organisation)
    if (to.matched.some(record => record.meta.requiresAdmin)) {
      console.log('Vérification des droits admin pour', currentUser);
      if (!currentUser || currentUser.role !== 'admin') {
        // L'utilisateur n'a pas les droits d'administration d'organisation nécessaires
        console.warn('Accès refusé - Permissions admin requises');
        const redirectPath = getDashboardByRole(currentUser?.role);
        return next({ path: redirectPath });
      }
    }
    
    // Vérifier les permissions spécifiques (superadmin)
    if (to.matched.some(record => record.meta.requiresSuperAdmin)) {
      console.log('Vérification des droits superadmin pour', currentUser);
      if (!currentUser || currentUser.role !== 'superadmin') {
        // L'utilisateur n'a pas les droits de super administration nécessaires
        console.warn('Accès refusé - Permissions superadmin requises');
        const redirectPath = getDashboardByRole(currentUser?.role);
        return next({ path: redirectPath });
      }
    }
    
    // Vérifier les permissions spécifiques (collaborateur)
    if (to.matched.some(record => record.meta.requiresCollaborator)) {
      console.log('Vérification des droits collaborateur pour', currentUser);
      if (!currentUser || currentUser.role !== 'collaborator') {
        // L'utilisateur n'a pas les droits de collaborateur nécessaires
        console.warn('Accès refusé - Permissions collaborateur requises');
        const redirectPath = getDashboardByRole(currentUser?.role);
        return next({ path: redirectPath });
      }
    }
    
    // Vérifier les permissions spécifiques (signataire)
    if (to.matched.some(record => record.meta.requiresSigner)) {
      console.log('Vérification des droits signataire pour', currentUser);
      if (!currentUser || currentUser.role !== 'signer') {
        // L'utilisateur n'a pas les droits de signataire nécessaires
        console.warn('Accès refusé - Permissions signataire requises');
        const redirectPath = getDashboardByRole(currentUser?.role);
        return next({ path: redirectPath });
      }
    }
    
    // L'utilisateur est authentifié et a les autorisations nécessaires
    console.log('Accès autorisé à la route demandée');
    return next();
  }
  
  // Pour les routes qui ne nécessitent pas d'authentification
  // Vérifier si l'utilisateur est déjà connecté et essaie d'accéder à la page de connexion
  if (to.path === '/login' && AuthService.isAuthenticated()) {
    console.log('Utilisateur déjà connecté, redirection vers le tableau de bord approprié');
    const currentUser = AuthService.getCurrentUser();
    const redirectPath = getDashboardByRole(currentUser?.role);
    return next({ path: redirectPath });
  }
  
  // Pour toutes les autres routes qui ne nécessitent pas d'authentification
  console.log('Navigation autorisée vers une route publique');
  return next();
});


/*
  on exportes l'instance du routeur que qu'on a créée, ce qui permet de l'utiliser dans l'application Vue principale. 
  Ensuite, on pourra importer ce routeur dans le fichier principal (par exemple, main.js) 
  et l'utiliser dans l'application Vue avec la fonction useRouter(). 
*/
export default router;
