@echo off
REM Quick setup script for Ink2TeX portable version
echo ======================================
echo      Ink2TeX Portable Setup
echo ======================================
echo.
echo This portable version needs a Google Gemini API key to work.
echo.
echo 1. Get a free API key from: https://makersuite.google.com/app/apikey
echo 2. Edit the .api file in this folder
echo 3. Replace 'your_api_key_here' with your actual API key
echo 4. Save the file and run Ink2TeX.exe
echo.
echo Configuration files in this folder:
echo   .api       - Your Google API key (EDIT THIS!)
echo   .config    - App settings (optional to edit)
echo   prompt.txt - AI behavior (optional to edit)
echo.
echo Press Enter to open the .api file for editing...
pause >nul
notepad.exe .api
echo.
echo Setup complete! You can now run Ink2TeX.exe
pause
