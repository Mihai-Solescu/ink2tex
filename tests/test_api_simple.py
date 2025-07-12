#!/usr/bin/env python3
"""Simple test script to debug API configuration without hanging"""

import sys
import os
import signal

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def test_api_step_by_step():
    """Test API configuration step by step with timeouts"""
    print("=== API Configuration Test ===")
    
    # Test 1: Import modules
    try:
        print("1. Importing modules...")
        import google.generativeai as genai
        print("   ✓ google.generativeai imported")
    except Exception as e:
        print(f"   ❌ Failed to import: {e}")
        return False
    
    # Test 2: Read API key
    try:
        print("2. Reading API key...")
        from ink2tex.core.config import ConfigReader
        api_key = ConfigReader.read_api_key_from_config()
        print(f"   ✓ API key loaded: {api_key[:10]}..." if api_key else "   ❌ No API key loaded")
    except Exception as e:
        print(f"   ❌ Failed to read API key: {e}")
        return False
    
    # Test 3: Configure API
    try:
        print("3. Configuring API...")
        genai.configure(api_key=api_key)
        print("   ✓ API configured")
    except Exception as e:
        print(f"   ❌ Failed to configure API: {e}")
        return False
    
    # Test 4: Create model (with timeout)
    try:
        print("4. Creating model...")
        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        # Try the experimental model first
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("   ✓ Created gemini-2.0-flash-exp model")
        except:
            # Fall back to stable model
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("   ✓ Created gemini-1.5-flash model (fallback)")
        
        signal.alarm(0)  # Cancel timeout
        
    except TimeoutError:
        print("   ❌ Model creation timed out")
        return False
    except Exception as e:
        print(f"   ❌ Failed to create model: {e}")
        return False
    
    print("5. ✓ All tests passed!")
    return True

if __name__ == "__main__":
    test_api_step_by_step()
