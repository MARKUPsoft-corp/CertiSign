

<template>
    <h1>BIENVENU {{ nom }}</h1>
    
</template>

<script setup>

    import { ref } from 'vue';
    const nom = ref("")
    nom.value = prompt("entrez votre nom") 

</script>