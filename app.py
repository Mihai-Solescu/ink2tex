#!/usr/bin/env python3
"""
Ink2TeX - Handwritten Math to LaTeX Converter
A PyQt6 desktop application for converting handwritten mathematics to LaTeX using Google Gemini AI.

Features:
- System-wide drawing overlay
- Real-time handwriting to LaTeX conversion
- Live LaTeX preview
- Clipboard integration
- Stylus/mouse input support

Author: GitHub Copilot
Date: July 12, 2025
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QFileDialog, QMessageBox, QProgressBar, QSplitter, 
                             QGroupBox, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QRect
from PyQt6.QtGui import (QPixmap, QFont, QKeySequence, QShortcut, QPainter, 
                         QPen, QBrush, QColor, QIcon, QAction)
import google.generativeai as genai
from PIL import Image
import io

# Set matplotlib backend before importing
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Optional imports for additional features
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("Warning: pyperclip not available - clipboard functionality disabled")

try:
    import pyautogui
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("Warning: pyautogui not available - screenshot functionality disabled")

try:
    import winreg
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    print("Warning: winreg not available - auto-startup functionality disabled")

try:
    import pynput.keyboard as keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not available - global hotkeys disabled")


class ConfigReader:
    """Utility class to read configuration from .api and .config files"""
    
    @staticmethod
    def read_api_key_from_config(config_path='.api'):
        """Read Google API key from .api file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"API configuration file '{config_path}' not found.")
        
        with open(config_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('/'):
                continue
                
            if '=' in line and line.upper().startswith('GOOGLE_API_KEY'):
                key_part = line.split('=', 1)[1].strip()
                if key_part:
                    return key_part
        
        raise ValueError("API key not found in .api file")
    
    @staticmethod
    def read_config_value(key, config_path='.config', default=None):
        """Read a configuration value from .config file"""
        if not os.path.exists(config_path):
            return default
        
        with open(config_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if '=' in line and line.upper().startswith(key.upper()):
                value = line.split('=', 1)[1].strip()
                if value:
                    return value
        
        return default
    
    @staticmethod
    def read_prompt_from_file(prompt_file=None):
        """Read the Gemini prompt from file"""
        if prompt_file is None:
            prompt_file = ConfigReader.read_config_value('PROMPT_FILE', default='prompt.txt')
        
        if not os.path.exists(prompt_file):
            # Fallback to default prompt if file not found
            return """From the provided image, convert the handwritten mathematics into LaTeX. Follow these rules exactly:

1.  Each line of handwritten text must be on its own new line in the output.
2.  Enclose each separate line of LaTeX within single dollar signs ($).
3.  Your entire response must consist ONLY of the resulting LaTeX code. Do not add any introductory text, explanations, or markdown formatting like ```latex."""
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()


class WindowsStartupManager:
    """Manages Windows startup registry entries for auto-start functionality"""
    
    APP_NAME = "Ink2TeX"
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    @staticmethod
    def is_startup_enabled():
        """Check if auto-startup is enabled in Windows registry"""
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, WindowsStartupManager.APP_NAME)
                return bool(value)
        except (FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def enable_startup():
        """Enable auto-startup by adding registry entry"""
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            # Get the path to the current executable
            import sys
            if getattr(sys, 'frozen', False):
                # Running as executable
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            
            # Add to registry
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, 
                              winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, WindowsStartupManager.APP_NAME, 0, winreg.REG_SZ, exe_path)
            
            return True
        except Exception as e:
            print(f"Failed to enable startup: {e}")
            return False
    
    @staticmethod
    def disable_startup():
        """Disable auto-startup by removing registry entry"""
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, 
                              winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, WindowsStartupManager.APP_NAME)
            return True
        except (FileNotFoundError, OSError):
            return True  # Already disabled
        except Exception as e:
            print(f"Failed to disable startup: {e}")
            return False
    
    @staticmethod
    def toggle_startup():
        """Toggle auto-startup setting"""
        if WindowsStartupManager.is_startup_enabled():
            return WindowsStartupManager.disable_startup()
        else:
            return WindowsStartupManager.enable_startup()


