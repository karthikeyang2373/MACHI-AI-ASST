@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo          MACHI AI Assistant — Quick Installer
echo =======================================================
echo.

set "MACHI_DIR=%~dp0"
set "MACHI_DIR=%MACHI_DIR:~0,-1%"

:: 1. Check Python
echo [*] Checking Python installation...
python --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ and tick "Add python.exe to PATH".
    pause
    exit /b 1
)
python --version

:: 2. Install dependencies
echo.
echo [*] Installing required Python dependencies...
python -m pip install -r "%MACHI_DIR%\requirements.txt" --quiet
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Some dependencies had warnings or issues. Attempting core packages...
    python -m pip install customtkinter speechrecognition sounddevice numpy psutil pyautogui pygetwindow python-dotenv pycaw comtypes pyttsx3
)

:: 3. Add to User PATH
echo.
echo [*] Registering 'machi' command into Windows User PATH...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User');" ^
    "$target = '%MACHI_DIR%';" ^
    "if ($currentPath -split ';' -notcontains $target) {" ^
    "    $newPath = if ($currentPath) { $currentPath.TrimEnd(';') + ';' + $target } else { $target };" ^
    "    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User');" ^
    "    Write-Host '[SUCCESS] Added %MACHI_DIR% to User PATH!';" ^
    "} else {" ^
    "    Write-Host '[INFO] %MACHI_DIR% is already present in User PATH.';" ^
    "}"

:: 4. Create Desktop Shortcut via VBScript
echo.
echo [*] Creating Desktop Shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$WshShell = New-Object -comObject WScript.Shell;" ^
    "$Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\MACHI AI Assistant.lnk');" ^
    "$Shortcut.TargetPath = '%MACHI_DIR%\machi.cmd';" ^
    "$Shortcut.WorkingDirectory = '%MACHI_DIR%';" ^
    "$Shortcut.Description = 'MACHI AI Voice Control Laptop Assistant';" ^
    "$Shortcut.Save();" ^
    "Write-Host '[SUCCESS] Desktop shortcut created!';"

echo.
echo =======================================================
echo          MACHI Installation Complete!
echo =======================================================
echo.
echo You can now run MACHI anywhere!
echo Open a NEW Command Prompt or PowerShell and type:
echo.
echo     machi
echo.
echo Other useful commands:
echo     machi --version
echo     machi --help
echo     machi --settings
echo     machi --cli "increase volume"
echo.
pause
