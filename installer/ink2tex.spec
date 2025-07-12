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
    ('../.api', '.'),           # API key file
    ('../.config', '.'),        # Configuration file  
    ('../prompt.txt', '.'),     # AI prompt file
    ('../README.md', '.'),      # Documentation
]

# Ensure hidden imports match your choice of PyQt6
hidden_imports = [
    'google.generativeai',
    'PIL._tkinter_finder',
    'matplotlib.backends.backend_qtagg', # Use QtAgg for PyQt6
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'queue',
    'multiprocessing.pool',
    'multiprocessing.util',
]

# Exclude unnecessary modules to reduce file size
# Note: Being conservative with exclusions to avoid runtime errors
excludes = [
    'tkinter',  # GUI toolkit we don't use (we use PyQt6)
    'test',     # Python test modules
    'unittest', # Python unit testing
    'pydoc',    # Python documentation generator
    # Removed: pdb, doctest, difflib, inspect - these might be used by dependencies
]

a = Analysis(
    ['../app.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=['installer/hooks/runtime_hook_numpy.py'],
    hooksconfig={},
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

# Custom distribution directory
import shutil
import os

def move_to_standalone():
    """Move the built executable to dist/standalone directory"""
    source_dir = 'dist'
    target_dir = 'dist/standalone'
    
    # Create standalone directory
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Move executable
    exe_name = f'{app_name}.exe'
    if os.path.exists(os.path.join(source_dir, exe_name)):
        # Remove existing file if it exists
        target_file = os.path.join(target_dir, exe_name)
        if os.path.exists(target_file):
            os.remove(target_file)
        shutil.move(os.path.join(source_dir, exe_name), target_file)

# Execute the move after build
move_to_standalone()
