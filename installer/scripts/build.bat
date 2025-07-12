@echo off
REM Ink2TeX Master Build Script
REM This script is located in installer\scripts\ but executed from the base directory
REM Builds both executable and installer from root directory

echo ===================================================
echo           Ink2TeX Master Build Script
echo ===================================================
echo.

echo [1/2] Building executable...
call installer\scripts\build_exe.bat
if errorlevel 1 (
    echo ERROR: Executable build failed
    pause
    exit /b 1
)

echo.
echo [2/2] Building installer...
call installer\scripts\build_installer.bat
if errorlevel 1 (
    echo ERROR: Installer build failed
    pause
    exit /b 1
)

echo.
echo ===================================================
echo ✅ Complete build successful!
echo.
echo Executable: dist\standalone\Ink2TeX.exe
echo Installer: dist\installer\Ink2TeX_Setup_v1.0.0.exe
echo ===================================================
echo.
pause
