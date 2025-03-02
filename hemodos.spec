# -*- mode: python ; coding: utf-8 -*-
import os
import json
from pathlib import Path
import sys
import platform
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

# Sistema operativo
system = platform.system()

# Configurazione specifica per sistema
if system == "Windows":
    icon = 'src/assets/logo.ico'
elif system == "Darwin":
    icon = 'src/assets/icon.icns'
else:
    icon = 'src/assets/icon.png'


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
    'user_guide_64px.png',
    'icon_1024x1024.png'
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

# Raccogli tutti i dati necessari
datas = []

# Aggiungi qt_material e le sue dipendenze
try:
    datas.extend(collect_data_files('qt_material'))
    datas.extend(collect_data_files('qtawesome'))
except Exception as e:
    print(f"WARNING: qt_material/qtawesome files not found: {e}")

# Aggiungi gli assets come data files
datas.extend([
    ('dist/assets', 'assets'),
    ('dist/templates', 'templates'),
    ('dist/static', 'static'),
    ('LICENSE.md', '.'),
    ('README.md', '.'),
])

# Raccogli tutti i submoduli necessari
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
    'cryptography.hazmat.backends.openssl',
    'cryptography.hazmat.bindings._openssl',
    'qt_material',
    'qt_material.resources',
    'qtawesome',
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

# Raccogli le librerie dinamiche
binaries = []
try:
    # Aggiungi le librerie di cryptography
    binaries.extend(collect_dynamic_libs('cryptography'))
    # Aggiungi le librerie Qt
    binaries.extend(collect_dynamic_libs('PyQt5'))
except Exception as e:
    print(f"WARNING: dynamic libs not found: {e}")

# Configurazione dell'analisi
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

# Rimuovi file duplicati
def remove_duplicates(list_of_tuples):
    seen = set()
    return [x for x in list_of_tuples if not (tuple(x) in seen or seen.add(tuple(x)))]

a.datas = remove_duplicates(a.datas)
a.binaries = remove_duplicates(a.binaries)

# Configurazione del PYZ
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Configurazione specifica per sistema operativo
if platform.system() == 'Darwin':
    icon_file = 'src/assets/logo.icns'
    if not os.path.exists(icon_file):
        icon_file = None
        
    exe = EXE(
        pyz,
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
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file
    )
    
    app = BUNDLE(
        exe,
        name='Hemodos.app',
        icon=icon_file,
        bundle_identifier='com.emmanuele.hemodos',
        info_plist={
            'CFBundleShortVersionString': '1.0.8',
            'CFBundleVersion': '1.0.8',
            'NSHighResolutionCapable': 'True'
        }
    )
else:
    icon_file = 'src/assets/logo.ico'
    if not os.path.exists(icon_file):
        icon_file = None
        
    version_file = 'file_version_info.txt'
    if not os.path.exists(version_file):
        version_file = None
        
    exe = EXE(
        pyz,
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
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file,
        version=version_file,
        uac_admin=False,
    )

print("Build completata con successo!") 