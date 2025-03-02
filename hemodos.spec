# -*- mode: python ; coding: utf-8 -*-
import os
import json
from pathlib import Path
import sys
import platform

block_cipher = None

# Sistema operativo
system = platform.system()

# Configurazione specifica per sistema
if system == "Windows":
    icon = 'src/assets/icon.ico'
    binary_ext = '.exe'
    syncthing_binary = 'syncthing.exe'
    syncthing_path = f'syncthing/windows/{syncthing-windows-setup.exe}'
elif system == "Darwin":
    icon = 'src/assets/icon.icns'
    binary_ext = ''
    syncthing_binary = 'syncthing'
    syncthing_path = f'syncthing/macos/{syncthing.dmg}'
else:
    icon = 'src/assets/icon_512x512.png'
    binary_ext = ''
    syncthing_binary = 'syncthing'
    syncthing_path = f'syncthing/linux/{syncthing.appimage}'

# Definisci i percorsi base
BASE_PATH = Path('.')
SRC_PATH = BASE_PATH / 'src'
ASSETS_PATH = SRC_PATH / 'assets'  # Cartella assets dentro src
DOCS_PATH = BASE_PATH / 'docs'

# Crea le directory necessarie
os.makedirs('dist', exist_ok=True)
os.makedirs('dist/assets', exist_ok=True)
os.makedirs('dist/docs', exist_ok=True)
os.makedirs(ASSETS_PATH, exist_ok=True)
os.makedirs(DOCS_PATH, exist_ok=True)

# Lista di file necessari in assets
required_assets = [
    'logo.png',
    'logo_info.png',
    'logo.ico',
    'user_guide.png',
    'trash.png',
    'arrow_down.png',
    'WizardImageFile.bmp',
    'WizardSmallImageFile.bmp',
    'cogwheel.png',
    'add_time.png',
    'diskette.png',
    'doc.png',
    'printer.png',
    'database_64px.png',
    'exit_64px.png',
    'user_guide_64px.png'
]

# Verifica che i file necessari esistano
if not ASSETS_PATH.exists():
    raise FileNotFoundError(f"Directory assets non trovata in {ASSETS_PATH}")

for asset in required_assets:
    if not (ASSETS_PATH / asset).exists():
        raise FileNotFoundError(f"File {asset} non trovato in {ASSETS_PATH}")

# Configurazione di default aggiornata
default_config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "hemodos_db",
        "user": "admin",
        "password": "password",
        "backup_dir": "backups"
    },
    "app": {
        "debug": True,
        "log_level": "INFO",
        "autosave": {"enabled": True, "interval": 5},
        "cloud": {"service": "Locale", "sync_interval": 30},
        "show_welcome": True  # Aggiunto controllo per welcome dialog
    },
    "ui": {
        "theme": "dark",
        "primary_color": "#004d4d",
        "font": "SF Pro Display",
        "window": {
            "width": 1024,
            "height": 768,
            "min_width": 800,
            "min_height": 600
        }
    }
}

# Salva il config.json nella directory di build
config_path = os.path.join('dist', 'config.json')
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(default_config, f, indent=4)

# Dati comuni
datas = [
    ('src/assets/*', 'assets'),
    ('LICENSE.md', '.'),
    ('README.md', '.'),
    ('config.json', '.'),
    (syncthing_path, '.')  # Includi Syncthing nella root del pacchetto
]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Hemodos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon
)

# Configurazione specifica per macOS
if system == "Darwin":
    app = BUNDLE(
        exe,
        name='Hemodos.app',
        icon=icon,
        bundle_identifier='com.emmanuele.hemodos',
        info_plist={
            'CFBundleShortVersionString': '1.0.9',
            'CFBundleVersion': '1.0.9',
            'NSHighResolutionCapable': 'True'
        }
    )
else:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='Hemodos'
    )

# Copia i file necessari
import shutil

# Assicurati che la directory dist/assets esista
os.makedirs('dist/assets', exist_ok=True)

# Copia le icone nella cartella assets
for asset in required_assets:
    src_path = os.path.join('src/assets', asset)
    dst_path = os.path.join('dist/assets', asset)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
    else:
        print(f"Attenzione: {asset} non trovato in {src_path}")

print("Build completata con successo!") 