@echo off
taskkill /f /im pythonw.exe 2>nul
del "%~dp0auto_sync.pid" 2>nul
echo Автосинхронизация остановлена.
pause
