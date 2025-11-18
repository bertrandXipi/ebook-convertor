#!/bin/bash
# Workflow complet : EPUB→PDF + Upload NotebookLM
# Double-clic pour lancer

# Aller dans le dossier du script
cd "$(dirname "$0")"

# Activer l'environnement virtuel
source venv/bin/activate

# Demander le dossier et le titre
echo "🚀 Workflow complet : EPUB → PDF → NotebookLM"
echo "=============================================="
echo ""
echo "Dossier à traiter (ex: ~/Downloads/mes_livres) :"
read FOLDER

echo ""
echo "Titre du notebook NotebookLM :"
read TITLE

echo ""
echo "🔄 Lancement du workflow..."
echo ""

# Lancer le workflow
python3 full_workflow.py --folder "$FOLDER" --title "$TITLE"

# Garder la fenêtre ouverte
echo ""
read -p "Appuyez sur Entrée pour fermer..."
