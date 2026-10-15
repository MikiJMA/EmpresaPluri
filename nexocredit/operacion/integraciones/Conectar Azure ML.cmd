@echo off
title Conectar NexoCredit con Azure ML
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\configurar-azure-ml.ps1"
if errorlevel 1 echo No se completo la configuracion. Revisa el mensaje anterior sin compartir la clave.
pause
