@echo off
REM Ink2TeX Build Script
REM Creates a standalone executable using PyInstaller

echo ===================================================
echo             Ink2TeX Build Script
echo ===================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [1/6] Checking and setting up virtual environment...

REM Check if .venv exists and has the required packages
set "venv_ready=0"
if exist ".venv\Scripts\activate.bat" (
    echo ✓ Virtual environment .venv found
    call .venv\Scripts\activate.bat
    
    REM Check if PyInstaller is installed
    pyinstaller --version >nul 2>&1
    if not errorlevel 1 (
        echo ✓ Virtual environment appears ready
        set "venv_ready=1"
    ) else (
        echo ⚠ Virtual environment exists but missing build dependencies
    )
) else (
    echo ⚠ Virtual environment .venv not found
)

REM Initialize .venv if not ready
if "!venv_ready!"=="0" (
    echo.
    echo Initializing virtual environment with build dependencies...
    call scripts\init_venv.bat
    if errorlevel 1 (
        echo ERROR: Failed to initialize virtual environment
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
)

echo.
echo [2/6] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [3/6] Creating application icon...
if not exist "assets" mkdir "assets"
REM You can replace this with a proper icon file
echo Creating default icon placeholder...

echo.
echo [4/6] Building executable with PyInstaller...
cd installer
pyinstaller ink2tex.spec --noconfirm --clean
cd ..
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [5/6] Verifying build...
if exist "dist\standalone\Ink2TeX.exe" (
    echo ✓ Build successful!
    echo ✓ Executable created: dist\standalone\Ink2TeX.exe
    echo.
    echo File size:
    for %%I in ("dist\standalone\Ink2TeX.exe") do echo   %%~zI bytes
    echo.
    echo You can now run: dist\standalone\Ink2TeX.exe
    echo Or create an installer using: build_installer.bat
) else (
    echo ERROR: Build failed - executable not found
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
pause
