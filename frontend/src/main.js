/* eslint-disable vue/multi-word-component-names */

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import LoginPage from './views/LoginPage.vue';
import HomePage from './views/HomePage.vue';


import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';  // Si tu veux utiliser les composants JavaScript (comme les modals, dropdowns, etc.)


const app = createApp(App);
app.component('LoginPage', LoginPage)
app.component('home', HomePage)
app.use(router);
app.mount('#app');
