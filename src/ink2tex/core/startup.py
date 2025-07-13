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
Windows startup management for Ink2TeX.
Handles Windows registry entries for auto-start functionality.
"""

import os
import sys
from typing import Optional

# Windows registry import with fallback
try:
    import winreg
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False


class WindowsStartupManager:
    """Manages Windows startup registry entries for auto-start functionality"""
    
    APP_NAME = "Ink2TeX"
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    @staticmethod
    def is_startup_enabled() -> bool:
        """Check if auto-startup is enabled in Windows registry
        
        Returns:
            True if auto-startup is enabled, False otherwise
        """
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, WindowsStartupManager.APP_NAME)
                return bool(value)
        except (FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def enable_startup() -> bool:
        """Enable auto-startup by adding registry entry
        
        Returns:
            True if successful, False otherwise
        """
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            # Get the path to the current executable
            if getattr(sys, 'frozen', False):
                # Running as executable
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            
            # Add to registry
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, 
                            winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, WindowsStartupManager.APP_NAME, 0, winreg.REG_SZ, exe_path)
            
            return True
        except Exception as e:
            print(f"Failed to enable startup: {e}")
            return False
    
    @staticmethod
    def disable_startup() -> bool:
        """Disable auto-startup by removing registry entry
        
        Returns:
            True if successful, False otherwise
        """
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, 
                            winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, WindowsStartupManager.APP_NAME)
            return True
        except (FileNotFoundError, OSError):
            return True  # Already disabled
        except Exception as e:
            print(f"Failed to disable startup: {e}")
            return False
    
    @staticmethod
    def toggle_startup() -> bool:
        """Toggle auto-startup setting
        
        Returns:
            True if successful, False otherwise
        """
        if WindowsStartupManager.is_startup_enabled():
            return WindowsStartupManager.disable_startup()
        else:
            return WindowsStartupManager.enable_startup()
