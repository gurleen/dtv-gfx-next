# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['app.py'],
             pathex=[],
             binaries=[],
             datas=[('static/', 'static/'), ('CONFIG', '.')],
             hiddenimports=['engineio.async_drivers.aiohttp', 'engineio.async_aiohttp'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='DragonsTV Graphics',
          icon='./static/favicon.ico',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
