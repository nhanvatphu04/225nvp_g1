# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('assets/models/*', 'assets/models'),
    ('assets/chessboard/*', 'assets/chessboard'),
    ('assets/background/*', 'assets/background'),
    ('assets/bgmusic/*', 'assets/bgmusic'),
    ('assets/fonts/*', 'assets/fonts'),
    ('assets/icon/*', 'assets/icon'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Chess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False để tắt console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon/icon.ico'  # Icon cho app
)