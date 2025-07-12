"""
Settings window for Ink2TeX.
Provides UI for configuring application preferences including auto-startup.
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from ink2tex.core.startup import WindowsStartupManager
from ink2tex.core.config import ConfigReader


class SettingsWindow(QWidget):
    """Settings window for configuring application preferences"""
    
    def __init__(self, parent=None):
        """Initialize the settings window
        
        Args:
            parent: Parent application instance
        """
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the settings UI"""
        self.setWindowTitle("Ink2TeX Settings")
        self.setFixedSize(500, 400)
        self.setWindowIcon(self.parent_app.icon if self.parent_app else QIcon())
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Ink2TeX Settings")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Startup Settings Group
        startup_group = QGroupBox("Startup Settings")
        startup_layout = QVBoxLayout(startup_group)
        
        self.auto_start_checkbox = QPushButton("Enable Auto-Start with Windows")
        self.auto_start_checkbox.setCheckable(True)
        self.auto_start_checkbox.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QPushButton:checked {
                background-color: #e7f3ff;
                border-color: #0066cc;
                color: #0066cc;
            }
        """)
        self.auto_start_checkbox.clicked.connect(self.toggle_auto_start)
        
        startup_info = QLabel("When enabled, Ink2TeX will start automatically when Windows starts.\nThe application will run in the background (system tray).")
        startup_info.setStyleSheet("color: #666; font-size: 10px;")
        startup_info.setWordWrap(True)
        
        startup_layout.addWidget(self.auto_start_checkbox)
        startup_layout.addWidget(startup_info)
        layout.addWidget(startup_group)
        
        # Hotkey Settings Group
        hotkey_group = QGroupBox("Hotkey Settings")
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        hotkey_info = QLabel("Global hotkey to open overlay:")
        hotkey_value = QLabel("Ctrl + Shift + I")
        hotkey_value.setFont(QFont("Courier", 12, QFont.Weight.Bold))
        hotkey_value.setStyleSheet("color: #0066cc; background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        
        hotkey_note = QLabel("This hotkey works system-wide, even when other applications are focused.")
        hotkey_note.setStyleSheet("color: #666; font-size: 10px;")
        hotkey_note.setWordWrap(True)
        
        hotkey_layout.addWidget(hotkey_info)
        hotkey_layout.addWidget(hotkey_value)
        hotkey_layout.addWidget(hotkey_note)
        layout.addWidget(hotkey_group)
        
        # API Settings Group
        api_group = QGroupBox("API Settings")
        api_layout = QVBoxLayout(api_group)
        
        # Check if API is configured by looking at parent app
        api_configured = (hasattr(self.parent_app, 'api_manager') and 
                         self.parent_app.api_manager.is_configured())
        
        api_status = QLabel("Google Gemini API: ✓ Configured" if api_configured else "Google Gemini API: ❌ Not Configured")
        api_status.setStyleSheet("font-weight: bold; color: green;" if api_configured else "font-weight: bold; color: red;")
        
        api_info = QLabel("To configure the API key, edit the .api file in the application folder.")
        api_info.setStyleSheet("color: #666; font-size: 10px;")
        api_info.setWordWrap(True)
        
        api_layout.addWidget(api_status)
        api_layout.addWidget(api_info)
        layout.addWidget(api_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.cancel_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def load_settings(self):
        """Load current settings and update UI"""
        try:
            # Check auto-start status from registry
            registry_enabled = WindowsStartupManager.is_startup_enabled()
            
            # Check config file setting
            config_enabled = ConfigReader.read_config_value('AUTO_START_WITH_WINDOWS', default='false').lower() == 'true'
            
            # Use registry as the authoritative source
            self.auto_start_checkbox.setChecked(registry_enabled)
            
            # Update button text based on state
            self.update_auto_start_button_text()
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def update_auto_start_button_text(self):
        """Update auto-start button text based on current state"""
        if self.auto_start_checkbox.isChecked():
            self.auto_start_checkbox.setText("✓ Auto-Start Enabled - Click to Disable")
        else:
            self.auto_start_checkbox.setText("☐ Auto-Start Disabled - Click to Enable")
    
    def toggle_auto_start(self):
        """Toggle auto-start setting"""
        try:
            if self.auto_start_checkbox.isChecked():
                # Enable auto-start
                success = WindowsStartupManager.enable_startup()
                if success:
                    self.update_auto_start_button_text()
                    self.show_message("Auto-Start Enabled", "Ink2TeX will now start automatically with Windows.")
                else:
                    self.auto_start_checkbox.setChecked(False)
                    self.show_message("Error", "Failed to enable auto-start. Please run as administrator.")
            else:
                # Disable auto-start
                success = WindowsStartupManager.disable_startup()
                if success:
                    self.update_auto_start_button_text()
                    self.show_message("Auto-Start Disabled", "Ink2TeX will no longer start automatically with Windows.")
                else:
                    self.auto_start_checkbox.setChecked(True)
                    self.show_message("Error", "Failed to disable auto-start. Please run as administrator.")
                    
        except Exception as e:
            print(f"Error toggling auto-start: {e}")
            self.show_message("Error", f"Failed to change auto-start setting: {str(e)}")
    
    def save_settings(self):
        """Save settings to configuration file"""
        try:
            # Update config file to match registry setting
            auto_start_value = 'true' if self.auto_start_checkbox.isChecked() else 'false'
            ConfigReader.update_config_setting('AUTO_START_WITH_WINDOWS', auto_start_value)
            
            self.show_message("Settings Saved", "Your settings have been saved successfully.")
            self.close()
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.show_message("Error", f"Failed to save settings: {str(e)}")
    
    def show_message(self, title: str, message: str):
        """Show a message box
        
        Args:
            title: Message box title
            message: Message content
        """
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
