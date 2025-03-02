# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/assets/*', 'assets/'),
        ('src/templates/*', 'templates/'),
        ('src/static/*', 'static/'),
        ('LICENSE.md', '.'),
        ('README.md', '.')
    ],
    hiddenimports=[
        'pkg_resources',
        'sqlalchemy.sql.default_comparator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    icon='src/assets/icon.icns'
)

app = BUNDLE(
    exe,
    name='Hemodos.app',
    icon='src/assets/icon.icns',
    bundle_identifier='com.emmanuele.hemodos',
    info_plist={
        'CFBundleShortVersionString': '1.0.9',
        'CFBundleVersion': '1.0.9',
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'NSRequiresAquaSystemAppearance': 'False',
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
        }
    }
) 