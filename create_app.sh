#!/bin/bash
# Crée une application macOS pour le convertisseur EPUB

APP_NAME="EPUB to PDF"
APP_DIR="$HOME/Applications/$APP_NAME.app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Création de l'application macOS..."

# Créer la structure de l'app
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Créer le script de lancement
cat > "$APP_DIR/Contents/MacOS/launcher" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"

# Ouvrir un terminal et lancer le script
osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && source venv/bin/activate && python3 run_converter.py"
end tell
APPLESCRIPT
EOF

chmod +x "$APP_DIR/Contents/MacOS/launcher"

# Créer Info.plist
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.xipirons.epub-to-pdf</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
</dict>
</plist>
EOF

# Créer une icône avec SF Symbols (icône native macOS)
echo "🎨 Création de l'icône..."
python3 << 'PYTHON'
import subprocess
import os

app_dir = os.path.expanduser("~/Applications/EPUB to PDF.app/Contents/Resources")

# Utiliser sips pour créer une icône à partir d'un emoji/symbole
# On va utiliser l'icône de document de macOS
subprocess.run([
    "sips", "-s", "format", "icns",
    "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/BookmarkIcon.icns",
    "--out", f"{app_dir}/AppIcon.icns"
], capture_output=True)

print("✓ Icône créée")
PYTHON

echo "✅ Application créée : $APP_DIR"
echo ""
echo "📱 Pour l'ajouter au Dock :"
echo "   1. Ouvre le Finder"
echo "   2. Va dans ~/Applications/"
echo "   3. Glisse '$APP_NAME.app' vers le Dock"
echo ""
echo "🎯 Pour lancer : Clique sur l'icône dans le Dock"
