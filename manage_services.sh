#!/bin/bash

# ==============================================================================
# Script de gestion des services CertiSign
# ==============================================================================
# Outil de maintenance pour gérer les services systemd de CertiSign
# ==============================================================================

set -e

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

# Services CertiSign
SERVICES=("certisign-django" "certisign-api-gateway" "certisign-certificat" "certisign-signature")

show_help() {
    echo "Usage: $0 [COMMANDE]"
    echo ""
    echo "Commandes disponibles :"
    echo "  status     - Afficher le statut de tous les services"
    echo "  start      - Démarrer tous les services"
    echo "  stop       - Arrêter tous les services"
    echo "  restart    - Redémarrer tous les services"
    echo "  logs       - Afficher les logs en temps réel"
    echo "  logs-all   - Afficher tous les logs"
    echo "  health     - Vérification de santé des services"
    echo "  ports      - Vérifier les ports utilisés"
    echo "  nginx      - Redémarrer Nginx"
    echo "  build      - Recompiler le frontend"
    echo "  help       - Afficher cette aide"
    echo ""
    echo "Exemples :"
    echo "  $0 status"
    echo "  $0 restart"
    echo "  $0 logs certisign-django"
}

check_service_status() {
    local service=$1
    if sudo systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✅${NC} $service"
    else
        echo -e "${RED}❌${NC} $service"
    fi
}

show_status() {
    print_info "Statut des services CertiSign :"
    echo ""
    for service in "${SERVICES[@]}"; do
        check_service_status "$service"
    done
    echo ""
    
    # Vérifier Nginx
    if sudo systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅${NC} nginx"
    else
        echo -e "${RED}❌${NC} nginx"
    fi
}

start_services() {
    print_info "Démarrage des services..."
    for service in "${SERVICES[@]}"; do
        print_info "Démarrage de $service..."
        sudo systemctl start "$service"
        sleep 2
        check_service_status "$service"
    done
}

stop_services() {
    print_info "Arrêt des services..."
    for service in "${SERVICES[@]}"; do
        print_info "Arrêt de $service..."
        sudo systemctl stop "$service"
        check_service_status "$service"
    done
}

restart_services() {
    print_info "Redémarrage des services..."
    for service in "${SERVICES[@]}"; do
        print_info "Redémarrage de $service..."
        sudo systemctl restart "$service"
        sleep 2
        check_service_status "$service"
    done
}

show_logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        print_info "Logs en temps réel pour $service :"
        sudo journalctl -u "$service" -f
    else
        print_info "Logs en temps réel pour tous les services :"
        sudo journalctl -f -u certisign-*
    fi
}

show_all_logs() {
    print_info "Tous les logs des services :"
    for service in "${SERVICES[@]}"; do
        echo ""
        print_info "=== Logs de $service ==="
        sudo journalctl -u "$service" --no-pager -n 20
    done
}

health_check() {
    print_info "Vérification de santé des services..."
    echo ""
    
    # Vérifier les services systemd
    for service in "${SERVICES[@]}"; do
        if sudo systemctl is-active --quiet "$service"; then
            print_success "$service: ACTIF"
        else
            print_error "$service: INACTIF"
        fi
    done
    
    echo ""
    
    # Vérifier les ports
    ports=(8000 8001 8002 8003)
    for port in "${ports[@]}"; do
        if sudo lsof -i :$port > /dev/null 2>&1; then
            print_success "Port $port: OCCUPÉ"
        else
            print_error "Port $port: LIBRE"
        fi
    done
    
    echo ""
    
    # Vérifier Nginx
    if sudo systemctl is-active --quiet nginx; then
        print_success "Nginx: ACTIF"
    else
        print_error "Nginx: INACTIF"
    fi
}

check_ports() {
    print_info "Ports utilisés par CertiSign :"
    echo ""
    ports=(8000 8001 8002 8003)
    for port in "${ports[@]}"; do
        local process=$(sudo lsof -i :$port 2>/dev/null | head -2 | tail -1 | awk '{print $1, $2}' || echo "Aucun")
        if [ "$process" != "Aucun" ]; then
            print_success "Port $port: $process"
        else
            print_error "Port $port: Aucun processus"
        fi
    done
}

restart_nginx() {
    print_info "Redémarrage de Nginx..."
    sudo systemctl reload nginx
    if sudo systemctl is-active --quiet nginx; then
        print_success "Nginx redémarré avec succès"
    else
        print_error "Échec du redémarrage de Nginx"
    fi
}

build_frontend() {
    print_info "Recompilation du frontend..."
    cd "$(dirname "${BASH_SOURCE[0]}")/frontend"
    
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules non trouvé. Installation des dépendances..."
        npm install
    fi
    
    npm run build
    print_success "Frontend recompilé avec succès"
}

# Script principal
case "${1:-help}" in
    "status")
        show_status
        ;;
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "logs")
        show_logs "$2"
        ;;
    "logs-all")
        show_all_logs
        ;;
    "health")
        health_check
        ;;
    "ports")
        check_ports
        ;;
    "nginx")
        restart_nginx
        ;;
    "build")
        build_frontend
        ;;
    "help"|*)
        show_help
        ;;
esac 