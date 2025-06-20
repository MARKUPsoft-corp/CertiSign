#!/bin/bash

# ==============================================================================
# Script de démarrage des services CertiSign
# ==============================================================================
# Ce script démarre tous les services nécessaires pour l'application CertiSign :
# - Frontend Vue.js (port 8080)
# - API Gateway FastAPI (port 8001)
# - Microservice lecture certificat (port 8002)
# - Microservice signature (port 8003)
# - Backend Django (port 8000)
# ==============================================================================

set -e  # Arrêter le script en cas d'erreur

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
    
    print_info "Vérification du port $port pour $service_name..."
    
    # Trouver les PIDs utilisant le port
    local pids=$(sudo lsof -t -i:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_warning "Processus trouvés sur le port $port: $pids"
        print_info "Arrêt des processus sur le port $port..."
        sudo kill -9 $pids 2>/dev/null || true
        sleep 2
        print_success "Port $port libéré"
    else
        print_info "Port $port déjà libre"
    fi
}

# Fonction pour attendre qu'un port soit libre
wait_for_port_free() {
    local port=$1
    local max_wait=10
    local wait_time=0
    
    while sudo lsof -i:$port >/dev/null 2>&1; do
        if [ $wait_time -ge $max_wait ]; then
            print_error "Timeout: le port $port n'est toujours pas libre après ${max_wait}s"
            return 1
        fi
        sleep 1
        wait_time=$((wait_time + 1))
    done
    return 0
}

# Fonction pour vérifier si un service est démarré
check_service() {
    local port=$1
    local service_name=$2
    local max_wait=30
    local wait_time=0
    
    print_info "Vérification du démarrage de $service_name sur le port $port..."
    
    while ! sudo lsof -i:$port >/dev/null 2>&1; do
        if [ $wait_time -ge $max_wait ]; then
            print_error "Timeout: $service_name n'a pas démarré sur le port $port après ${max_wait}s"
            return 1
        fi
        sleep 1
        wait_time=$((wait_time + 1))
        echo -n "."
    done
    echo
    print_success "$service_name démarré avec succès sur le port $port"
    return 0
}

# Répertoire racine du projet
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

print_info "Démarrage des services CertiSign..."
print_info "Répertoire de travail: $PROJECT_ROOT"

# ==============================================================================
# 1. ARRÊT DES SERVICES EXISTANTS
# ==============================================================================

print_info "=== ÉTAPE 1: Arrêt des services existants ==="

kill_port 8080 "Frontend Vue.js"
kill_port 8001 "API Gateway"
kill_port 8002 "Microservice certificat"
kill_port 8003 "Microservice signature"
kill_port 8000 "Backend Django"

print_success "Tous les services ont été arrêtés"
sleep 2

# ==============================================================================
# 2. DÉMARRAGE DU BACKEND DJANGO
# ==============================================================================

print_info "=== ÉTAPE 2: Démarrage du Backend Django (port 8000) ==="

cd "$PROJECT_ROOT/backend/django-project"

# Vérifier que l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    print_error "Environnement virtuel .venv non trouvé dans backend/django-project"
    exit 1
fi

# Démarrer Django en arrière-plan
print_info "Activation de l'environnement virtuel Django..."
nohup bash -c "source .venv/bin/activate && python3 manage.py runserver_plus --cert-file ssl/cert.pem --key-file ssl/key.pem 192.168.4.131:8000 --insecure" > "$PROJECT_ROOT/logs/django.log" 2>&1 &

# Vérifier le démarrage
check_service 8000 "Django"

# ==============================================================================
# 3. DÉMARRAGE DE L'API GATEWAY
# ==============================================================================

print_info "=== ÉTAPE 3: Démarrage de l'API Gateway (port 8001) ==="

cd "$PROJECT_ROOT/backend/fastapi/api_gateway"

# Vérifier que l'environnement virtuel existe
if [ ! -d "../.venv" ]; then
    print_error "Environnement virtuel .venv non trouvé dans backend/fastapi"
    exit 1
fi

# Démarrer l'API Gateway en arrière-plan
print_info "Activation de l'environnement virtuel FastAPI..."
nohup bash -c "source ../.venv/bin/activate && uvicorn main:app --ssl-certfile ssl/cert.pem --ssl-keyfile ssl/key.pem --host 192.168.4.131 --port 8001 --reload" > "$PROJECT_ROOT/logs/api_gateway.log" 2>&1 &

