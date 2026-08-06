@echo off
setlocal

rem Launcher en raiz para abrir la app de analisis de planos por localhost.
set "PORT=8765"
set "BASE=%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
	start "" cmd /c "cd /d ""%BASE%"" && py -3 -m http.server %PORT% >nul 2>&1"
) else (
	where python >nul 2>nul
	if %errorlevel%==0 (
		start "" cmd /c "cd /d ""%BASE%"" && python -m http.server %PORT% >nul 2>&1"
	)
)

start "" "http://127.0.0.1:%PORT%/dashboard/layout_workbench.html"

endlocal