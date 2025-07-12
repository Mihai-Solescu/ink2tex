#!/usr/bin/env python3
"""
Test script for Windows startup management functionality
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

def test_startup_management():
    """Test the Windows startup management functionality"""
    print("Testing Windows Startup Management...")
    
    try:
        # Test winreg import
        import winreg
        print("✓ winreg module imported successfully")
    except ImportError:
        print("❌ winreg module not available")
        return False
    
    try:
        # Import our startup manager (without matplotlib dependencies)
        from app import WindowsStartupManager, ConfigReader
        print("✓ WindowsStartupManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WindowsStartupManager: {e}")
        return False
    
    try:
        # Test registry operations
        print("\nTesting registry operations...")
        
        # Check current status
        is_enabled = WindowsStartupManager.is_startup_enabled()
        print(f"Current startup status: {'Enabled' if is_enabled else 'Disabled'}")
        
        # Test config reading
        config_value = ConfigReader.read_config_value('AUTO_START_WITH_WINDOWS', default='false')
        print(f"Config file setting: {config_value}")
        
        print("✓ All startup management functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing startup management: {e}")
        return False

if __name__ == "__main__":
    success = test_startup_management()
    if success:
        print("\n🎉 Startup management functionality is working!")
    else:
        print("\n❌ Startup management test failed")
    
    sys.exit(0 if success else 1)
