<template>
  <div class="logo-container">
    <div class="logo-icon">
      <i class="bi bi-shield-lock-fill"></i>
    </div>
    <h1 class="logo-text" v-if="!collapsed">
      <span class="logo-ce">Ce</span><span class="logo-r">r</span><span class="logo-ti">ti</span>
      <span class="badge-cert"><i class="bi bi-patch-check-fill"></i></span>
      <span class="logo-sign">Sign</span>
    </h1>
  </div>
</template>

<script>
export default {
  name: 'CertiSignLogo',
  props: {
    collapsed: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'default',
      validator: (value) => ['small', 'default', 'large'].includes(value)
    }
  }
}
</script>

<style scoped>
.logo-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  width: v-bind('size === "small" ? "36px" : size === "large" ? "60px" : "50px"');
  height: v-bind('size === "small" ? "36px" : size === "large" ? "60px" : "50px"');
  border-radius: 10px;
  background-color: var(--primary-dark, #1a2638);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-light, #ffffff);
  font-size: v-bind('size === "small" ? "1.25rem" : size === "large" ? "1.75rem" : "1.5rem"');
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.1));
}

.logo-text {
  font-size: v-bind('size === "small" ? "1.3rem" : size === "large" ? "2rem" : "1.6rem"');
  font-weight: bold;
  display: flex;
  align-items: center;
  white-space: nowrap;
  margin: 0;
}

.logo-ce {
  color: #17c722; /* Vert pour "Ce" */
  font-weight: bold;
}

.logo-r {
  color: #e42d2d; /* Rouge pour "r" */
  font-weight: bold;
}

.logo-ti {
  color: #e4c52d; /* Jaune pour "ti" */
  font-weight: bold;
}

.logo-sign {
  color: #2266e3; /* Bleu pour "Sign" */
  font-weight: bold;
}

.badge-cert {
  display: inline-flex;
  margin: 0 0.25rem;
  color: #2266e3; /* Bleu pour le badge */
  position: relative;
  top: -2px;
}
</style>
