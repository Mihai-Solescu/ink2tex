@echo off
REM Deployment test script - executed from project root
REM This script is located in installer\scripts\ but executed from the base directory
REM Tests if all components are ready for building

echo ===================================================
echo              Deployment Test Script
echo ===================================================
echo.

echo [TEST 1] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL: Python not found
    goto :end_with_error
) else (
    python --version
    echo ✅ PASS: Python is available
)

echo.
echo [TEST 2] Checking required files...

set "missing_files="

if not exist "app.py" (
    echo ❌ MISSING: app.py
    set "missing_files=1"
) else (
    echo ✅ Found: app.py
)

if not exist ".api" (
    echo ❌ MISSING: .api file
    set "missing_files=1"
) else (
    echo ✅ Found: .api file
)

if not exist ".config" (
    echo ❌ MISSING: .config file
    set "missing_files=1"
) else (
    echo ✅ Found: .config file
)

if not exist "prompt.txt" (
    echo ❌ MISSING: prompt.txt
    set "missing_files=1"
) else (
    echo ✅ Found: prompt.txt
)

if not exist "installer\ink2tex.spec" (
    echo ❌ MISSING: installer\ink2tex.spec
    set "missing_files=1"
) else (
    echo ✅ Found: installer\ink2tex.spec
)

if "%missing_files%"=="1" (
    echo ❌ FAIL: Required files missing
    goto :end_with_error
) else (
    echo ✅ PASS: All required files present
)

echo.
echo [TEST 3] Testing app imports...
python -c "import sys; import PyQt6; import google.generativeai; import PIL; import matplotlib; import pynput; print('✅ All imports successful')" 2>nul
if errorlevel 1 (
    echo ❌ FAIL: Missing dependencies
    echo Run: pip install -r installer\requirements-build.txt
    goto :end_with_error
) else (
    echo ✅ PASS: All dependencies available
)

echo.
echo [TEST 4] Checking build tools...
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ❌ MISSING: PyInstaller not found
    echo Run: pip install pyinstaller
    goto :end_with_error
) else (
    echo ✅ Found: PyInstaller
)

echo.
echo ===================================================
echo ✅ ALL DEPLOYMENT TESTS PASSED!
echo Ready to build with: build.bat
echo ===================================================
echo.
pause
exit /b 0

:end_with_error
echo.
echo ===================================================
echo ❌ DEPLOYMENT TEST FAILED
echo Please fix the issues above before building.
echo ===================================================
echo.
pause
exit /b 1
