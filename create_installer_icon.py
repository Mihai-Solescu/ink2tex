#!/usr/bin/env python3
"""
Generate a proper Windows ICO file for the installer
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def create_installer_icon():
    """Create a proper ICO file for the installer"""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPen, QFont
        from PyQt6.QtCore import Qt
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create icon at multiple sizes for proper ICO format
        sizes = [16, 24, 32, 48, 64, 128, 256]
        icon = QIcon()
        
        for size in sizes:
            # Create pixmap at this size
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Calculate proportional sizes
            border_width = max(1, size // 16)
            circle_margin = max(1, size // 8)
            font_size = max(8, size // 2)
            
            # Draw background circle
            painter.setBrush(QBrush(QColor(70, 130, 180)))  # Steel blue
            painter.setPen(QPen(QColor(25, 25, 112), border_width))  # Navy border
            painter.drawEllipse(circle_margin, circle_margin, 
                              size - 2*circle_margin, size - 2*circle_margin)
            
            # Draw LaTeX symbol
            painter.setPen(QPen(Qt.GlobalColor.white, border_width))
            font = QFont("Arial", font_size, QFont.Weight.Bold)
            painter.setFont(font)
            
            # Center the text
            text_rect = painter.fontMetrics().boundingRect("∫")
            x = (size - text_rect.width()) // 2
            y = (size + text_rect.height()) // 2
            painter.drawText(x, y, "∫")  # Integral symbol
            
            painter.end()
            
            # Add to icon
            icon.addPixmap(pixmap)
        
        # Save the icon
        output_path = Path("src/ink2tex/assets/installer_icon.ico")
        
        # Convert to ICO format by saving as pixmap and using system conversion
        # Get the largest size for conversion
        pixmap_256 = icon.pixmap(256, 256)
        
        # Save as ICO using Qt's built-in conversion
        success = pixmap_256.save(str(output_path), "ICO")
        
        if success:
            print(f"✓ Created installer icon: {output_path}")
            print(f"  - File size: {output_path.stat().st_size} bytes")
            return True
        else:
            print("❌ Failed to save ICO file")
            return False
            
    except Exception as e:
        print(f"❌ Error creating installer icon: {e}")
        return False
    finally:
        if 'app' in locals():
            app.quit()

if __name__ == "__main__":
    success = create_installer_icon()
    sys.exit(0 if success else 1)
