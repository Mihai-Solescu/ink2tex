@echo off
REM Ink2TeX Build Wrapper
REM Convenience script to run builds from the base folder
REM Delegates to scripts in the scripts/ folder

REM Check if scripts directory exists
if not exist "scripts\" (
    echo ERROR: scripts\ directory not found!
    echo This script must be run from the project root.
    exit /b 1
)

REM Handle command line arguments
set "choice=full"
if "%~1" neq "" (
    set "choice=%~1"
    echo Ink2TeX Build Wrapper - Running %choice% build
    echo.
    goto :process_choice
) 

echo ===============================================
echo Ink2TeX Build Wrapper
echo ===============================================
echo.
echo Default: Full build (executable + installer)
echo.
echo Available options:
echo   full      - Full build (executable + installer) [DEFAULT]
echo   exe       - Executable only (faster)
echo   installer - Installer only
echo   test      - Test deployment
echo   init      - Initialize virtual environment (.venv)
echo   help      - Show this help
echo.
echo Usage: build_wrapper.bat [full^|exe^|installer^|test^|init^|help]
echo        build_wrapper.bat          (runs full build)
echo.
set /p choice="Press Enter for full build, or type option: "
if "%choice%"=="" set "choice=full"

:process_choice

if /i "%choice%"=="full" (
    echo.
    echo Running full build...
    call scripts\build.bat
) else if /i "%choice%"=="exe" (
    echo.
    echo Running executable build...
    call scripts\build_exe.bat
) else if /i "%choice%"=="installer" (
    echo.
    echo Running installer build...
    call scripts\build_installer.bat
) else if /i "%choice%"=="test" (
    echo.
    echo Running deployment test...
    call scripts\test_deployment.bat
) else if /i "%choice%"=="init" (
    echo.
    echo Initializing virtual environment...
    call scripts\init_venv.bat
) else if /i "%choice%"=="help" (
    echo.
    echo Ink2TeX Build System Help
    echo ========================
    echo.
    echo Available commands:
    echo   full      - Complete build ^(executable + installer^)
    echo   exe       - Build executable only ^(faster for testing^)
    echo   installer - Build installer only ^(requires existing executable^)
    echo   test      - Test deployment readiness
    echo   init      - Initialize virtual environment with dependencies
    echo   help      - Show this help message
    echo.
    echo Examples:
    echo   build_wrapper.bat           ^(runs full build^)
    echo   build_wrapper.bat exe       ^(builds executable only^)
    echo   build_wrapper.bat init      ^(sets up virtual environment^)
    goto :end
) else (
    echo Invalid choice: "%choice%"
    echo.
    echo Valid options: full, exe, installer, test, init, help
    if "%~1" neq "" (
        echo Command line usage: build_wrapper.bat [full^|exe^|installer^|test^|init^|help]
        exit /b 1
    ) else (
        echo Try again with a valid option.
        exit /b 1
    )
)

:end
echo.
if "%~1" neq "" (
    echo Operation completed. Exit code: %ERRORLEVEL%
) else (
    echo Operation completed.
)
