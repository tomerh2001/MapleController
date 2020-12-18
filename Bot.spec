# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['bot.py'],
             pathex=['C:\\Users\\Tomer\\Desktop\\Projects\\Practice\\Python\\Maplestory\\AFK Bot'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['hook-data.py'],
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
          name='bot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
