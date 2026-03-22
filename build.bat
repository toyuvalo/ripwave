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
echo Building ripwave.exe...
pyinstaller --onefile --windowed ^
    --name RipWave ^
    --icon assets\icon.ico ^
    --add-data "assets\icon.ico;assets" ^
    ripwave.py

if not exist dist\RipWave.exe (
    echo Build failed.
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
