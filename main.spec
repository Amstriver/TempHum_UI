# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py', 'SerialSetting.py', 'SerialUi.py', 'C:\\ProgramData\\anaconda3\\envs\\ulov5\\Lib\\csv.py'],
    pathex=['C:\\ProgramData\\anaconda3\\envs\\ulov5\\Lib\\site-packages'],
    binaries=[],
    datas=[("C:\\Users\\admin\\Desktop\\TempHum_UI\\icon", "icon")],
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
    name='温湿度监测平台',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon\icon.ico',  # 添加图标路径
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
