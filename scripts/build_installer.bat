@echo off
REM Ink2TeX Installer Build Script
REM Creates a Windows installer using Inno Setup

echo ===================================================
echo          Ink2TeX Installer Build Script
echo ===================================================
echo.

REM Check if the executable exists
if not exist "dist\standalone\Ink2TeX.exe" (
    echo ERROR: Executable not found!
    echo Please run build_exe.bat first to create the executable
    pause
    exit /b 1
)

REM Check if Inno Setup is installed
echo [1/3] Checking for Inno Setup...
set "INNO_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if "%INNO_PATH%"=="" (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo Then run this script again.
    pause
    exit /b 1
)

echo ✓ Found Inno Setup at: %INNO_PATH%

echo.
echo [2/3] Creating installer output directory...
if not exist "dist\installer" mkdir "dist\installer"

echo.
echo [3/3] Building installer...
"%INNO_PATH%" "installer\installer.iss"
if errorlevel 1 (
    echo ERROR: Installer build failed
    pause
    exit /b 1
)

echo.
echo ===================================================
echo ✓ Installer build successful!
echo.
if exist "dist\installer\Ink2TeX_Setup_v1.0.0.exe" (
    echo 📦 Installer created: dist\installer\Ink2TeX_Setup_v1.0.0.exe
    echo.
    echo File size:
    for %%I in ("dist\installer\Ink2TeX_Setup_v1.0.0.exe") do echo   %%~zI bytes
    echo.
    echo The installer includes:
    echo   • Ink2TeX.exe - Main application
    echo   • Configuration files (.api, .config, prompt.txt)
    echo   • Automatic uninstaller
    echo   • Start menu shortcuts
    echo   • Optional desktop icon
    echo   • Optional auto-start with Windows
    echo.
    echo Users can now run the installer for one-click installation!
) else (
    echo ERROR: Installer file not found after build
)

echo ===================================================
pause
