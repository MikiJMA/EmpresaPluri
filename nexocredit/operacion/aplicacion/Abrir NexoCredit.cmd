@echo off
title Abrir NexoCredit
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\docker.ps1" abrir
set "NEXOCREDIT_EXIT=%ERRORLEVEL%"
if not "%NEXOCREDIT_EXIT%"=="0" pause
exit /b %NEXOCREDIT_EXIT%
