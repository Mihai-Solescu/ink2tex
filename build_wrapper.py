#!/usr/bin/env python3
"""
Ink2TeX Build Wrapper
Convenience script to run builds from the project root
Delegates to other build scripts in the scripts/ folder
"""

import sys
import subprocess
from pathlib import Path
import argparse

def find_project_root():
    """Find the project root directory by looking for pyproject.toml"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")

def main():
    PROJECT_ROOT = find_project_root()
    SCRIPTS_DIR = PROJECT_ROOT / "scripts"
    
    # Check if scripts directory exists
    if not SCRIPTS_DIR.exists():
        print(f"ERROR: {SCRIPTS_DIR} directory not found!")
        print("This script must be run from the project root.")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Ink2TeX Build Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  --full      - Full build (executable + installer) [DEFAULT]
  --exe       - Executable only (faster)
  --installer - Installer only
  --test      - Test deployment
  --init      - Initialize virtual environment (.venv)
  --startup   - Test application startup
  --clean     - Clean build artifacts
  --help      - Show this help

Examples:
  python build_wrapper.py           (runs full build)
  python build_wrapper.py --exe     (builds executable only)
  python build_wrapper.py --init    (sets up virtual environment)
  python build_wrapper.py --startup (tests app startup)
        """
    )
    
    parser.add_argument('--full', action='store_true', help='Full build (executable + installer) [DEFAULT]')
    parser.add_argument('--exe', action='store_true', help='Executable only (faster)')
    parser.add_argument('--installer', action='store_true', help='Installer only')
    parser.add_argument('--test', action='store_true', help='Test deployment')
    parser.add_argument('--init', action='store_true', help='Initialize virtual environment')
    parser.add_argument('--startup', action='store_true', help='Test application startup')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    
    args = parser.parse_args()
    
    # Determine which command to run
    command = None
    if args.full:
        command = 'full'
    elif args.exe:
        command = 'exe'
    elif args.installer:
        command = 'installer'
    elif args.test:
        command = 'test'
    elif args.init:
        command = 'init'
    elif args.startup:
        command = 'startup'
    elif args.clean:
        command = 'clean'
    else:
        # Default to full build if no arguments provided
        command = 'full'
    
    print("===============================================")
    print("Ink2TeX Build Wrapper")
    print("===============================================")
    print()
    
    if len(sys.argv) == 1:
        print("No command specified - using default: --full build")
        print()
        print("Available options:")
        print("  --full      - Full build (executable + installer) [DEFAULT]")
        print("  --exe       - Executable only (faster)")
        print("  --installer - Installer only")
        print("  --test      - Test deployment")
        print("  --init      - Initialize virtual environment (.venv)")
        print("  --startup   - Test application startup")
        print("  --clean     - Clean build artifacts")
        print("  --help      - Show this help")
        print()
        print("Usage: python build_wrapper.py [--option]")
        print("Running --full build in 3 seconds... (Ctrl+C to cancel)")
        
        # Give user a chance to cancel, but don't wait for input
        try:
            import time
            for i in range(3, 0, -1):
                print(f"\rStarting in {i}...", end="", flush=True)
                time.sleep(1)
            print("\rStarting --full build...   ")
        except KeyboardInterrupt:
            print("\nCancelled by user.")
            return 0
    
    # Map commands to scripts
    command_map = {
        'full': 'build.py',
        'exe': 'build_exe.py', 
        'installer': 'build_installer.py',
        'test': 'test_deployment.py',
        'init': 'init_venv.py',
        'startup': '../test_startup.py',  # Special case - in project root
        'clean': 'clean.py'
    }
    
    if command not in command_map:
        print(f"Invalid choice: \"{command}\"")
        print()
        print("Valid options: --full, --exe, --installer, --test, --init, --startup, --clean, --help")
        print("Usage: python build_wrapper.py [--full|--exe|--installer|--test|--init|--startup|--clean|--help]")
        sys.exit(1)
    
    script_name = command_map[command]
    
    # Handle special case for startup script (in project root)
    if command == 'startup':
        script_path = PROJECT_ROOT / 'test_startup.py'
    else:
        script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        print(f"ERROR: {script_path} not found!")
        sys.exit(1)
    
    print(f"Running --{command} build...")
    print()
    
    # Change to project root and run the script
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              cwd=PROJECT_ROOT, 
                              check=False)
        
        print()
        if len(sys.argv) > 1:
            print(f"Operation completed. Exit code: {result.returncode}")
        else:
            print("Operation completed.")

        return result.returncode
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error running script: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
