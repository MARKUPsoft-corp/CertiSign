#!/bin/bash

# Variables
PROJECT_ROOT="$(pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend/django"
LOG_DIR="$PROJECT_ROOT/logs"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
FONT_BOLD="\e[1m"
FONT_RESET="\e[0m"

# Ports pour les services
BACKEND_PORT=8000
FRONTEND_PORT=8080
API_GATEWAY_PORT=8001
SIGNATURE_SERVICE_PORT=8002

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Créer le répertoire de logs s'il n'existe pas
mkdir -p "$LOG_DIR"

# Fonction pour afficher des messages stylisés
print_header() {
    echo -e "\n${BLUE}${FONT_BOLD}$1${FONT_RESET}${NC}\n"
}

print_info() {
    echo -e "${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Vérifier si un port est déjà utilisé
is_port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port est utilisé
    else
        return 1  # Port est libre
    fi
}

# Vérifier si le terminal supporte plusieurs onglets
check_terminal_support() {
    if command -v gnome-terminal &> /dev/null; then
        TERMINAL_CMD="gnome-terminal"
        TERMINAL_SUPPORTED=true
    elif command -v xterm &> /dev/null; then
        TERMINAL_CMD="xterm"
        TERMINAL_ARGS="-T"
        TERMINAL_SUPPORTED=true
    else
        TERMINAL_SUPPORTED=false
    fi
}

# Fonction pour vérifier l'état des services
check_service() {
    local service=$1
    local url=$2
    local max_attempts=$3
    local attempt=1
    
    print_info "Vérification de $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "$service est disponible à $url"
            return 0
        else
            if [ $attempt -lt $max_attempts ]; then
                echo -n "."
                sleep 2
            fi
        fi
        attempt=$((attempt+1))
    done
    
    print_warning "$service n'est pas encore disponible à $url, mais il pourrait être en cours de démarrage"
    return 0  # On continue même si le service n'est pas détecté
}

# Fonction pour arrêter proprement tous les services
cleanup() {
    print_header "Arrêt des services CertiSign"
    
    # Trouver et arrêter les processus Django (backend)
    print_info "Arrêt du backend Django..."
    pkill -f "python.*manage.py runserver" || true
    print_success "Backend Django arrêté"
    
    # Trouver et arrêter les processus npm (frontend)
    print_info "Arrêt du frontend Vue.js..."
    pkill -f "node.*vue-cli-service" || true
    print_success "Frontend Vue.js arrêté"
    
    print_success "Tous les services ont été arrêtés"
    exit 0
}

# Intercepter CTRL+C pour nettoyage
trap cleanup SIGINT SIGTERM

# Afficher l'en-tête
clear
echo -e "${YELLOW}${FONT_BOLD}"
echo "   ______          __  _ _____ _             "
echo "  / ____/__  _____/ /_(_) ___/(_)___ _____   "
echo " / /   / _ \/ ___/ __/ /\__ \/ / __ \`/ __ \  "
echo "/ /___/  __/ /  / /_/ /___/ / / /_/ / / / /  "
echo "\____/\___/_/   \__/_//____/_/\__, /_/ /_/   "
echo "                             /____/          "
echo -e "${FONT_RESET}${NC}"
echo -e "${BLUE}Solution de Signature Électronique${NC}"
echo -e "${YELLOW}----------------------------------------${NC}"

# Vérifier si l'installation est complète
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    print_error "L'environnement virtuel Python n'existe pas!"
    print_info "Veuillez d'abord installer le backend avec: "
    print_info "cd $BACKEND_DIR && ./setup.sh"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    print_warning "Les dépendances frontend ne semblent pas être installées."
    print_info "Voulez-vous installer les dépendances frontend maintenant? (o/n)"
    read -r answer
    if [[ "$answer" =~ ^[Oo]$ ]]; then
        print_header "Installation des dépendances frontend"
        cd "$FRONTEND_DIR" && npm install
        if [ $? -ne 0 ]; then
            print_error "Échec de l'installation des dépendances frontend."
            exit 1
        fi
        print_success "Dépendances frontend installées avec succès!"
    else
        print_warning "Les dépendances frontend ne seront pas installées."
        print_info "Vous pouvez les installer manuellement avec: cd $FRONTEND_DIR && npm install"
    fi
