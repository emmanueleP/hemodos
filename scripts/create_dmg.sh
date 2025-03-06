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
VERSION="1.0.0"
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
mkdir -p "$TMP_DMG_DIR"

# Copia l'app nella directory temporanea
cp -r "$BUILD_DIR/$APP_NAME.app" "$TMP_DMG_DIR/"

# Crea un link simbolico ad Applications
ln -s /Applications "$TMP_DMG_DIR/Applications"

# Crea il DMG
echo "Creazione del DMG..."
create-dmg \
    --volname "$APP_NAME" \
    --volicon "$PROJECT_ROOT/src/assets/icons/hemodos.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "$APP_NAME.app" 175 190 \
    --hide-extension "$APP_NAME.app" \
    --app-drop-link 425 190 \
    --no-internet-enable \
    "$PROJECT_ROOT/$DMG_NAME.dmg" \
    "$TMP_DMG_DIR"

# Verifica che il DMG sia stato creato
if [ -f "$PROJECT_ROOT/$DMG_NAME.dmg" ]; then
    echo "DMG creato con successo: $DMG_NAME.dmg"
    
    # Pulisci la directory temporanea
    rm -rf "$TMP_DMG_DIR"
else
    echo "Errore durante la creazione del DMG"
    exit 1
fi

# Calcola e mostra l'hash SHA256 del DMG
echo "SHA256 del DMG:"
shasum -a 256 "$PROJECT_ROOT/$DMG_NAME.dmg" 