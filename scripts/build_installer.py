#!/usr/bin/env python3
"""
Ink2TeX Installer Build Script
Creates a Windows installer using Inno Setup
"""

import sys
import subprocess
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

def find_inno_setup():
    """Find Inno Setup compiler executable"""
    possible_paths = [
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files (x86)/Inno Setup 5/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 5/ISCC.exe")
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def main():
    try:
        PROJECT_ROOT = find_project_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    
    print("===================================================")
    print("          Ink2TeX Installer Build Script")
    print("===================================================")
    print()
    
    # Check if the executable exists
    STANDALONE_EXE = PROJECT_ROOT / "dist" / "standalone" / "Ink2TeX.exe"
    if not STANDALONE_EXE.exists():
        print("ERROR: Executable not found!")
        print(f"Expected: {STANDALONE_EXE}")
        print("Please run: python build_wrapper.py exe")
        print("Or run full build: python build_wrapper.py full")
        return 1
    
    print(f"✓ Found executable: {STANDALONE_EXE}")
    
    # Check if Inno Setup is installed
    print()
    print("[1/3] Checking for Inno Setup...")
    inno_path = find_inno_setup()
    
    if not inno_path:
        print("ERROR: Inno Setup not found!")
        print()
        print("Please install Inno Setup from: https://jrsoftware.org/isinfo.php")
        print("Then run this script again.")
        return 1
    
    print(f"✓ Found Inno Setup at: {inno_path}")
    
    # Create installer output directory
    print()
    print("[2/3] Creating installer output directory...")
    INSTALLER_OUTPUT_DIR = PROJECT_ROOT / "dist" / "installer"
    INSTALLER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Output directory: {INSTALLER_OUTPUT_DIR}")
    
    # Build installer
    print()
    print("[3/3] Building installer...")
    
    INSTALLER_SCRIPT = PROJECT_ROOT / "installer" / "installer.iss"
    if not INSTALLER_SCRIPT.exists():
        print(f"ERROR: Installer script not found: {INSTALLER_SCRIPT}")
        return 1
    
    # Run Inno Setup compiler
    cmd = [str(inno_path), str(INSTALLER_SCRIPT)]
    
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, 
                              capture_output=True, text=True)
        
        print("✓ Installer build completed")
        
    except subprocess.CalledProcessError as e:
        print("ERROR: Installer build failed")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return 1
    
    # Verify installer was created
    print()
    INSTALLER_FILE = INSTALLER_OUTPUT_DIR / "Ink2TeX_Setup_v1.0.0.exe"
    
    if INSTALLER_FILE.exists():
        file_size = INSTALLER_FILE.stat().st_size
        print("===================================================")
        print("✅ Installer build successful!")
        print()
        print(f"📦 Installer created: {INSTALLER_FILE}")
        print(f"   File size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
        print()
        print("The installer includes:")
        print("  • Ink2TeX.exe - Main application")
        print("  • Configuration files (.api, .config, prompt.txt)")
        print("  • Automatic uninstaller")
        print("  • Start menu shortcuts")
        print("  • Optional desktop icon")
        print("  • Optional auto-start with Windows")
        print()
        print("Users can now run the installer for one-click installation!")
        print("===================================================")
        return 0
    else:
        print("ERROR: Installer file not found after build")
        print(f"Expected: {INSTALLER_FILE}")
        
        # List what was actually created
        if INSTALLER_OUTPUT_DIR.exists():
            print(f"Contents of {INSTALLER_OUTPUT_DIR}:")
            for item in INSTALLER_OUTPUT_DIR.iterdir():
                print(f"  {item}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
