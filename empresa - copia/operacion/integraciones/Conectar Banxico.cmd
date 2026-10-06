@echo off
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\configurar-banxico.ps1"
if errorlevel 1 (
  pause
  exit /b 1
)
pause
