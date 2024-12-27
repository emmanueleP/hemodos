# -*- mode: python ; coding: utf-8 -*-
import os
import json
from pathlib import Path

block_cipher = None

# Definisci i percorsi base
BASE_PATH = Path('.')
SRC_PATH = BASE_PATH / 'src'
ASSETS_PATH = SRC_PATH / 'assets'  # Cambiato per usare assets dentro src
DOCS_PATH = BASE_PATH / 'docs'

# Crea le directory necessarie
os.makedirs('dist', exist_ok=True)
os.makedirs('dist/assets', exist_ok=True)
os.makedirs('dist/docs', exist_ok=True)
os.makedirs(ASSETS_PATH, exist_ok=True)
os.makedirs(DOCS_PATH, exist_ok=True)

# Verifica che i file necessari esistano
if not ASSETS_PATH.exists():
    raise FileNotFoundError(f"Directory assets non trovata in {ASSETS_PATH}")

if not (ASSETS_PATH / 'logo.png').exists():
    raise FileNotFoundError(f"File logo.png non trovato in {ASSETS_PATH}")

# Crea il config.json di default se non esiste
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
        "cloud": {"service": "Locale", "sync_interval": 30}
    },
    "ui": {
        "theme": "light",
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

a = Analysis([str(SRC_PATH / 'main.py')],
    pathex=[str(BASE_PATH), str(SRC_PATH)],
    binaries=[],
    datas=[
        (str(ASSETS_PATH), 'assets'),  # Copia tutta la cartella assets
        (config_path, '.'),
        (str(DOCS_PATH), 'docs')
    ],
    hiddenimports=[
        'PyQt5.QtPrintSupport',
        'matplotlib',
        'docx',
        'watchdog'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
    cipher=block_cipher)

exe = EXE(pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Hemodos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    version='file_version_info.txt',
    icon=str(ASSETS_PATH / 'logo.ico'))

# Copia file aggiuntivi assicurandosi che la struttura delle cartelle sia mantenuta
import shutil
for src_dir in [ASSETS_PATH, DOCS_PATH]:
    if src_dir.exists():
        dst_dir = Path('dist') / src_dir.name
        dst_dir.mkdir(exist_ok=True)
        for src_file in src_dir.rglob('*'):
            if src_file.is_file():
                rel_path = src_file.relative_to(src_dir)
                dst_file = dst_dir / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file) 