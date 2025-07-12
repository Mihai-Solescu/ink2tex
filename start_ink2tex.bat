@echo off
REM Ink2TeX System Tray Application Launcher
REM This script starts Ink2TeX in the background as a system tray application

echo Starting Ink2TeX system tray application...
echo.
echo The application will run in the background with a system tray icon.
echo LaTeX preview loads quickly on first use for optimal performance.
echo.
echo Controls:
echo   - Ctrl+Shift+I: Open overlay (global hotkey)
echo   - Double-click tray icon: Open overlay  
echo   - Right-click tray icon: Show menu
echo   - Esc: Close overlay (always works)
echo.

cd /d "%~dp0"
python app.py

echo.
echo Ink2TeX has stopped.
pause
