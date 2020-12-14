# -*- mode: python ; coding: utf-8 -*-

import platform

bins = []
if platform.system() == "Windows":
    # We need to include SDL2 and Glew DLLs
    from kivy_deps import sdl2, glew

    bins = [Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]

block_cipher = None


a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[("libs/graphical_interface/*.kv", "libs/graphical_interface")],
    hiddenimports=[],
    hookspath=[],
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
    *bins,
    [],
    name="main",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True
)