fi

# Vérifier la connexion réseau
print_header "Vérification de la connectivité"
if ping -c 1 google.com > /dev/null 2>&1; then
    print_success "Connexion Internet active"
else
    print_warning "Aucune connexion Internet détectée. Le projet fonctionnera mais sans accès aux services externes."
fi

# Vérifier si les ports sont déjà utilisés
print_header "Vérification des ports"
if is_port_in_use $BACKEND_PORT; then
    print_warning "Port $BACKEND_PORT (backend Django) est déjà utilisé!"
    print_info "Tentative d'arrêt du processus existant..."
    
    # Tenter de tuer le processus sur ce port
    sudo lsof -t -i:$BACKEND_PORT | xargs -r kill -9
    sleep 1
    
    if is_port_in_use $BACKEND_PORT; then
        print_error "Impossible de libérer le port $BACKEND_PORT pour le backend Django."
        print_info "Veuillez arrêter le processus qui utilise ce port et réessayer."
        exit 1
    else
        print_success "Port $BACKEND_PORT libéré avec succès."
    fi
else
    print_success "Port $BACKEND_PORT (backend Django) est disponible."
fi

if is_port_in_use $FRONTEND_PORT; then
    print_warning "Port $FRONTEND_PORT (frontend Vue.js) est déjà utilisé!"
    print_info "Tentative d'arrêt du processus existant..."
    
    # Tenter de tuer le processus sur ce port
    sudo lsof -t -i:$FRONTEND_PORT | xargs -r kill -9
    sleep 1
    
    if is_port_in_use $FRONTEND_PORT; then
        print_error "Impossible de libérer le port $FRONTEND_PORT pour le frontend Vue.js."
        print_info "Veuillez arrêter le processus qui utilise ce port et réessayer."
        exit 1
    else
        print_success "Port $FRONTEND_PORT libéré avec succès."
    fi
else
    print_success "Port $FRONTEND_PORT (frontend Vue.js) est disponible."
fi

if is_port_in_use $API_GATEWAY_PORT; then
    print_warning "Port $API_GATEWAY_PORT (API Gateway) est déjà utilisé!"
    print_info "Tentative d'arrêt du processus existant..."
    
    # Tenter de tuer le processus sur ce port
    sudo lsof -t -i:$API_GATEWAY_PORT | xargs -r kill -9
    sleep 1
    
    if is_port_in_use $API_GATEWAY_PORT; then
        print_error "Impossible de libérer le port $API_GATEWAY_PORT pour l'API Gateway."
        print_info "Veuillez arrêter le processus qui utilise ce port et réessayer."
        exit 1
    else
        print_success "Port $API_GATEWAY_PORT libéré avec succès."
    fi
else
    print_success "Port $API_GATEWAY_PORT (API Gateway) est disponible."
fi

if is_port_in_use $SIGNATURE_SERVICE_PORT; then
    print_warning "Port $SIGNATURE_SERVICE_PORT (Service de Signature) est déjà utilisé!"
    print_info "Tentative d'arrêt du processus existant..."
    
    # Tenter de tuer le processus sur ce port
    sudo lsof -t -i:$SIGNATURE_SERVICE_PORT | xargs -r kill -9
    sleep 1
    
    if is_port_in_use $SIGNATURE_SERVICE_PORT; then
        print_error "Impossible de libérer le port $SIGNATURE_SERVICE_PORT pour le Service de Signature."
        print_info "Veuillez arrêter le processus qui utilise ce port et réessayer."
        exit 1
    else
        print_success "Port $SIGNATURE_SERVICE_PORT libéré avec succès."
    fi
else
    print_success "Port $SIGNATURE_SERVICE_PORT (Service de Signature) est disponible."
fi

# Vérifier le support terminal
check_terminal_support

# Lancer le backend Django
print_header "Démarrage du backend Django"
cd "$BACKEND_DIR"

