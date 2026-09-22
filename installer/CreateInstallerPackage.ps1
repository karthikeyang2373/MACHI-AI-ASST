# PowerShell Standalone Installer Generator for Machi AI Assistant
param (
    [string]$SourceDir = "d:\MACHI\dist\Machi",
    [string]$OutputDir = "d:\MACHI\dist"
)

$ErrorActionPreference = "Stop"
Write-Host "Creating setup package for Machi AI Assistant..."

if (-not (Test-Path $SourceDir)) {
    Write-Error "Source directory $SourceDir does not exist. Run PyInstaller first."
    exit 1
}

$zipPath = Join-Path $OutputDir "Machi_Package.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($SourceDir, $zipPath)

$setupScript = @"
@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo     Welcome to the Machi AI Assistant Setup
echo =======================================================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\Machi"
echo [*] Target Directory: !INSTALL_DIR!

if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"

echo [*] Extracting files...
powershell -NoProfile -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%~dp0Machi_Package.zip', '!INSTALL_DIR!', `$true)"

echo [*] Registering 'machi' command into User PATH...
powershell -NoProfile -Command ^
    "`$current = [Environment]::GetEnvironmentVariable('Path', 'User');" ^
    "`$target = '!INSTALL_DIR!';" ^
    "if (`$current -split ';' -notcontains `$target) {" ^
    "    `$new = if (`$current) { `$current.TrimEnd(';') + ';' + `$target } else { `$target };" ^
    "    [Environment]::SetEnvironmentVariable('Path', `$new, 'User');" ^
    "    Write-Host '[SUCCESS] Registered in User PATH!';" ^
    "}"

echo [*] Creating Start Menu Shortcut...
powershell -NoProfile -Command ^
    "`$wsh = New-Object -ComObject WScript.Shell;" ^
    "`$s = `$wsh.CreateShortcut([Environment]::GetFolderPath('Programs') + '\Machi AI Assistant.lnk');" ^
    "`$s.TargetPath = '!INSTALL_DIR!\Machi.exe';" ^
    "`$s.WorkingDirectory = '!INSTALL_DIR!';" ^
    "`$s.IconLocation = '!INSTALL_DIR!\assets\icon.ico';" ^
    "`$s.Save();"

echo [*] Creating Desktop Shortcut...
powershell -NoProfile -Command ^
    "`$wsh = New-Object -ComObject WScript.Shell;" ^
    "`$s = `$wsh.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Machi AI Assistant.lnk');" ^
    "`$s.TargetPath = '!INSTALL_DIR!\Machi.exe';" ^
    "`$s.WorkingDirectory = '!INSTALL_DIR!';" ^
    "`$s.IconLocation = '!INSTALL_DIR!\assets\icon.ico';" ^
    "`$s.Save();"

echo.
echo =======================================================
echo   Machi has been successfully installed!
echo =======================================================
echo.
echo Open a NEW CMD or PowerShell window and run:
echo.
echo     machi
echo.
pause
"@

$batPath = Join-Path $OutputDir "Machi_Setup.bat"
[System.IO.File]::WriteAllText($batPath, $setupScript)
Write-Host "Generated: $batPath and $zipPath"
