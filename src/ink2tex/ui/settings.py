"""
Settings window for Ink2TeX.
Provides comprehensive UI for configuring all application preferences.
"""

import os
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QGroupBox, QMessageBox, QLineEdit, QTextEdit,
                            QTabWidget, QFileDialog, QCheckBox, QSpinBox, QComboBox,
                            QFormLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from ..core.startup import WindowsStartupManager
from ..core.config import ConfigReader


class SettingsWindow(QWidget):
    """Comprehensive settings window for configuring all application preferences"""
    
    def __init__(self, parent=None):
        """Initialize the settings window
        
        Args:
            parent: Parent application instance
        """
        super().__init__(parent)
        self.parent_app = parent
        self.settings_data = {}
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the settings UI with tabs for different categories"""
        self.setWindowTitle("Ink2TeX Settings")
        self.setFixedSize(700, 600)
        self.setWindowIcon(self.parent_app.icon if self.parent_app else QIcon())
        
        # Set window flags to ensure it shows properly
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        # Center the window on screen
        self.center_on_screen()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Ink2TeX Settings")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_general_tab()
        self.create_api_tab()
        self.create_ui_tab()
        self.create_hotkey_tab()
        self.create_prompt_tab()
        self.create_advanced_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Save All Settings")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 12px 20px; border-radius: 6px; font-weight: bold; font-size: 12px;")
        self.save_btn.clicked.connect(self.save_all_settings)
        
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 12px 20px; border-radius: 6px; font-weight: bold; font-size: 12px;")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("background-color: #f44336; color: white; padding: 12px 20px; border-radius: 6px; font-weight: bold; font-size: 12px;")
        self.cancel_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def center_on_screen(self):
        """Center the settings window on the screen"""
        try:
            from PyQt6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen().geometry()
            window_size = self.geometry()
            x = (screen.width() - window_size.width()) // 2
            y = (screen.height() - window_size.height()) // 2
            self.move(x, y)
        except Exception as e:
            print(f"Error centering window: {e}")
            # Fallback position
            self.move(100, 100)
    
    def create_general_tab(self):
        """Create the general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Startup Settings Group
        startup_group = QGroupBox("🚀 Startup Settings")
        startup_layout = QFormLayout(startup_group)
        
        self.auto_start_checkbox = QCheckBox("Start with Windows")
        self.auto_start_checkbox.setToolTip("Automatically start Ink2TeX when Windows starts")
        startup_layout.addRow("Auto-start:", self.auto_start_checkbox)
        
        layout.addWidget(startup_group)
        
        # Performance Settings Group
        perf_group = QGroupBox("⚡ Performance Settings")
        perf_layout = QFormLayout(perf_group)
        
        self.fast_preview_checkbox = QCheckBox("Enable fast preview")
        self.fast_preview_checkbox.setToolTip("Use optimized rendering for better performance")
        perf_layout.addRow("Fast preview:", self.fast_preview_checkbox)
        
        self.deferred_loading_checkbox = QCheckBox("Enable deferred loading")
        self.deferred_loading_checkbox.setToolTip("Load components only when needed")
        perf_layout.addRow("Deferred loading:", self.deferred_loading_checkbox)
        
        layout.addWidget(perf_group)
        
        layout.addStretch()
        self.tabs.addTab(tab, "🏠 General")
    
    def create_api_tab(self):
        """Create the API settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # API Key Group
        api_group = QGroupBox("🔑 Google Gemini API Configuration")
        api_layout = QVBoxLayout(api_group)
        
        # API Status
        self.api_status_label = QLabel()
        self.api_status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        api_layout.addWidget(self.api_status_label)
        
        # API Key Input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Google Gemini API key here...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_layout.addWidget(self.api_key_input)
        
        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.setToolTip("Show/hide API key")
        self.show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        key_layout.addWidget(self.show_key_btn)
        
        api_layout.addLayout(key_layout)
        
        # Instructions
        instructions = QLabel("""
📋 How to get your API key:
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it above
5. Click "Test API Connection" to verify

