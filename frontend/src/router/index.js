/* 
  le fichier index.js dans le dossier router sert à  configurer le Vue Router pour gérer la navigation entre 
  les différentes vues de l'application. C'est ici qu'on définis les routes et où on crées l'instance 
  du routeur. 
*/

import { createRouter, createWebHistory } from 'vue-router'; //ici, on importe deux fonctions depuis le module vue-router. 
//createwebhistory permet de créer un mode de navigation basé sur l'historique de l'URL du navigateur, ce qui signifie qu'il utilise les chemins d'URL propres (sans #).
import LoginPage from '@/views/LoginPage.vue'; //Ici, on importes le composant LoginPage.vue situé dans le répertoire @/views. Le symbole @ fait référence au dossier src du projet, ce qui est un raccourci couramment utilisé dans Vue.js pour accéder facilement aux fichiers.
import HomePage from '@/views/HomePage.vue'; // pareil ici pour la HomePage

/* 
  const routes = [...] crée un tableau routes qui définit la configuration des routes pour l'application. 
  Chaque objet dans ce tableau représente une route de l'application.
*/
const routes = [
  {
    path: '/login',
    name: 'LoginPage', 
    component: LoginPage
  },

  {
    path: '/',
    name: 'home',
    component: HomePage
  },

];

 /*
  on crée une instance du routeur avec la fonction createRouter
  on passe la constante routes définie précédement qui contient toutes les informations des routes de l'application
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
});

/*
  on exportes l'instance du routeur que qu'on a créée, ce qui permet de l'utiliser dans l'application Vue principale. 
  Ensuite, on pourra importer ce routeur dans le fichier principal (par exemple, main.js) 
  et l'utiliser dans l'application Vue avec la fonction useRouter(). 
*/
export default router;
