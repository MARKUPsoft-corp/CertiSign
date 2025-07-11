<template>
  <!-- Réutilisation intégrale du composant SignSimple -->
  <SignSimple @close="emit('close')" />
</template>

<script setup>
import { defineEmits, defineProps, onMounted } from 'vue';
import AuthService from '@/services/AuthService';
import SignSimple from '@/views/SignSimple.vue';

const props = defineProps({
  organizationName: {
    type: String,
    default: ''
  }
});

// Émission de l'événement close vers le parent (dashboard)
const emit = defineEmits(['close']);

// S'assurer que le nom d'organisation est présent dans l'objet user stocké
onMounted(() => {
  const currentUser = AuthService.getCurrentUser();
  if (currentUser) {
    const updates = {};
    if (props.organizationName && !currentUser.organization) {
      updates.organization = props.organizationName;
    }
    if (currentUser.organization && currentUser.organization.id) {
      updates.organizationId = currentUser.organization.id;
    }
    if (Object.keys(updates).length) {
      AuthService.updateCurrentUser(updates);
    }
  }
});
</script> 