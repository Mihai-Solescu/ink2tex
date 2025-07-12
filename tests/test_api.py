"""
Unit tests for API management

Tests the GeminiAPIManager class to ensure proper API configuration
and image-to-LaTeX conversion functionality.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, Mock
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestGeminiAPIManager(unittest.TestCase):
    """Test GeminiAPIManager class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import here to avoid issues with module loading
        from ink2tex.core.api import GeminiAPIManager
        self.api_manager = GeminiAPIManager()
    
    def test_initial_state(self):
        """Test initial state of API manager"""
        self.assertFalse(self.api_manager.configured)
        self.assertIsNone(self.api_manager.model)
        self.assertFalse(self.api_manager.is_configured())
    
    @patch('ink2tex.core.api.genai')
    def test_configure_api_success(self, mock_genai):
        """Test successful API configuration"""
        # Setup mock
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test configuration
        result = self.api_manager.configure_api('test_api_key')
        
        # Verify results
        self.assertTrue(result)
        self.assertTrue(self.api_manager.configured)
        self.assertEqual(self.api_manager.model, mock_model)
        self.assertTrue(self.api_manager.is_configured())
        
        # Verify API calls
        mock_genai.configure.assert_called_once_with(api_key='test_api_key')
        mock_genai.GenerativeModel.assert_called_once_with('gemini-1.5-flash')
    
    @patch('ink2tex.core.api.genai')
    def test_configure_api_failure(self, mock_genai):
        """Test API configuration failure"""
        # Setup mock to raise exception
        mock_genai.configure.side_effect = Exception("API configuration failed")
        
        # Test configuration
        result = self.api_manager.configure_api('invalid_key')
        
        # Verify results
        self.assertFalse(result)
        self.assertFalse(self.api_manager.configured)
        self.assertIsNone(self.api_manager.model)
        self.assertFalse(self.api_manager.is_configured())
    
    @patch('ink2tex.core.api.genai')
    def test_configure_api_import_error(self, mock_genai):
        """Test API configuration with import error"""
        # Setup mock to raise ImportError
        mock_genai.configure.side_effect = ImportError("google-generativeai not found")
        
        # Test configuration
        result = self.api_manager.configure_api('test_key')
        
        # Verify results
        self.assertFalse(result)
        self.assertFalse(self.api_manager.configured)
    
    def test_convert_image_not_configured(self):
        """Test image conversion when API is not configured"""
        callback_success = MagicMock()
        callback_error = MagicMock()
        
        result = self.api_manager.convert_image_to_latex(
            "test_image.png", callback_success, callback_error
        )
        
        # Should return None and call error callback
        self.assertIsNone(result)
        callback_error.assert_called_once_with("Gemini API not configured")
        callback_success.assert_not_called()
    
    @patch('ink2tex.core.api.ConversionThread')
    def test_convert_image_success(self, mock_thread_class):
        """Test successful image conversion"""
        # Setup API manager as configured
        self.api_manager.configured = True
        self.api_manager.model = MagicMock()
        
        # Setup mock thread
        mock_thread = MagicMock()
        mock_thread_class.return_value = mock_thread
        
        callback_success = MagicMock()
        callback_error = MagicMock()
        
        result = self.api_manager.convert_image_to_latex(
            "test_image.png", callback_success, callback_error
        )
        
        # Verify thread creation and setup
        self.assertEqual(result, mock_thread)
        mock_thread_class.assert_called_once_with("test_image.png", self.api_manager.model)
        mock_thread.finished.connect.assert_called_once_with(callback_success)
        mock_thread.error.connect.assert_called_once_with(callback_error)
        mock_thread.start.assert_called_once()
    
    @patch('ink2tex.core.api.ConversionThread')
    def test_convert_image_thread_exception(self, mock_thread_class):
        """Test image conversion with thread creation exception"""
        # Setup API manager as configured
        self.api_manager.configured = True
        self.api_manager.model = MagicMock()
        
        # Setup mock to raise exception
        mock_thread_class.side_effect = Exception("Thread creation failed")
        
        callback_success = MagicMock()
        callback_error = MagicMock()
        
        result = self.api_manager.convert_image_to_latex(
            "test_image.png", callback_success, callback_error
        )
        
        # Should return None and call error callback
        self.assertIsNone(result)
        callback_error.assert_called_once_with("Failed to start conversion: Thread creation failed")
        callback_success.assert_not_called()


class TestConversionThread(unittest.TestCase):
    """Test ConversionThread class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        from ink2tex.core.api import ConversionThread
        self.mock_model = MagicMock()
        self.temp_dir = tempfile.mkdtemp()
        self.test_image = os.path.join(self.temp_dir, 'test.png')
        
        # Create a dummy image file
        with open(self.test_image, 'wb') as f:
            f.write(b'fake_image_data')
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('ink2tex.core.api.Image')
    @patch('ink2tex.core.api.ConfigReader')
    def test_conversion_success(self, mock_config_reader, mock_image):
        """Test successful image conversion"""
        from ink2tex.core.api import ConversionThread
        
        # Setup mocks
        mock_img = MagicMock()
        mock_image.open.return_value = mock_img
        mock_config_reader.read_prompt_from_file.return_value = "test prompt"
        
        mock_response = MagicMock()
        mock_response.text = "x^2 + y^2 = z^2"
        self.mock_model.generate_content.return_value = mock_response
        
        # Create thread
        thread = ConversionThread(self.test_image, self.mock_model)
        
        # Mock the signals
        thread.finished = MagicMock()
        thread.error = MagicMock()
        
        # Run the conversion
        thread.run()
        
        # Verify the results
        thread.finished.emit.assert_called_once_with("x^2 + y^2 = z^2")
        thread.error.emit.assert_not_called()
        
        # Verify API calls
        mock_image.open.assert_called_once_with(self.test_image)
        self.mock_model.generate_content.assert_called_once_with(["test prompt", mock_img])
    
    @patch('ink2tex.core.api.Image')
    def test_conversion_image_error(self, mock_image):
        """Test image conversion with image loading error"""
        from ink2tex.core.api import ConversionThread
        
        # Setup mock to raise exception
        mock_image.open.side_effect = Exception("Cannot open image")
        
        # Create thread
        thread = ConversionThread(self.test_image, self.mock_model)
        
        # Mock the signals
        thread.finished = MagicMock()
        thread.error = MagicMock()
        
        # Run the conversion
        thread.run()
        
        # Verify error handling
        thread.error.emit.assert_called_once_with("Cannot open image")
        thread.finished.emit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
