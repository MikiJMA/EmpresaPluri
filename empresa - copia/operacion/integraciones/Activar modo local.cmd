@echo off
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\modo-local.ps1" local
if errorlevel 1 pause
