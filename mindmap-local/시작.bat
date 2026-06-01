@echo off
chcp 65001 > nul
echo.
echo  ╔══════════════════════════════════════╗
echo  ║   MindFlow - Claude Code 구독 기반   ║
echo  ╚══════════════════════════════════════╝
echo.
echo  서버 시작 중...
echo  브라우저에서 http://localhost:5050 으로 접속하세요
echo.
cd /d "%~dp0"
start http://localhost:5050
python server.py
pause
