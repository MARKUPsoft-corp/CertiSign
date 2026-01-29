#!/bin/bash

# ==============================================================================
# Script de déploiement en production pour CertiSign
# ==============================================================================
# Ce script utilise les services systemd pour une gestion robuste des processus
# et compile le frontend Vue.js pour être servi statiquement par Nginx.
# ==============================================================================

set -e # Arrêter le script en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Répertoire racine du projet
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

print_info "🚀 Déploiement en production de CertiSign avec services systemd..."

# ==============================================================================
# 1. ARRÊT DES SERVICES EXISTANTS
# ==============================================================================
print_info "=== ÉTAPE 1: Arrêt des services existants ==="

services=("certisign-django" "certisign-api-gateway" "certisign-certificat" "certisign-signature")

for service in "${services[@]}"; do
    if sudo systemctl is-active --quiet "$service"; then
        print_info "Arrêt du service $service..."
        sudo systemctl stop "$service"
        print_success "Service $service arrêté."
    else
        print_info "Service $service déjà arrêté."
    fi
done

# ==============================================================================
# 2. BUILD DU FRONTEND
# ==============================================================================
print_info "=== ÉTAPE 2: Compilation du frontend Vue.js ==="
cd "$PROJECT_ROOT/frontend"

# Vérifier si node_modules existe
if [ ! -d "node_modules" ]; then
    print_warning "node_modules non trouvé. Installation des dépendances..."
    npm install
fi

# Build du frontend
print_info "Compilation du frontend..."
npm run build
print_success "Frontend compilé avec succès dans /frontend/dist"

# ==============================================================================
# 3. VÉRIFICATION DES ENVIRONNEMENTS VIRTUELS
# ==============================================================================
print_info "=== ÉTAPE 3: Vérification des environnements virtuels ==="

# Django
if [ ! -d "$PROJECT_ROOT/backend/django-project/.venv" ]; then
    print_error "Environnement virtuel Django non trouvé !"
    exit 1
fi

# FastAPI
if [ ! -d "$PROJECT_ROOT/backend/fastapi/.venv" ]; then
    print_error "Environnement virtuel FastAPI non trouvé !"
    exit 1
fi

print_success "Environnements virtuels vérifiés."

# ==============================================================================
# 4. COPIE DES SERVICES SYSTEMD
# ==============================================================================
print_info "=== ÉTAPE 4: Configuration des services systemd ==="

# Copier les fichiers de service
sudo cp "$PROJECT_ROOT/systemd/"*.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

print_success "Services systemd configurés."

# ==============================================================================
# 5. DÉMARRAGE DES SERVICES
# ==============================================================================
print_info "=== ÉTAPE 5: Démarrage des services ==="

# Activer et démarrer les services
for service in "${services[@]}"; do
    print_info "Activation et démarrage du service $service..."
    sudo systemctl enable "$service"
    sudo systemctl start "$service"
    
    # Vérifier le statut
    if sudo systemctl is-active --quiet "$service"; then
        print_success "Service $service démarré avec succès."
    else
        print_error "Échec du démarrage du service $service"
        sudo systemctl status "$service"
        exit 1
    fi
done

# ==============================================================================
# 6. VÉRIFICATION DES PORTS
# ==============================================================================
print_info "=== ÉTAPE 6: Vérification des ports ==="

ports=(8000 8001 8002 8003)
for port in "${ports[@]}"; do
    if sudo lsof -i :$port > /dev/null 2>&1; then
        print_success "Port $port: OK"
    else
        print_error "Port $port: AUCUN SERVICE"
    fi
done

# ==============================================================================
# 7. REDÉMARRAGE DE NGINX
# ==============================================================================
print_info "=== ÉTAPE 7: Redémarrage de Nginx ==="

# Copier la configuration Nginx
sudo cp "$PROJECT_ROOT/nginx_prod.conf" /etc/nginx/sites-available/certisign
sudo ln -sf /etc/nginx/sites-available/certisign /etc/nginx/sites-enabled/

# Tester la configuration
if sudo nginx -t; then
    sudo systemctl reload nginx
    print_success "Nginx rechargé avec succès."
else
    print_error "Erreur dans la configuration Nginx"
    exit 1
fi

# ==============================================================================
# 8. VÉRIFICATION FINALE
# ==============================================================================
print_info "=== ÉTAPE 8: Vérification finale ==="

# Statut des services
print_info "Statut des services systemd :"
for service in "${services[@]}"; do
    status=$(sudo systemctl is-active "$service")
    if [ "$status" = "active" ]; then
        print_success "✅ $service: $status"
    else
        print_error "❌ $service: $status"
    fi
done

# Vérifier Nginx
if sudo systemctl is-active --quiet nginx; then
    print_success "✅ Nginx: actif"
else
    print_error "❌ Nginx: inactif"
fi

print_success "🎉 Déploiement de production terminé avec succès !"
print_info "📊 Services déployés :"
print_info "   - Frontend Vue.js (statique via Nginx)"
print_info "   - Backend Django (Gunicorn, port 8000)"
print_info "   - API Gateway (Gunicorn, port 8001)"
print_info "   - Microservice Certificat (Gunicorn, port 8002)"
print_info "   - Microservice Signature (Gunicorn, port 8003)"
print_info "   - Nginx (reverse proxy + fichiers statiques)"

print_warning "💡 Commandes utiles :"
print_warning "   - sudo systemctl status certisign-* (statut des services)"
print_warning "   - sudo journalctl -u certisign-* -f (logs en temps réel)"
print_warning "   - sudo systemctl restart certisign-* (redémarrage d'un service)" 