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
set "VT_CHAT_DEFAULT_PORT=8031"
set "VT_GUI_OPEN_TAB=chat"

echo [LLM Chat] 26B GGUF IQ3_S (:8031) default
start "LLM Chat (26B IQ3_S)" cmd /k "%PY% gui_panel.py"
exit /b 0
