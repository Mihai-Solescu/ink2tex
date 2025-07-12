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
    return True

def verify_build(PROJECT_ROOT):
    """Verify that the build was successful"""
    print()
    print("[5/6] Verifying build...")
    
    STANDALONE_DIR = PROJECT_ROOT / "dist" / "standalone"
    EXE_FILE = STANDALONE_DIR / "Ink2TeX.exe"
    
    if EXE_FILE.exists():
        file_size = EXE_FILE.stat().st_size
        print("✓ Build successful!")
        print(f"✓ Executable created: {EXE_FILE}")
        print(f"  File size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
        print()
        print(f"You can now run: {EXE_FILE}")
        print("Or create an installer using: python build_wrapper.py installer")
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
