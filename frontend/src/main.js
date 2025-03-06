/* eslint-disable vue/multi-word-component-names */

import { createApp } from 'vue'; /*createAp est une fonction de Vue.js utilisée pour créer une instance de l'application vue. Elle est appelée avec le composant principal comme argument pour l'initialiser. */
import App from './App.vue'; //App.vue est le composant racine de l'application Vue. ce fichier contient la structure de l'interface principale de l'application et sert de point de depart pour le reste de l'application.
import router from './router'; //le fichier router/index.js contient la configuration des routes de l'application, c'est-à-dire l'association des chemins URL aux composants Vue correspondants. Cela permet à l'application de naviguer entre différentes vues sans recharger la page. Ici router fait référence à l'instance de Vue Router.
import LoginPage from './views/LoginPage.vue';
import HomePage from './views/HomePage.vue';
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
import Vue from 'vue'

/*import des composants de bootstrap */
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';  // Si on veut utiliser les composants JavaScript (comme les modals, dropdowns, etc.)
Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
/*
    createApp(App) crée une nouvelle instance de l'application Vue avec le composant principal App.vue. 
    Le composant App.vue devient ainsi le point d'entrée dans l'arbre des composants de l'application Vue.
*/
const app = createApp(App);

/*
    vue nregistrer un composant global dans l'application. Une fois le composant enregistré de cette manière, 
    il peut être utilisé dans n'importe quel autre composant de l'application sans avoir à 
    le réimporter explicitement à chaque fois. 
    */
app.component('LoginPage', LoginPage)
app.component('home', HomePage)

/*
    enregistre le routeur dans l'application. cela permet à vue la navigation entre les différentes vues de l'application. 
    En utilisant use, Vue intègre le routeur, ce qui permet d'afficher les composants en fonction de l'url.
*/
app.use(router);

/*
    app.mount('#app') attache l'instance Vue créée à un élément du DOM. 
    L'élément #app fait référence à un élément HTML dans la page (par exemple, <div id="app"></div> dans le fichier index.html). 
    L'application Vue s'y monte, et tout son contenu sera rendu à l'intérieur de cet élément.
*/
app.mount('#app');
