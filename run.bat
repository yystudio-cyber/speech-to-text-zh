@echo off
chcp 65001 >nul
cd /d "%~dp0"

python --version >nul 2>nul
if %errorlevel%==0 (
  python -m speech_to_text_zh
) else (
  py -3 -m speech_to_text_zh
)
