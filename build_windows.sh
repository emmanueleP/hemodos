#!/bin/bash

# Installa requisiti Python
pip install -r requirements.txt

# Build con PyInstaller
pyinstaller hemodos.spec

# Crea cartella per l'installer
mkdir -p dist/installer

# Copia i file necessari per l'installer
cp setup.iss dist/installer/
cp -r dist/Hemodos/* dist/installer/
cp LICENSE.md dist/installer/
cp README.md dist/installer/

# Verifica se Inno Setup è installato
if [ -f "/c/Program Files (x86)/Inno Setup 6/ISCC.exe" ]; then
    ISCC="/c/Program Files (x86)/Inno Setup 6/ISCC.exe"
elif [ -f "/c/Program Files/Inno Setup 6/ISCC.exe" ]; then
    ISCC="/c/Program Files/Inno Setup 6/ISCC.exe"
else
    echo "Inno Setup non trovato. Installalo da: https://jrsoftware.org/isdl.php"
    exit 1
fi

# Build dell'installer
"$ISCC" setup.iss

# Sposta l'installer nella cartella dist
mv Output/HemodosSetup.exe dist/

# Pulisci le cartelle temporanee
rm -rf Output
rm -rf dist/installer

echo "Build completata! L'installer si trova in dist/HemodosSetup.exe" 