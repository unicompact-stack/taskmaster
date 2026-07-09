@echo off
cd /d "%~dp0"
echo Запуск автосинхронизации через WSL...
start /b wsl python3 auto_sync.py
echo Готово! Синхронизация работает в фоне.
echo Остановка: stop_sync.bat
pause
