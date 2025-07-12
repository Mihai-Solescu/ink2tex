@echo off
REM Ink2TeX Deployment Test Wrapper
REM Calls the deployment test script from installer\scripts directory

echo ===================================================
echo           Ink2TeX Deployment Test
echo ===================================================
echo.

if not exist "installer\scripts\test_deployment.bat" (
    echo ERROR: Test script not found in installer\scripts directory
    echo Please ensure installer\scripts\test_deployment.bat exists
    pause
    exit /b 1
)

echo Executing deployment test from installer\scripts directory...
call installer\scripts\test_deployment.bat
exit /b %errorlevel%