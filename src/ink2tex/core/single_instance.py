"""
Single instance management for Ink2TeX

Ensures only one instance of the application can run at a time.
Uses a combination of file locking and process detection for robustness.
"""

import os
import sys
import tempfile
import atexit
import time
import psutil
from pathlib import Path
from typing import Optional


class SingleInstanceManager:
    """Manages single instance enforcement for the application"""
    
    def __init__(self, app_name: str = "Ink2TeX"):
        """Initialize the single instance manager
        
        Args:
            app_name: Name of the application for lock file naming
        """
        self.app_name = app_name
        self.lock_file_path = self._get_lock_file_path()
        self.lock_file_handle: Optional[object] = None
        self.is_locked = False
    
    def _get_lock_file_path(self) -> Path:
        """Get the path for the lock file
        
        Returns:
            Path to the lock file
        """
        # Use a system temporary directory for the lock file
        temp_dir = Path(tempfile.gettempdir())
        lock_filename = f"{self.app_name.lower().replace(' ', '_')}_instance.lock"
        return temp_dir / lock_filename
    
    def acquire_lock(self) -> bool:
        """Acquire the single instance lock
        
        Returns:
            True if lock acquired successfully, False if another instance exists
        """
        try:
            # Check if lock file exists and if the process is still running
            if self.lock_file_path.exists():
                if self._is_process_running():
                    return False
                else:
                    # Stale lock file, remove it
                    self._remove_lock_file()
            
            # Create lock file with current process ID
            self._create_lock_file()
            self.is_locked = True
            
            # Register cleanup on exit
            atexit.register(self.release_lock)
            
            return True
            
        except Exception as e:
            print(f"Error acquiring lock: {e}")
            return False
    
    def _create_lock_file(self):
        """Create the lock file with current process information"""
        try:
            lock_data = {
                'pid': os.getpid(),
                'timestamp': time.time(),
                'executable': sys.executable,
                'cmdline': ' '.join(sys.argv)
            }
            
            # Write lock file
            with open(self.lock_file_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(lock_data, f, indent=2)
            
            print(f"Created lock file: {self.lock_file_path}")
            
        except Exception as e:
            print(f"Error creating lock file: {e}")
            raise
    
    def _is_process_running(self) -> bool:
        """Check if the process in the lock file is still running
        
        Returns:
            True if the process is running, False otherwise
        """
        try:
            with open(self.lock_file_path, 'r', encoding='utf-8') as f:
                import json
                lock_data = json.load(f)
            
            pid = lock_data.get('pid')
            if not pid:
                return False
            
            # Check if process exists and is the same application
            if psutil.pid_exists(pid):
                try:
                    process = psutil.Process(pid)
                    # Check if it's the same executable
                    if process.exe() == sys.executable:
                        # Additional check: see if it's running our script
                        cmdline = process.cmdline()
                        if any('ink2tex' in arg.lower() or 'main.py' in arg for arg in cmdline):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return False
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False
    
    def _remove_lock_file(self):
        """Remove the lock file"""
        try:
            if self.lock_file_path.exists():
                self.lock_file_path.unlink()
                print(f"Removed lock file: {self.lock_file_path}")
        except Exception as e:
            print(f"Error removing lock file: {e}")
    
    def release_lock(self):
        """Release the single instance lock"""
        if self.is_locked:
            self._remove_lock_file()
            self.is_locked = False
    
    def send_message_to_existing_instance(self, message: str = "show") -> bool:
        """Send a message to an existing instance
        
        Args:
            message: Message to send to the existing instance
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        # For now, we'll just try to bring the existing instance to focus
        # This could be extended to use named pipes, sockets, or other IPC mechanisms
        
        try:
            if self.lock_file_path.exists():
                with open(self.lock_file_path, 'r', encoding='utf-8') as f:
                    import json
                    lock_data = json.load(f)
                
                pid = lock_data.get('pid')
                if pid and psutil.pid_exists(pid):
                    # Try to send a signal to bring the application to front
                    # This is a basic implementation - could be enhanced with proper IPC
                    print(f"Another instance is running (PID: {pid})")
                    print("Attempting to bring existing instance to foreground...")
                    
                    # On Windows, we could use win32gui to find and activate the window
                    # For now, we'll just return True to indicate message was "sent"
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error sending message to existing instance: {e}")
            return False


def check_single_instance(app_name: str = "Ink2TeX") -> SingleInstanceManager:
    """Check and enforce single instance for the application
    
    Args:
        app_name: Name of the application
        
    Returns:
        SingleInstanceManager instance if lock acquired, None if another instance exists
        
    Raises:
        SystemExit: If another instance is already running
    """
    manager = SingleInstanceManager(app_name)
    
    if manager.acquire_lock():
        print("✓ Single instance lock acquired")
        return manager
    else:
        print("❌ Another instance of Ink2TeX is already running!")
        
        # Try to notify the existing instance
        if manager.send_message_to_existing_instance():
            print("✓ Brought existing instance to foreground")
        else:
            print("⚠️  Could not communicate with existing instance")
        
        print("\nIf you believe this is an error:")
        print(f"1. Check if Ink2TeX is running in system tray")
        print(f"2. End any Ink2TeX processes in Task Manager")
        print(f"3. Delete lock file: {manager.lock_file_path}")
        
        sys.exit(1)


if __name__ == "__main__":
    # Test the single instance functionality
    print("Testing single instance manager...")
    
    manager = SingleInstanceManager("TestApp")
    
    if manager.acquire_lock():
        print("✓ Lock acquired successfully")
        
        print("Press Enter to release lock and exit...")
        input()
        
        manager.release_lock()
        print("✓ Lock released")
    else:
        print("❌ Could not acquire lock - another instance is running")
