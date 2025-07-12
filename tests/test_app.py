"""
Unit tests for main application functionality

Tests the SystemTrayApp class to ensure proper application lifecycle,
system tray integration, and component initialization.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSystemTrayApp(unittest.TestCase):
    """Test SystemTrayApp class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Ensure QApplication exists for tests
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up any created overlays or windows
        pass
    
    @patch('ink2tex.app.QSystemTrayIcon.isSystemTrayAvailable')
    @patch('ink2tex.app.GeminiAPIManager')
    @patch('ink2tex.app.ConfigReader')
    def test_app_initialization(self, mock_config_reader, mock_api_manager_class, mock_tray_available):
        """Test application initialization"""
        from ink2tex.app import SystemTrayApp
        
        # Setup mocks
        mock_tray_available.return_value = True
        mock_api_manager = MagicMock()
        mock_api_manager_class.return_value = mock_api_manager
        mock_config_reader.read_api_key_from_config.return_value = "test_api_key"
        
        # Create app instance
        with patch.object(SystemTrayApp, 'setup_system_tray'), \
             patch.object(SystemTrayApp, 'setup_global_hotkeys'), \
             patch.object(SystemTrayApp, 'apply_startup_settings'):
            
            app = SystemTrayApp()
            
            # Verify initialization
            self.assertIsNotNone(app.api_manager)
            self.assertIsNone(app.overlay)
            self.assertIsNone(app.settings_window)
    
    @patch('ink2tex.app.QSystemTrayIcon.isSystemTrayAvailable')
    @patch('ink2tex.app.GeminiAPIManager')
    @patch('ink2tex.app.ConfigReader')
    def test_api_configuration_success(self, mock_config_reader, mock_api_manager_class, mock_tray_available):
        """Test successful API configuration"""
        from ink2tex.app import SystemTrayApp
        
        # Setup mocks
        mock_tray_available.return_value = True
        mock_api_manager = MagicMock()
        mock_api_manager.configure_api.return_value = True
        mock_api_manager_class.return_value = mock_api_manager
        mock_config_reader.read_api_key_from_config.return_value = "valid_api_key"
        
        # Create app instance
        with patch.object(SystemTrayApp, 'setup_system_tray'), \
             patch.object(SystemTrayApp, 'setup_global_hotkeys'), \
             patch.object(SystemTrayApp, 'apply_startup_settings'):
            
            app = SystemTrayApp()
            
            # Verify API configuration was attempted
            mock_api_manager.configure_api.assert_called_once_with("valid_api_key")
    
    @patch('ink2tex.app.QSystemTrayIcon.isSystemTrayAvailable')
    @patch('ink2tex.app.GeminiAPIManager')
    @patch('ink2tex.app.ConfigReader')
    def test_api_configuration_failure(self, mock_config_reader, mock_api_manager_class, mock_tray_available):
        """Test API configuration failure handling"""
        from ink2tex.app import SystemTrayApp
        
        # Setup mocks
        mock_tray_available.return_value = True
        mock_api_manager = MagicMock()
        mock_api_manager.configure_api.return_value = False
        mock_api_manager_class.return_value = mock_api_manager
        mock_config_reader.read_api_key_from_config.return_value = "invalid_api_key"
        
        # Create app instance
        with patch.object(SystemTrayApp, 'setup_system_tray'), \
             patch.object(SystemTrayApp, 'setup_global_hotkeys'), \
             patch.object(SystemTrayApp, 'apply_startup_settings'), \
             patch.object(SystemTrayApp, 'show_message') as mock_show_message:
            
            app = SystemTrayApp()
            
            # Verify error message was shown
            mock_show_message.assert_called()
    
    @patch('ink2tex.app.QSystemTrayIcon.isSystemTrayAvailable')
    @patch('ink2tex.app.GeminiAPIManager')
    @patch('ink2tex.app.ConfigReader')
    def test_overlay_creation(self, mock_config_reader, mock_api_manager_class, mock_tray_available):
        """Test overlay creation"""
        from ink2tex.app import SystemTrayApp
        
        # Setup mocks
        mock_tray_available.return_value = True
        mock_api_manager = MagicMock()
        mock_api_manager_class.return_value = mock_api_manager
        mock_config_reader.read_api_key_from_config.return_value = "test_api_key"
        
        # Create app instance
        with patch.object(SystemTrayApp, 'setup_system_tray'), \
             patch.object(SystemTrayApp, 'setup_global_hotkeys'), \
             patch.object(SystemTrayApp, 'apply_startup_settings'):
            
            app = SystemTrayApp()
            
            # Test overlay creation
            with patch('ink2tex.app.QTimer.singleShot') as mock_timer:
                app.open_overlay()
                
                # Verify timer was set to defer overlay creation
                mock_timer.assert_called_once_with(50, app._create_overlay)
    
    @patch('ink2tex.app.QSystemTrayIcon.isSystemTrayAvailable')
    @patch('ink2tex.app.GeminiAPIManager')
    @patch('ink2tex.app.ConfigReader')
    @patch('ink2tex.app.TransparentOverlay')
    def test_create_overlay(self, mock_overlay_class, mock_config_reader, mock_api_manager_class, mock_tray_available):
        """Test actual overlay creation"""
        from ink2tex.app import SystemTrayApp
        
        # Setup mocks
        mock_tray_available.return_value = True
        mock_api_manager = MagicMock()
        mock_api_manager_class.return_value = mock_api_manager
        mock_config_reader.read_api_key_from_config.return_value = "test_api_key"
        
        mock_overlay = MagicMock()
        mock_overlay_class.return_value = mock_overlay
        
        # Create app instance
        with patch.object(SystemTrayApp, 'setup_system_tray'), \
             patch.object(SystemTrayApp, 'setup_global_hotkeys'), \
             patch.object(SystemTrayApp, 'apply_startup_settings'):
            
            app = SystemTrayApp()
            
            # Test overlay creation
            app._create_overlay()
            
            # Verify overlay was created and configured
            mock_overlay_class.assert_called_once_with(app)
            mock_overlay.show.assert_called_once()
            mock_overlay.raise_.assert_called_once()
            mock_overlay.activateWindow.assert_called_once()
            mock_overlay.setFocus.assert_called_once()
            
            self.assertEqual(app.overlay, mock_overlay)


class TestSingleInstanceLock(unittest.TestCase):
    """Test single instance functionality"""
    
    def test_single_instance_detection(self):
        """Test that only one instance can run at a time"""
        # This would test the single instance mechanism
        # Implementation depends on the chosen approach (file lock, socket, etc.)
        pass


if __name__ == '__main__':
    unittest.main()
