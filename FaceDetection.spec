# -*- mode: python ; coding: utf-8 -*-

from kivy.deps import sdl2, glew

block_cipher = None


a = Analysis(['C:\\Users\\User\\Desktop\\4 курс\\Семестр 2\\Прикладные задачи построения современных вычислительных систем\\Задание 2\\SPBU_FaceDetection\\main.py'],
             pathex=['C:\\Users\\User\\Desktop\\4 курс\\Семестр 2\\Прикладные задачи построения современных вычислительных систем\\Задание 2\\SPBU_FaceDetection'],
             binaries=[],
             datas=[('data', 'data'), ('src\\core\\viola_jones\\*.xml', 'src\\core\\viola_jones')],
             hiddenimports=[],
             hookspath=[],
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
          name='FaceDetection',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='FaceDetection')
