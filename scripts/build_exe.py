#!/usr/bin/env python3
"""
Ink2TeX Executable Build Script
Creates a standalone executable using PyInstaller
"""

import sys
import subprocess
import shutil
import os
from pathlib import Path

def find_project_root():
    """Find the project root directory by looking for pyproject.toml"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")

def run_command(cmd, cwd=None, check=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False

def check_and_setup_venv(PROJECT_ROOT):
    """Check if .venv exists and has required packages, initialize if needed"""
    print("[1/6] Checking and setting up virtual environment...")
    
    VENV_DIR = PROJECT_ROOT / ".venv"
    
    if sys.platform == "win32":
        python_exe = VENV_DIR / "Scripts" / "python.exe"
        activate_script = VENV_DIR / "Scripts" / "activate.bat"
    else:
        python_exe = VENV_DIR / "bin" / "python"
        activate_script = VENV_DIR / "bin" / "activate"
    
    venv_ready = False
    
    if python_exe.exists():
        print("✓ Virtual environment .venv found")
        
        # Check if PyInstaller is installed
        try:
            result = subprocess.run([str(python_exe), "-c", "import PyInstaller"], 
                                  capture_output=True, check=True)
            print("✓ Virtual environment appears ready")
            venv_ready = True
        except subprocess.CalledProcessError:
            print("⚠ Virtual environment exists but missing build dependencies")
    else:
        print("⚠ Virtual environment .venv not found")
    
    # Initialize .venv if not ready
    if not venv_ready:
        print()
        print("Initializing virtual environment with build dependencies...")
        
        init_script = PROJECT_ROOT / "scripts" / "init_venv.py"
        if not init_script.exists():
            print(f"ERROR: {init_script} not found")
            return None
        
        if not run_command(f'"{sys.executable}" "{init_script}"', cwd=PROJECT_ROOT):
            print("ERROR: Failed to initialize virtual environment")
            return None
    
    return python_exe

def clean_previous_builds(PROJECT_ROOT):
    """Clean previous build artifacts"""
    print()
    print("[2/6] Cleaning previous builds...")
    
    DIST_DIR = PROJECT_ROOT / "dist"
    BUILD_DIR = PROJECT_ROOT / "build"
    
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            print(f"Removing {directory}")
            shutil.rmtree(directory)
    
    print("✓ Previous builds cleaned")

def prepare_assets(PROJECT_ROOT):
    """Prepare application assets"""
    print()
    print("[3/6] Preparing application assets...")
    
    ASSETS_DIR = PROJECT_ROOT / "assets"
    ASSETS_DIR.mkdir(exist_ok=True)
    
    print("✓ Assets directory ready")

def build_executable(PROJECT_ROOT, python_exe):
    """Build executable with PyInstaller"""
    print()
    print("[4/6] Building executable with PyInstaller...")
    
    INSTALLER_DIR = PROJECT_ROOT / "installer"
    SPEC_FILE = INSTALLER_DIR / "ink2tex.spec"
    
    if not SPEC_FILE.exists():
        print(f"ERROR: {SPEC_FILE} not found")
        return False
    
    # Run PyInstaller from the installer directory
    cmd = f'"{python_exe}" -m PyInstaller "{SPEC_FILE.name}" --noconfirm --clean'
    
    print(f"Running: {cmd}")
    print(f"Working directory: {INSTALLER_DIR}")
    
    if not run_command(cmd, cwd=INSTALLER_DIR):
        print("ERROR: PyInstaller build failed")
        return False
    
    print("✓ PyInstaller build completed")
    
    # Move executable to the correct location
    move_executable_to_portable(PROJECT_ROOT)
    
    return True

def move_executable_to_portable(PROJECT_ROOT):
    """Move the built executable from installer/dist to PROJECT_ROOT/dist/portable"""
    print()
    print("[4.5/6] Moving executable to portable directory...")
    
    # PyInstaller creates the executable in installer/dist/
    INSTALLER_DIST = PROJECT_ROOT / "installer" / "dist"
    EXE_SOURCE = INSTALLER_DIST / "Ink2TeX.exe"
    
    # We want it in PROJECT_ROOT/dist/portable/
    PORTABLE_DIR = PROJECT_ROOT / "dist" / "portable"
    PORTABLE_DIR.mkdir(parents=True, exist_ok=True)
    EXE_TARGET = PORTABLE_DIR / "Ink2TeX.exe"
    
    if EXE_SOURCE.exists():
        # Remove existing target if it exists
        if EXE_TARGET.exists():
            EXE_TARGET.unlink()
        
        # Move the executable
        shutil.move(str(EXE_SOURCE), str(EXE_TARGET))
        print(f"✓ Moved executable from {EXE_SOURCE} to {EXE_TARGET}")
        
        # Clean up the installer/dist directory
        if INSTALLER_DIST.exists():
            shutil.rmtree(INSTALLER_DIST)
            print("✓ Cleaned up temporary build directory")
            
        # Create portable package structure
        create_portable_package(PROJECT_ROOT, PORTABLE_DIR)
    else:
        print(f"WARNING: Executable not found at expected location: {EXE_SOURCE}")
        
        # List what was actually created
        if INSTALLER_DIST.exists():
            print(f"Contents of {INSTALLER_DIST}:")
            for item in INSTALLER_DIST.rglob("*"):
                print(f"  {item}")
        else:
            print(f"ERROR: {INSTALLER_DIST} does not exist")

def create_portable_package(PROJECT_ROOT, PORTABLE_DIR):
    """Create a complete portable package with config templates"""
    print()
    print("[4.6/6] Creating portable package structure...")
    
    # Create config template files for portable version
    config_templates = {
        '.api': '''# Google Gemini API Key Configuration for Ink2TeX
# Get your free API key from: https://makersuite.google.com/app/apikey
# Replace 'your_api_key_here' with your actual API key

GOOGLE_API_KEY=your_api_key_here
''',
        '.config': '''# Ink2TeX Configuration File
# Application settings and preferences

# Auto-start with Windows (true/false)
AUTO_START=false

# Global hotkey for overlay (default: ctrl+shift+i)
HOTKEY=ctrl+shift+i

# AI prompt file location (relative to executable directory)
PROMPT_FILE=prompt.txt

# Application behavior settings
STARTUP_NOTIFICATION=true
TRAY_ICON_TOOLTIP=Ink2TeX - Math to LaTeX Converter
''',
        'prompt.txt': '''From the provided image, convert the handwritten mathematics into LaTeX. Follow these rules exactly:

1. Each line of handwritten text must be on its own new line in the output.
2. Enclose each separate line of LaTeX within single dollar signs ($).
3. Your entire response must consist ONLY of the resulting LaTeX code. Do not add any introductory text, explanations, or markdown formatting like ```latex.'''
    }
    
    # Create template config files
    for filename, content in config_templates.items():
        template_file = PORTABLE_DIR / filename
        template_file.write_text(content, encoding='utf-8')
        print(f"✓ Created config template: {template_file.name}")
    
    # Copy documentation
    readme_source = PROJECT_ROOT / "README.md"
    if readme_source.exists():
        readme_target = PORTABLE_DIR / "README.md"
        shutil.copy2(readme_source, readme_target)
        print(f"✓ Copied documentation: README.md")
    
    # Create setup script for easy configuration
    setup_script_content = '''@echo off
REM Quick setup script for Ink2TeX portable version
echo ======================================
echo      Ink2TeX Portable Setup
echo ======================================
echo.
echo This portable version needs a Google Gemini API key to work.
echo.
echo 1. Get a free API key from: https://makersuite.google.com/app/apikey
echo 2. Edit the .api file in this folder
echo 3. Replace 'your_api_key_here' with your actual API key
echo 4. Save the file and run Ink2TeX.exe
echo.
echo Configuration files in this folder:
echo   .api       - Your Google API key (EDIT THIS!)
echo   .config    - App settings (optional to edit)
echo   prompt.txt - AI behavior (optional to edit)
echo.
echo Press Enter to open the .api file for editing...
pause >nul
notepad.exe .api
echo.
echo Setup complete! You can now run Ink2TeX.exe
pause
'''
    
    setup_script = PORTABLE_DIR / "setup.bat"
    setup_script.write_text(setup_script_content, encoding='utf-8')
    print(f"✓ Created setup script: setup.bat")
    
    print("✓ Portable package structure created")
    print(f"  📁 Portable package location: {PORTABLE_DIR}")
    print(f"  📋 Users should run setup.bat for easy configuration")

def verify_build(PROJECT_ROOT):
    """Verify that the build was successful"""
    print()
    print("[5/6] Verifying build...")
    
    PORTABLE_DIR = PROJECT_ROOT / "dist" / "portable"
    EXE_FILE = PORTABLE_DIR / "Ink2TeX.exe"
    
    if EXE_FILE.exists():
        file_size = EXE_FILE.stat().st_size
        print("✓ Build successful!")
        print(f"✓ Executable created: {EXE_FILE}")
        print(f"  File size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
        
        # Verify portable package structure
        config_files = ['.api', '.config', 'prompt.txt', 'setup.bat', 'README.md']
        missing_files = []
        
        for config_file in config_files:
            if (PORTABLE_DIR / config_file).exists():
                print(f"✓ Config template: {config_file}")
            else:
                missing_files.append(config_file)
        
        if missing_files:
            print(f"⚠️  Missing config files: {', '.join(missing_files)}")
        
        print()
        print("📦 Portable Package Ready!")
        print(f"   Location: {PORTABLE_DIR}")
        print("   Users should:")
        print("   1. Run setup.bat for easy configuration")
        print("   2. Edit .api file with their Google Gemini API key")
        print("   3. Run Ink2TeX.exe")
        print()
        print("🚀 Next steps:")
        print("   - Test the executable: python build_wrapper.py --startup")
        print("   - Create installer: python build_wrapper.py --installer")
        return True
    else:
        print("ERROR: Build failed - executable not found")
        print(f"Expected: {EXE_FILE}")
        
        # List what was actually created
        dist_dir = PROJECT_ROOT / "dist"
        if dist_dir.exists():
            print(f"Contents of {dist_dir}:")
            for item in dist_dir.rglob("*"):
                if item.is_file():
                    print(f"  {item}")
        
        return False

def main():
    try:
        PROJECT_ROOT = find_project_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    
    print("===================================================")
    print("             Ink2TeX Build Script")
    print("===================================================")
    print()
    
    # Check if Python is available
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"Python version: {result.stdout.strip()}")
    except Exception:
        print("ERROR: Python is not installed or not in PATH")
        print("Please install Python 3.8+ and try again")
        return 1
    
    # Step 1: Check and setup virtual environment
    python_exe = check_and_setup_venv(PROJECT_ROOT)
    if not python_exe:
        return 1
    
    # Step 2: Clean previous builds
    clean_previous_builds(PROJECT_ROOT)
    
    # Step 3: Prepare assets
    prepare_assets(PROJECT_ROOT)
    
    # Step 4: Build executable
    if not build_executable(PROJECT_ROOT, python_exe):
        return 1
    
    # Step 5: Verify build
    if not verify_build(PROJECT_ROOT):
        return 1
    
    print()
    print("Build completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
