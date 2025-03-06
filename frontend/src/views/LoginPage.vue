<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header text-center">
            <h4>Se connecter</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="login">
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Mot de passe</label>
                <input type="password" class="form-control" id="password" v-model="password" required />
              </div>
              <button type="submit" class="btn btn-primary w-100">Se connecter</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  
</script>

<style scoped>
/* Vous pouvez ajouter vos propres styles personnalisés ici */
</style>