⚠️ Keep your API key secure and don't share it with others.
        """)
        instructions.setStyleSheet("color: #666; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        instructions.setWordWrap(True)
        api_layout.addWidget(instructions)
        
        # Test Connection Button
        self.test_api_btn = QPushButton("🧪 Test API Connection")
        self.test_api_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        self.test_api_btn.clicked.connect(self.test_api_connection)
        api_layout.addWidget(self.test_api_btn)
        
        layout.addWidget(api_group)
        layout.addStretch()
        self.tabs.addTab(tab, "🔑 API")
    
    def create_ui_tab(self):
        """Create the UI settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Overlay Settings Group
        overlay_group = QGroupBox("🎨 Overlay Appearance")
        overlay_layout = QFormLayout(overlay_group)
        
        self.opacity_input = QSpinBox()
        self.opacity_input.setRange(10, 100)
        self.opacity_input.setSuffix("%")
        self.opacity_input.setToolTip("Overlay transparency (lower = more transparent)")
        overlay_layout.addRow("Default opacity:", self.opacity_input)
        
        self.bg_color_input = QLineEdit()
        self.bg_color_input.setPlaceholderText("#1a1a1a")
        self.bg_color_input.setToolTip("Canvas background color (hex format)")
        overlay_layout.addRow("Background color:", self.bg_color_input)
        
        self.brush_color_input = QLineEdit()
        self.brush_color_input.setPlaceholderText("#ffffff")
        self.brush_color_input.setToolTip("Drawing brush color (hex format)")
        overlay_layout.addRow("Brush color:", self.brush_color_input)
        
        self.brush_width_input = QSpinBox()
        self.brush_width_input.setRange(1, 20)
        self.brush_width_input.setSuffix(" px")
        self.brush_width_input.setToolTip("Drawing brush width in pixels")
        overlay_layout.addRow("Brush width:", self.brush_width_input)
        
        layout.addWidget(overlay_group)
        layout.addStretch()
        self.tabs.addTab(tab, "🎨 UI")
    
    def create_hotkey_tab(self):
        """Create the hotkey settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Hotkey Settings Group
        hotkey_group = QGroupBox("⌨️ Global Hotkey Configuration")
        hotkey_layout = QFormLayout(hotkey_group)
        
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("ctrl+shift+i")
        self.hotkey_input.setToolTip("Global hotkey to open overlay")
        hotkey_layout.addRow("Global hotkey:", self.hotkey_input)
        
        # Instructions
        hotkey_info = QLabel("""
ℹ️ Hotkey Format:
• Use "ctrl", "shift", "alt" for modifier keys
• Separate keys with "+"
• Examples: "ctrl+shift+i", "alt+space", "ctrl+alt+m"
• The hotkey works system-wide

