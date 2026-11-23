@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 bootstrap.py --check-only
) else (
  python bootstrap.py --check-only
)
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install pytest
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pytest -q
set "RESULT=%errorlevel%"
echo.
echo Test run finished. Exit status: %RESULT%
pause
exit /b %RESULT%
:error
echo Python/dependency setup failed.
pause
exit /b 1
