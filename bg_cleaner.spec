# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for BG Cleaner.
Build with:  pyinstaller bg_cleaner.spec
"""
import os, sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all rembg + onnxruntime submodules so the exe can find them
hidden = collect_submodules("rembg") + collect_submodules("onnxruntime") + collect_submodules("pymatting")

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("app/templates", "app/templates"),
        ("app/static",    "app/static"),
    ],
    hiddenimports=hidden,
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
    name="BG Cleaner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,          # show console so user sees "Running at http://localhost:5000"
    icon=None,             # add an .ico here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="BG Cleaner",
)
