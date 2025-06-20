const { defineConfig } = require('@vue/cli-service')
const fs = require('fs')
const path = require('path')

// Fonction pour vérifier l'existence des certificats SSL
function getHttpsConfig() {
  const keyPath = path.join(__dirname, 'ssl', 'key.pem')
  const certPath = path.join(__dirname, 'ssl', 'cert.pem')
  
  try {
    if (fs.existsSync(keyPath) && fs.existsSync(certPath)) {
      return {
        key: fs.readFileSync(keyPath),
        cert: fs.readFileSync(certPath)
      }
    } else {
      console.warn('⚠️  Certificats SSL non trouvés, utilisation du mode HTTP')
      return false
    }
  } catch (error) {
    console.warn('⚠️  Erreur lors de la lecture des certificats SSL:', error.message)
    return false
  }
}

module.exports = defineConfig({
  transpileDependencies: true,
  
  // Configuration du serveur de développement
  devServer: {
    port: 8080,
    host: '0.0.0.0', // Écouter sur toutes les interfaces
    allowedHosts: 'all', // Permettre l'accès via l'IP
    
    // Configuration HTTPS conditionnelle
    https: getHttpsConfig(),
    
    // Configuration du proxy
    proxy: {
      '/api': {
        target: 'https://192.168.4.131:8000',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug' // Ajout de logs pour le débogage
      },
      '/dh-exchange': {
        target: 'https://192.168.4.131:8001', // API Gateway
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      },
      '/gateway': {
        target: 'https://192.168.4.131:8001', // API Gateway
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      }
    },
    
    // Ajout d'options pour éviter les blocages
    open: false, // Ne pas ouvrir automatiquement le navigateur
    hot: true,
    liveReload: true
  },
  
  // Configuration de webpack pour les feature flags
  configureWebpack: {
    plugins: [
      new (require('webpack').DefinePlugin)({
        __VUE_OPTIONS_API__: true,
        __VUE_PROD_DEVTOOLS__: false,
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
      })
    ]
  }
})