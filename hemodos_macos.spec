# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Raccogli tutti i file dalla directory assets
assets_dir = os.path.join('src', 'assets')
assets_files = []
for file in os.listdir(assets_dir):
    if file.endswith(('.png', '.icns')):
        source = os.path.join(assets_dir, file)
        dest = os.path.join('assets', file)
        assets_files.append((source, dest))

a = Analysis(['src/main.py'],
             pathex=[],
             binaries=[],
             datas=[
                *assets_files,  # Espandi la lista dei file assets
                ('src/core', 'core'),      # Core modules
                ('src/gui', 'gui'),        # GUI modules
                ('config.json', '.'),      # File di configurazione
                ('LICENSE.md', '.'),
                ('README.md', '.'),
             ],
             hiddenimports=[
                'PyQt5',
                'PyQt5.QtCore',
                'PyQt5.QtGui',
                'PyQt5.QtWidgets',
                'cryptography'
             ],
             hookspath=[],
             hooksconfig={},
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
          entitlements_file=None)

app = BUNDLE(exe,
            a.binaries,
            a.zipfiles,
            a.datas,
            name='Hemodos.app',
            icon='src/assets/hemodos.icns',  # Percorso corretto dell'icona
            bundle_identifier='com.hemodos.app',
            info_plist={
                'CFBundleName': 'Hemodos',
                'CFBundleDisplayName': 'Hemodos',
                'CFBundleGetInfoString': "Hemodos",
                'CFBundleIdentifier': "com.hemodos.app",
                'CFBundleVersion': "1.0.9",
                'CFBundleShortVersionString': "1.0.9",
                'NSHighResolutionCapable': 'True',
                'LSMinimumSystemVersion': '10.13.0',
            }) 