"""
LaTeX preview widget for Ink2TeX.
Provides real-time rendering of LaTeX equations using matplotlib.
"""

from typing import Optional

# Heavy imports done locally to prevent PyInstaller issues
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class LaTeXPreviewWidget(QWidget):
    """Widget to preview rendered LaTeX using matplotlib"""
    
    def __init__(self):
        """Initialize the preview widget"""
        super().__init__()
        self.figure = None
        self.canvas = None
        self.initialized = False
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the preview UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("LaTeX Preview")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Placeholder that will be replaced with matplotlib canvas
        self.placeholder = QLabel("LaTeX preview will appear here\n(loads on first use)")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: gray; font-style: italic;")
        self.placeholder.setMinimumSize(300, 200)
        layout.addWidget(self.placeholder)
        
        # Clear button
        clear_btn = QPushButton("Clear Preview")
        clear_btn.clicked.connect(self.clear_preview)
        layout.addWidget(clear_btn)
    
    def _initialize_matplotlib(self):
        """Initialize matplotlib canvas on first use"""
        if self.initialized:
            return
            
        try:
            # Import matplotlib locally to avoid PyInstaller issues
            import matplotlib
            matplotlib.use('QtAgg')  # Use QtAgg for PyQt6 compatibility
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            
            # Create matplotlib canvas
            self.figure = Figure(figsize=(4, 3), facecolor='white', dpi=80)
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumSize(300, 200)
            
            # Replace placeholder with actual canvas
            layout = self.layout()
            layout.replaceWidget(self.placeholder, self.canvas)
            self.placeholder.hide()
            
            # Initialize with placeholder text
            ax = self.figure.add_subplot(111)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.text(0.1, 0.5, "LaTeX preview ready", 
                transform=ax.transAxes, fontsize=9, color='gray',
                ha='left', va='center')
            self.canvas.draw()
            
            self.initialized = True
            print("✓ LaTeX preview initialized")
            
        except Exception as e:
            print(f"Preview initialization warning: {e}")
        
    def update_preview(self, latex_text: str):
        """Update the LaTeX preview with error handling
        
        Args:
            latex_text: The LaTeX code to render
        """
        # Initialize matplotlib on first use
        if not self.initialized:
            self._initialize_matplotlib()
            if not self.initialized:
                return
        
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
            if self.initialized and self.figure:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.1, 0.5, f"Preview Error:\n{str(e)[:50]}...", 
                    transform=ax.transAxes, fontsize=9, color='red',
                    verticalalignment='center')
                ax.axis('off')
                self.canvas.draw()
    
    def clear_preview(self):
        """Clear the preview"""
        if not self.initialized:
            return
            
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.1, 0.5, "Preview cleared", 
                transform=ax.transAxes, fontsize=12, color='gray')
            ax.axis('off')
            self.canvas.draw()
        except Exception as e:
            print(f"Error clearing preview: {e}")
