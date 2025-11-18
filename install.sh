#!/bin/bash
# Script d'installation pour l'auto-convertisseur EPUB vers PDF

echo "🚀 Installation de l'auto-convertisseur EPUB → PDF"
echo "=================================================="

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 n'est pas installé"
    echo "Installez Python depuis : https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 détecté : $(python3 --version)"

# Vérifier Calibre
if [ ! -f "/Applications/calibre.app/Contents/MacOS/ebook-convert" ]; then
    echo "✗ Calibre n'est pas installé"
    echo "Installez Calibre depuis : https://calibre-ebook.com/download_osx"
    exit 1
fi

echo "✓ Calibre détecté"

# Installer les dépendances Python
echo ""
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

echo "📦 Installation des dépendances Python..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dépendances installées avec succès"
else
    echo "✗ Erreur lors de l'installation des dépendances"
    exit 1
fi

# Rendre main.py exécutable
chmod +x main.py

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Pour démarrer la surveillance :"
echo "  source venv/bin/activate && python3 main.py"
echo ""
echo "Pour arrêter : Ctrl+C"
