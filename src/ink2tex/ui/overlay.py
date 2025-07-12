"""
Transparent overlay widget for Ink2TeX.
Provides a full-screen drawing interface with LaTeX preview and editing capabilities.
"""

import os
from typing import Optional, List

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPixmap, QFont, QPainter, QPen, QBrush, QColor, QCursor
from PyQt6.QtWidgets import QApplication

# Optional clipboard import
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


class TransparentOverlay(QWidget):
    """Transparent full-screen overlay with canvas on right and preview/edit on left"""
    
    def __init__(self, parent=None):
        """Initialize the transparent overlay
        
        Args:
            parent: Parent application instance
        """
        super().__init__(parent)
        self.parent_window = parent
        self.current_image = None
        self.latex_text = ""
        
        # Initialize drawing state
        self.drawing = False
        self.brush_size = 3
        self.brush_color = QColor(0, 0, 255)  # Blue ink
        self.last_point = QPoint()
        self.drawn_paths: List[List[QPoint]] = []
        self.current_path: List[QPoint] = []
        
        # Thread management for API calls
        self.conversion_thread = None
        
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
        
        # Create preview widget from ui.preview module
        from ink2tex.ui.preview import LaTeXPreviewWidget
        self.preview_widget = LaTeXPreviewWidget()
        # Remove the title since we have one above
        self.preview_widget.layout().removeWidget(self.preview_widget.layout().itemAt(0).widget())
        preview_layout.addWidget(self.preview_widget)
        
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
        
        # Right side - Drawing canvas
        self.canvas_widget = QWidget()
        self.canvas_widget.setStyleSheet("background-color: rgba(255, 255, 255, 30);")
        self.canvas_widget.setCursor(Qt.CursorShape.CrossCursor)
        
        # Add to main layout
        self.layout().addWidget(left_panel)
        self.layout().addWidget(self.canvas_widget)
        
        # Update canvas dimensions
        self.update_canvas_dimensions()
        
        # Set up canvas cursor after everything is created
        QTimer.singleShot(150, self._setup_canvas_cursor)
    
    def _setup_canvas_cursor(self):
        """Set up the canvas cursor after UI is fully initialized"""
        if hasattr(self, 'canvas_widget') and self.canvas_widget:
            self.canvas_widget.setCursor(Qt.CursorShape.CrossCursor)
    
    def update_canvas_dimensions(self):
        """Update canvas dimensions to cover the entire right side"""
        # Canvas covers from right side of left panel to screen edge
        left_panel_width = 450  # 400px panel + 50px margin
        canvas_start_x = 50  # Small margin from left panel
        canvas_start_y = 50  # Small margin from top
        
        # Calculate available space
        canvas_width = max(600, self.screen_width - left_panel_width - 100)
        canvas_height = max(400, self.screen_height - 150)
        
        self.canvas_rect = QRect(canvas_start_x, canvas_start_y, canvas_width, canvas_height)
        
    def setup_drawing(self):
        """Initialize drawing variables"""
        # Canvas for drawing - start with smaller size for faster init
        self.canvas_pixmap = QPixmap(800, 600)
        self.canvas_pixmap.fill(Qt.GlobalColor.transparent)
        
    def resize_canvas_for_screen(self):
        """Resize canvas pixmap to match actual screen dimensions"""
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
        
    def calculate_handwriting_bounds(self) -> Optional[QRect]:
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
        
    def crop_canvas_to_handwriting(self) -> QPixmap:
        """Create a cropped image containing only the handwriting area"""
        bounds = self.calculate_handwriting_bounds()
        
        if bounds is None:
            # No handwriting, return current image or empty white image
            if self.current_image:
                return self.canvas_pixmap
            else:
                empty_pixmap = QPixmap(200, 200)
                empty_pixmap.fill(Qt.GlobalColor.white)
                return empty_pixmap
        
        # Create cropped image with white background
        cropped_pixmap = QPixmap(bounds.size())
        cropped_pixmap.fill(Qt.GlobalColor.white)
        
        # Copy the relevant part of the canvas
        painter = QPainter(cropped_pixmap)
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
        if not hasattr(self, 'canvas_widget') or not hasattr(self, 'canvas_rect'):
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the actual canvas position on screen
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
                
                # Draw line on canvas
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
        
        # Focus management
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
        self.grabKeyboard()
        print("✓ Overlay has keyboard focus")
    
    def focusOutEvent(self, event):
        """Handle focus out event"""
        super().focusOutEvent(event)
        self.releaseKeyboard()
    
    def closeEvent(self, event):
        """Handle close event"""
        # Clean up any running conversion thread
        if hasattr(self, 'conversion_thread') and self.conversion_thread and self.conversion_thread.isRunning():
            self.conversion_thread.quit()
            self.conversion_thread.wait(2000)  # Wait up to 2 seconds for thread to finish
        
        self.releaseKeyboard()
        super().closeEvent(event)
    
    def paintEvent(self, event):
        """Paint the overlay"""
        if not hasattr(self, 'canvas_widget') or not hasattr(self, 'canvas_rect'):
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get canvas position in widget coordinates
        canvas_x = self.canvas_widget.x() + self.canvas_rect.x()
        canvas_y = self.canvas_widget.y() + self.canvas_rect.y()
        canvas_rect = QRect(canvas_x, canvas_y, self.canvas_rect.width(), self.canvas_rect.height())
        
        # Draw dashed border around canvas
        painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.PenStyle.DashLine))
        painter.drawRect(canvas_rect)
        
        # Draw canvas content
        if hasattr(self, 'canvas_pixmap') and not self.canvas_pixmap.isNull():
            painter.drawPixmap(canvas_x, canvas_y, self.canvas_pixmap)
            
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
        """Generate LaTeX from the current canvas"""
        if not (self.drawn_paths or self.current_image):
            return
        
        # Cancel any existing conversion thread
        if self.conversion_thread and self.conversion_thread.isRunning():
            print("Cancelling previous conversion...")
            self.conversion_thread.quit()
            self.conversion_thread.wait(1000)  # Wait up to 1 second
            
        # Save only the cropped handwriting area
        temp_path = os.path.join("temp", "temp_overlay_drawing.png")
        
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        # Get cropped image containing only handwriting with padding
        cropped_image = self.crop_canvas_to_handwriting()
        
        # Save the cropped image
        cropped_image.save(temp_path)
        
        # Convert using parent's API manager
        if (self.parent_window and 
            hasattr(self.parent_window, 'api_manager') and 
            self.parent_window.api_manager.is_configured()):
            
            # Store reference to the thread for proper cleanup
            self.conversion_thread = self.parent_window.api_manager.convert_image_to_latex(
                temp_path, 
                self.on_latex_result,
                self.on_latex_error
            )
    
    def on_latex_result(self, latex_text: str):
        """Handle LaTeX conversion result"""
        self.latex_text = latex_text
        self.latex_edit.setText(latex_text)
        self.update_preview()
        
        # Clear the thread reference since it's finished
        self.conversion_thread = None
    
    def on_latex_error(self, error_text: str):
        """Handle LaTeX conversion error"""
        print(f"LaTeX conversion error: {error_text}")
        self.latex_edit.setText(f"Error: {error_text}")
        
        # Clear the thread reference since it's finished
        self.conversion_thread = None
    
    def on_latex_changed(self):
        """Handle manual LaTeX text changes"""
        self.latex_text = self.latex_edit.toPlainText()
        QTimer.singleShot(500, self.update_preview)  # Debounced update
    
    def update_preview(self):
        """Update LaTeX preview"""
        if hasattr(self, 'preview_widget'):
            self.preview_widget.update_preview(self.latex_text)
    
    def copy_latex(self):
        """Copy LaTeX to clipboard"""
        if CLIPBOARD_AVAILABLE and self.latex_text:
            pyperclip.copy(self.latex_text)
            # Brief visual feedback
            original_style = self.copy_btn.styleSheet()
            self.copy_btn.setStyleSheet("background-color: lightgreen; border: 1px solid green; padding: 2px;")
            QTimer.singleShot(200, lambda: self.copy_btn.setStyleSheet(original_style))
    
    def close_overlay(self):
        """Close overlay and copy LaTeX if available"""
        # Clean up any running conversion thread
        if hasattr(self, 'conversion_thread') and self.conversion_thread and self.conversion_thread.isRunning():
            self.conversion_thread.quit()
            self.conversion_thread.wait(2000)  # Wait up to 2 seconds for thread to finish
        
        if self.latex_text and CLIPBOARD_AVAILABLE:
            pyperclip.copy(self.latex_text)
        self.releaseKeyboard()
        self.close()
    
    def close_and_copy(self):
        """Close overlay and copy LaTeX to clipboard"""
        if self.latex_text and CLIPBOARD_AVAILABLE:
            pyperclip.copy(self.latex_text)
        self.releaseKeyboard()
        self.close()
