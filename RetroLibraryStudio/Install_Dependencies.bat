@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 bootstrap.py --check-only
) else (
  python bootstrap.py --check-only
)
if errorlevel 1 (
  echo Dependency setup failed. See logs\startup_last.log.
  pause
  exit /b 1
)
echo Dependencies are ready. Run Start_Retro_Library_Studio.bat.
pause
