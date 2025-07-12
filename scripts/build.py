#!/usr/bin/env python3
"""
Ink2TeX Master Build Script
Builds both executable and installer
"""

import sys
import subprocess
from pathlib import Path

def find_project_root():
    """Find the project root directory by looking for pyproject.toml"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")

def run_script(script_path, cwd=None):
    """Run a Python script and return success status"""
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script failed with exit code: {e.returncode}")
        return False

def main():
    try:
        PROJECT_ROOT = find_project_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    
    SCRIPTS_DIR = PROJECT_ROOT / "scripts"
    
    print("===================================================")
    print("           Ink2TeX Master Build Script")
    print("===================================================")
    print()
    
    # Step 1: Build executable
    print("[1/2] Building executable...")
    build_exe_script = SCRIPTS_DIR / "build_exe.py"
    if not build_exe_script.exists():
        print(f"ERROR: {build_exe_script} not found")
        return 1
    
    if not run_script(build_exe_script, cwd=PROJECT_ROOT):
        print("ERROR: Executable build failed")
        return 1
    
    print()
    
    # Step 2: Build installer
    print("[2/2] Building installer...")
    build_installer_script = SCRIPTS_DIR / "build_installer.py"
    if not build_installer_script.exists():
        print(f"ERROR: {build_installer_script} not found")
        return 1
    
    if not run_script(build_installer_script, cwd=PROJECT_ROOT):
        print("ERROR: Installer build failed")
        return 1
    
    print()
    print("===================================================")
    print("✅ Complete build successful!")
    print()
    
    # Show output locations
    STANDALONE_EXE = PROJECT_ROOT / "dist" / "standalone" / "Ink2TeX.exe"
    INSTALLER_EXE = PROJECT_ROOT / "dist" / "installer" / "Ink2TeX_Setup_v1.0.0.exe"
    
    if STANDALONE_EXE.exists():
        size_mb = STANDALONE_EXE.stat().st_size / (1024 * 1024)
        print(f"Executable: {STANDALONE_EXE} ({size_mb:.1f} MB)")
    
    if INSTALLER_EXE.exists():
        size_mb = INSTALLER_EXE.stat().st_size / (1024 * 1024)
        print(f"Installer: {INSTALLER_EXE} ({size_mb:.1f} MB)")
    
    print("===================================================")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
