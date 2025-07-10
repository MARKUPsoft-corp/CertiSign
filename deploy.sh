#!/bin/bash

# Script de déploiement automatique pour CertiSign
# Ce script doit être exécuté sur le serveur de production

echo "🚀 Début du déploiement automatique CertiSign..."
echo "📅 $(date)"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Répertoire du projet 
PROJECT_DIR="/home/ssatl/Documents/Doc@uthANTIC"
LOG_FILE="$PROJECT_DIR/logs/deploy.log"

# Fonction de logging
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Vérifier si on est dans le bon répertoire
if [ ! -d "$PROJECT_DIR/.git" ]; then
    log "${RED}❌ Erreur: Répertoire Git non trouvé dans $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

log "${YELLOW}📁 Répertoire courant: $(pwd)${NC}"

# Sauvegarder l'état actuel
log "${YELLOW}💾 Sauvegarde de l'état actuel...${NC}"
git stash push -m "Auto-stash avant déploiement $(date)"

# Récupérer les derniers changements
log "${YELLOW}📥 Récupération des changements depuis le repository distant...${NC}"
git fetch origin

# Vérifier s'il y a des changements
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/prod)

if [ "$LOCAL" = "$REMOTE" ]; then
    log "${GREEN}✅ Aucun changement détecté. Déploiement non nécessaire.${NC}"
    exit 0
fi

log "${YELLOW}🔄 Nouveaux changements détectés. Mise à jour en cours...${NC}"


# Mettre à jour le code
log "${YELLOW}⬇️  Pull des changements...${NC}"
if git pull origin prod; then
    log "${GREEN}✅ Code mis à jour avec succès${NC}"
else
    log "${RED}❌ Erreur lors du pull${NC}"
    exit 1
fi

# Migrations Django si nécessaire (uniquement)
if [ -f "backend/django-project/manage.py" ]; then
    log "${YELLOW}🗃️  Application des migrations Django...${NC}"
    cd backend/django-project
    if [ -d "../../.venv" ]; then
        source ../../.venv/bin/activate
        python3 manage.py migrate --noinput
        deactivate
    fi
    cd "$PROJECT_DIR"
fi


log "${GREEN}🎉 Déploiement terminé avec succès !${NC}"
log "${GREEN}📍 Version déployée: $(git rev-parse --short HEAD)${NC}"
log "${GREEN}📅 $(date)${NC}"

echo ""
log "${GREEN}✨ CertiSign est maintenant à jour et fonctionnel !${NC}" 