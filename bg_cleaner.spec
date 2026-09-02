# -*- mode: python ; coding: utf-8 -*-
import os, sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect ALL submodules for every package rembg needs
hidden = (
    collect_submodules("rembg") +
    collect_submodules("onnxruntime") +
    collect_submodules("pymatting") +
    collect_submodules("scipy") +
    collect_submodules("skimage") +
    collect_submodules("numpy") +
    collect_submodules("PIL") +
    collect_submodules("imageio") +
    collect_submodules("networkx") +
    ["encodings", "encodings.utf_8", "encodings.ascii", "encodings.latin_1"]
)

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
    console=True,
    icon=None,
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
