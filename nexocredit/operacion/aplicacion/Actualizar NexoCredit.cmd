@echo off
title Construir y actualizar NexoCredit
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\docker.ps1" iniciar
set "NEXOCREDIT_EXIT=%ERRORLEVEL%"
pause
exit /b %NEXOCREDIT_EXIT%
