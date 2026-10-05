@echo off
title Conectar PluriOne con Azure ML
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\configurar-azure-ml.ps1"
if errorlevel 1 echo No se completo la configuracion. Revisa el mensaje anterior sin compartir la clave.
pause
