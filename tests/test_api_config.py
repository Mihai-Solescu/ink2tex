#!/usr/bin/env python3
"""Test script to debug API configuration"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ink2tex.core.config import ConfigReader
from ink2tex.core.api import GeminiAPIManager

def test_api_configuration():
    """Test API configuration step by step"""
    print("=== API Configuration Test ===")
    
    # Test 1: Read API key from config
    try:
        print("1. Reading API key from config...")
        api_key = ConfigReader.read_api_key_from_config()
        print(f"   ✓ API key loaded: {api_key[:10]}..." if api_key else "   ❌ No API key loaded")
    except Exception as e:
        print(f"   ❌ Failed to read API key: {e}")
        return False
    
    # Test 2: Configure API manager
    try:
        print("2. Configuring API manager...")
        api_manager = GeminiAPIManager()
        print(f"   Initial configured state: {api_manager.is_configured()}")
        
        print("   Attempting to configure API...")
        success = api_manager.configure_api(api_key)
        print(f"   ✓ Configuration success: {success}")
        print(f"   Final configured state: {api_manager.is_configured()}")
        
        if not success:
            print("   ❌ API configuration failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to configure API: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test a simple conversion (we'll skip this for now)
    print("3. API configuration test completed successfully!")
    return True

if __name__ == "__main__":
    test_api_configuration()
