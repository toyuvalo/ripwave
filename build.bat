@echo off
setlocal
title RipWave Build
cd /d "%~dp0"

echo.
echo  ================================
echo   RipWave Build
echo  ================================
echo.

:: Install PyInstaller if needed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller --quiet
)

:: Build exe
:: Remove the previous binary FIRST. PyInstaller writes to the fixed path
:: dist\RipWave.exe, so on a failed build the old exe survives -- and the
:: "if not exist" check below would pass on it, then the packaging step would
:: zip a stale binary into the release. Delete-then-recreate makes the
:: existence check a genuine freshness check.
if exist dist\RipWave.exe del /q dist\RipWave.exe

echo Building ripwave.exe...
pyinstaller --onefile --windowed ^
    --name RipWave ^
    --icon assets\icon.ico ^
    --version-file version_info.txt ^
    --add-data "assets\icon.ico;assets" ^
    ripwave.py

if errorlevel 1 (
    echo Build failed - PyInstaller returned %errorlevel%.
    pause & exit /b 1
)

if not exist dist\RipWave.exe (
    echo Build failed - PyInstaller exited 0 but produced no dist\RipWave.exe.
    pause & exit /b 1
)

:: Copy runtime dependencies into dist\
echo Copying yt-dlp and ffmpeg...
if exist yt-dlp.exe  copy /y yt-dlp.exe  dist\ >nul
if exist ffmpeg.exe  copy /y ffmpeg.exe  dist\ >nul

:: Package into a zip for release
echo Packaging release zip...
powershell -NoProfile -Command ^
    "Compress-Archive -Path 'dist\*' -DestinationPath 'dist\RipWave-windows.zip' -Force"

echo.
echo  ================================
echo   Build complete: dist\RipWave.exe
echo   Release zip:    dist\RipWave-windows.zip
echo  ================================
echo.
pause
endlocal
