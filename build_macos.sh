#!/bin/bash

# Installa requisiti
pip3 install -r requirements.txt

# Build con PyInstaller
pyinstaller hemodos.spec

# Crea il DMG
create-dmg \
    --volname "Hemodos" \
    --volicon "src/assets/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "Hemodos.app" 175 120 \
    --hide-extension "Hemodos.app" \
    --app-drop-link 425 120 \
    "dist/Hemodos.dmg" \
    "dist/Hemodos.app"

echo "Build completata! L'app si trova in dist/Hemodos.app e il DMG in dist/Hemodos.dmg" 