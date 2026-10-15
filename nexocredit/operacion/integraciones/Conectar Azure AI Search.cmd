@echo off
title Configurar Azure AI Search para NexoCredit
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\configurar-azure-search.ps1"
if errorlevel 1 echo No se completo la configuracion. No compartas claves ni el archivo .env.
pause
