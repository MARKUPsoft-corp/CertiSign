<!-- Ici c'est le composant de la barre de navigation qui sera présent sur toutes les pages de l'application -->
<template>
    <!-- Barre de navigation Bootstrap -->
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
            <!-- Logo ou nom du site -->
            <a class="navbar-brand" href="#">CertiSign</a>

            <!-- Bouton pour le menu déroulant en mode mobile -->
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" 
                aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>

            <!-- Contenu de la barre de navigation -->
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <!-- Lien vers la page d'accueil -->
                    <li class="nav-item">
                        <router-link to="/" class="nav-link active" aria-current="page">Accueil</router-link>
                    </li>

                    <!-- Lien vers la page de connexion -->
                    <li class="nav-item">
                        <router-link to="/login" class="nav-link">Login</router-link>
                    </li>

                    <!-- Menu déroulant -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            Dropdown
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#">Action</a></li>
                            <li><a class="dropdown-item" href="#">Another action</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="#">Something else here</a></li>
                        </ul>
                    </li>

                    <!-- Lien désactivé -->
                    <li class="nav-item">
                        <a class="nav-link disabled" aria-disabled="true">Disabled</a>
                    </li>
                </ul>

                <!-- Barre de recherche -->
                <form class="d-flex" role="search">
                    <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search">
                    <button class="btn btn-outline-success" type="submit">Search</button>
                </form>
            </div>
        </div>
    </nav>
</template>

<script setup>
// Ce composant n'a pas de logique spécifique pour l'instant.
</script>
