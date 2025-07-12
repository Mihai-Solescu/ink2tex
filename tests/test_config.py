"""
Unit tests for configuration management

Tests the ConfigManager and ConfigReader classes to ensure proper
cross-platform configuration file handling.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ink2tex.core.config import ConfigManager, ConfigReader


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_portable_mode_with_api_file(self):
        """Test portable mode detection when .api file exists"""
        # Create a temporary .api file
        api_file = Path(self.temp_dir) / '.api'
        api_file.write_text('GOOGLE_API_KEY=test_key')
        
        with patch('ink2tex.core.config.Path.cwd', return_value=Path(self.temp_dir)):
            result = self.config_manager._detect_portable_mode()
            self.assertTrue(result)
    
    def test_detect_portable_mode_without_api_file(self):
        """Test portable mode detection when .api file doesn't exist"""
        with patch('ink2tex.core.config.Path.cwd', return_value=Path(self.temp_dir)):
            result = self.config_manager._detect_portable_mode()
            self.assertFalse(result)
    
    def test_get_config_directories_portable(self):
        """Test config directories in portable mode"""
        with patch.object(self.config_manager, '_detect_portable_mode', return_value=True):
            with patch('ink2tex.core.config.Path.cwd', return_value=Path(self.temp_dir)):
                dirs = self.config_manager.get_config_directories()
                self.assertEqual(len(dirs), 1)
                self.assertEqual(dirs[0], Path(self.temp_dir))
    
    @patch('platform.system')
    def test_get_config_directories_windows(self, mock_system):
        """Test config directories on Windows"""
        mock_system.return_value = 'Windows'
        
        with patch.object(self.config_manager, '_detect_portable_mode', return_value=False):
            with patch.dict(os.environ, {'APPDATA': str(self.temp_dir)}):
                dirs = self.config_manager.get_config_directories()
                expected_dir = Path(self.temp_dir) / 'Ink2TeX'
                self.assertIn(expected_dir, dirs)
    
    def test_find_config_file_exists(self):
        """Test finding existing config file"""
        # Create test config file
        config_file = Path(self.temp_dir) / '.api'
        config_file.write_text('GOOGLE_API_KEY=test_key')
        
        with patch.object(self.config_manager, 'get_config_directories', return_value=[Path(self.temp_dir)]):
            result = self.config_manager.find_config_file('.api')
            self.assertEqual(result, str(config_file))
    
    def test_find_config_file_not_exists(self):
        """Test finding non-existent config file"""
        with patch.object(self.config_manager, 'get_config_directories', return_value=[Path(self.temp_dir)]):
            result = self.config_manager.find_config_file('.nonexistent')
            self.assertIsNone(result)


class TestConfigReader(unittest.TestCase):
    """Test ConfigReader class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_read_api_key_valid(self):
        """Test reading valid API key from config"""
        # Create test API config file
        api_file = Path(self.temp_dir) / '.api'
        api_file.write_text('GOOGLE_API_KEY=test_api_key_123')
        
        with patch.object(ConfigReader, '_get_manager') as mock_manager_getter:
            mock_manager = MagicMock()
            mock_manager.find_config_file.return_value = str(api_file)
            mock_manager_getter.return_value = mock_manager
            
            result = ConfigReader.read_api_key_from_config()
            self.assertEqual(result, 'test_api_key_123')
    
    def test_read_api_key_with_comments(self):
        """Test reading API key from config with comments"""
        # Create test API config file with comments
        api_content = '''# Google Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=test_api_key_456
# This is a comment
'''
        api_file = Path(self.temp_dir) / '.api'
        api_file.write_text(api_content)
        
        with patch.object(ConfigReader, '_get_manager') as mock_manager_getter:
            mock_manager = MagicMock()
            mock_manager.find_config_file.return_value = str(api_file)
            mock_manager_getter.return_value = mock_manager
            
            result = ConfigReader.read_api_key_from_config()
            self.assertEqual(result, 'test_api_key_456')
    
    def test_read_api_key_file_not_found(self):
        """Test handling when API config file doesn't exist"""
        with patch.object(ConfigReader, '_get_manager') as mock_manager_getter:
            mock_manager = MagicMock()
            mock_manager.find_config_file.return_value = None
            mock_manager.create_default_config_files.return_value = {}
            mock_manager_getter.return_value = mock_manager
            
            with self.assertRaises(FileNotFoundError):
                ConfigReader.read_api_key_from_config()
    
    def test_read_api_key_invalid_format(self):
        """Test handling invalid API key format"""
        # Create test API config file with invalid format
        api_file = Path(self.temp_dir) / '.api'
        api_file.write_text('# No API key here\nsome_other_setting=value')
        
        with patch.object(ConfigReader, '_get_manager') as mock_manager_getter:
            mock_manager = MagicMock()
            mock_manager.find_config_file.return_value = str(api_file)
            mock_manager_getter.return_value = mock_manager
            
            with self.assertRaises(ValueError):
                ConfigReader.read_api_key_from_config()


if __name__ == '__main__':
    unittest.main()
