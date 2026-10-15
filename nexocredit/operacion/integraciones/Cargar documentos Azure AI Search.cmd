@echo off
title Cargar documentos demo en Azure AI Search
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" "scripts\cargar_documentos_search.py"
if errorlevel 1 echo Carga no completada. No compartas claves.
pause
