@echo off
setlocal
chcp 65001 > nul
cd /d "%~dp0..\llm_server"

set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (
    echo [ERROR] venv python not found. Run exebat\00_setup.bat first.
    pause
    exit /b 1
)

if "%VT_MODEL_BASE%"=="" set "VT_MODEL_BASE=%~dp0..\Model"
if "%~1"=="" (
    set "VT_CHAT_DEFAULT_PORT=8031"
) else (
    set "VT_CHAT_DEFAULT_PORT=%~1"
)
set "VT_GUI_OPEN_TAB=chat"

echo [LLM Chat] open (default port: %VT_CHAT_DEFAULT_PORT%)
start "LLM Chat" cmd /k "%PY% gui_panel.py"
exit /b 0
