@echo off
setlocal
cd /d "%~dp0"
title Retro Library Studio - Startup
where py >nul 2>nul
if not errorlevel 1 (
  py -3 bootstrap.py
) else (
  python bootstrap.py
)
set "RESULT=%errorlevel%"
if not "%RESULT%"=="0" (
  echo.
  echo Something prevented Retro Library Studio from opening.
  echo Read the message above. A log is saved in logs\startup_last.log.
  echo Press any key to close this window.
  pause >nul
)
exit /b %RESULT%
