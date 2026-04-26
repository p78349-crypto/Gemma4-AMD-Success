@echo off
setlocal
chcp 65001 > nul

call "%~dp0start_26b_iq3.bat"
timeout /t 2 > nul
call "%~dp0open_chat_26b_iq3.bat"
exit /b 0