if [ "$TERMINAL_SUPPORTED" = true ] && [ "$TERMINAL_CMD" = "gnome-terminal" ]; then
    print_info "Démarrage du backend dans un nouvel onglet..."
    gnome-terminal --tab --title="CertiSign Backend" -- bash -c "$VENV_PYTHON manage.py runserver $BACKEND_PORT; exec bash" &
    backend_pid=$!
    print_success "Backend Django démarré dans un nouvel onglet"
elif [ "$TERMINAL_SUPPORTED" = true ] && [ "$TERMINAL_CMD" = "xterm" ]; then
    print_info "Démarrage du backend dans un nouvel onglet..."
    xterm $TERMINAL_ARGS "CertiSign Backend" -e bash -c "$VENV_PYTHON manage.py runserver $BACKEND_PORT; exec bash" &
    backend_pid=$!
    print_success "Backend Django démarré dans un nouvel onglet"
else
    print_info "Démarrage du backend en arrière-plan..."
    $VENV_PYTHON manage.py runserver $BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
    backend_pid=$!
    print_success "Backend Django démarré (PID: $backend_pid, logs: $LOG_DIR/backend.log)"
fi

# Laisser le backend démarrer
print_info "Attente du démarrage du backend (10 secondes)..."
sleep 10

# Vérifier que le backend est disponible
check_service "Backend Django" "http://localhost:$BACKEND_PORT/api" 5

# Lancer le frontend Vue.js
print_header "Démarrage du frontend Vue.js"
cd "$FRONTEND_DIR"

if [ "$TERMINAL_SUPPORTED" = true ] && [ "$TERMINAL_CMD" = "gnome-terminal" ]; then
    print_info "Démarrage du frontend dans un nouvel onglet..."
    gnome-terminal --tab --title="CertiSign Frontend" -- bash -c "PORT=$FRONTEND_PORT npm run serve; exec bash" &
    frontend_pid=$!
    print_success "Frontend Vue.js démarré dans un nouvel onglet"
elif [ "$TERMINAL_SUPPORTED" = true ] && [ "$TERMINAL_CMD" = "xterm" ]; then
    print_info "Démarrage du frontend dans un nouvel onglet..."
    xterm $TERMINAL_ARGS "CertiSign Frontend" -e bash -c "PORT=$FRONTEND_PORT npm run serve; exec bash" &
    frontend_pid=$!
    print_success "Frontend Vue.js démarré dans un nouvel onglet"
else
    print_info "Démarrage du frontend en arrière-plan..."
    PORT=$FRONTEND_PORT npm run serve > "$LOG_DIR/frontend.log" 2>&1 &
    frontend_pid=$!
    print_success "Frontend Vue.js démarré (PID: $frontend_pid, logs: $LOG_DIR/frontend.log)"
fi

# Laisser le frontend démarrer - augmenter le temps d'attente
print_info "Attente du démarrage du frontend (20 secondes)..."
sleep 20

# Vérifier que le frontend est disponible
check_service "Frontend Vue.js" "http://localhost:$FRONTEND_PORT" 10

# Résumé des services
print_header "Informations de connexion"
echo -e "${GREEN}${FONT_BOLD}L'application CertiSign est prête !${FONT_RESET}${NC}"
echo -e "${CYAN}Frontend        :${NC} http://localhost:$FRONTEND_PORT"
echo -e "${CYAN}API Backend     :${NC} http://localhost:$BACKEND_PORT/api"
echo -e "${CYAN}Admin Django    :${NC} http://localhost:$BACKEND_PORT/admin"
echo ""
echo -e "${YELLOW}Comptes de test :${NC}"
echo -e "${CYAN}Administrateur  :${NC} admin / password"
echo -e "${CYAN}Utilisateur     :${NC} jean.dupont / password"
echo ""
echo -e "${YELLOW}${FONT_BOLD}Appuyez sur Ctrl+C pour arrêter tous les services${FONT_RESET}${NC}"

print_info "Si les services ne sont pas accessibles, vérifiez les logs dans le dossier $LOG_DIR"
print_info "Vous pouvez également voir l'activité dans les onglets du terminal ouverts par ce script"

# Attendre que l'utilisateur appuie sur Ctrl+C
wait 