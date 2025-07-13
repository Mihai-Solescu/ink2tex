#
# Copyright July 2025 Mihai Solescu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Main application class for Ink2TeX.
Manages the system tray application and coordinates all components.
"""

import os
from typing import Optional

# Import PyQt6 components locally to prevent early loading
from PyQt6.QtWidgets import (QWidget, QSystemTrayIcon, QMenu, QMessageBox, 
                            QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor, QPen, QIcon, QFont, QAction

# Import our modular components
from ink2tex.core.config import ConfigReader
from ink2tex.core.startup import WindowsStartupManager
from ink2tex.core.hotkey import GlobalHotkeyManager
from ink2tex.core.api import GeminiAPIManager


class Ink2TeXSystemTrayApp(QWidget):
    """System tray application for Ink2TeX"""
    
    def __init__(self):
        """Initialize the system tray application"""
        super().__init__()
        
        # Initialize managers
        self.api_manager = GeminiAPIManager()
        self.hotkey_manager: Optional[GlobalHotkeyManager] = None
        
        # UI state
        self.overlay = None
        self.settings_window = None
        
        # Initialize the application
        self.init_app()
        self.setup_system_tray()
        self.setup_gemini_api()
        self.setup_global_hotkeys()
        self.apply_startup_settings()
        
    def init_app(self):
        """Initialize the application without showing a window"""
        # Hide the main window - we only use system tray
        self.hide()
        
    def setup_gemini_api(self):
        """Setup Gemini API using config file"""
        try:
            print("Debug: Starting Gemini API setup...")
            # Read API key
            api_key = ConfigReader.read_api_key_from_config()
            print(f"Debug: API key loaded: {api_key[:10]}..." if api_key else "Debug: No API key loaded")
            
            # Add a timeout mechanism by using QTimer for non-blocking configuration
            print("Debug: Attempting API configuration...")
            success = self.api_manager.configure_api(api_key)
            print(f"Debug: API configuration success: {success}")
            
            if not success:
                print("Debug: API configuration failed - app will continue with limited functionality")
                self.show_message("API Configuration", 
                                "Gemini API configuration failed. You can still draw and manually edit LaTeX. Use the Retry button in the overlay to try again.", 
                                QSystemTrayIcon.MessageIcon.Warning)
            else:
                print("Debug: API configuration successful!")
            
        except Exception as e:
            print(f"❌ API setup failed: {str(e)}")
            # Don't show critical error - let app continue
            self.show_message("API Configuration", 
                            f"Gemini API setup encountered an error: {str(e)}\\n\\n"
                            "You can still draw and manually edit LaTeX. Check your .api file and use the Retry button.", 
                            QSystemTrayIcon.MessageIcon.Warning)
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                            "System tray is not available on this system.")
            return
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon
        self.create_tray_icon()
        
        # Create context menu
        self.create_tray_menu()
        
        # Set up tray icon
        self.tray_icon.setIcon(self.icon)
        self.tray_icon.setToolTip("Ink2TeX - Handwritten Math to LaTeX Converter\\nCtrl+Shift+I to open overlay")
        
        # Connect double-click to open overlay
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Show startup notification
        self.show_message("Ink2TeX Started", 
                        "Ink2TeX is running in the background.\\nPress Ctrl+Shift+I to open the overlay,\\nor right-click the tray icon for options.",
                        QSystemTrayIcon.MessageIcon.Information)
    
    def create_tray_icon(self):
        """Create the tray icon using the application icon"""
        from ink2tex.core.resources import get_application_icon
        
        # Use the application icon, which has fallback support
        self.icon = get_application_icon()
    
    def create_tray_menu(self):
        """Create the system tray context menu"""
        self.tray_menu = QMenu()
        
        # Open Overlay action
        open_action = QAction("🖊️ Open Overlay", self)
        open_action.triggered.connect(self.open_overlay)
        self.tray_menu.addAction(open_action)
        
        # Separator
        self.tray_menu.addSeparator()
        
        # About action
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        self.tray_menu.addAction(about_action)
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show_settings)
        self.tray_menu.addAction(settings_action)
        
        # Status action
        status_action = QAction("ℹ️ Status", self)
        status_action.triggered.connect(self.show_status)
        self.tray_menu.addAction(status_action)
        
        # Separator
        self.tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("❌ Exit", self)
        exit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(exit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(self.tray_menu)
    
    def setup_global_hotkeys(self):
        """Setup global hotkey support"""
        self.hotkey_manager = GlobalHotkeyManager(self)
        
        if self.hotkey_manager.start_listening():
            print("✓ Global hotkey (Ctrl+Shift+I) enabled")
        else:
            print("⚠️ Global hotkey setup failed")
    
    def apply_startup_settings(self):
        """Apply startup settings from configuration"""
        try:
            # Check if auto-start is enabled in config
            auto_start_config = ConfigReader.read_config_value('AUTO_START_WITH_WINDOWS', default='false').lower() == 'true'
            auto_start_registry = WindowsStartupManager.is_startup_enabled()
            
            # Sync config with registry (registry is authoritative)
            if auto_start_config != auto_start_registry:
                print(f"Syncing startup setting: config={auto_start_config}, registry={auto_start_registry}")
                if auto_start_registry:
                    ConfigReader.update_config_setting('AUTO_START_WITH_WINDOWS', 'true')
                else:
                    ConfigReader.update_config_setting('AUTO_START_WITH_WINDOWS', 'false')
            
        except Exception as e:
            print(f"Error applying startup settings: {e}")
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_overlay()
    
    def open_overlay(self):
        """Open the transparent overlay"""
        try:
            # Close existing overlay if open
            if self.overlay:
                self.overlay.close()
                self.overlay = None
            
            # Use QTimer to defer overlay creation to avoid threading issues
            QTimer.singleShot(50, self._create_overlay)
            
        except Exception as e:
            print(f"Error opening overlay: {str(e)}")
            self.show_message("Error", f"Failed to open overlay: {str(e)}", 
                            QSystemTrayIcon.MessageIcon.Critical)
    
    def _create_overlay(self):
        """Create and show the overlay (called from main thread)"""
        try:
            # Import overlay locally to prevent early PyQt6 loading
            from ink2tex.ui.overlay import TransparentOverlay
            
            # Create overlay
            self.overlay = TransparentOverlay(self)
            
            # Show overlay with proper threading
            self.overlay.show()
            self.overlay.raise_()
            self.overlay.activateWindow()
            
            # Focus management
            self.overlay.setFocus(Qt.FocusReason.OtherFocusReason)
            
            # Use a timer to ensure focus is set after the window is fully shown
            QTimer.singleShot(100, lambda: self.overlay.setFocus(Qt.FocusReason.OtherFocusReason))
            
            print("🖊️ Transparent overlay opened")
            
        except Exception as e:
            print(f"Error creating overlay: {str(e)}")
            self.show_message("Error", f"Failed to create overlay: {str(e)}", 
                            QSystemTrayIcon.MessageIcon.Critical)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h3>Ink2TeX</h3>
<p><b>Version:</b> 1.0</p>
<p><b>Description:</b> Handwritten Math to LaTeX Converter</p>
<p><b>Date:</b> July 12, 2025</p>

<h4>Features:</h4>
<ul>
<li>🖊️ Transparent system overlay</li>
<li>🤖 AI-powered conversion using Google Gemini</li>
<li>👁️ Live LaTeX preview</li>
<li>📋 Clipboard integration</li>
<li>⌨️ Global hotkey (Ctrl+Shift+I)</li>
</ul>

<h4>Usage:</h4>
<p>Press <b>Ctrl+Shift+I</b> anywhere to open the overlay,<br>
draw your math equation, and press <b>Enter</b> to convert.</p>
"""
        
        msg = QMessageBox()
        msg.setWindowTitle("About Ink2TeX")
        msg.setText(about_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def show_settings(self):
        """Show settings window"""
        try:
            # Close existing settings window if open
            if self.settings_window:
                self.settings_window.close()
                self.settings_window = None
            
            # Import settings locally to prevent early PyQt6 loading
            from ink2tex.ui.settings import SettingsWindow
            
            # Create and show settings window
            self.settings_window = SettingsWindow(self)
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            
            # Ensure window is brought to front
            QTimer.singleShot(100, lambda: self.settings_window.activateWindow())
            
            print("⚙️ Settings window opened")
            
        except Exception as e:
            print(f"Error showing settings: {e}")
            self.show_message("Error", f"Failed to open settings: {str(e)}", 
                            QSystemTrayIcon.MessageIcon.Critical)
    
    def show_status(self):
        """Show application status"""
        hotkey_status = "✓ Enabled" if (self.hotkey_manager and self.hotkey_manager.enabled) else "❌ Disabled"
        api_status = "✓ Configured" if self.api_manager.is_configured() else "❌ Not configured"
        
        status_text = f"""
<h3>Ink2TeX Status</h3>

<p><b>Global Hotkey:</b> {hotkey_status}</p>
<p><b>Gemini API:</b> {api_status}</p>
<p><b>System Tray:</b> ✓ Active</p>

<h4>Controls:</h4>
<ul>
<li><b>Ctrl+Shift+I:</b> Open overlay (global)</li>
<li><b>Double-click tray icon:</b> Open overlay</li>
<li><b>Right-click tray icon:</b> Show menu</li>
</ul>

<h4>Overlay Controls:</h4>
<ul>
<li><b>Enter:</b> Generate LaTeX</li>
<li><b>Esc:</b> Close and copy to clipboard</li>
<li><b>Ctrl+Z:</b> Undo last stroke</li>
<li><b>Q:</b> Quit entire application</li>
</ul>
"""
        
        msg = QMessageBox()
        msg.setWindowTitle("Ink2TeX Status")
        msg.setText(status_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show system tray notification
        
        Args:
            title: Notification title
            message: Notification message
            icon: Notification icon type
        """
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, 3000)  # 3 seconds
    
    def quit_application(self):
        """Quit the application"""
        # Stop global hotkeys
        if self.hotkey_manager:
            self.hotkey_manager.stop_listening()
        
        # Close overlay if open
        if self.overlay:
            self.overlay.close()
        
        # Hide tray icon
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        
        print("Ink2TeX shutting down...")
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle close event - minimize to tray instead of closing"""
        # When user tries to close, just hide to tray
        event.ignore()
        self.hide()
        
        if self.tray_icon:
            self.show_message("Ink2TeX", 
                            "Application is still running in the system tray.\\nRight-click the tray icon to exit.",
                            QSystemTrayIcon.MessageIcon.Information)
