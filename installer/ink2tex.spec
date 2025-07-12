# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Ink2TeX
Creates a portable executable with all dependencies bundled
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_dynamic_libs
#from PyInstaller.utils.hooks import collect_data_files

# Build configuration
block_cipher = None
app_name = 'Ink2TeX'
version = '1.0.0'

# Collect all data files that need to be included
data_files = [
    # Note: Config files (.api, .config, prompt.txt) are NOT bundled
    # They will be created externally for user customization
    ('../README.md', '.'),      # Documentation
    ('../src/ink2tex', 'src/ink2tex'),  # Include entire modular package
]

# Ensure hidden imports match your choice of PyQt6 and include all modular components
hidden_imports = [
    'numpy',
    'matplotlib',
    'PyQt6.sip',
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
    'psutil',  # Required for single instance management
    'pyperclip',  # Clipboard operations
    'atexit',  # Exit handlers
    'winreg',  # Windows registry access
    # Include all modular components
    'src.ink2tex',
    'src.ink2tex.app',
    'src.ink2tex.core',
    'src.ink2tex.core.config',
    'src.ink2tex.core.startup',
    'src.ink2tex.core.hotkey',
    'src.ink2tex.core.api',
    'src.ink2tex.core.single_instance',  # Single instance management
    'src.ink2tex.ui',
    'src.ink2tex.ui.overlay',
    'src.ink2tex.ui.preview',
    'src.ink2tex.ui.settings',
]

# Exclude unnecessary modules to reduce file size
# Note: Being conservative with exclusions to avoid runtime errors
excludes = [
    'tkinter',  # GUI toolkit we don't use (we use PyQt6)
    'test',     # Python test modules
    'unittest', # Python unit testing
    'pydoc',    # Python documentation generator
]

a = Analysis(
    ['../src/ink2tex/main.py'],  # Paths relative to installer directory
    pathex=['../src'],  # Paths where the modules are
    binaries=collect_dynamic_libs('numpy'),
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=['hooks/runtime_hook_numpy.py'],  # Relative to installer directory
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
    icon='../assets/icon.ico' if Path('../assets/icon.ico').exists() else None,
    version='version_info.txt' if Path('version_info.txt').exists() else None,
)

# Note: The executable will be created in installer/dist/ and then moved by the build script
