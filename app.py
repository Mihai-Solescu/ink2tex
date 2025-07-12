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
                             QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QRect
from PyQt6.QtGui import (QPixmap, QFont, QKeySequence, QShortcut, QPainter, 
                         QPen, QBrush, QColor)
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


class ConfigReader:
    """Utility class to read configuration from .config file"""
    
    @staticmethod
    def read_api_key_from_config(config_path='.config'):
        """Read Google API key from config file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
        
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
        
        raise ValueError("API key not found in .config file")


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
            
            # Prompt for handwriting to LaTeX conversion
            prompt = """
From the provided image, convert the handwritten mathematics into LaTeX. Follow these rules exactly:

1.  Each line of handwritten text must be on its own new line in the output.
2.  Enclose each separate line of LaTeX within single dollar signs ($).
3.  Your entire response must consist ONLY of the resulting LaTeX code. Do not add any introductory text, explanations, or markdown formatting like ```latex.
"""
            
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
        self.setup_overlay()
        self.setup_ui()
        self.setup_drawing()
        # Resize canvas after UI is set up
        self.resize_canvas_for_screen()
        
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
        
        # Create matplotlib canvas for LaTeX preview
        self.preview_figure = Figure(figsize=(4, 2), facecolor='white', dpi=80)
        self.preview_canvas = FigureCanvas(self.preview_figure)
        preview_layout.addWidget(self.preview_canvas)
        
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
        self.canvas_widget.setStyleSheet("background-color: rgba(255, 255, 255, 50);")
        
        # Add to main layout
        self.layout().addWidget(left_panel)
        self.layout().addWidget(self.canvas_widget)
        
        # Canvas will cover the entire right side - calculate dynamically
        self.update_canvas_dimensions()
        
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
        """Initialize drawing variables"""
        self.drawing = False
        self.brush_size = 3
        self.brush_color = QColor(0, 0, 255)  # Blue ink
        self.last_point = QPoint()
        
        # Canvas for drawing - will be resized when overlay shows
        self.canvas_pixmap = QPixmap(1000, 1000)  # Large default size
        self.canvas_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Store drawn paths for undo functionality and bounding box calculation
        self.drawn_paths = []
        
    def resize_canvas_for_screen(self):
        """Resize canvas pixmap to match actual screen dimensions"""
        self.update_canvas_dimensions()
        
        # Create new pixmap with correct size
        new_pixmap = QPixmap(self.canvas_rect.size())
        new_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Copy existing content if any
        if not self.canvas_pixmap.isNull():
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
                
                # Draw line on canvas
                painter = QPainter(self.canvas_pixmap)
                painter.setPen(QPen(self.brush_color, self.brush_size, 
                                  Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, 
                                  Qt.PenJoinStyle.RoundJoin))
                painter.drawLine(self.last_point, canvas_point)
                painter.end()
                
                # Add to current path
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
                
    def paintEvent(self, event):
        """Paint the overlay"""
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
        if not self.canvas_pixmap.isNull():
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
            self.close_and_copy()
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
    
    def close_and_copy(self):
        """Close overlay and copy LaTeX to clipboard"""
        if self.latex_text and CLIPBOARD_AVAILABLE:
            pyperclip.copy(self.latex_text)
        self.close()


class HotkeyManager:
    """Manages local keyboard shortcuts"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.enabled = False
        
    def start_listening(self):
        """Set up local shortcuts"""
        try:
            # Create a local shortcut instead of global
            self.shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self.main_window)
            self.shortcut.activated.connect(self.on_hotkey_pressed)
            self.enabled = True
            return True
        except Exception as e:
            print(f"Failed to setup shortcut: {e}")
            return False
    
    def stop_listening(self):
        """Stop listening"""
        self.enabled = False
    
    def on_hotkey_pressed(self):
        """Handle shortcut press"""
        self.main_window.open_drawing_canvas()


class Ink2TeXMainWindow(QMainWindow):
    """Simplified main application window for Ink2TeX"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_gemini_api()
        self.setup_enhanced_features()
        
    def init_ui(self):
        """Initialize the simplified user interface"""
        self.setWindowTitle("Ink2TeX - Handwritten Math to LaTeX Converter")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        title = QLabel("Ink2TeX Converter")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Click below to open the transparent overlay and start converting handwritten math to LaTeX")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; margin: 20px;")
        layout.addWidget(desc)
        
        # Main button
        self.open_overlay_btn = QPushButton("🖊️ Open Transparent Overlay")
        self.open_overlay_btn.setMinimumHeight(60)
        self.open_overlay_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.open_overlay_btn.clicked.connect(self.open_drawing_canvas)
        layout.addWidget(self.open_overlay_btn)
        
        # Hotkey info
        hotkey_label = QLabel("Shortcut: Ctrl+Shift+I (when window focused)")
        hotkey_label.setStyleSheet("color: #999; font-style: italic; font-size: 10px;")
        hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hotkey_label)
        
        # Status label
        self.status_label = QLabel("Ready to convert handwritten math!")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("margin: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
    def setup_gemini_api(self):
        """Setup Gemini API using config file"""
        try:
            # Read API key
            api_key = ConfigReader.read_api_key_from_config()
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.status_label.setText("✓ Gemini API configured successfully!")
            
        except Exception as e:
            self.status_label.setText(f"❌ API setup failed: {str(e)}")
            QMessageBox.warning(self, "API Error", 
                              f"Failed to setup Gemini API: {str(e)}\n\n"
                              "Please check your .config file with GOOGLE_API_KEY.")
    
    def setup_enhanced_features(self):
        """Setup enhanced features"""
        try:
            # Setup hotkey manager
            self.hotkey_manager = HotkeyManager(self)
            
            # Try to start hotkey listener
            if self.hotkey_manager.start_listening():
                self.status_label.setText("✓ Ready! Use Ctrl+Shift+I or click canvas button")
            else:
                self.status_label.setText("⚠️ Shortcut setup failed - use button instead")
                
        except Exception as e:
            print(f"Error setting up enhanced features: {e}")
            self.status_label.setText("✓ Basic mode ready - use canvas button")
    
    def open_drawing_canvas(self):
        """Open the transparent overlay"""
        try:
            self.overlay = TransparentOverlay(self)
            self.overlay.show()
            self.status_label.setText("🖊️ Transparent overlay opened - draw your math!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open overlay: {str(e)}")
    
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
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            self.hotkey_manager.stop_listening()
        except:
            pass
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Ink2TeX")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Ink2TeX")
    
    try:
        # Create and show main window
        window = Ink2TeXMainWindow()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to start Ink2TeX:\n{str(e)}\n\n"
                           "Please check:\n"
                           "1. All dependencies are installed\n"
                           "2. .config file exists with Google API key\n"
                           "3. Internet connection is available")
        sys.exit(1)


if __name__ == "__main__":
    main()