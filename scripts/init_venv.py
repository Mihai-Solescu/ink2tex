#!/usr/bin/env python3
"""
Ink2TeX Virtual Environment Initialization Script
Creates and configures .venv with build dependencies
"""

import sys
import subprocess
import shutil
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
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, 
                              capture_output=False, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False

def main():
    PROJECT_ROOT = find_project_root()
    VENV_DIR = PROJECT_ROOT / ".venv"
    REQUIREMENTS_FILE = PROJECT_ROOT / "installer" / "requirements-build.txt"
    
    print("===============================================")
    print("Ink2TeX Virtual Environment Setup")
    print("===============================================")
    print()
    
    # Check if requirements file exists
    if not REQUIREMENTS_FILE.exists():
        print(f"ERROR: {REQUIREMENTS_FILE} not found!")
        print("This script must be run from the project root directory.")
        return 1
    
    # Check if .venv already exists
    if VENV_DIR.exists():
        print("Virtual environment .venv already exists.")
        response = input("Do you want to recreate it? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping virtual environment creation.")
        else:
            print()
            print("Removing existing .venv...")
            try:
                shutil.rmtree(VENV_DIR)
            except Exception as e:
                print(f"WARNING: Could not fully remove .venv: {e}")
                print("Please close any applications using the virtual environment and try again.")
                return 1
    
    if not VENV_DIR.exists():
        print("Creating virtual environment .venv...")
        if not run_command(f'"{sys.executable}" -m venv "{VENV_DIR}"', cwd=PROJECT_ROOT):
            print("ERROR: Failed to create virtual environment.")
            print("Make sure Python is installed and accessible.")
            return 1
    
    # Determine the activation script path
    if sys.platform == "win32":
        activate_script = VENV_DIR / "Scripts" / "activate.bat"
        python_exe = VENV_DIR / "Scripts" / "python.exe"
    else:
        activate_script = VENV_DIR / "bin" / "activate"
        python_exe = VENV_DIR / "bin" / "python"
    
    if not python_exe.exists():
        print("ERROR: Failed to create virtual environment properly.")
        return 1
    
    print()
    print("Activating virtual environment...")
    
    print()
    print("Upgrading pip...")
    if not run_command(f'"{python_exe}" -m pip install --upgrade pip', cwd=PROJECT_ROOT, check=False):
        print("WARNING: Failed to upgrade pip, continuing anyway...")
    
    print()
    print(f"Installing build dependencies from {REQUIREMENTS_FILE.name}...")
    if not run_command(f'"{python_exe}" -m pip install -r "{REQUIREMENTS_FILE}"', cwd=PROJECT_ROOT):
        print("ERROR: Failed to install dependencies.")
        print(f"Check that {REQUIREMENTS_FILE} exists and is valid.")
        return 1
    
    print()
    print("Installing project in development mode...")
    if not run_command(f'"{python_exe}" -m pip install -e .', cwd=PROJECT_ROOT):
        print("ERROR: Failed to install project in development mode.")
        return 1
    
    print()
    print("===============================================")
    print("Virtual Environment Setup Complete!")
    print("===============================================")
    print()
    print("The .venv virtual environment has been created and configured with:")
    print(f"- All build dependencies from {REQUIREMENTS_FILE.name}")
    print("- The ink2tex project installed in development mode")
    print()
    print("To activate the environment manually:")
    if sys.platform == "win32":
        print("  .venv\\Scripts\\activate")
    else:
        print("  source .venv/bin/activate")
    print()
    print("To deactivate:")
    print("  deactivate")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
