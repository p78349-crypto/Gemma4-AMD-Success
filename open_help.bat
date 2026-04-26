@echo off
setlocal
chcp 65001 > nul

set "HELP_TXT=%~dp0..\llm_server\control_panel\help\chat_help.txt"
if not exist "%HELP_TXT%" (
    echo [ERROR] help file not found:
    echo         %HELP_TXT%
    pause
    exit /b 1
)

start "Chat Help" notepad "%HELP_TXT%"
exit /b 0
