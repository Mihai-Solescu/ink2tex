@echo off
REM Quick deployment test script
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
)
if not exist ".api" (
    echo ❌ MISSING: .api file
    set "missing_files=1"
)
if not exist ".config" (
    echo ❌ MISSING: .config file  
    set "missing_files=1"
)
if not exist "prompt.txt" (
    echo ❌ MISSING: prompt.txt
    set "missing_files=1"
)
if not exist "ink2tex.spec" (
    echo ❌ MISSING: ink2tex.spec
    set "missing_files=1"
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
    echo Run: pip install -r requirements-build.txt
    goto :end_with_error
) else (
    echo ✅ PASS: All dependencies available
)

echo.
echo [TEST 4] Testing configuration loading...
python -c "import sys; sys.path.insert(0, '.'); from app import ConfigReader; key = ConfigReader.read_api_key_from_config(); print('✅ PASS: API key loaded successfully') if key and len(key) > 10 else print('❌ FAIL: API key appears invalid')"
if errorlevel 1 goto :end_with_error

echo.
echo ===================================================
echo ✅ ALL TESTS PASSED!
echo.
echo Your deployment environment is ready.
echo You can now run:
echo   1. build_exe.bat      - Create standalone executable
echo   2. build_installer.bat - Create Windows installer
echo ===================================================
goto :end

:end_with_error
echo.
echo ===================================================
echo ❌ DEPLOYMENT TEST FAILED
echo.
echo Please fix the issues above before building.
echo ===================================================

:end
pause
