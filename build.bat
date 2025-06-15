@echo off
echo Building Galactic Conquest Executable...
echo ========================================

REM Clean previous build
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "GalacticConquest.spec" del "GalacticConquest.spec"

echo Cleaned previous build files.

REM Build the executable
python -m PyInstaller --onefile --name=GalacticConquest main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo Executable created: dist\GalacticConquest.exe
    echo File size: 
    dir dist\GalacticConquest.exe | find "GalacticConquest.exe"
    echo.
    echo You can now distribute the 'dist' folder or just the .exe file.
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the error messages above.
    echo.
    pause
) 