@echo off
title Configurar Azure AI Search para PluriOne
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\configurar-azure-search.ps1"
if errorlevel 1 echo No se completo la configuracion. No compartas claves ni el archivo .env.
pause
