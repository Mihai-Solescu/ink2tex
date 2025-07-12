#!/usr/bin/env python3
"""
Optional dependency installer for Ink2TeX
This script installs the optional pynput package for global hotkey support.
"""

import subprocess
import sys

def install_pynput():
    """Install pynput for global hotkey support"""
    try:
        print("Installing pynput for global hotkey support...")
        print("This allows Ctrl+Shift+I to work from anywhere on your system.")
        
        # Install pynput
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
        
        print("✓ pynput installed successfully!")
        print("✓ Global hotkeys (Ctrl+Shift+I) are now available")
        print("\nRestart Ink2TeX to enable global hotkey support.")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pynput: {e}")
        print("You can still use Ink2TeX by double-clicking the tray icon")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main installation function"""
    print("=== Ink2TeX Optional Dependencies Installer ===")
    print()
    
    # Check if pynput is already installed
    try:
        import pynput
        print("✓ pynput is already installed - global hotkeys should work!")
        print("If hotkeys aren't working, try restarting Ink2TeX.")
        return
    except ImportError:
        pass
    
    print("pynput is not installed.")
    print("Without pynput, you can only open the overlay by:")
    print("  - Double-clicking the system tray icon")
    print("  - Right-clicking tray icon → 'Open Overlay'")
    print()
    print("With pynput, you can also use:")
    print("  - Global hotkey Ctrl+Shift+I from anywhere")
    print()
    
    response = input("Would you like to install pynput for global hotkey support? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        install_pynput()
    else:
        print("Skipping pynput installation.")
        print("You can install it later by running this script again.")

if __name__ == "__main__":
    main()
