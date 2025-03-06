#!/bin/bash

# Verifica che siamo su macOS
if [ "$(uname)" != "Darwin" ]; then
    echo "Questo script può essere eseguito solo su macOS"
    exit 1
fi

# Verifica che create-dmg sia installato
if ! command -v create-dmg &> /dev/null; then
    echo "create-dmg non trovato. Installalo con: brew install create-dmg"
    exit 1
fi

# Directory dello script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Directory root del progetto
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
# Directory di build
BUILD_DIR="$PROJECT_ROOT/dist"
# Nome dell'applicazione
APP_NAME="Hemodos"
# Versione dell'app
VERSION="1.0.9"
# Nome del DMG
DMG_NAME="$APP_NAME-$VERSION"

# Pulisci le directory di build precedenti
echo "Pulizia delle directory di build..."
rm -rf "$BUILD_DIR"
rm -f "$PROJECT_ROOT/$DMG_NAME.dmg"

# Costruisci l'app con PyInstaller
echo "Building dell'applicazione con PyInstaller..."
cd "$PROJECT_ROOT"
pyinstaller hemodos_macos.spec

# Verifica che la build sia andata a buon fine
if [ ! -d "$BUILD_DIR/$APP_NAME.app" ]; then
    echo "Errore durante la build dell'applicazione"
    exit 1
fi

# Crea una directory temporanea per il DMG
TMP_DMG_DIR="$BUILD_DIR/dmg_temp"
rm -rf "$TMP_DMG_DIR"
mkdir -p "$TMP_DMG_DIR"

# Copia l'app nella directory temporanea
cp -r "$BUILD_DIR/$APP_NAME.app" "$TMP_DMG_DIR/"

# Crea un DMG temporaneo non compresso
TMP_DMG="$BUILD_DIR/tmp.dmg"
rm -f "$TMP_DMG"

echo "Creazione del DMG..."
hdiutil create -volname "$APP_NAME" -srcfolder "$TMP_DMG_DIR" -ov -format UDRW "$TMP_DMG"

# Monta il DMG
MOUNT_DIR="/Volumes/$APP_NAME"
if [ -d "$MOUNT_DIR" ]; then
    hdiutil detach "$MOUNT_DIR" -force
fi
hdiutil attach "$TMP_DMG"

# Crea il link ad Applications
echo "Configurazione del DMG..."
ln -s /Applications "$MOUNT_DIR/Applications"

# Configura la vista della finestra
echo '
   tell application "Finder"
     tell disk "'$APP_NAME'"
           open
           set current view of container window to icon view
           set toolbar visible of container window to false
           set statusbar visible of container window to false
           set the bounds of container window to {200, 120, 800, 520}
           set theViewOptions to the icon view options of container window
           set arrangement of theViewOptions to not arranged
           set icon size of theViewOptions to 100
           set position of item "'$APP_NAME.app'" of container window to {175, 190}
           set position of item "Applications" of container window to {425, 190}
           close
           update without registering applications
           delay 2
     end tell
   end tell
' | osascript

# Smonta il DMG
hdiutil detach "$MOUNT_DIR"

# Converti il DMG in formato compresso
echo "Compressione del DMG finale..."
rm -f "$PROJECT_ROOT/$DMG_NAME.dmg"
hdiutil convert "$TMP_DMG" -format UDZO -o "$PROJECT_ROOT/$DMG_NAME.dmg"

# Pulisci i file temporanei
rm -f "$TMP_DMG"
rm -rf "$TMP_DMG_DIR"

# Verifica che il DMG sia stato creato
if [ -f "$PROJECT_ROOT/$DMG_NAME.dmg" ]; then
    echo "DMG creato con successo: $DMG_NAME.dmg"
    
    # Calcola e mostra l'hash SHA256 del DMG
    echo "SHA256 del DMG:"
    shasum -a 256 "$PROJECT_ROOT/$DMG_NAME.dmg"
    exit 0
else
    echo "Errore durante la creazione del DMG"
    exit 1
fi 