class SettingsWindow(QWidget):
    """Settings window for configuring application preferences"""
    
    def __init__(self, parent=None):
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
        
        api_status = QLabel("Google Gemini API: ✓ Configured" if hasattr(self.parent_app, 'model') else "Google Gemini API: ❌ Not Configured")
        api_status.setStyleSheet("font-weight: bold; color: green;" if hasattr(self.parent_app, 'model') else "font-weight: bold; color: red;")
        
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
            
            # Read current config file
            config_lines = []
            config_path = '.config'
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_lines = f.readlines()
            
            # Update or add AUTO_START_WITH_WINDOWS setting
            updated = False
            for i, line in enumerate(config_lines):
                if line.strip().upper().startswith('AUTO_START_WITH_WINDOWS'):
                    config_lines[i] = f'AUTO_START_WITH_WINDOWS={auto_start_value}\n'
                    updated = True
                    break
            
            if not updated:
                config_lines.append(f'AUTO_START_WITH_WINDOWS={auto_start_value}\n')
            
            # Write back to file
            with open(config_path, 'w') as f:
                f.writelines(config_lines)
            
            self.show_message("Settings Saved", "Your settings have been saved successfully.")
            self.close()
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.show_message("Error", f"Failed to save settings: {str(e)}")
    
    def show_message(self, title, message):
        """Show a message box"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


class ConversionThread(QThread):
    """Thread for handling Gemini API conversion without blocking UI"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, image_path, model):
        super().__init__()
        self.image_path = image_path
        self.model = model
    
    def run(self):
        try:
            # Load image
            img = Image.open(self.image_path)
            
            # Load prompt from file
            prompt = ConfigReader.read_prompt_from_file()
            
            # Send request to Gemini
            response = self.model.generate_content([prompt, img])
            self.finished.emit(response.text)
            
        except Exception as e:
            self.error.emit(str(e))


class LaTeXPreviewWidget(QWidget):
    """Widget to preview rendered LaTeX using matplotlib"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the preview UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("LaTeX Preview")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Matplotlib canvas for LaTeX rendering
        self.figure = Figure(figsize=(4, 3), facecolor='white', dpi=80)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(300, 200)
        layout.addWidget(self.canvas)
        
        # Clear button
        clear_btn = QPushButton("Clear Preview")
        clear_btn.clicked.connect(self.clear_preview)
        layout.addWidget(clear_btn)
        
    def update_preview(self, latex_text):
        """Update the LaTeX preview with error handling"""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Split latex into lines and clean them
            lines = [line.strip() for line in latex_text.strip().split('\n') if line.strip()]
            
            if not lines:
                ax.text(0.1, 0.5, "No LaTeX to preview", 
                       transform=ax.transAxes, fontsize=12, color='gray')
                self.canvas.draw()
                return
            
            y_pos = 0.9
            y_step = 0.8 / max(len(lines), 1)  # Distribute evenly
            
            for line in lines:
                if line and y_pos > 0:
                    # Remove dollar signs and clean the line
                    clean_line = line.replace('$', '').strip()
                    if clean_line:
                        try:
                            # Try to render as LaTeX
                            ax.text(0.05, y_pos, f'${clean_line}$', 
                                   fontsize=10, transform=ax.transAxes, 
                                   verticalalignment='top')
                        except Exception:
                            # Fallback to plain text
                            ax.text(0.05, y_pos, line, 
                                   fontsize=9, transform=ax.transAxes,
                                   verticalalignment='top')
                        y_pos -= y_step
            
            self.canvas.draw()
            
        except Exception as e:
            # Show error in preview
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.1, 0.5, f"Preview Error:\n{str(e)[:50]}...", 
                   transform=ax.transAxes, fontsize=9, color='red',
                   verticalalignment='center')
            ax.axis('off')
            self.canvas.draw()
    
    def clear_preview(self):
        """Clear the preview"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.1, 0.5, "Preview cleared", 
               transform=ax.transAxes, fontsize=12, color='gray')
        ax.axis('off')
        self.canvas.draw()


