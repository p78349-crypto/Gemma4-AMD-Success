@echo off
chcp 65001 > nul
cd /d "%~dp0..\llm_server"
if "%VT_MODEL_BASE%"=="" set "VT_MODEL_BASE=%~dp0..\Model"

set "PY=.venv\Scripts\python.exe"
if not exist "%PY%" (
    echo [ERROR] venv python not found. Run 00_setup.bat first.
    pause
    exit /b 1
)

echo [26B-GGUF] IQ3_S :8031 starting...
start "Gemma4-26B GGUF IQ3_S :8031" cmd /k "%PY% llama_gguf\start.py --family 26b --model IQ3_S --port 8031 --ngl 99"
echo done.
exit /b 0
