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


class DrawingCanvasOverlay(QWidget):
    """Full-screen overlay for drawing handwritten math"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_overlay()
        self.setup_drawing()
        
    def setup_overlay(self):
        """Setup the full-screen overlay"""
        # Make window full screen and on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        
        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Semi-transparent background to dim the screen
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        
        # Capture screenshot before overlay if available
        self.capture_background()
        
        # Drawing area in the center
        self.drawing_rect = QRect(
            screen.width() // 4, screen.height() // 4,
            screen.width() // 2, screen.height() // 2
        )
        
    def capture_background(self):
        """Capture screenshot of current screen"""
        if not SCREENSHOT_AVAILABLE:
            self.background_pixmap = None
            return
            
        try:
            # Hide temporarily to capture clean screenshot
            self.hide()
            screenshot = pyautogui.screenshot()
            # Convert PIL to QPixmap
            screenshot_rgb = screenshot.convert('RGB')
            w, h = screenshot_rgb.size
            rgb_image = screenshot_rgb.tobytes('raw', 'RGB')
            qimg = QPixmap.fromImage(qimg.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio))
            self.background_pixmap = qimg
            self.show()
        except Exception as e:
            print(f"Screenshot capture failed: {e}")
            self.background_pixmap = None
            
    def setup_drawing(self):
        """Initialize drawing variables"""
        self.drawing = False
        self.brush_size = 3
        self.brush_color = QColor(0, 0, 255)  # Blue ink
        self.last_point = QPoint()
        
        # Canvas for drawing
        self.canvas = QPixmap(self.drawing_rect.size())
        self.canvas.fill(Qt.GlobalColor.white)
        
        # Store drawn paths for undo functionality
        self.drawn_paths = []
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is in drawing area
            if self.drawing_rect.contains(event.position().toPoint()):
                self.drawing = True
                # Convert to canvas coordinates
                canvas_point = event.position().toPoint() - self.drawing_rect.topLeft()
                self.last_point = canvas_point
                
                # Start new path
                self.current_path = [canvas_point]
            elif event.position().toPoint().y() < 50:  # Top area for close
                self.close_overlay()
                
    def mouseMoveEvent(self, event):
        """Handle mouse move events for drawing"""
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            if self.drawing_rect.contains(event.position().toPoint()):
                # Convert to canvas coordinates
                canvas_point = event.position().toPoint() - self.drawing_rect.topLeft()
                
                # Draw line on canvas
                painter = QPainter(self.canvas)
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
        
        # Draw dimmed background if available
        if hasattr(self, 'background_pixmap') and self.background_pixmap:
            painter.setOpacity(0.3)
            painter.drawPixmap(self.rect(), self.background_pixmap)
            painter.setOpacity(1.0)
        
        # Draw white drawing area
        painter.fillRect(self.drawing_rect, QBrush(Qt.GlobalColor.white))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(self.drawing_rect)
        
        # Draw the canvas content
        painter.drawPixmap(self.drawing_rect.topLeft(), self.canvas)
        
        # Draw instructions
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawText(20, 30, "Draw your math equation in the white area | ESC: Cancel | ENTER: Convert | CTRL+Z: Undo")
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close_overlay()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.convert_drawing()
        elif event.key() == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.undo_last_stroke()
            
    def undo_last_stroke(self):
        """Remove the last drawn stroke"""
        if self.drawn_paths:
            self.drawn_paths.pop()
            self.redraw_canvas()
            
    def redraw_canvas(self):
        """Redraw the canvas from saved paths"""
        self.canvas.fill(Qt.GlobalColor.white)
        painter = QPainter(self.canvas)
        painter.setPen(QPen(self.brush_color, self.brush_size,
                          Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                          Qt.PenJoinStyle.RoundJoin))
        
        for path in self.drawn_paths:
            if len(path) > 1:
                for i in range(1, len(path)):
                    painter.drawLine(path[i-1], path[i])
        
        painter.end()
        self.update()
            
    def convert_drawing(self):
        """Convert the drawing to LaTeX and close overlay"""
        if self.drawn_paths:
            # Save canvas as image
            canvas_image = self.canvas.toImage()
            
            # Convert to PIL Image
            buffer = canvas_image.bits().asstring(canvas_image.sizeInBytes())
            pil_image = Image.frombytes("RGBA", 
                                      (canvas_image.width(), canvas_image.height()), 
                                      buffer)
            # Convert to RGB
            pil_image = pil_image.convert('RGB')
            
            # Save temporary image
            temp_path = "temp_drawing.png"
            pil_image.save(temp_path)
            
            # Signal parent to process this image
            if hasattr(self.parent(), 'load_image'):
                self.parent().load_image(temp_path)
                self.parent().convert_to_latex()
            
            self.close_overlay()
        else:
            # No drawing, just close
            self.close_overlay()
            
    def close_overlay(self):
        """Close the overlay"""
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
    """Main application window for Ink2TeX"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_gemini_api()
        self.setup_enhanced_features()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Ink2TeX - Handwritten Math to LaTeX Converter")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel for image and results
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Ink2TeX Converter")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Hotkey info
        hotkey_label = QLabel("Shortcut: Ctrl+Shift+I (when window focused)")
        hotkey_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        hotkey_label.setWordWrap(True)
        layout.addWidget(hotkey_label)
        
        # Buttons
        self.open_canvas_btn = QPushButton("🖊️ Open Drawing Canvas")
        self.open_canvas_btn.setMinimumHeight(50)
        self.open_canvas_btn.clicked.connect(self.open_drawing_canvas)
        layout.addWidget(self.open_canvas_btn)
        
        self.select_image_btn = QPushButton("📁 Select Image File")
        self.select_image_btn.setMinimumHeight(40)
        self.select_image_btn.clicked.connect(self.select_image_file)
        layout.addWidget(self.select_image_btn)
        
        self.convert_btn = QPushButton("🔄 Convert to LaTeX")
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.clicked.connect(self.convert_to_latex)
        self.convert_btn.setEnabled(False)
        layout.addWidget(self.convert_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to convert handwritten math!")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        return panel
        
    def create_right_panel(self):
        """Create the right panel with preview"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create splitter for image and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - original image display
        image_group = QGroupBox("Handwritten Input")
        image_layout = QVBoxLayout(image_group)
        
        self.image_label = QLabel("No image selected")
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("border: 2px dashed #aaa; background-color: #f9f9f9;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.image_label)
        
        splitter.addWidget(image_group)
        
        # Right side - LaTeX preview
        preview_group = QGroupBox("LaTeX Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.latex_preview = LaTeXPreviewWidget()
        preview_layout.addWidget(self.latex_preview)
        
        splitter.addWidget(preview_group)
        
        # Set equal proportions
        splitter.setSizes([300, 300])
        layout.addWidget(splitter)
        
        # LaTeX output text area
        latex_title = QLabel("LaTeX Code:")
        latex_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(latex_title)
        
        self.latex_output = QTextEdit()
        self.latex_output.setPlaceholderText("LaTeX code will appear here...")
        self.latex_output.setMaximumHeight(120)
        
        # Connect text change with timer to avoid too many updates
        self.latex_timer = QTimer()
        self.latex_timer.setSingleShot(True)
        self.latex_timer.timeout.connect(self.on_latex_timer)
        self.latex_output.textChanged.connect(self.on_latex_changed)
        layout.addWidget(self.latex_output)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        button_layout.addWidget(self.copy_btn)
        
        self.preview_btn = QPushButton("👁️ Update Preview")
        self.preview_btn.clicked.connect(self.update_preview)
        self.preview_btn.setEnabled(False)
        button_layout.addWidget(self.preview_btn)
        
        layout.addLayout(button_layout)
        
        return panel
        
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
        """Open the drawing canvas overlay"""
        try:
            self.overlay = DrawingCanvasOverlay(self)
            self.overlay.show()
            self.status_label.setText("🖊️ Drawing canvas opened - draw your math!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open drawing canvas: {str(e)}")
    
    def select_image_file(self):
        """Open file dialog to select an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Handwritten Math Image", "",
            "Image files (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """Load and display the selected image"""
        try:
            # Load and display image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, 
                                        Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
            # Store image path and enable convert button
            self.current_image_path = file_path
            self.convert_btn.setEnabled(True)
            self.status_label.setText(f"✓ Image loaded: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def convert_to_latex(self):
        """Convert the current image to LaTeX"""
        if not hasattr(self, 'current_image_path'):
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("🔄 Converting handwriting to LaTeX...")
        
        # Start conversion in a separate thread
        self.conversion_thread = ConversionThread(self.current_image_path, self.model)
        self.conversion_thread.finished.connect(self.on_conversion_finished)
        self.conversion_thread.error.connect(self.on_conversion_error)
        self.conversion_thread.start()
    
    def on_conversion_finished(self, latex_result):
        """Handle successful conversion"""
        self.progress_bar.setVisible(False)
        self.latex_output.setText(latex_result)
        self.copy_btn.setEnabled(True)
        self.status_label.setText("✅ Conversion completed successfully!")
        # Auto-update preview after a short delay
        QTimer.singleShot(100, self.update_preview)
    
    def on_conversion_error(self, error_message):
        """Handle conversion error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ Conversion failed: {error_message}")
        QMessageBox.critical(self, "Conversion Error", error_message)
    
    def on_latex_changed(self):
        """Handle LaTeX text changes with debouncing"""
        # Start/restart timer instead of immediate update
        self.latex_timer.start(500)  # 500ms delay
        
    def on_latex_timer(self):
        """Handle delayed latex change"""
        has_text = bool(self.latex_output.toPlainText().strip())
        self.preview_btn.setEnabled(has_text)
        self.copy_btn.setEnabled(has_text)
    
    def update_preview(self):
        """Update the LaTeX preview"""
        latex_text = self.latex_output.toPlainText()
        if latex_text.strip():
            # Update in next event loop cycle to keep UI responsive
            QTimer.singleShot(10, lambda: self.latex_preview.update_preview(latex_text))
    
    def copy_to_clipboard(self):
        """Copy LaTeX output to clipboard"""
        if not CLIPBOARD_AVAILABLE:
            QMessageBox.warning(self, "Warning", "Clipboard functionality not available. Please install pyperclip.")
            return
            
        latex_text = self.latex_output.toPlainText()
        if latex_text:
            pyperclip.copy(latex_text)
            self.status_label.setText("📋 LaTeX copied to clipboard!")
        else:
            QMessageBox.warning(self, "Warning", "No LaTeX to copy!")
    
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