class TransparentOverlay(QWidget):
    """Transparent full-screen overlay with canvas on right and preview/edit on left"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_image = None
        self.latex_text = ""
        
        # Initialize these first to avoid threading issues
        self.drawing = False
        self.brush_size = 3
        self.brush_color = QColor(0, 0, 255)  # Blue ink
        self.last_point = QPoint()
        self.drawn_paths = []
        
        # Setup overlay properties immediately
        self.setup_overlay()
        
        # Defer heavy operations using QTimer to avoid blocking
        QTimer.singleShot(0, self.setup_ui)
        QTimer.singleShot(50, self.setup_drawing)
        QTimer.singleShot(100, self.resize_canvas_for_screen)
        
    def setup_overlay(self):
        """Setup the transparent full-screen overlay"""
        # Make window full screen and on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        
        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Make completely transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Ensure the overlay can receive focus and keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_KeyCompression, False)
        
        # Store screen dimensions
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        
    def setup_ui(self):
        """Setup the UI layout matching the design"""
        # Create main layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(50, 50, 50, 50)
        
        # Left side - Preview and Edit panels
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # Top toolbar buttons
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: rgba(50, 50, 50, 200); border-radius: 5px;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar.setFixedHeight(40)
        
        self.upload_btn = QPushButton("📁 Upload")
        self.upload_btn.setStyleSheet("color: white; border: none; padding: 5px;")
        self.upload_btn.clicked.connect(self.upload_image)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setStyleSheet("color: white; border: none; padding: 5px;")
        self.clear_btn.clicked.connect(self.clear_canvas)
        
        toolbar_layout.addWidget(self.upload_btn)
        toolbar_layout.addWidget(self.clear_btn)
        toolbar_layout.addStretch()
        
        # LaTeX Preview panel
        preview_panel = QWidget()
        preview_panel.setStyleSheet("background-color: rgba(255, 255, 255, 230); border: 2px solid gray; border-radius: 5px;")
        preview_panel.setFixedHeight(200)
        preview_layout = QVBoxLayout(preview_panel)
        
        preview_label = QLabel("LaTeX Preview")
        preview_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)
        
        # Create matplotlib canvas for LaTeX preview (deferred for speed)
        self.preview_figure = None
        self.preview_canvas = None
        
        # Create placeholder widget that will be replaced with matplotlib canvas when needed
        self.preview_placeholder = QLabel("LaTeX preview will appear here\n(loads on first use)")
        self.preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_placeholder.setStyleSheet("color: gray; font-style: italic;")
        self.preview_placeholder.setMinimumSize(280, 150)
        preview_layout.addWidget(self.preview_placeholder)
        
        # Will create matplotlib canvas on first use for faster startup
        self.preview_initialized = False
        
        # Edit window
        edit_panel = QWidget()
        edit_panel.setStyleSheet("background-color: rgba(255, 255, 255, 230); border: 2px solid gray; border-radius: 5px;")
        edit_layout = QVBoxLayout(edit_panel)
        
        edit_header = QHBoxLayout()
        edit_label = QLabel("Edit Window")
        edit_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setStyleSheet("background-color: lightblue; border: 1px solid blue; padding: 2px;")
        self.copy_btn.clicked.connect(self.copy_latex)
        
        edit_header.addWidget(edit_label)
        edit_header.addStretch()
        edit_header.addWidget(self.copy_btn)
        
        edit_layout.addLayout(edit_header)
        
        self.latex_edit = QTextEdit()
        self.latex_edit.setPlaceholderText("Write LaTeX here...")
        self.latex_edit.setStyleSheet("background-color: white; border: none;")
        self.latex_edit.textChanged.connect(self.on_latex_changed)
        edit_layout.addWidget(self.latex_edit)
        
        # Add panels to left layout
        left_layout.addWidget(toolbar)
        left_layout.addWidget(preview_panel)
        left_layout.addWidget(edit_panel)
        
        # Right side - Drawing canvas with dashed border (covers rest of screen)
        self.canvas_widget = QWidget()
        self.canvas_widget.setStyleSheet("background-color: rgba(255, 255, 255, 30);")  # More transparent for better performance
        self.canvas_widget.setCursor(Qt.CursorShape.CrossCursor)  # Set drawing cursor
        
        # Add to main layout
        self.layout().addWidget(left_panel)
        self.layout().addWidget(self.canvas_widget)
        
        # Canvas will cover the entire right side - calculate dynamically
        self.update_canvas_dimensions()
        
        # Set normal cursor to avoid busy cursor
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # Set up canvas cursor after everything is created
        QTimer.singleShot(150, self._setup_canvas_cursor)
    
    def _setup_canvas_cursor(self):
        """Set up the canvas cursor after UI is fully initialized"""
        if hasattr(self, 'canvas_widget') and self.canvas_widget:
            self.canvas_widget.setCursor(Qt.CursorShape.CrossCursor)
    
    def _init_preview_canvas(self):
        """Initialize matplotlib preview canvas on first use"""
        if self.preview_initialized:
            return
            
        try:
            # Create matplotlib canvas
            self.preview_figure = Figure(figsize=(4, 2), facecolor='white', dpi=60)
            self.preview_canvas = FigureCanvas(self.preview_figure)
            self.preview_canvas.setMinimumSize(280, 150)
            
            # Replace placeholder with actual canvas
            parent_layout = self.preview_placeholder.parent().layout()
            parent_layout.replaceWidget(self.preview_placeholder, self.preview_canvas)
            self.preview_placeholder.hide()
            
            # Initialize with placeholder text
            ax = self.preview_figure.add_subplot(111)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.text(0.1, 0.5, "LaTeX preview ready", 
                   transform=ax.transAxes, fontsize=9, color='gray',
                   ha='left', va='center')
            self.preview_canvas.draw()
            
            self.preview_initialized = True
            print("✓ LaTeX preview initialized")
            
        except Exception as e:
            print(f"Preview init warning: {e}")
        
    def update_canvas_dimensions(self):
        """Update canvas dimensions to cover the entire right side"""
        # Canvas covers from right side of left panel to screen edge
        left_panel_width = 450  # 400px panel + 50px margin
        canvas_start_x = 50  # Small margin from left panel
        canvas_start_y = 50  # Small margin from top
        
        # Calculate available space (will be updated when overlay is shown)
        canvas_width = max(600, self.screen_width - left_panel_width - 100)  # Ensure minimum size
        canvas_height = max(400, self.screen_height - 150)  # Ensure minimum size, leave margin
        
        self.canvas_rect = QRect(canvas_start_x, canvas_start_y, canvas_width, canvas_height)
        
    def setup_drawing(self):
        """Initialize drawing variables (optimized for fast startup)"""
        # Canvas for drawing - start with smaller size for faster init
        self.canvas_pixmap = QPixmap(800, 600)  # Smaller initial size
        self.canvas_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Set cursor to normal to avoid busy cursor
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
    def resize_canvas_for_screen(self):
        """Resize canvas pixmap to match actual screen dimensions"""
        # Skip if not ready
        if not hasattr(self, 'canvas_rect'):
            return
            
        self.update_canvas_dimensions()
        
        # Create new pixmap with correct size
        new_pixmap = QPixmap(self.canvas_rect.size())
        new_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Copy existing content if any
        if hasattr(self, 'canvas_pixmap') and not self.canvas_pixmap.isNull():
            painter = QPainter(new_pixmap)
            painter.drawPixmap(0, 0, self.canvas_pixmap)
            painter.end()
        
        self.canvas_pixmap = new_pixmap
        
    def calculate_handwriting_bounds(self):
        """Calculate the bounding rectangle of all handwriting with padding"""
        if not self.drawn_paths:
            return None
            
        # Find min/max coordinates of all drawn points
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for path in self.drawn_paths:
            for point in path:
                min_x = min(min_x, point.x())
                min_y = min(min_y, point.y())
                max_x = max(max_x, point.x())
                max_y = max(max_y, point.y())
        
        if min_x == float('inf'):  # No valid points
            return None
            
        # Add padding around the handwriting
        padding = 30
        min_x = max(0, min_x - padding)
        min_y = max(0, min_y - padding)
        max_x = min(self.canvas_rect.width(), max_x + padding)
        max_y = min(self.canvas_rect.height(), max_y + padding)
        
        # Ensure minimum size for AI recognition
        min_width = 100
        min_height = 100
        
        width = max(min_width, max_x - min_x)
        height = max(min_height, max_y - min_y)
        
        return QRect(int(min_x), int(min_y), int(width), int(height))
        
    def crop_canvas_to_handwriting(self):
        """Create a cropped image containing only the handwriting area"""
        bounds = self.calculate_handwriting_bounds()
        
        if bounds is None:
            # No handwriting, return full canvas or current image
            if self.current_image:
                return self.canvas_pixmap
            else:
                # Return empty white image
                empty_pixmap = QPixmap(200, 200)
                empty_pixmap.fill(Qt.GlobalColor.white)
                return empty_pixmap
        
        # Create cropped image with white background
        cropped_pixmap = QPixmap(bounds.size())
        cropped_pixmap.fill(Qt.GlobalColor.white)
        
        # Copy the relevant part of the canvas using the correct drawPixmap overload
        painter = QPainter(cropped_pixmap)
        # Use the overload: drawPixmap(x, y, pixmap, sx, sy, sw, sh)
        painter.drawPixmap(0, 0, self.canvas_pixmap, 
                          bounds.x(), bounds.y(), bounds.width(), bounds.height())
        painter.end()
        
        return cropped_pixmap
        
    def upload_image(self):
        """Upload an image to display in the canvas"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Image files (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if file_path:
            try:
                # Load image
                pixmap = QPixmap(file_path)
                # Scale to fit canvas
                scaled_pixmap = pixmap.scaled(self.canvas_rect.size(), 
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                
                # Clear canvas and set background image
                self.canvas_pixmap = QPixmap(self.canvas_rect.size())
                self.canvas_pixmap.fill(Qt.GlobalColor.white)
                
                painter = QPainter(self.canvas_pixmap)
                # Center the image
                x = (self.canvas_rect.width() - scaled_pixmap.width()) // 2
                y = (self.canvas_rect.height() - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                self.current_image = file_path
                self.update()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def clear_canvas(self):
        """Clear the drawing canvas"""
        self.canvas_pixmap.fill(Qt.GlobalColor.transparent)
        self.drawn_paths = []
        self.current_image = None
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Skip if UI not initialized
        if not hasattr(self, 'canvas_widget') or not hasattr(self, 'canvas_rect'):
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the actual canvas position on screen (dynamic size)
            canvas_global_rect = QRect(
                self.canvas_widget.x() + self.canvas_rect.x(),
                self.canvas_widget.y() + self.canvas_rect.y(),
                self.canvas_rect.width(),
                self.canvas_rect.height()
            )
            
            if canvas_global_rect.contains(event.position().toPoint()):
                self.drawing = True
                # Convert to canvas coordinates
                canvas_point = QPoint(
                    event.position().toPoint().x() - canvas_global_rect.x(),
                    event.position().toPoint().y() - canvas_global_rect.y()
                )
                self.last_point = canvas_point
                self.current_path = [canvas_point]
                
    def mouseMoveEvent(self, event):
        """Handle mouse move events for drawing"""
        # Skip if UI not initialized  
        if not hasattr(self, 'canvas_widget') or not hasattr(self, 'canvas_rect'):
            return
            
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            canvas_global_rect = QRect(
                self.canvas_widget.x() + self.canvas_rect.x(),
                self.canvas_widget.y() + self.canvas_rect.y(),
                self.canvas_rect.width(),
                self.canvas_rect.height()
            )
            
            if canvas_global_rect.contains(event.position().toPoint()):
                # Convert to canvas coordinates
                canvas_point = QPoint(
                    event.position().toPoint().x() - canvas_global_rect.x(),
                    event.position().toPoint().y() - canvas_global_rect.y()
                )
                
                # Draw line on canvas (check if canvas_pixmap exists)
                if hasattr(self, 'canvas_pixmap') and not self.canvas_pixmap.isNull():
                    painter = QPainter(self.canvas_pixmap)
                    painter.setPen(QPen(self.brush_color, self.brush_size, 
                                      Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, 
                                      Qt.PenJoinStyle.RoundJoin))
                    painter.drawLine(self.last_point, canvas_point)
                    painter.end()
                
                    # Add to current path
                    if hasattr(self, 'current_path'):
                        self.current_path.append(canvas_point)
                    self.last_point = canvas_point
                    
                    # Update display
                    self.update()
                
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            # Save completed path
            if hasattr(self, 'current_path') and len(self.current_path) > 1:
                self.drawn_paths.append(self.current_path.copy())
                
    def showEvent(self, event):
        """Handle show event to ensure proper cursor and focus"""
        super().showEvent(event)
        
        # Ensure normal cursor (not busy)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # Set drawing cursor for canvas widget if it exists
        if hasattr(self, 'canvas_widget') and self.canvas_widget:
            self.canvas_widget.setCursor(Qt.CursorShape.CrossCursor)
        
        # Aggressive focus management to ensure keyboard events work immediately
        self.setFocus(Qt.FocusReason.OtherFocusReason)
        self.activateWindow()
        self.raise_()
        
        # Use timer to ensure focus after window is fully rendered
        QTimer.singleShot(50, lambda: self.setFocus(Qt.FocusReason.OtherFocusReason))
        QTimer.singleShot(100, lambda: self.activateWindow())
        
        # Force update
        self.update()
    
    def focusInEvent(self, event):
        """Handle focus in event to ensure keyboard events work"""
        super().focusInEvent(event)
        # Grab keyboard focus to ensure all key events come to this widget
        self.grabKeyboard()
        print("✓ Overlay has keyboard focus")
    
    def focusOutEvent(self, event):
        """Handle focus out event"""
        super().focusOutEvent(event)
        # Release keyboard grab when losing focus
        self.releaseKeyboard()
    
    def closeEvent(self, event):
        """Handle close event"""
        # Make sure to release keyboard grab when closing
        self.releaseKeyboard()
        super().closeEvent(event)
    
    def paintEvent(self, event):
        """Paint the overlay"""
        # Skip painting if UI not yet initialized
        if not hasattr(self, 'canvas_widget') or not hasattr(self, 'canvas_rect'):
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get canvas position in widget coordinates (dynamic size)
        canvas_x = self.canvas_widget.x() + self.canvas_rect.x()
        canvas_y = self.canvas_widget.y() + self.canvas_rect.y()
        canvas_rect = QRect(canvas_x, canvas_y, self.canvas_rect.width(), self.canvas_rect.height())
        
        # Draw dashed border around canvas
        painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.PenStyle.DashLine))
        painter.drawRect(canvas_rect)
        
        # Draw canvas content (scaled if necessary)
        if hasattr(self, 'canvas_pixmap') and not self.canvas_pixmap.isNull():
            painter.drawPixmap(canvas_x, canvas_y, self.canvas_pixmap)
            
        # Optional: Draw handwriting bounds for debugging (uncomment to see bounds)
        # bounds = self.calculate_handwriting_bounds()
        # if bounds:
        #     painter.setPen(QPen(QColor(255, 0, 0), 1, Qt.PenStyle.DotLine))
        #     debug_rect = QRect(canvas_x + bounds.x(), canvas_y + bounds.y(), bounds.width(), bounds.height())
        #     painter.drawRect(debug_rect)
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close_overlay()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.generate_latex()
        elif event.key() == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.undo_last_stroke()
            
    def undo_last_stroke(self):
        """Remove the last drawn stroke"""
        if self.drawn_paths:
            self.drawn_paths.pop()
            self.redraw_canvas()
            
    def redraw_canvas(self):
        """Redraw the canvas from saved paths"""
        # Preserve background image if exists
        if self.current_image:
            self.canvas_pixmap.fill(Qt.GlobalColor.white)
            try:
                pixmap = QPixmap(self.current_image)
                scaled_pixmap = pixmap.scaled(self.canvas_rect.size(), 
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                painter = QPainter(self.canvas_pixmap)
                x = (self.canvas_rect.width() - scaled_pixmap.width()) // 2
                y = (self.canvas_rect.height() - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
            except:
                pass
        else:
            self.canvas_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Redraw all paths
        painter = QPainter(self.canvas_pixmap)
        painter.setPen(QPen(self.brush_color, self.brush_size,
                          Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                          Qt.PenJoinStyle.RoundJoin))
        
        for path in self.drawn_paths:
            if len(path) > 1:
                for i in range(1, len(path)):
                    painter.drawLine(path[i-1], path[i])
        
        painter.end()
        self.update()
    
    def generate_latex(self):
        """Generate LaTeX from the current canvas (cropped to handwriting area)"""
        if not (self.drawn_paths or self.current_image):
            return
            
        # Save only the cropped handwriting area
        temp_path = "temp_overlay_drawing.png"
        
        # Get cropped image containing only handwriting with padding
        cropped_image = self.crop_canvas_to_handwriting()
        
        # Save the cropped image
        cropped_image.save(temp_path)
        
        # Convert using parent's conversion system
        if self.parent_window and hasattr(self.parent_window, 'convert_image_to_latex'):
            self.parent_window.convert_image_to_latex(temp_path, self.on_latex_result)
    
    def on_latex_result(self, latex_text):
        """Handle LaTeX conversion result"""
        self.latex_text = latex_text
        self.latex_edit.setText(latex_text)
        self.update_preview()
    
    def on_latex_changed(self):
        """Handle manual LaTeX text changes"""
        self.latex_text = self.latex_edit.toPlainText()
        QTimer.singleShot(500, self.update_preview)  # Debounced update
    
    def update_preview(self):
        """Update LaTeX preview"""
        try:
            # Initialize preview canvas on first use for faster startup
            if not self.preview_initialized:
                self._init_preview_canvas()
                if not self.preview_initialized:
                    return  # Failed to initialize
            
            self.preview_figure.clear()
            ax = self.preview_figure.add_subplot(111)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            if self.latex_text.strip():
                # Clean and render LaTeX
                lines = [line.strip().replace('$', '') for line in self.latex_text.strip().split('\n') if line.strip()]
                y_pos = 0.8
                
                for line in lines:
                    if line and y_pos > 0:
                        try:
                            ax.text(0.05, y_pos, f'${line}$', 
                                   fontsize=10, transform=ax.transAxes)
                            y_pos -= 0.3
                        except:
                            ax.text(0.05, y_pos, line, 
                                   fontsize=9, transform=ax.transAxes)
                            y_pos -= 0.2
            else:
                ax.text(0.1, 0.5, "LaTeX preview will appear here", 
                       transform=ax.transAxes, fontsize=10, color='gray')
            
            self.preview_canvas.draw()
            
        except Exception as e:
            print(f"Preview error: {e}")
    
    def copy_latex(self):
        """Copy LaTeX to clipboard"""
        if CLIPBOARD_AVAILABLE and self.latex_text:
            pyperclip.copy(self.latex_text)
            # Brief visual feedback
            original_style = self.copy_btn.styleSheet()
            self.copy_btn.setStyleSheet("background-color: lightgreen; border: 1px solid green; padding: 2px;")
            QTimer.singleShot(200, lambda: self.copy_btn.setStyleSheet(original_style))
    
    def close_overlay(self):
        """Close overlay (always works, copies LaTeX if available)"""
        if self.latex_text and CLIPBOARD_AVAILABLE:
            pyperclip.copy(self.latex_text)
        # Ensure keyboard is released before closing
        self.releaseKeyboard()
        self.close()
    
    def close_and_copy(self):
        """Close overlay and copy LaTeX to clipboard"""
        if self.latex_text and CLIPBOARD_AVAILABLE:
            pyperclip.copy(self.latex_text)
        # Ensure keyboard is released before closing
        self.releaseKeyboard()
        self.close()


class GlobalHotkeyManager:
    """Manages global keyboard shortcuts for system tray app"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.enabled = False
        
    def start_listening(self):
        """Set up global shortcuts using pynput if available"""
        try:
            if not PYNPUT_AVAILABLE:
                print("pynput not available - global hotkeys disabled")
                return False
                
            import pynput.keyboard as keyboard
            
            def on_hotkey():
                """Handle global hotkey press"""
                self.main_app.open_overlay()
            
            # Set up global hotkey Ctrl+Shift+I
            self.hotkey = keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+i': on_hotkey
            })
            self.hotkey.start()
            self.enabled = True
            return True
            
        except ImportError:
            print("pynput not available - global hotkeys disabled")
            return False
        except Exception as e:
            print(f"Failed to setup global hotkey: {e}")
            return False
    
    def stop_listening(self):
        """Stop listening for global hotkeys"""
        if hasattr(self, 'hotkey') and self.hotkey:
            try:
                self.hotkey.stop()
            except:
                pass
        self.enabled = False


class Ink2TeXSystemTrayApp(QWidget):
    """System tray application for Ink2TeX"""
    
    def __init__(self):
        super().__init__()
        self.overlay = None
        self.settings_window = None
        self.init_app()
        self.setup_gemini_api()
        self.setup_system_tray()
        self.setup_global_hotkeys()
        self.apply_startup_settings()
        
    def init_app(self):
        """Initialize the application without showing a window"""
        # Hide the main window - we only use system tray
        self.hide()
        
    def setup_gemini_api(self):
        """Setup Gemini API using config file"""
        try:
            # Read API key
            api_key = ConfigReader.read_api_key_from_config()
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✓ Gemini API configured successfully!")
            
        except Exception as e:
            print(f"❌ API setup failed: {str(e)}")
            self.show_message("API Error", 
                            f"Failed to setup Gemini API: {str(e)}\n\n"
                            "Please check your .config file with GOOGLE_API_KEY.", 
                            QSystemTrayIcon.MessageIcon.Critical)
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            return
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon (you can replace with a custom icon file)
        self.create_tray_icon()
        
        # Create context menu
        self.create_tray_menu()
        
        # Set up tray icon
        self.tray_icon.setIcon(self.icon)
        self.tray_icon.setToolTip("Ink2TeX - Handwritten Math to LaTeX Converter\nCtrl+Shift+I to open overlay")
        
        # Connect double-click to open overlay
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Show startup notification
        self.show_message("Ink2TeX Started", 
                         "Ink2TeX is running in the background.\nPress Ctrl+Shift+I to open the overlay,\nor right-click the tray icon for options.",
                         QSystemTrayIcon.MessageIcon.Information)
    
    def create_tray_icon(self):
        """Create a simple tray icon"""
        # Create a simple icon with the Ink2TeX logo
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a simple math symbol background
        painter.setBrush(QBrush(QColor(70, 130, 180)))  # Steel blue
        painter.setPen(QPen(QColor(25, 25, 112), 2))    # Navy border
        painter.drawEllipse(2, 2, 28, 28)
        
        # Draw LaTeX symbol
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(8, 22, "∫")  # Integral symbol
        
        painter.end()
        
        self.icon = QIcon(pixmap)
    
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
        
        # Settings/Status action
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
                    self.update_config_setting('AUTO_START_WITH_WINDOWS', 'true')
                else:
                    self.update_config_setting('AUTO_START_WITH_WINDOWS', 'false')
            
        except Exception as e:
            print(f"Error applying startup settings: {e}")
    
    def update_config_setting(self, key, value):
        """Update a single setting in the config file"""
        try:
            config_path = '.config'
            config_lines = []
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_lines = f.readlines()
            
            # Update or add setting
            updated = False
            for i, line in enumerate(config_lines):
                if line.strip().upper().startswith(key.upper()):
                    config_lines[i] = f'{key}={value}\n'
                    updated = True
                    break
            
            if not updated:
                config_lines.append(f'{key}={value}\n')
            
            # Write back to file
            with open(config_path, 'w') as f:
                f.writelines(config_lines)
                
        except Exception as e:
            print(f"Error updating config setting: {e}")
    
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
            # Ensure we're in the main thread
            self.overlay = TransparentOverlay(self)
            
            # Show overlay with proper threading
            self.overlay.show()
            self.overlay.raise_()
            self.overlay.activateWindow()
            
            # Stronger focus management to ensure keyboard events work immediately
            self.overlay.setFocus(Qt.FocusReason.OtherFocusReason)
            
            # Use a timer to ensure focus is set after the window is fully shown
            QTimer.singleShot(100, lambda: self.overlay.setFocus(Qt.FocusReason.OtherFocusReason))
            
            print("🖊️ Transparent overlay opened")
            
        except Exception as e:
            print(f"Error creating overlay: {str(e)}")
            self.show_message("Error", f"Failed to create overlay: {str(e)}", 
                            QSystemTrayIcon.MessageIcon.Critical)
    
    def convert_image_to_latex(self, image_path, callback):
        """Convert image to LaTeX using Gemini API"""
        try:
            # Start conversion in a separate thread
            self.conversion_thread = ConversionThread(image_path, self.model)
            self.conversion_thread.finished.connect(callback)
            self.conversion_thread.error.connect(lambda error: print(f"Conversion error: {error}"))
            self.conversion_thread.start()
        except Exception as e:
            print(f"Failed to start conversion: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h3>Ink2TeX</h3>
<p><b>Version:</b> 1.0</p>
<p><b>Description:</b> Handwritten Math to LaTeX Converter</p>
<p><b>Author:</b> GitHub Copilot</p>
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
            
            # Create and show settings window
            self.settings_window = SettingsWindow(self)
            self.settings_window.show()
            
        except Exception as e:
            print(f"Error showing settings: {e}")
            self.show_message("Error", f"Failed to open settings: {str(e)}", 
                            QSystemTrayIcon.MessageIcon.Critical)
    
    def show_status(self):
        """Show application status"""
        hotkey_status = "✓ Enabled" if self.hotkey_manager.enabled else "❌ Disabled"
        api_status = "✓ Configured" if hasattr(self, 'model') else "❌ Not configured"
        
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
</ul>
"""
        
        msg = QMessageBox()
        msg.setWindowTitle("Ink2TeX Status")
        msg.setText(status_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show system tray notification"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, 3000)  # 3 seconds
    
    def quit_application(self):
        """Quit the application"""
        # Stop global hotkeys
        if hasattr(self, 'hotkey_manager'):
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
                            "Application is still running in the system tray.\nRight-click the tray icon to exit.",
                            QSystemTrayIcon.MessageIcon.Information)


def main():
    """Main function to run the Ink2TeX system tray application"""
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
    main()