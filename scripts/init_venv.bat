@echo off
REM Ink2TeX Virtual Environment Initialization Script
REM Creates and configures .venv with build dependencies

setlocal EnableDelayedExpansion

echo ===============================================
echo Ink2TeX Virtual Environment Setup
echo ===============================================
echo.

REM Check if we're in the project root
if not exist "installer\requirements-build.txt" (
    echo ERROR: installer\requirements-build.txt not found!
    echo This script must be run from the project root directory.
    pause
    exit /b 1
)

REM Check if .venv already exists
if exist ".venv\" (
    echo Virtual environment .venv already exists.
    set /p recreate="Do you want to recreate it? (y/N): "
    if /i "!recreate!" neq "y" (
        echo Skipping virtual environment creation.
        goto :activate_and_install
    )
    echo.
    echo Removing existing .venv...
    rmdir /s /q ".venv" 2>nul
    if exist ".venv\" (
        echo WARNING: Could not fully remove .venv. Some files may be in use.
        echo Please close any applications using the virtual environment and try again.
        pause
        exit /b 1
    )
)

echo Creating virtual environment .venv...
python -m venv .venv
if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure Python is installed and accessible via 'python' command.
    pause
    exit /b 1
)

:activate_and_install
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if !ERRORLEVEL! neq 0 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

echo.
echo Installing build dependencies from installer\requirements-build.txt...
pip install -r installer\requirements-build.txt
if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to install dependencies.
    echo Check that installer\requirements-build.txt exists and is valid.
    pause
    exit /b 1
)

echo.
echo Installing project in development mode...
pip install -e .
if !ERRORLEVEL! neq 0 (
    echo ERROR: Failed to install project in development mode.
    pause
    exit /b 1
)

echo.
echo ===============================================
echo Virtual Environment Setup Complete!
echo ===============================================
echo.
echo The .venv virtual environment has been created and configured with:
echo - All build dependencies from installer\requirements-build.txt
echo - The ink2tex project installed in development mode
echo.
echo To activate the environment manually:
echo   .venv\Scripts\activate
echo.
echo To deactivate:
echo   deactivate
echo.
pause
