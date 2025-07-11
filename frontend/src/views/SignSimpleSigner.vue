<template>
  <!-- Réutilisation intégrale du composant SignSimple -->
  <SignSimple @close="emit('close')" />
</template>

<script setup>
import { defineEmits } from 'vue';
import SignSimple from '@/views/SignSimple.vue';

// Émission de l'événement close vers le parent (dashboard)
const emit = defineEmits(['close']);
</script> 