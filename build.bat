@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo          MACHI AI Assistant — Full Automated Builder
echo =======================================================
echo.

set "MACHI_DIR=%~dp0"
set "MACHI_DIR=%MACHI_DIR:~0,-1%"

:: 1. Ensure PyInstaller and Pillow are installed
echo [*] Checking build dependencies...
python -m pip install pyinstaller pillow --quiet

:: 2. Ensure assets/icon.ico exists
if not exist "%MACHI_DIR%\assets\icon.ico" (
    echo [*] Generating icon assets...
    python -c "
from PIL import Image, ImageDraw
from pathlib import Path
assets = Path('assets')
assets.mkdir(parents=True, exist_ok=True)
img = Image.new('RGBA', (256, 256), (0,0,0,0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([12, 12, 244, 244], radius=48, fill=(18, 18, 28, 255), outline=(59, 130, 246, 255), width=6)
d.ellipse([36, 36, 220, 220], fill=(24, 24, 38, 255), outline=(139, 92, 246, 200), width=4)
pts = [(65, 185), (65, 75), (128, 140), (191, 75), (191, 185), (170, 185), (170, 115), (128, 160), (86, 115), (86, 185)]
d.polygon(pts, fill=(59, 130, 246, 255))
img.save(assets / 'icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
img.save(assets / 'logo.png', 'PNG')
"
)

:: 3. Run PyInstaller
echo.
echo [*] Packaging Machi.exe with PyInstaller...
python -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --console ^
    --name "Machi" ^
    --icon "assets/icon.ico" ^
    --add-data "data;data" ^
    --add-data "assets;assets" ^
    --add-data "logs;logs" ^
    --add-data ".env;." ^
    --hidden-import "customtkinter" ^
    --hidden-import "sounddevice" ^
    --hidden-import "speech_recognition" ^
    --hidden-import "pyttsx3" ^
    --hidden-import "pyautogui" ^
    --hidden-import "pygetwindow" ^
    --hidden-import "psutil" ^
    --hidden-import "pycaw" ^
    --hidden-import "comtypes" ^
    --hidden-import "google.generativeai" ^
    --hidden-import "dotenv" ^
    --collect-all "customtkinter" ^
    --exclude-module "PySide6" ^
    --exclude-module "shiboken6" ^
    --exclude-module "PyQt5" ^
    --exclude-module "PyQt6" ^
    --exclude-module "matplotlib" ^
    --exclude-module "scipy" ^
    --exclude-module "pandas" ^
    --exclude-module "IPython" ^
    --exclude-module "notebook" ^
    --exclude-module "tornado" ^
    "%MACHI_DIR%\main.py"

if %ERRORLEVEL% neq 0 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

:: Copy CLI launcher shims to dist\Machi\
copy /Y "%MACHI_DIR%\machi.cmd" "%MACHI_DIR%\dist\Machi\machi.cmd" >nul
copy /Y "%MACHI_DIR%\machi.bat" "%MACHI_DIR%\dist\Machi\machi.bat" >nul
copy /Y "%MACHI_DIR%\LICENSE" "%MACHI_DIR%\dist\Machi\LICENSE" >nul
if exist "%MACHI_DIR%\.env" copy /Y "%MACHI_DIR%\.env" "%MACHI_DIR%\dist\Machi\.env" >nul
xcopy /E /I /Y "%MACHI_DIR%\assets" "%MACHI_DIR%\dist\Machi\assets" >nul

echo [SUCCESS] Machi.exe built in: %MACHI_DIR%\dist\Machi\

:: 4. Build Setup Package
echo.
echo [*] Generating installer package...
powershell -NoProfile -ExecutionPolicy Bypass -File "%MACHI_DIR%\installer\CreateInstallerPackage.ps1"

:: 5. Locate and run Inno Setup Compiler (ISCC.exe) if available
set "ISCC_PATH="
where iscc >nul 2>nul
if %ERRORLEVEL% equ 0 set "ISCC_PATH=iscc"

if not defined ISCC_PATH (
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
    if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if defined ISCC_PATH (
    echo [*] Compiling Inno Setup installer using: "!ISCC_PATH!"
    "!ISCC_PATH!" "%MACHI_DIR%\installer\Machi.iss"
    if %ERRORLEVEL% equ 0 (
        echo [SUCCESS] Machi_Setup.exe compiled with Inno Setup!
    )
) else (
    echo [*] Inno Setup script ready at %MACHI_DIR%\installer\Machi.iss
)

echo.
echo =======================================================
echo          BUILD COMPLETE!
echo =======================================================
echo Portable Binary : %MACHI_DIR%\dist\Machi\Machi.exe
echo Setup Package   : %MACHI_DIR%\dist\Machi_Setup.bat
echo Inno Setup Spec : %MACHI_DIR%\installer\Machi.iss
echo.
pause
