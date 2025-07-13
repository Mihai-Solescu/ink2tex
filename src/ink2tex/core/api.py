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
Google Gemini API handling for Ink2TeX.
Manages image-to-LaTeX conversion using Google's Generative AI.
"""

import os
from typing import Optional

# Heavy imports are done locally within methods to prevent PyInstaller issues
from PyQt6.QtCore import QThread, pyqtSignal


class ConversionThread(QThread):
    """Thread for handling Gemini API conversion without blocking UI"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, image_path: str, model):
        """Initialize the conversion thread
        
        Args:
            image_path: Path to the image file to convert
            model: Configured Gemini model instance
        """
        super().__init__()
        self.image_path = image_path
        self.model = model
    
    def run(self):
        """Run the conversion in a separate thread"""
        try:
            # Import heavy dependencies locally to avoid PyInstaller issues
            from PIL import Image
            from ink2tex.core.config import ConfigReader
            
            # Load image
            img = Image.open(self.image_path)
            
            # Load prompt from file
            prompt = ConfigReader.read_prompt_from_file()
            
            # Send request to Gemini
            response = self.model.generate_content([prompt, img])
            self.finished.emit(response.text)
            
        except Exception as e:
            self.error.emit(str(e))


class GeminiAPIManager:
    """Manager for Google Gemini API operations"""
    
    def __init__(self):
        """Initialize the API manager"""
        self.model = None
        self.configured = False
    
    def configure_api(self, api_key: str) -> bool:
        """Configure the Gemini API with the provided key
        
        Args:
            api_key: Google Gemini API key
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # Import heavy dependencies locally
            import google.generativeai as genai
            
            print("Configuring Gemini API...")
            
            # Configure API with timeout-like behavior
            # We'll catch any hanging issues by using a simple approach
            genai.configure(api_key=api_key)
            
            # Try to create a model - start with the most stable one
            print("Creating Gemini model...")
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.configured = True
            print("✓ Gemini API configured successfully with gemini-1.5-flash!")
            return True
            
        except ImportError as e:
            print(f"❌ Missing google-generativeai package: {str(e)}")
            self.configured = False
            return False
        except Exception as e:
            print(f"❌ API setup failed: {str(e)}")
            # Common issues and suggestions
            error_str = str(e).lower()
            if "api" in error_str and "key" in error_str:
                print("💡 Tip: Check that your API key in .api file is valid")
            elif "network" in error_str or "connection" in error_str:
                print("💡 Tip: Check your internet connection")
            elif "quota" in error_str or "limit" in error_str:
                print("💡 Tip: You may have exceeded your API quota")
            
            self.configured = False
            return False
    
    def is_configured(self) -> bool:
        """Check if API is properly configured
        
        Returns:
            True if API is configured, False otherwise
        """
        return self.configured and self.model is not None
    
    def convert_image_to_latex(self, image_path: str, callback_success, callback_error) -> Optional[ConversionThread]:
        """Convert image to LaTeX using Gemini API
        
        Args:
            image_path: Path to the image file
            callback_success: Callback function for successful conversion
            callback_error: Callback function for errors
            
        Returns:
            ConversionThread instance if started successfully, None otherwise
        """
        if not self.is_configured():
            callback_error("Gemini API not configured")
            return None
            
        try:
            # Start conversion in a separate thread
            conversion_thread = ConversionThread(image_path, self.model)
            conversion_thread.finished.connect(callback_success)
            conversion_thread.error.connect(callback_error)
            conversion_thread.start()
            return conversion_thread
        except Exception as e:
            callback_error(f"Failed to start conversion: {e}")
            return None
