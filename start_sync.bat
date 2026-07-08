@echo off
cd /d "%~dp0"
echo Запуск автосинхронизации...
start /b pythonw auto_sync.py
echo Готово! Синхронизация работает в фоне.
echo Остановка: stop_sync.bat
pause
