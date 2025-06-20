# Appels API depuis le Front-end

Cette section détaille comment le frontend CertiSign interagit avec les API backend.

## Configuration d'Axios

CertiSign utilise Axios pour gérer les requêtes HTTP. La configuration est centralisée dans le fichier `src/services/api.js` :

```javascript
import axios from 'axios';
import store from '@/store';

const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Intercepteur pour ajouter le token JWT à chaque requête
apiClient.interceptors.request.use(config => {
  const token = store.getters['auth/token'];
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur pour gérer les erreurs
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      store.dispatch('auth/logout');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## Services API

Les appels API sont organisés en services pour une meilleure maintenabilité:

### Service d'authentification

```javascript
// src/services/auth.service.js
import api from './api';

export default {
  login(credentials) {
    return api.post('/auth/login', credentials);
  },
  
  logout() {
    return api.post('/auth/logout');
  },
  
  register(userData) {
    return api.post('/auth/register', userData);
  },
  
  refreshToken() {
    return api.post('/auth/refresh');
  }
};
```

### Service de gestion des documents

```javascript
// src/services/documents.service.js
import api from './api';

export default {
  getAll() {
    return api.get('/documents');
  },
  
  get(id) {
    return api.get(`/documents/${id}`);
  },
  
  upload(formData) {
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  sign(id, signatureData) {
    return api.post(`/documents/${id}/sign`, signatureData);
  },
  
  verify(id) {
    return api.get(`/documents/${id}/verify`);
  }
};
```

### Service de gestion des certificats

```javascript
// src/services/certificates.service.js
import api from './api';

export default {
  getAll() {
    return api.get('/certificates');
  },
  
  get(id) {
    return api.get(`/certificates/${id}`);
  },
  
  create(certificateData) {
    return api.post('/certificates', certificateData);
  },
  
  import(formData) {
    return api.post('/certificates/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  delete(id) {
    return api.delete(`/certificates/${id}`);
  }
};
```

## Utilisation dans les composants

Exemple d'utilisation des services API dans un composant Vue :

```javascript
// src/components/DocumentList.vue
<template>
  <div class="document-list">
    <h2>Mes documents</h2>
    <div v-if="loading" class="loading">Chargement...</div>
    <ul v-else>
      <li v-for="doc in documents" :key="doc.id">
        {{ doc.name }}
        <button @click="signDocument(doc.id)">Signer</button>
      </li>
    </ul>
  </div>
</template>

<script>
import documentsService from '@/services/documents.service';

export default {
  data() {
    return {
      documents: [],
      loading: true
    };
  },
  
  async created() {
    try {
      const response = await documentsService.getAll();
      this.documents = response.data;
    } catch (error) {
      console.error('Erreur lors du chargement des documents:', error);
      this.$toast.error('Impossible de charger les documents');
    } finally {
      this.loading = false;
    }
  },
  
  methods: {
    async signDocument(id) {
      try {
        await documentsService.sign(id, {
          // Données de signature
        });
        this.$toast.success('Document signé avec succès');
      } catch (error) {
        console.error('Erreur lors de la signature:', error);
        this.$toast.error('Impossible de signer le document');
      }
    }
  }
};
</script>
```

## Gestion des erreurs

CertiSign implémente une gestion cohérente des erreurs API :

1. Les erreurs 401 (Non autorisé) déconnectent automatiquement l'utilisateur
2. Les autres erreurs sont affichées via des notifications (utilisant la bibliothèque `vue-toastification`)
3. Les erreurs sont également journalisées pour le débogage

## Documentation Swagger/OpenAPI

Pour une référence complète des endpoints API disponibles, consultez [la documentation API REST](../backend/api_rest.md). 