#!/bin/bash
# Convertit une image PNG en icône macOS et l'applique à l'app

if [ -z "$1" ]; then
    echo "Usage: ./set_icon.sh chemin/vers/ton/image.png"
    echo "Exemple: ./set_icon.sh ~/Downloads/mon_icone.png"
    exit 1
fi

IMAGE_PATH="$1"
APP_PATH="$HOME/Applications/EPUB to PDF.app"
ICONSET_PATH="/tmp/AppIcon.iconset"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "❌ Fichier introuvable : $IMAGE_PATH"
    exit 1
fi

echo "🎨 Conversion de l'icône..."

# Créer le dossier iconset
mkdir -p "$ICONSET_PATH"

# Générer toutes les tailles requises pour macOS
sips -z 16 16     "$IMAGE_PATH" --out "$ICONSET_PATH/icon_16x16.png" > /dev/null 2>&1
sips -z 32 32     "$IMAGE_PATH" --out "$ICONSET_PATH/icon_16x16@2x.png" > /dev/null 2>&1
sips -z 32 32     "$IMAGE_PATH" --out "$ICONSET_PATH/icon_32x32.png" > /dev/null 2>&1
sips -z 64 64     "$IMAGE_PATH" --out "$ICONSET_PATH/icon_32x32@2x.png" > /dev/null 2>&1
sips -z 128 128   "$IMAGE_PATH" --out "$ICONSET_PATH/icon_128x128.png" > /dev/null 2>&1
sips -z 256 256   "$IMAGE_PATH" --out "$ICONSET_PATH/icon_128x128@2x.png" > /dev/null 2>&1
sips -z 256 256   "$IMAGE_PATH" --out "$ICONSET_PATH/icon_256x256.png" > /dev/null 2>&1
sips -z 512 512   "$IMAGE_PATH" --out "$ICONSET_PATH/icon_256x256@2x.png" > /dev/null 2>&1
sips -z 512 512   "$IMAGE_PATH" --out "$ICONSET_PATH/icon_512x512.png" > /dev/null 2>&1
sips -z 1024 1024 "$IMAGE_PATH" --out "$ICONSET_PATH/icon_512x512@2x.png" > /dev/null 2>&1

# Convertir en .icns
iconutil -c icns "$ICONSET_PATH" -o "$APP_PATH/Contents/Resources/AppIcon.icns"

# Nettoyer
rm -rf "$ICONSET_PATH"

# Forcer le Finder à rafraîchir l'icône
touch "$APP_PATH"
killall Finder 2>/dev/null || true

echo "✅ Icône mise à jour !"
echo "📱 L'icône devrait apparaître dans quelques secondes"
echo ""
echo "Si l'icône ne change pas :"
echo "  1. Retire l'app du Dock"
echo "  2. Remets-la dans le Dock"
