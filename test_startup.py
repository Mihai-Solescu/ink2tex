#!/usr/bin/env python3
"""
Ink2TeX Startup Testing Script
Tests the main app startup functionality
"""

import sys
import subprocess
import time
import signal
from pathlib import Path

def find_project_root():
    """Find the project root directory by looking for pyproject.toml"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")

def test_script_startup():
    """Test the main Python script startup"""
    try:
        PROJECT_ROOT = find_project_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return False
    
    MAIN_SCRIPT = PROJECT_ROOT / "main.py"
    if not MAIN_SCRIPT.exists():
        print(f"ERROR: Main script not found: {MAIN_SCRIPT}")
        return False
    
    print(f"Testing script startup: {MAIN_SCRIPT}")
    
    try:
        # Start the process
        process = subprocess.Popen(
            [sys.executable, str(MAIN_SCRIPT)],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        poll_result = process.poll()
        
        if poll_result is None:
            print("✓ Application started successfully (process is running)")
            
            # Terminate the process gracefully
            try:
                process.terminate()
                process.wait(timeout=5)
                print("✓ Application terminated gracefully")
                return True
            except subprocess.TimeoutExpired:
                print("⚠ Process didn't terminate gracefully, forcing kill")
                process.kill()
                return True
                
        else:
            print(f"✗ Application exited immediately with code: {poll_result}")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing script startup: {e}")
        return False

def test_executable_startup():
    """Test the standalone executable startup"""
    try:
        PROJECT_ROOT = find_project_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return False
    
    EXECUTABLE = PROJECT_ROOT / "dist" / "standalone" / "Ink2TeX.exe"
    if not EXECUTABLE.exists():
        print(f"⚠ Executable not found: {EXECUTABLE}")
        print("  (This is normal if exe hasn't been built yet)")
        return None
    
    print(f"Testing executable startup: {EXECUTABLE}")
    
    try:
        # Start the process
        process = subprocess.Popen(
            [str(EXECUTABLE)],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        poll_result = process.poll()
        
        if poll_result is None:
            print("✓ Executable started successfully (process is running)")
            
            # Terminate the process gracefully
            try:
                process.terminate()
                process.wait(timeout=5)
                print("✓ Executable terminated gracefully")
                return True
            except subprocess.TimeoutExpired:
                print("⚠ Process didn't terminate gracefully, forcing kill")
                process.kill()
                return True
                
        else:
            print(f"✗ Executable exited immediately with code: {poll_result}")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing executable startup: {e}")
        return False

def main():
    print("===================================================")
    print("          Ink2TeX Startup Test")
    print("===================================================")
    print()
    
    # Test script startup
    print("[1/2] Testing Python script startup...")
    script_result = test_script_startup()
    print()
    
    # Test executable startup
    print("[2/2] Testing executable startup...")
    exe_result = test_executable_startup()
    print()
    
    # Summary
    print("===================================================")
    print("               Test Results")
    print("===================================================")
    
    if script_result:
        print("✅ Python script startup: PASSED")
    else:
        print("❌ Python script startup: FAILED")
    
    if exe_result is True:
        print("✅ Executable startup: PASSED")
    elif exe_result is False:
        print("❌ Executable startup: FAILED")
    else:
        print("⚠️  Executable startup: SKIPPED (exe not found)")
    
    print()
    
    if script_result and (exe_result is None or exe_result is True):
        print("🎉 All available tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed - check the output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
