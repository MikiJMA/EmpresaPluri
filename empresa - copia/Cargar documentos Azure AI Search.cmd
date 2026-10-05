@echo off
title Cargar documentos demo en Azure AI Search
"%~dp0.venv\Scripts\python.exe" "%~dp0scripts\cargar_documentos_search.py"
if errorlevel 1 echo Carga no completada. No compartas claves.
pause
