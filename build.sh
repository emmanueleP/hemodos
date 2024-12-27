#!/bin/bash

# Pulisci le directory di build
rm -rf build/ dist/

# Crea l'ambiente virtuale se non esiste
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Attiva l'ambiente virtuale
source venv/bin/activate  # Per Linux/Mac
# venv\Scripts\activate  # Per Windows

# Installa le dipendenze
pip install -r requirements.txt
pip install pyinstaller

# Esegui il build
pyinstaller hemodos.spec

# Copia i file necessari
cp config.json dist/
cp -r assets dist/
mkdir -p dist/docs
cp docs/README.md dist/docs/
cp docs/LICENSE.md dist/docs/

echo "Build completato! L'eseguibile si trova in dist/Hemodos" 