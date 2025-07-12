"""
Unit tests for single instance management

Tests the SingleInstanceManager class to ensure proper single instance
enforcement across multiple application launches.
"""

import unittest
import tempfile
import os
import time
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ink2tex.core.single_instance import SingleInstanceManager, check_single_instance


class TestSingleInstanceManager(unittest.TestCase):
    """Test SingleInstanceManager class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_app_name = "TestInk2TeX"
        
        # Create manager with custom temp directory
        self.manager = SingleInstanceManager(self.test_app_name)
        
        # Override lock file path to use our temp directory
        self.test_lock_file = self.temp_dir / f"{self.test_app_name.lower()}_instance.lock"
        self.manager.lock_file_path = self.test_lock_file
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.manager.is_locked:
            self.manager.release_lock()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_acquire_lock_first_time(self):
        """Test acquiring lock when no other instance exists"""
        result = self.manager.acquire_lock()
        
        self.assertTrue(result)
        self.assertTrue(self.manager.is_locked)
        self.assertTrue(self.test_lock_file.exists())
        
        # Verify lock file content
        with open(self.test_lock_file, 'r') as f:
            lock_data = json.load(f)
        
        self.assertEqual(lock_data['pid'], os.getpid())
        self.assertIn('timestamp', lock_data)
        self.assertEqual(lock_data['executable'], sys.executable)
    
    def test_acquire_lock_with_stale_lock(self):
        """Test acquiring lock when a stale lock file exists"""
        # Create a stale lock file with non-existent PID
        stale_lock_data = {
            'pid': 999999,  # Non-existent PID
            'timestamp': time.time() - 3600,  # Old timestamp
            'executable': sys.executable,
            'cmdline': 'old_command'
        }
        
        with open(self.test_lock_file, 'w') as f:
            json.dump(stale_lock_data, f)
        
        # Should be able to acquire lock (removing stale lock)
        result = self.manager.acquire_lock()
        
        self.assertTrue(result)
        self.assertTrue(self.manager.is_locked)
        
        # Verify new lock file content
        with open(self.test_lock_file, 'r') as f:
            lock_data = json.load(f)
        
        self.assertEqual(lock_data['pid'], os.getpid())
        self.assertNotEqual(lock_data['pid'], 999999)
    
    @patch('ink2tex.core.single_instance.psutil.pid_exists')
    @patch('ink2tex.core.single_instance.psutil.Process')
    def test_acquire_lock_with_running_instance(self, mock_process_class, mock_pid_exists):
        """Test acquiring lock when another instance is running"""
        # Create a lock file for a "running" process
        existing_pid = 12345
        existing_lock_data = {
            'pid': existing_pid,
            'timestamp': time.time(),
            'executable': sys.executable,
            'cmdline': 'ink2tex main.py'
        }
        
        with open(self.test_lock_file, 'w') as f:
            json.dump(existing_lock_data, f)
        
        # Mock process exists and is our application
        mock_pid_exists.return_value = True
        mock_process = MagicMock()
        mock_process.exe.return_value = sys.executable
        mock_process.cmdline.return_value = ['python', 'main.py', '--ink2tex']
        mock_process_class.return_value = mock_process
        
        # Should NOT be able to acquire lock
        result = self.manager.acquire_lock()
        
        self.assertFalse(result)
        self.assertFalse(self.manager.is_locked)
    
    def test_release_lock(self):
        """Test releasing the lock"""
        # First acquire lock
        self.manager.acquire_lock()
        self.assertTrue(self.test_lock_file.exists())
        
        # Then release it
        self.manager.release_lock()
        
        self.assertFalse(self.manager.is_locked)
        self.assertFalse(self.test_lock_file.exists())
    
    def test_is_process_running_nonexistent_pid(self):
        """Test process running check with non-existent PID"""
        # Create lock file with non-existent PID
        lock_data = {
            'pid': 999999,
            'timestamp': time.time(),
            'executable': sys.executable,
            'cmdline': 'test'
        }
        
        with open(self.test_lock_file, 'w') as f:
            json.dump(lock_data, f)
        
        result = self.manager._is_process_running()
        self.assertFalse(result)
    
    def test_is_process_running_different_executable(self):
        """Test process running check with different executable"""
        with patch('ink2tex.core.single_instance.psutil.pid_exists') as mock_pid_exists, \
             patch('ink2tex.core.single_instance.psutil.Process') as mock_process_class:
            
            # Create lock file with current PID but different executable
            lock_data = {
                'pid': os.getpid(),
                'timestamp': time.time(),
                'executable': '/different/executable',
                'cmdline': 'different_app'
            }
            
            with open(self.test_lock_file, 'w') as f:
                json.dump(lock_data, f)
            
            # Mock process exists but is different executable
            mock_pid_exists.return_value = True
            mock_process = MagicMock()
            mock_process.exe.return_value = '/different/executable'
            mock_process_class.return_value = mock_process
            
            result = self.manager._is_process_running()
            self.assertFalse(result)
    
    def test_malformed_lock_file(self):
        """Test handling of malformed lock file"""
        # Create malformed lock file
        with open(self.test_lock_file, 'w') as f:
            f.write("invalid json content")
        
        result = self.manager._is_process_running()
        self.assertFalse(result)
        
        # Should be able to acquire lock despite malformed file
        result = self.manager.acquire_lock()
        self.assertTrue(result)


class TestCheckSingleInstance(unittest.TestCase):
    """Test the check_single_instance function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('ink2tex.core.single_instance.SingleInstanceManager')
    def test_check_single_instance_success(self, mock_manager_class):
        """Test successful single instance check"""
        # Mock manager that acquires lock successfully
        mock_manager = MagicMock()
        mock_manager.acquire_lock.return_value = True
        mock_manager_class.return_value = mock_manager
        
        result = check_single_instance("TestApp")
        
        self.assertEqual(result, mock_manager)
        mock_manager.acquire_lock.assert_called_once()
    
    @patch('ink2tex.core.single_instance.SingleInstanceManager')
    @patch('sys.exit')
    def test_check_single_instance_failure(self, mock_exit, mock_manager_class):
        """Test single instance check when another instance exists"""
        # Mock manager that fails to acquire lock
        mock_manager = MagicMock()
        mock_manager.acquire_lock.return_value = False
        mock_manager.send_message_to_existing_instance.return_value = True
        mock_manager_class.return_value = mock_manager
        
        check_single_instance("TestApp")
        
        # Should call sys.exit(1)
        mock_exit.assert_called_once_with(1)
        mock_manager.send_message_to_existing_instance.assert_called_once()


if __name__ == '__main__':
    unittest.main()
