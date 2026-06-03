@echo off
echo Installing Claude Usage Widget dependencies...
pip install -r "%~dp0requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: pip failed. Make sure Python is installed and "Add Python to PATH" was ticked.
    echo Download Python from: https://www.python.org/downloads/
)
echo.
echo Done. Run launch.bat to start the widget.
pause