⚠️ Changes require application restart to take effect.
        """)
        hotkey_info.setStyleSheet("color: #666; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        hotkey_info.setWordWrap(True)
        hotkey_layout.addRow("", hotkey_info)
        
        layout.addWidget(hotkey_group)
        layout.addStretch()
        self.tabs.addTab(tab, "⌨️ Hotkeys")
    
    def create_prompt_tab(self):
        """Create the AI prompt settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Prompt Settings Group
        prompt_group = QGroupBox("🤖 AI Prompt Configuration")
        prompt_layout = QVBoxLayout(prompt_group)
        
        prompt_layout.addWidget(QLabel("AI Prompt Template:"))
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter the prompt that will be sent to the AI...")
        self.prompt_input.setMinimumHeight(200)
        self.prompt_input.setToolTip("This prompt tells the AI how to convert your handwriting to LaTeX")
        prompt_layout.addWidget(self.prompt_input)
        
        # Reset to default prompt button
        reset_prompt_btn = QPushButton("🔄 Reset to Default Prompt")
        reset_prompt_btn.clicked.connect(self.reset_prompt_to_default)
        prompt_layout.addWidget(reset_prompt_btn)
        
        # Instructions
        prompt_info = QLabel("""
💡 Prompt Tips:
• Be specific about the desired output format
• Include examples if needed
• Mention LaTeX syntax requirements
• Test changes with sample equations

🔧 The default prompt is optimized for math equations.
        """)
        prompt_info.setStyleSheet("color: #666; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        prompt_info.setWordWrap(True)
        prompt_layout.addWidget(prompt_info)
        
        layout.addWidget(prompt_group)
        self.tabs.addTab(tab, "🤖 Prompt")
    
    def create_advanced_tab(self):
        """Create the advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File Locations Group
        files_group = QGroupBox("📁 File Locations")
        files_layout = QFormLayout(files_group)
        
        # Config file location
        config_path = self.get_config_file_path()
        config_label = QLabel(f"Config: {config_path}")
        config_label.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        config_label.setWordWrap(True)
        files_layout.addRow("Configuration file:", config_label)
        
        # API file location
        api_path = self.get_api_file_path()
        api_label = QLabel(f"API: {api_path}")
        api_label.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        api_label.setWordWrap(True)
        files_layout.addRow("API key file:", api_label)
        
        # Prompt file location
        prompt_path = self.get_prompt_file_path()
        prompt_label = QLabel(f"Prompt: {prompt_path}")
        prompt_label.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        prompt_label.setWordWrap(True)
        files_layout.addRow("Prompt file:", prompt_label)
        
        layout.addWidget(files_group)
        
        # Actions Group
        actions_group = QGroupBox("🔧 Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        open_config_btn = QPushButton("📝 Open Config Folder")
        open_config_btn.clicked.connect(self.open_config_folder)
        actions_layout.addWidget(open_config_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        self.tabs.addTab(tab, "🔧 Advanced")
    
    def load_settings(self):
        """Load current settings from all configuration sources"""
        try:
            # Load startup settings
            registry_enabled = WindowsStartupManager.is_startup_enabled()
            self.auto_start_checkbox.setChecked(registry_enabled)
            
            # Load UI settings from config file with safe defaults
            opacity_value = ConfigReader.read_config_value('DEFAULT_OVERLAY_OPACITY', '0.3')
            try:
                opacity_percent = int(float(opacity_value or '0.3') * 100)
            except (ValueError, TypeError):
                opacity_percent = 30
            self.opacity_input.setValue(opacity_percent)
            
            self.bg_color_input.setText(ConfigReader.read_config_value('CANVAS_BACKGROUND_COLOR', '#1a1a1a') or '#1a1a1a')
            self.brush_color_input.setText(ConfigReader.read_config_value('BRUSH_COLOR', '#ffffff') or '#ffffff')
            
            brush_width_value = ConfigReader.read_config_value('BRUSH_WIDTH', '3')
            try:
                brush_width = int(brush_width_value or '3')
            except (ValueError, TypeError):
                brush_width = 3
            self.brush_width_input.setValue(brush_width)
            
            # Load performance settings
            fast_preview_value = ConfigReader.read_config_value('ENABLE_FAST_PREVIEW', 'true')
            self.fast_preview_checkbox.setChecked((fast_preview_value or 'true').lower() == 'true')
            
            deferred_loading_value = ConfigReader.read_config_value('DEFERRED_LOADING', 'true')
            self.deferred_loading_checkbox.setChecked((deferred_loading_value or 'true').lower() == 'true')
            
            # Load hotkey setting
            self.hotkey_input.setText(ConfigReader.read_config_value('GLOBAL_HOTKEY', 'ctrl+shift+i') or 'ctrl+shift+i')
            
            # Load API key
            api_key = ConfigReader.read_api_key_from_config()
            if api_key:
                self.api_key_input.setText(api_key)
            
            # Load AI prompt
            prompt_content = self.load_prompt_file()
            if prompt_content:
                self.prompt_input.setPlainText(prompt_content)
            else:
                # Set default prompt if none exists
                self.reset_prompt_to_default()
            
            # Update API status
            self.update_api_status()
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.show_message("Error", f"Failed to load some settings: {str(e)}")
            # Set safe defaults on error
            self.set_safe_defaults()
    
    def set_safe_defaults(self):
        """Set safe default values for all settings"""
        try:
            self.auto_start_checkbox.setChecked(False)
            self.opacity_input.setValue(30)
            self.bg_color_input.setText("#1a1a1a")
            self.brush_color_input.setText("#ffffff")
            self.brush_width_input.setValue(3)
            self.fast_preview_checkbox.setChecked(True)
            self.deferred_loading_checkbox.setChecked(True)
            self.hotkey_input.setText("ctrl+shift+i")
            self.reset_prompt_to_default()
        except Exception as e:
            print(f"Error setting safe defaults: {e}")
    
    def update_api_status(self):
        """Update the API status display"""
        try:
            api_configured = (hasattr(self.parent_app, 'api_manager') and 
                             self.parent_app and
                             self.parent_app.api_manager and
                             self.parent_app.api_manager.is_configured())
            
            if api_configured:
                self.api_status_label.setText("✅ Google Gemini API: Connected")
                self.api_status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.api_status_label.setText("❌ Google Gemini API: Not Connected")
                self.api_status_label.setStyleSheet("color: red; font-weight: bold;")
        except Exception as e:
            print(f"Error updating API status: {e}")
            # Set default status on error
            self.api_status_label.setText("⚠️ Google Gemini API: Status Unknown")
            self.api_status_label.setStyleSheet("color: orange; font-weight: bold;")
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility in the input field"""
        if self.show_key_btn.isChecked():
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("👁")
    
    def test_api_connection(self):
        """Test the API connection with the current key"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.show_message("Error", "Please enter an API key first.")
            return
        
        try:
            # Import and test the API
            from ..core.api import GeminiAPIManager
            
            test_manager = GeminiAPIManager()
            success = test_manager.configure_api(api_key)
            
            if success:
                self.show_message("Success", "✅ API connection successful!\nYour API key is valid and working.")
                self.update_api_status()
            else:
                self.show_message("Error", "❌ API connection failed.\nPlease check your API key and internet connection.")
                
        except Exception as e:
            self.show_message("Error", f"Failed to test API connection: {str(e)}")
    
    def reset_prompt_to_default(self):
        """Reset the AI prompt to default"""
        default_prompt = '''From the provided image, convert the handwritten mathematics into LaTeX. Follow these rules exactly:

1. Each line of handwritten text must be on its own new line in the output.
2. Enclose each separate line of LaTeX within single dollar signs ($).
3. Your entire response must consist ONLY of the resulting LaTeX code. Do not add any introductory text, explanations, or markdown formatting like ```latex.'''
        
        self.prompt_input.setPlainText(default_prompt)
    
    def get_config_file_path(self):
        """Get the configuration file path"""
        try:
            return str(Path.cwd() / ".config")
        except:
            return "Not found"
    
    def get_api_file_path(self):
        """Get the API file path"""
        try:
            return str(Path.cwd() / ".api")
        except:
            return "Not found"
    
    def get_prompt_file_path(self):
        """Get the prompt file path"""
        try:
            return str(Path.cwd() / "prompt.txt")
        except:
            return "Not found"
    
    def load_prompt_file(self):
        """Load the prompt file content"""
        try:
            prompt_file = Path.cwd() / "prompt.txt"
            if prompt_file.exists():
                content = prompt_file.read_text(encoding='utf-8')
                return content if content.strip() else None
            return None
        except Exception as e:
            print(f"Error loading prompt file: {e}")
            return None
    
    def open_config_folder(self):
        """Open the configuration folder in file explorer"""
        try:
            import subprocess
            config_dir = Path.cwd()
            subprocess.run(['explorer', str(config_dir)], check=True)
        except Exception as e:
            self.show_message("Error", f"Failed to open config folder: {str(e)}")
    
    def save_all_settings(self):
        """Save all settings to their respective files"""
        try:
            # Save startup setting
            if self.auto_start_checkbox.isChecked():
                WindowsStartupManager.enable_startup()
            else:
                WindowsStartupManager.disable_startup()
            
            # Save config file settings
            config_updates = {
                'DEFAULT_OVERLAY_OPACITY': str(self.opacity_input.value() / 100.0),
                'CANVAS_BACKGROUND_COLOR': self.bg_color_input.text().strip(),
                'BRUSH_COLOR': self.brush_color_input.text().strip(),
                'BRUSH_WIDTH': str(self.brush_width_input.value()),
                'ENABLE_FAST_PREVIEW': 'true' if self.fast_preview_checkbox.isChecked() else 'false',
                'DEFERRED_LOADING': 'true' if self.deferred_loading_checkbox.isChecked() else 'false',
                'GLOBAL_HOTKEY': self.hotkey_input.text().strip(),
                'AUTO_START_WITH_WINDOWS': 'true' if self.auto_start_checkbox.isChecked() else 'false'
            }
            
            for key, value in config_updates.items():
                ConfigReader.update_config_setting(key, value)
            
            # Save API key
            api_key = self.api_key_input.text().strip()
            if api_key:
                self.save_api_key(api_key)
            
            # Save prompt
            prompt_content = self.prompt_input.toPlainText().strip()
            if prompt_content:
                self.save_prompt_file(prompt_content)
            
            self.show_message("Success", "✅ All settings saved successfully!\n\nSome changes may require restarting the application to take effect.")
            self.close()
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.show_message("Error", f"Failed to save settings: {str(e)}")
    
    def save_api_key(self, api_key):
        """Save API key to .api file"""
        try:
            api_file = Path.cwd() / ".api"
            content = f"# Google Gemini API Key Configuration for Ink2TeX\n"
            content += f"# Get your free API key from: https://makersuite.google.com/app/apikey\n\n"
            content += f"GOOGLE_API_KEY={api_key}\n"
            api_file.write_text(content, encoding='utf-8')
        except Exception as e:
            raise Exception(f"Failed to save API key: {str(e)}")
    
    def save_prompt_file(self, content):
        """Save prompt content to prompt.txt file"""
        try:
            prompt_file = Path.cwd() / "prompt.txt"
            prompt_file.write_text(content, encoding='utf-8')
        except Exception as e:
            raise Exception(f"Failed to save prompt file: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?\n\nThis will overwrite your current configuration.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Reset UI controls to defaults
                self.auto_start_checkbox.setChecked(False)
                self.opacity_input.setValue(30)
                self.bg_color_input.setText("#1a1a1a")
                self.brush_color_input.setText("#ffffff")
                self.brush_width_input.setValue(3)
                self.fast_preview_checkbox.setChecked(True)
                self.deferred_loading_checkbox.setChecked(True)
                self.hotkey_input.setText("ctrl+shift+i")
                self.api_key_input.setText("")
                self.reset_prompt_to_default()
                
                self.show_message("Success", "Settings reset to defaults. Click 'Save All Settings' to apply.")
                
            except Exception as e:
                self.show_message("Error", f"Failed to reset settings: {str(e)}")
    
    def show_message(self, title: str, message: str):
        """Show a message box"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
