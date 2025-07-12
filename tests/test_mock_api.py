#!/usr/bin/env python3
"""Mock API manager for testing without network dependencies"""

import sys
import os
import time
from PyQt6.QtCore import QThread, pyqtSignal

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class MockConversionThread(QThread):
    """Mock conversion thread that simulates LaTeX generation"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
    
    def run(self):
        """Simulate conversion with a delay"""
        try:
            # Simulate processing time
            time.sleep(2)
            
            # Return mock LaTeX
            mock_latex = r"\frac{d}{dx}[x^2] = 2x"
            self.finished.emit(mock_latex)
            
        except Exception as e:
            self.error.emit(str(e))

class MockGeminiAPIManager:
    """Mock API manager for testing"""
    
    def __init__(self):
        self.configured = True  # Always configured for testing
    
    def configure_api(self, api_key: str) -> bool:
        """Mock configuration - always succeeds"""
        print("✓ Mock API configured successfully!")
        self.configured = True
        return True
    
    def is_configured(self) -> bool:
        """Mock configuration check"""
        return self.configured
    
    def convert_image_to_latex(self, image_path: str, callback_success, callback_error):
        """Mock conversion"""
        print(f"Mock: Converting {image_path} to LaTeX...")
        thread = MockConversionThread(image_path)
        thread.finished.connect(callback_success)
        thread.error.connect(callback_error)
        thread.start()
        return thread

# Test the mock
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    def on_success(latex):
        print(f"Success: {latex}")
        app.quit()
    
    def on_error(error):
        print(f"Error: {error}")
        app.quit()
    
    # Test mock API
    api = MockGeminiAPIManager()
    print(f"Configured: {api.is_configured()}")
    
    # Test conversion
    api.convert_image_to_latex("test.png", on_success, on_error)
    
    app.exec()
