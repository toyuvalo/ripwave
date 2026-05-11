@echo off
setlocal
title RipWave Build (PERSONAL)
cd /d "%~dp0"

echo.
echo  ===================================
echo   RipWave Build — PERSONAL
echo   (adds youtubedownloader alias)
echo  ===================================
echo.

:: Build the EXE first (same as prod)
call build.bat
if %errorlevel% neq 0 (
    echo Build of RipWave.exe failed.
    exit /b %errorlevel%
)

:: Locate Inno Setup
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo.
    echo  Inno Setup 6 not found. Install from https://jrsoftware.org/isinfo.php
    echo  Skipping installer build — RipWave.exe is in dist\ for direct use.
    exit /b 0
)

:: Read version from ripwave.py
for /f "tokens=2 delims==" %%v in ('findstr /R "^VERSION =" ripwave.py') do (
    set "RAW=%%v"
)
set "VER=%RAW: =%"
set "VER=%VER:"=%"

echo Building personal installer with version %VER%...
"%ISCC%" "/DMyAppVersion=%VER%" /DPERSONAL_BUILD installer\ripwave.iss
if %errorlevel% neq 0 (
    echo Installer build failed.
    exit /b %errorlevel%
)

echo.
echo  ===================================
echo   Personal installer: installer\RipWave-Setup.exe
echo   Includes youtubedownloader Start Menu alias.
echo  ===================================
echo.
endlocal
