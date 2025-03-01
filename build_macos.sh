#!/bin/bash

# Installa requisiti
pip3 install -r requirements.txt

# Build con PyInstaller
pyinstaller hemodos.spec

# Crea cartella temporanea per il DMG
mkdir -p dist/dmg_temp
cp -r "dist/Hemodos.app" dist/dmg_temp/

# Crea script di avvio che gestisce anche Syncthing
cat > "dist/dmg_temp/Hemodos.app/Contents/MacOS/start.sh" << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$DIR/syncthing" --no-browser --no-restart &
"$DIR/Hemodos"
EOF

chmod +x "dist/dmg_temp/Hemodos.app/Contents/MacOS/start.sh"

# Modifica Info.plist per usare lo script di avvio
/usr/libexec/PlistBuddy -c "Set :CFBundleExecutable start.sh" "dist/dmg_temp/Hemodos.app/Contents/Info.plist"

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
    "dist/dmg_temp/"

# Pulisci
rm -rf dist/dmg_temp

echo "Build completata! L'app si trova in dist/Hemodos.app e il DMG in dist/Hemodos.dmg" 