# Vérifier le démarrage
check_service 8001 "API Gateway"

# ==============================================================================
# 4. DÉMARRAGE DU MICROSERVICE DE LECTURE DE CERTIFICAT
# ==============================================================================

print_info "=== ÉTAPE 4: Démarrage du Microservice certificat (port 8002) ==="

cd "$PROJECT_ROOT/backend/fastapi/microservices/lecture_certificat"

# Démarrer le microservice en arrière-plan
print_info "Activation de l'environnement virtuel FastAPI..."
nohup bash -c "source ../../.venv/bin/activate && uvicorn main:app --ssl-certfile ssl/cert.pem --ssl-keyfile ssl/key.pem --host 192.168.4.131 --port 8002 --reload" > "$PROJECT_ROOT/logs/microservice_certificat.log" 2>&1 &

# Vérifier le démarrage
check_service 8002 "Microservice certificat"

# ==============================================================================
# 5. DÉMARRAGE DU MICROSERVICE DE SIGNATURE
# ==============================================================================

print_info "=== ÉTAPE 5: Démarrage du Microservice signature (port 8003) ==="

cd "$PROJECT_ROOT/backend/fastapi/microservices/signature_document"

# Démarrer le microservice en arrière-plan
print_info "Activation de l'environnement virtuel FastAPI..."
nohup bash -c "source ../../.venv/bin/activate && uvicorn main:app --ssl-certfile ssl/cert.pem --ssl-keyfile ssl/key.pem --host 192.168.4.131 --port 8003 --reload" > "$PROJECT_ROOT/logs/microservice_signature.log" 2>&1 &

# Vérifier le démarrage
check_service 8003 "Microservice signature"

# ==============================================================================
# 6. DÉMARRAGE DU FRONTEND VUE.JS
# ==============================================================================

print_info "=== ÉTAPE 6: Démarrage du Frontend Vue.js (port 8080) ==="

cd "$PROJECT_ROOT/frontend"

# Vérifier que node_modules existe
if [ ! -d "node_modules" ]; then
    print_warning "node_modules non trouvé, installation des dépendances..."
    npm install
fi

# Démarrer le frontend en arrière-plan
print_info "Démarrage du serveur de développement Vue.js..."
nohup npm run serve > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &

# Vérifier le démarrage
check_service 8080 "Frontend Vue.js"

# ==============================================================================
# 7. VÉRIFICATION FINALE ET RÉCAPITULATIF
# ==============================================================================

print_info "=== ÉTAPE 7: Vérification finale ==="

# Créer le répertoire logs s'il n'existe pas
mkdir -p "$PROJECT_ROOT/logs"

sleep 3

print_success "=== TOUS LES SERVICES CERTISIGN SONT DÉMARRÉS ==="
echo
print_info "📊 État des services :"
echo "  🟢 Frontend Vue.js    : https://192.168.4.131:8080"
echo "  🟢 API Gateway        : https://192.168.4.131:8001"
echo "  🟢 Microservice Cert  : https://192.168.4.131:8002"
echo "  🟢 Microservice Sign  : https://192.168.4.131:8003"
echo "  🟢 Backend Django     : https://192.168.4.131:8000"
echo
print_info "📋 Administration :"
echo "  📱 Application        : https://192.168.4.131:8080"
echo "  ⚙️  Django Admin       : https://192.168.4.131:8000/admin/"
echo "  📖 API Documentation  : https://192.168.4.131:8001/docs"
echo
print_info "📝 Logs disponibles dans le dossier: $PROJECT_ROOT/logs/"
echo "  - django.log"
echo "  - api_gateway.log"
echo "  - microservice_certificat.log"
echo "  - microservice_signature.log"
echo "  - frontend.log"
echo
print_warning "Pour arrêter tous les services, utilisez: ./stop_certisign_services.sh"
print_info "Ou manuellement avec: sudo fuser -k 8000/tcp 8001/tcp 8002/tcp 8003/tcp 8080/tcp"
echo

# Afficher les processus actifs pour vérification
print_info "Processus actifs sur les ports CertiSign :"
sudo netstat -tlnp | grep -E ':800[0-3]|:8080' | while read line; do
    echo "  $line"
done

print_success "🎉 CertiSign est prêt à l'utilisation !" 