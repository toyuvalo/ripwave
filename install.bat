@echo off
setlocal enabledelayedexpansion
title RipWave Installer
cd /d "%~dp0"

echo.
echo  ================================
echo   RipWave Installer
echo  ================================
echo.

:: ── 1. Check Python ──────────────────────────────────────────────────────────
echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo.
        echo  Python not found.
        echo  Installing via winget...
        winget install --id Python.Python.3.12 -e --silent
        if !errorlevel! neq 0 (
            echo.
            echo  winget failed. Please install Python manually from:
            echo    https://www.python.org/downloads/
            echo  Then re-run this installer.
            pause & exit /b 1
        )
        echo  Python installed. Please restart this installer.
        pause & exit /b 0
    )
)
echo  Python OK

:: ── 2. Download yt-dlp.exe ───────────────────────────────────────────────────
echo [2/3] Getting yt-dlp...
if exist yt-dlp.exe (
    echo  yt-dlp already present, updating...
    yt-dlp.exe -U >nul 2>&1
) else (
    powershell -NoProfile -Command ^
        "Invoke-WebRequest -Uri 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe' -OutFile 'yt-dlp.exe'" ^
        2>nul
    if not exist yt-dlp.exe (
        echo  Failed to download yt-dlp.exe. Check your internet connection.
        pause & exit /b 1
    )
)
echo  yt-dlp OK

:: ── 3. Download ffmpeg.exe ───────────────────────────────────────────────────
echo [3/3] Getting ffmpeg...
if exist ffmpeg.exe (
    echo  ffmpeg already present, skipping.
) else (
    echo  Downloading ffmpeg (this may take a moment)...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$tmp = '$env:TEMP\rw_ffmpeg.zip';" ^
        "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile $tmp;" ^
        "Add-Type -AssemblyName System.IO.Compression.FileSystem;" ^
        "$zip = [IO.Compression.ZipFile]::OpenRead($tmp);" ^
        "$entry = $zip.Entries | Where-Object { $_.Name -eq 'ffmpeg.exe' } | Select-Object -First 1;" ^
        "[IO.Compression.ZipFileExtensions]::ExtractToFile($entry, (Join-Path (Get-Location) 'ffmpeg.exe'), $true);" ^
        "$zip.Dispose();" ^
        "Remove-Item $tmp -Force" ^
        2>nul
    if not exist ffmpeg.exe (
        echo  Failed to download ffmpeg. Check your internet connection.
        pause & exit /b 1
    )
)
echo  ffmpeg OK

:: ── Create desktop shortcut ──────────────────────────────────────────────────
echo.
echo  Creating desktop shortcut...
powershell -NoProfile -Command ^
    "$sh = New-Object -ComObject WScript.Shell;" ^
    "$lnk = $sh.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\RipWave.lnk');" ^
    "$lnk.TargetPath = 'pythonw';" ^
    "$lnk.Arguments = '\"%~dp0ripwave.py\"';" ^
    "$lnk.WorkingDirectory = '%~dp0';" ^
    "$lnk.IconLocation = '%~dp0assets\icon.ico';" ^
    "$lnk.Save()" ^
    2>nul

:: ── Done ─────────────────────────────────────────────────────────────────────
echo.
echo  ================================
echo   Done! RipWave is ready.
echo   Shortcut created on your desktop.
echo  ================================
echo.
set /p "launch= Launch now? [Y/n]: "
if /i "!launch!" neq "n" (
    start "" pythonw "%~dp0ripwave.py"
)
endlocal
