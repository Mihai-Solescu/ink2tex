#!/usr/bin/env python3
"""
Ink2TeX Clean Script
Removes build artifacts and cache directories
"""

import sys
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

def main():
    try:
        PROJECT_ROOT = find_project_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    
    print("===================================================")
    print("          Ink2TeX Clean Script")
    print("===================================================")
    print()
    
    cleaned_items = []
    
    # Remove dist directory
    DIST_DIR = PROJECT_ROOT / "dist"
    if DIST_DIR.exists():
        print(f"Removing: {DIST_DIR}")
        shutil.rmtree(DIST_DIR)
        cleaned_items.append("dist/ directory")
    
    # Remove build directory
    BUILD_DIR = PROJECT_ROOT / "build"
    if BUILD_DIR.exists():
        print(f"Removing: {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR)
        cleaned_items.append("build/ directory")
    
    # Remove __pycache__ directories
    pycache_dirs = list(PROJECT_ROOT.rglob("__pycache__"))
    for pycache in pycache_dirs:
        if pycache.is_dir():
            print(f"Removing: {pycache}")
            shutil.rmtree(pycache)
            cleaned_items.append(f"__pycache__ ({pycache.parent.name})")
    
    # Remove .pyc files
    pyc_files = list(PROJECT_ROOT.rglob("*.pyc"))
    for pyc_file in pyc_files:
        print(f"Removing: {pyc_file}")
        pyc_file.unlink()
        cleaned_items.append(f"{pyc_file.name}")
    
    # Remove .spec files from PyInstaller
    spec_files = list(PROJECT_ROOT.glob("*.spec"))
    for spec_file in spec_files:
        print(f"Removing: {spec_file}")
        spec_file.unlink()
        cleaned_items.append(f"{spec_file.name}")
    
    # Remove temporary files
    temp_patterns = ["temp_*.png", "*.tmp", "*.temp"]
    for pattern in temp_patterns:
        temp_files = list(PROJECT_ROOT.rglob(pattern))
        for temp_file in temp_files:
            print(f"Removing: {temp_file}")
            temp_file.unlink()
            cleaned_items.append(f"{temp_file.name}")
    
    print()
    print("===================================================")
    print("               Clean Results")
    print("===================================================")
    
    if cleaned_items:
        print(f"✅ Cleaned {len(cleaned_items)} items:")
        for item in cleaned_items:
            print(f"   • {item}")
    else:
        print("✓ No build artifacts found - already clean!")
    
    print()
    print("🧹 Clean completed successfully!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
