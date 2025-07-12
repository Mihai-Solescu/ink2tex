# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Ink2TeX
Creates a standalone executable with all dependencies bundled
"""

import sys
from pathlib import Path

# Build configuration
block_cipher = None
app_name = 'Ink2TeX'
version = '1.0.0'

# Collect all data files that need to be included
data_files = [
    ('.api', '.'),           # API key file
    ('.config', '.'),        # Configuration file  
    ('prompt.txt', '.'),     # AI prompt file
    ('README.md', '.'),      # Documentation
]

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'google.generativeai',
    'PIL._tkinter_finder',
    'matplotlib.backends.backend_qt5agg',
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'queue',
]

# Exclude unnecessary modules to reduce file size
excludes = [
    'tkinter',
    'test',
    'unittest',
    'pdb',
    'doctest',
    'difflib',
    'inspect',
    'calendar',
    'pydoc',
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
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
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if Path('assets/icon.ico').exists() else None,
    version='version_info.txt' if Path('version_info.txt').exists() else None,
)
