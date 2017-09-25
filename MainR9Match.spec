# -*- mode: python -*-

block_cipher = None


a = Analysis(['MainR9Match.py'],
             pathex=['C:\\Users\\T450S\\workspace\\PY_CYP\\R9Match_ULDL_JAKO'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='MainR9Match',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='E:\\3.pic\\ico\\3.ico')
