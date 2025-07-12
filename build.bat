@echo off
REM Ink2TeX Build Wrapper
REM Calls the master build script from installer\scripts directory

echo ===================================================
echo           Ink2TeX Build System
echo ===================================================
echo.

if not exist "installer\scripts\build.bat" (
    echo ERROR: Build system not found in installer\scripts directory
    echo Please ensure installer\scripts\build.bat exists
    pause
    exit /b 1
)

echo Executing build from installer\scripts directory...
call installer\scripts\build.bat
exit /b %errorlevel%