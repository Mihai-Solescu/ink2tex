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

echo [1/5] Installing build dependencies...
pip install -r requirements-build.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [3/5] Creating application icon...
if not exist "assets" mkdir "assets"
REM You can replace this with a proper icon file
echo Creating default icon placeholder...

echo.
echo [4/5] Building executable with PyInstaller...
pyinstaller ink2tex.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [5/5] Verifying build...
if exist "dist\Ink2TeX.exe" (
    echo ✓ Build successful!
    echo ✓ Executable created: dist\Ink2TeX.exe
    echo.
    echo File size:
    for %%I in ("dist\Ink2TeX.exe") do echo   %%~zI bytes
    echo.
    echo You can now run: dist\Ink2TeX.exe
    echo Or create an installer using: build_installer.bat
) else (
    echo ERROR: Build failed - executable not found
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
pause
