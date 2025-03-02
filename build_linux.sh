#!/bin/bash

# Installa dipendenze
sudo apt-get update
sudo apt-get install -y python3-pip python3-pyqt5 python3-dev

# Installa requisiti Python
pip3 install -r requirements.txt

# Build con PyInstaller
pyinstaller hemodos.spec

# Crea pacchetto .deb
mkdir -p dist/deb/DEBIAN
mkdir -p dist/deb/usr/local/bin
mkdir -p dist/deb/usr/share/applications
mkdir -p dist/deb/usr/share/icons/hicolor/256x256/apps

# Copia i file
cp -r dist/Hemodos/* dist/deb/usr/local/bin/
cp src/assets/icon.png dist/deb/usr/share/icons/hicolor/256x256/apps/hemodos.png

# Crea il file .desktop
cat > dist/deb/usr/share/applications/hemodos.desktop << EOF
[Desktop Entry]
Name=Hemodos
Comment=Software per la gestione delle donazioni di sangue
Exec=/usr/local/bin/Hemodos
Icon=hemodos
Terminal=false
Type=Application
Categories=Office;
EOF

# Crea il file control
cat > dist/deb/DEBIAN/control << EOF
Package: hemodos
Version: 1.0.8
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Emmanuele Pani <email@example.com>
Description: Software per la gestione delle donazioni di sangue
 Hemodos è un'applicazione per gestire le prenotazioni
 delle donazioni di sangue.
EOF

# Build del pacchetto .deb
dpkg-deb --build dist/deb dist/hemodos_1.0.8_amd64.deb 