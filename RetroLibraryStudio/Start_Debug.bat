@echo off
setlocal
cd /d "%~dp0"
title Retro Library Studio - Safe Debug Startup
echo Retro Library Studio - Dependency check and debug mode
echo This launcher also installs any missing required libraries.
echo.
where py >nul 2>nul
if not errorlevel 1 (
  py -3 bootstrap.py --debug
) else (
  python bootstrap.py --debug
)
set "RESULT=%errorlevel%"
echo.
echo Finished. Exit status: %RESULT%.
echo Diagnostic log: logs\startup_last.log
pause
exit /b %RESULT%
