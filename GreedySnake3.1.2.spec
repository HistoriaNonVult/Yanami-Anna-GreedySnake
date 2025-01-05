# snake.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],  # 只包含必要的资源文件
    hiddenimports=['pygame'],
    excludes=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'tkinter.test',
        'lib2to3',
        'win32com',
        'unittest',
        'pydoc',
        'doctest',
        'test',
        'xml',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GreedySnake',
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
)