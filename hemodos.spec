# -*- mode: python ; coding: utf-8 -*-
import os
import json

block_cipher = None

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
with open(os.path.join('dist', 'config.json'), 'w', encoding='utf-8') as f:
    json.dump(default_config, f, indent=4)

a = Analysis(['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
        ('dist/config.json', '.'),  # Usa il config.json dalla directory dist
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
    icon='assets/logo.ico')

# Crea cartelle necessarie
os.makedirs('dist/assets', exist_ok=True)
os.makedirs('dist/docs', exist_ok=True)

# Copia file aggiuntivi
import shutil
shutil.copy2('docs/README.md', 'dist/docs/')
shutil.copy2('docs/LICENSE.md', 'dist/docs/')