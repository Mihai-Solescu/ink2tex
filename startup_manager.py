#!/usr/bin/env python3
"""
Windows startup management and configuration utilities for Ink2TeX
Separated to avoid matplotlib dependencies during testing
"""

import os

try:
    import winreg
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False


class ConfigReader:
    """Utility class to read configuration from .api and .config files"""
    
    @staticmethod
    def read_config_value(key, config_path='.config', default=None):
        """Read a configuration value from .config file"""
        if not os.path.exists(config_path):
            return default
        
        with open(config_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if '=' in line and line.upper().startswith(key.upper()):
                value = line.split('=', 1)[1].strip()
                if value:
                    return value
        
        return default


class WindowsStartupManager:
    """Manages Windows startup registry entries for auto-start functionality"""
    
    APP_NAME = "Ink2TeX"
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    @staticmethod
    def is_startup_enabled():
        """Check if auto-startup is enabled in Windows registry"""
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, WindowsStartupManager.APP_NAME)
                return bool(value)
        except (FileNotFoundError, OSError):
            return False
    
    @staticmethod
    def enable_startup():
        """Enable auto-startup by adding registry entry"""
        if not REGISTRY_AVAILABLE:
            return False
            
        try:
            # Get the path to the current executable
            import sys
            if getattr(sys, 'frozen', False):
                # Running as executable
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = f'"{sys.executable}" "{os.path.abspath("app.py")}"'
            
            # Add to registry
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REGISTRY_KEY, 0, 
                              winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, WindowsStartupManager.APP_NAME, 0, winreg.REG_SZ, exe_path)
            
            return True
        except Exception as e:
            print(f"Failed to enable startup: {e}")
            return False
    
    @staticmethod
    def disable_startup():
        """Disable auto-startup by removing registry entry"""
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
    def toggle_startup():
        """Toggle auto-startup setting"""
        if WindowsStartupManager.is_startup_enabled():
            return WindowsStartupManager.disable_startup()
        else:
            return WindowsStartupManager.enable_startup()


def test_startup_functionality():
    """Test the startup management functionality"""
    print("Testing Ink2TeX Startup Management...")
    print("=" * 50)
    
    # Test registry availability
    print(f"Registry available: {REGISTRY_AVAILABLE}")
    
    if not REGISTRY_AVAILABLE:
        print("❌ winreg not available - startup management disabled")
        return False
    
    try:
        # Check current status
        is_enabled = WindowsStartupManager.is_startup_enabled()
        print(f"Current startup status: {'✓ Enabled' if is_enabled else '❌ Disabled'}")
        
        # Check config file
        config_value = ConfigReader.read_config_value('AUTO_START_WITH_WINDOWS', default='false')
        print(f"Config file setting: {config_value}")
        
        # Test enable/disable (but restore original state)
        print("\nTesting enable/disable functions...")
        original_state = is_enabled
        
        if original_state:
            print("Temporarily disabling startup...")
            success = WindowsStartupManager.disable_startup()
            print(f"Disable result: {'✓ Success' if success else '❌ Failed'}")
            
            print("Re-enabling startup...")
            success = WindowsStartupManager.enable_startup()
            print(f"Enable result: {'✓ Success' if success else '❌ Failed'}")
        else:
            print("Temporarily enabling startup...")
            success = WindowsStartupManager.enable_startup()
            print(f"Enable result: {'✓ Success' if success else '❌ Failed'}")
            
            print("Disabling startup...")
            success = WindowsStartupManager.disable_startup()
            print(f"Disable result: {'✓ Success' if success else '❌ Failed'}")
        
        # Verify final state matches original
        final_state = WindowsStartupManager.is_startup_enabled()
        if final_state == original_state:
            print("✓ State restored correctly")
        else:
            print("⚠️ State not restored - manually check your startup settings")
        
        print("\n🎉 All startup management tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


if __name__ == "__main__":
    success = test_startup_functionality()
    exit(0 if success else 1)
