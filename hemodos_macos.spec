# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['src/main.py'],
             pathex=[],
             binaries=[],
             datas=[
                ('src/assets', 'assets'),  # Assets directory
                ('src/gui/themes', 'gui/themes'),  # Temi
                ('src/templates', 'templates'),  # Template files
                ('LICENSE', '.'),
                ('README.md', '.'),
             ],
             hiddenimports=[],
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
                'CFBundleVersion': "1.0.0",
                'CFBundleShortVersionString': "1.0.0",
                'NSHighResolutionCapable': 'True',
                'LSMinimumSystemVersion': '10.13.0',
            }) 