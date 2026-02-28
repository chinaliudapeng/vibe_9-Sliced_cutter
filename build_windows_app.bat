@echo off
REM Build script for 9-Slice Cutter Windows executable
REM This script creates a standalone .exe with custom icon

echo Building 9-Slice Cutter for Windows...
echo =====================================

REM Check if icon file exists
if not exist "icon\icon.png" (
    echo ERROR: Icon file icon\icon.png not found!
    pause
    exit /b 1
)

REM Run PyInstaller with icon support
python -m PyInstaller ^
    -F ^
    -w ^
    --icon="icon\icon.png" ^
    --name="9SliceCutter" ^
    main.py

REM Check if build succeeded
if %ERRORLEVEL% neq 0 (
    echo.
    echo BUILD FAILED! Check error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo BUILD COMPLETE!
echo Output: dist\9SliceCutter.exe
echo.

REM Check if the executable was created
if exist "dist\9SliceCutter.exe" (
    echo Executable successfully created: dist\9SliceCutter.exe
    echo File size:
    dir "dist\9SliceCutter.exe" | find "9SliceCutter.exe"
) else (
    echo WARNING: Executable file not found in dist directory!
)

echo.
echo Press any key to exit...
pause > nul