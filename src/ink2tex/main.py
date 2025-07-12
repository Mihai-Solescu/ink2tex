#!/usr/bin/env python3
"""
Ink2TeX - Handwritten Math to LaTeX Converter
Main application entry point.

This is the ONLY file that should contain an if __name__ == "__main__" block
and the ONLY place where multiprocessing setup should occur.
"""

import multiprocessing
import sys
from pathlib import Path

# Add the src directory to Python path if not already there
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Check for single instance before importing heavy modules
from ink2tex.core.single_instance import check_single_instance
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def main():
    """Main entry point for the Ink2TeX application."""
    # Import here to avoid loading heavy dependencies during multiprocessing setup
    from ink2tex.app import Ink2TeXSystemTrayApp
    from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMessageBox
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setQuitOnLastWindowClosed(False)  # Keep running when overlay closes
    app.setApplicationName("Ink2TeX")
    app.setApplicationVersion("1.0")
    app.setApplicationDisplayName("Ink2TeX - Handwritten Math to LaTeX")
    app.setOrganizationName("Ink2TeX")
    
    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray Error", 
                           "System tray is not available on this system.\n"
                           "Ink2TeX requires system tray support to run in the background.")
        return 1
    
    try:
        # Create the system tray application
        tray_app = Ink2TeXSystemTrayApp()
        
        # The app is now running in the background with system tray
        print("🚀 Ink2TeX system tray application started!")
        print("   - Right-click the tray icon for options")
        print("   - Press Ctrl+Shift+I anywhere to open overlay")
        print("   - Double-click tray icon to open overlay")
        
        return app.exec()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        QMessageBox.critical(None, "Application Error", 
                           f"Failed to start Ink2TeX: {str(e)}")
        return 1


if __name__ == "__main__":
    # CRITICAL: These lines MUST come first to prevent PyInstaller issues
    multiprocessing.freeze_support()
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Already set
    
    # Check single instance BEFORE creating QApplication
    print("🔒 Checking for existing Ink2TeX instances...")
    instance_manager = check_single_instance("Ink2TeX")
    
    # Run the application
    try:
        exit_code = main()
        instance_manager.release_lock()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Application error: {e}")
        instance_manager.release_lock()
        sys.exit(1)
