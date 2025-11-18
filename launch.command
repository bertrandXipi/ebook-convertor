#!/bin/bash
# Script de lancement simple - double-clic pour lancer

# Aller dans le dossier du script
cd "$(dirname "$0")"

# Activer l'environnement virtuel et lancer
source venv/bin/activate
python3 run_converter.py

# Garder la fenêtre ouverte
echo ""
read -p "Appuyez sur Entrée pour fermer..."
