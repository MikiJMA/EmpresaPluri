@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\respaldo-postgresql.ps1" -Accion crear
pause
