@echo off
echo Claude Usage Widget — Setup
echo ============================
echo.

echo Step 1: Installing Python dependencies...
pip install -r "%~dp0requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: pip install failed.
    echo Make sure Python 3.10+ is installed and "Add Python to PATH" was ticked during install.
    echo Download Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo Step 2: Creating desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1" "%~dp0"
if %ERRORLEVEL% neq 0 (
    echo.
    echo WARNING: Could not create desktop shortcut.
    echo You can still launch the widget by double-clicking launch.bat in this folder.
)

echo.
echo ============================
echo Setup complete!
echo.
echo A "Claude Usage Widget" shortcut has been added to your desktop.
echo Double-click it to start. You'll be prompted for your Claude session key on first launch.
echo.
pause
