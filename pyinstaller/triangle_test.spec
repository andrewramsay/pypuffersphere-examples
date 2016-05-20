# -*- mode: python -*-

block_cipher = None

# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Collect-Data-Files
def Datafiles(*filenames, **kw):
    import os

    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(datafile(filename, strip_path=strip_path) for filename in filenames if os.path.isfile(filename))

extradatafiles = Datafiles('images/leaf.png', strip_path=False)

a = Analysis(['..\\triangle_test.py'],
             pathex=[],
             binaries=None,
             datas=None,
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
          exclude_binaries=True,
          name='triangle_test',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               extradatafiles,
               strip=False,
               upx=True,
               name='triangle_test')
