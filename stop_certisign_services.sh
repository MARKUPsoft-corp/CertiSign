#!/bin/bash

# ==============================================================================
# Script d'arrêt des services CertiSign
# ==============================================================================
# Ce script arrête tous les services CertiSign en cours d'exécution
# ==============================================================================

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages colorés
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction pour tuer les processus sur un port donné
kill_port() {
    local port=$1
    local service_name=$2
    
    print_info "Arrêt de $service_name (port $port)..."
    
    # Trouver les PIDs utilisant le port
    local pids=$(sudo lsof -t -i:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_warning "Processus trouvés sur le port $port: $pids"
        sudo kill -9 $pids 2>/dev/null || true
        sleep 1
        
        # Vérifier si le port est libéré
        local remaining_pids=$(sudo lsof -t -i:$port 2>/dev/null || true)
        if [ -z "$remaining_pids" ]; then
            print_success "$service_name arrêté (port $port libéré)"
        else
            print_error "Échec de l'arrêt de $service_name (port $port toujours occupé)"
        fi
    else
        print_info "$service_name n'était pas en cours d'exécution (port $port libre)"
    fi
}

print_info "🛑 Arrêt des services CertiSign..."
echo

# Arrêter tous les services
kill_port 8080 "Frontend Vue.js"
kill_port 8001 "API Gateway FastAPI"
kill_port 8002 "Microservice certificat"
kill_port 8003 "Microservice signature"
kill_port 8000 "Backend Django"

echo
print_success "✅ Tous les services CertiSign ont été arrêtés"

# Vérification finale
print_info "Vérification finale des ports..."
active_ports=$(sudo netstat -tlnp | grep -E ':800[0-3]|:8080' || true)

if [ -z "$active_ports" ]; then
    print_success "🎉 Tous les ports CertiSign sont libres"
else
    print_warning "⚠️  Certains ports sont encore occupés :"
    echo "$active_ports"
fi

echo
print_info "Pour redémarrer tous les services, utilisez: ./start_certisign_services.sh" 