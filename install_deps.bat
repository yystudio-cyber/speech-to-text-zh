@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Installing dependencies for speech-to-text tool...
python --version >nul 2>nul
if %errorlevel%==0 (
  python -m pip install --user -r requirements.txt
) else (
  py -3 -m pip install --user -r requirements.txt
)

echo.
echo Done. You can run run.bat now.
pause
