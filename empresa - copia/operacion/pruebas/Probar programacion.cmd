@echo off
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\probar-programacion.ps1"
pause
