# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

# Definisci il percorso base
base_path = os.path.abspath(os.getcwd())

# Funzione per raccogliere tutti i file in una directory
def collect_data_files(source_dir, dest_dir):
    files = []
    if os.path.exists(source_dir):
        for root, dirs, filenames in os.walk(source_dir):
            for filename in filenames:
                source_path = os.path.join(root, filename)
                dest_path = os.path.relpath(root, source_dir)
                files.append((source_path, os.path.join(dest_dir, dest_path)))
    return files

# Raccogli i file dalle directory
assets_files = collect_data_files(os.path.join(base_path, 'src', 'assets'), 'assets')
templates_files = collect_data_files(os.path.join(base_path, 'src', 'templates'), 'templates') if os.path.exists(os.path.join(base_path, 'src', 'templates')) else []
static_files = collect_data_files(os.path.join(base_path, 'src', 'static'), 'static') if os.path.exists(os.path.join(base_path, 'src', 'static')) else []

# Combina tutti i dati
all_datas = []
all_datas.extend(assets_files)
all_datas.extend(templates_files)
all_datas.extend(static_files)

# Aggiungi i file singoli
additional_files = [
    (os.path.join(base_path, 'LICENSE.md'), '.'),
    (os.path.join(base_path, 'README.md'), '.')
]

# Aggiungi solo i file che esistono
for file_path, dest in additional_files:
    if os.path.exists(file_path):
        all_datas.append((file_path, dest))

a = Analysis(
    [os.path.join(base_path, 'src', 'main.py')],
    pathex=[base_path],
    binaries=[],
    datas=all_datas,
    hiddenimports=[
        'pkg_resources',
        'sqlalchemy.sql.default_comparator',
        'win32timezone',
        'win32api',
        'win32security',
        'win32con',
        'win32event',
        'win32process'
    ],
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
    icon=os.path.join(base_path, 'src', 'assets', 'logo.ico'),
    version='file_version_info.txt',
    uac_admin=True
) 