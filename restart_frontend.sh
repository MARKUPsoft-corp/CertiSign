#!/bin/bash

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

FRONTEND_DIR="$(pwd)/frontend"
LOG_DIR="$(pwd)/logs"
FRONTEND_PORT=8080

# Créer le répertoire de logs s'il n'existe pas
mkdir -p "$LOG_DIR"

echo -e "${BLUE}Redémarrage du frontend Vue.js${NC}"

# Arrêter les processus existants du frontend
echo -e "${YELLOW}Arrêt du frontend existant...${NC}"
pkill -f "node.*vue-cli-service" || true
sleep 2

# Vérifier si le port est déjà utilisé
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}Port $FRONTEND_PORT est encore utilisé. Tentative de libération...${NC}"
    lsof -t -i:$FRONTEND_PORT | xargs -r kill -9
    sleep 1
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}Impossible de libérer le port $FRONTEND_PORT. Veuillez le libérer manuellement.${NC}"
        exit 1
    fi
fi

# Démarrer le frontend
cd "$FRONTEND_DIR"
echo -e "${YELLOW}Démarrage du frontend...${NC}"
PORT=$FRONTEND_PORT npm run serve > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}Frontend Vue.js redémarré (PID: $FRONTEND_PID)${NC}"
echo -e "${CYAN}Vous pouvez accéder au frontend à l'adresse:${NC} http://localhost:$FRONTEND_PORT"
echo -e "${YELLOW}Les logs sont disponibles dans:${NC} $LOG_DIR/frontend.log"

echo -e "\n${BLUE}Surveillance des logs du frontend (Ctrl+C pour quitter)${NC}"
tail -f "$LOG_DIR/frontend.log" 