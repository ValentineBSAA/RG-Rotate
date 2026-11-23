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
".venv\Scripts\python.exe" -m pip install "pyinstaller>=6,<7"
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --collect-all py7zr --hidden-import packaging.version --name "RetroLibraryStudio" app.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --console --collect-all py7zr --hidden-import packaging.version --name "RetroLibraryScan" readonly_scan.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --console --collect-all py7zr --hidden-import packaging.version --hidden-import ps1_pipeline --name "RetroLibraryImport" import_worker.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --console --collect-all py7zr --hidden-import packaging.version --name "RetroLibraryArtwork" artwork_worker.py
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --console --collect-all py7zr --hidden-import packaging.version --name "RetroLibraryTransfer" transfer_worker.py
if errorlevel 1 goto error
echo Keep RetroLibraryStudio.exe, RetroLibraryScan.exe, RetroLibraryImport.exe, RetroLibraryArtwork.exe, and RetroLibraryTransfer.exe together in dist.
echo EXE ready in dist\RetroLibraryStudio.exe
pause
exit /b 0
:error
echo Windows EXE packaging failed; check the messages above.
pause
exit /b 1
