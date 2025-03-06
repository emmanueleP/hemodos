# -*- mode: python ; coding: utf-8 -*-
import os
import json
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Definisci i percorsi base
BASE_PATH = Path('.')
SRC_PATH = BASE_PATH / 'src'
ASSETS_PATH = SRC_PATH / 'assets'
DOCS_PATH = BASE_PATH / 'docs'

# Crea le directory necessarie
os.makedirs('dist', exist_ok=True)
os.makedirs('dist/assets', exist_ok=True)
os.makedirs('dist/docs', exist_ok=True)

# Lista di file necessari in assets
required_assets = [
    'logo.png',
    'logo_info.png',
    'hemodos.icns',
    'user_guide.png',
    'trash.png',
    'arrow_down.png',
    'cogwheel.png',
    'add_time.png',
    'diskette.png',
    'doc.png',
    'printer.png',
    'database_64px.png',
    'exit_64px.png',
    'user_guide_64px.png',
    'icon_1024x1024.png',
    'blood.png'
]

# Verifica che i file necessari esistano
if not ASSETS_PATH.exists():
    raise FileNotFoundError(f"Directory assets non trovata in {ASSETS_PATH}")

for asset in required_assets:
    if not (ASSETS_PATH / asset).exists():
        raise FileNotFoundError(f"File {asset} non trovato in {ASSETS_PATH}")

# Configurazione di default
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
        "show_welcome": True
    },
    "ui": {
        "theme": "dark",
        "primary_color": "#004d4d",
        "font": "SF Pro Display",  # Font di default per macOS
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

# Raccogli tutti i dati necessari
datas = [
    ('src/assets', 'assets'),  # Copia l'intera directory assets
    ('dist/config.json', '.'),
    ('LICENSE.md', '.'),
    ('README.md', '.')
]

# Hidden imports necessari per macOS
hidden_imports = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtPrintSupport',
    'PyQt5.sip',
    'PyQt5.QtSvg',
    'PyQt5.QtXml',
    'sqlite3',
    'cryptography',
    'json',
    'datetime',
    'logging',
    'hashlib',
    'base64',
    'os',
    'sys',
    'pathlib',
    'typing',
]

# Analisi
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Rimuovi duplicati
def remove_duplicates(list_of_tuples):
    seen = set()
    return [x for x in list_of_tuples if not (tuple(x) in seen or seen.add(tuple(x)))]

a.datas = remove_duplicates(a.datas)
a.binaries = remove_duplicates(a.binaries)

# PYZ
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Configurazione EXE per macOS
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
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/hemodos.icns'
)

# Configurazione COLLECT per macOS
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

# Configurazione BUNDLE per macOS
app = BUNDLE(
    coll,
    name='Hemodos.app',
    icon='src/assets/hemodos.icns',
    bundle_identifier='com.emmanuele.hemodos',
    info_plist={
        'CFBundleShortVersionString': '1.0.8',
        'CFBundleVersion': '1.0.8',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0'
    }
)

print("Build macOS completata con successo!") 