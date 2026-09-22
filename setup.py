#!/usr/bin/env python3
"""Setup script for MACHI project.

This script prepares a fresh Windows machine to run MACHI:
  1. Creates a Python virtual environment in the project root.
  2. Installs all Python dependencies from requirements.txt.
  3. (Optional) Adds the project folder to the user's PATH.
  4. (Optional) Creates a desktop shortcut for the `machi` command.

The script is deliberately lightweight – it does *not* perform any destructive
cleanup beyond what the user explicitly requested (the `build/` folder).  For
more advanced setup steps (e.g., pushing to GitHub) the user can extend this
script.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"

def run(cmd, check=True, shell=False):
    """Run a command and stream its output."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=shell, check=check, text=True)
    return result

def create_venv():
    if VENV_DIR.exists():
        print(f"Virtual environment already exists at {VENV_DIR}")
        return
    print("Creating virtual environment...")
    run([sys.executable, "-m", "venv", str(VENV_DIR)])

def install_requirements():
    pip_exe = VENV_DIR / "Scripts" / "pip.exe"
    if not pip_exe.exists():
        raise FileNotFoundError("pip executable not found in venv")
    requirements = PROJECT_ROOT / "requirements.txt"
    if not requirements.is_file():
        raise FileNotFoundError("requirements.txt not found")
    print("Installing dependencies from requirements.txt...")
    run([str(pip_exe), "install", "-r", str(requirements)])

def add_to_user_path():
    # Add the project folder to the user's PATH (persistent for future sessions)
    path = os.getenv("PATH", "")
    if str(PROJECT_ROOT) in path:
        print("Project folder already in PATH.")
        return
    cmd = [
        "powershell",
        "-Command",
        f"[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';{PROJECT_ROOT}', 'User')"
    ]
    print("Adding project folder to User PATH...")
    run(cmd, shell=True)

def create_desktop_shortcut():
    # Create a shortcut on the current user's Desktop that runs the MACHI command
    desktop = Path(os.path.expanduser('~')) / 'Desktop'
    shortcut_path = desktop / 'MACHI AI Assistant.lnk'
    target = VENV_DIR / "Scripts" / "python.exe"
    script = PROJECT_ROOT / "main.py"
    # Use PowerShell to create a .lnk file
    ps_script = f"$WshShell = New-Object -ComObject WScript.Shell; "
    ps_script += f"$Shortcut = $WshShell.CreateShortcut('{shortcut_path}'); "
    ps_script += f"$Shortcut.TargetPath = '{target}'; "
    ps_script += f"$Shortcut.Arguments = '{script}'; "
    ps_script += f"$Shortcut.WorkingDirectory = '{PROJECT_ROOT}'; "
    ps_script += "$Shortcut.IconLocation = 'shell32.dll,0'; "
    ps_script += "$Shortcut.Save()"
    run(["powershell", "-Command", ps_script], shell=True)
    print(f"Desktop shortcut created at {shortcut_path}")

def main():
    create_venv()
    install_requirements()
    add_to_user_path()
    create_desktop_shortcut()
    print("\nSetup complete! Open a new terminal and run 'machi' to start the assistant.")

if __name__ == "__main__":
    main()
