#!/bin/bash
# Script d'optimisation pour Flutter
# Exécutez ce script pour un lancement plus rapide de l'application

# Vider le cache Flutter pour nettoyer les anciens artefacts
flutter clean

# Obtenir les dépendances
flutter pub get

# Pré-compiler les ressources (accélère le premier lancement)
flutter precache

# Exécuter avec les options d'optimisation
flutter run \
  --purge-persistent-cache \
  --enable-impeller \
  --dart-define=ENABLE_LOGGING=false \
  --dart-define=SKIP_INTRO_ANIMATIONS=true \
  "$@"
