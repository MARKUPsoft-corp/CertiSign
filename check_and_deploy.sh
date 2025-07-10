#!/bin/bash

# Script de vérification et déploiement automatique pour CertiSign
# À utiliser avec cron pour vérifier régulièrement les changements
# Exemple cron: */5 * * * * /home/ssatl/Documents/Doc@uthANTIC/check_and_deploy.sh

# Configuration
PROJECT_DIR="/home/ssatl/Documents/Doc@uthANTIC"
LOG_FILE="$PROJECT_DIR/logs/auto-deploy.log"
LOCK_FILE="/tmp/certisign-deploy.lock"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de logging avec timestamp
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Vérifier si un déploiement est déjà en cours
if [ -f "$LOCK_FILE" ]; then
    # Vérifier si le processus existe encore
    PID=$(cat "$LOCK_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        log "${YELLOW}⏳ Déploiement déjà en cours (PID: $PID)${NC}"
        exit 0
    else
        # Le processus n'existe plus, on peut supprimer le lock
        rm -f "$LOCK_FILE"
    fi
fi

# Créer le lock file
echo $$ > "$LOCK_FILE"

# Fonction de nettoyage
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# Vérifier si on est dans le bon répertoire
if [ ! -d "$PROJECT_DIR/.git" ]; then
    log "${RED}❌ Erreur: Répertoire Git non trouvé dans $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Récupérer les informations du remote sans faire de pull
log "${YELLOW}🔍 Vérification des changements distants...${NC}"
git fetch origin >/dev/null 2>&1

# Comparer les commits local et distant
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/prod)

if [ "$LOCAL" = "$REMOTE" ]; then
    # Pas de changement, sortir silencieusement (pas de log pour éviter le spam)
    exit 0
fi

log "${GREEN}🆕 Nouveaux changements détectés !${NC}"
log "${YELLOW}Local:  $LOCAL${NC}"
log "${YELLOW}Remote: $REMOTE${NC}"

# Déclencher le déploiement
log "${YELLOW}🚀 Déclenchement du déploiement automatique...${NC}"

if [ -f "$PROJECT_DIR/deploy.sh" ]; then
    chmod +x "$PROJECT_DIR/deploy.sh"
    "$PROJECT_DIR/deploy.sh" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ Déploiement automatique réussi${NC}"
        
        # Notification optionnelle (décommentez si vous avez configuré mail)
        # echo "Déploiement CertiSign réussi à $(date)" | mail -s "CertiSign Auto-Deploy Success" admin@example.com
        
    else
        log "${RED}❌ Échec du déploiement automatique${NC}"
        
        # Notification d'erreur optionnelle
        # echo "Échec du déploiement CertiSign à $(date). Vérifiez les logs: $LOG_FILE" | mail -s "CertiSign Auto-Deploy Error" admin@example.com
    fi
else
    log "${RED}❌ Script deploy.sh non trouvé${NC}"
    exit 1
fi 