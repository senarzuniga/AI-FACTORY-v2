@echo off
setlocal

rem Launcher en raiz para abrir la app de analisis de planos por localhost.
set "PORT=8765"
set "API_PORT=8000"
set "BASE=%~dp0"
set "PYTHON_CMD="

if exist "%BASE%.venv\Scripts\python.exe" (
	set "PYTHON_CMD=""%BASE%.venv\Scripts\python.exe"""
)

if not defined PYTHON_CMD (
	where py >nul 2>nul
	if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
	where python >nul 2>nul
	if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
	echo Python no esta disponible. Instala Python o crea .venv antes de abrir la aplicacion.
	pause
	exit /b 1
)

start "" cmd /c "cd /d ""%BASE%"" && %PYTHON_CMD% -m http.server %PORT% >nul 2>&1"

netstat -ano | findstr /R /C:":%API_PORT% .*LISTENING" >nul
if errorlevel 1 (
	start "" cmd /c "cd /d ""%BASE%"" && %PYTHON_CMD% -m uvicorn api.routes.hub_api:app --host 127.0.0.1 --port %API_PORT% >nul 2>&1"
)

start "" "http://127.0.0.1:%PORT%/dashboard/layout_workbench.html"

endlocal