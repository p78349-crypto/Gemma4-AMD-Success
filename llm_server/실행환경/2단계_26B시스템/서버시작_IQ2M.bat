@echo off
chcp 65001 > nul
cd /d "%~dp0..\.."

set PY=.venv\Scripts\python.exe

if not exist "%PY%" (
    echo [오류] 가상환경 없음. llm_server\00_setup.bat 먼저 실행하세요.
    pause
    exit /b 1
)

echo ================================================
echo   26B 시스템 — 서버 시작 (IQ2_M VRAM절약)
echo   VRAM 부족 시 이 파일 사용 (IQ3_S 대신 IQ2_M)
echo ================================================
echo.

echo [1/3] Gemma4-26B GGUF (IQ2_M, Vulkan GPU) 시작...
echo       포트 8031 / IQ2_M = 9.3GB (IQ3_S보다 1GB 절약)
start "Gemma4-26B GGUF IQ2_M :8031" cmd /k ^
    "%PY% llama_gguf\start.py --model IQ2_M --port 8031 --ngl 99"
timeout /t 5 /nobreak > nul

echo [2/3] NLLB-1.3B 전문번역 서버 시작...
start "NLLB-1.3B :8012" cmd /k ^
    "%PY% -m uvicorn nllb_1p3b.server:app --port 8012 --workers 1"
timeout /t 3 /nobreak > nul

echo [3/3] Whisper Turbo STT 서버 시작...
start "Whisper Turbo :8021" cmd /k ^
    "%PY% -m uvicorn whisper_turbo.server:app --port 8021 --workers 1"

echo.
echo ================================================
echo   서버 로딩 중... 26B(IQ2_M)는 30~60초 소요
echo   26B API : http://localhost:8031/v1/chat/completions
echo   NLLB    : http://localhost:8012/v1/translate
echo   Whisper : http://localhost:8021/health
echo ================================================
pause
