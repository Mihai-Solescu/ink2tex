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
Resource management utilities for Ink2TeX.
Handles finding assets in both development and bundled environments.
"""

import os
import sys
from pathlib import Path
from typing import Optional


def get_resource_path(relative_path: str) -> Optional[Path]:
    """
    Get the absolute path to a resource file.
    
    This function works in both development and PyInstaller bundled environments.
    In development, it looks relative to the source directory.
    In bundled mode, it looks in the PyInstaller temporary directory.
    
    Args:
        relative_path: Path relative to the assets directory (e.g., 'icon.ico')
        
    Returns:
        Path object if the resource exists, None otherwise
    """
    try:
        # Get the base path - different for development vs bundled
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in PyInstaller bundle
            base_path = Path(sys._MEIPASS)
            # Look for the asset in the bundled location
            asset_path = base_path / 'src' / 'ink2tex' / 'assets' / relative_path
        else:
            # Running from source
            # Get the path to this file and navigate to assets
            current_file = Path(__file__)
            src_dir = current_file.parent.parent  # Go up from core/ to ink2tex/
            asset_path = src_dir / 'assets' / relative_path
        
        # Check if the file exists
        if asset_path.exists():
            return asset_path
        else:
            print(f"Warning: Resource not found: {asset_path}")
            return None
            
    except Exception as e:
        print(f"Error finding resource '{relative_path}': {e}")
        return None


def get_icon_path() -> Optional[Path]:
    """
    Get the path to the application icon.
    
    Returns:
        Path to icon.ico if it exists, None otherwise
    """
    return get_resource_path('icon.ico')


def get_icon_as_qicon():
    """
    Get the application icon as a QIcon object.
    
    Returns:
        QIcon object with the application icon, or None if not found
    """
    from PyQt6.QtGui import QIcon
    
    icon_path = get_icon_path()
    if icon_path:
        return QIcon(str(icon_path))
    else:
        print("Warning: Application icon not found, using default")
        return None


def create_fallback_icon():
    """
    Create a fallback icon when the main icon is not available.
    
    Returns:
        QIcon object with a generated icon
    """
    from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPen, QFont
    from PyQt6.QtCore import Qt
    
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
    
    return QIcon(pixmap)


def get_application_icon():
    """
    Get the application icon, with fallback to generated icon.
    
    Returns:
        QIcon object - either the real icon or a fallback
    """
    icon = get_icon_as_qicon()
    if icon is not None:
        print("✓ Application icon loaded successfully")
        return icon
    else:
        print("⚠️ Using fallback icon")
        return create_fallback_icon()
