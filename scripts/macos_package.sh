#!/bin/bash

# Crea il pacchetto principale
pyinstaller --windowed --name hemodos src/main.py

# Crea il pacchetto admin
pyinstaller --windowed --name hemodos_admin src/admin/hemodos_admin.py

# Crea la struttura del pacchetto
mkdir -p dist/Hemodos.app/Contents/MacOS/admin

# Sposta i file
mv dist/hemodos_admin/hemodos_admin dist/Hemodos.app/Contents/MacOS/admin/
cp -r resources dist/Hemodos.app/Contents/Resources

# Crea il DMG
create-dmg \
  --volname "Hemodos Installer" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "Hemodos.app" 200 190 \
  --hide-extension "Hemodos.app" \
  --app-drop-link 600 185 \
  "Hemodos.dmg" \
  "dist/Hemodos.app" 