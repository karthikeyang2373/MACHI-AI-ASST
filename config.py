import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"
SCREENSHOTS_DIR = Path(os.path.expanduser("~/Pictures/MACHI_Screenshots"))

# Create directories
for dir_path in [DATA_DIR, LOGS_DIR, ASSETS_DIR, SCREENSHOTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Version info
VERSION = "1.0.0"
APP_TITLE = "MACHI — AI Voice Control Laptop Assistant"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Assistant settings
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "MACHI")
WAKE_WORD = os.getenv("WAKE_WORD", "hey machi").lower()

# File paths
DATABASE_PATH = DATA_DIR / "machi.db"
LOG_FILE = LOGS_DIR / "machi.log"

# Voice settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1

# GUI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
THEME = "dark-blue"

# Security settings
DEFAULT_PERMISSIONS = {
    "file_access": "ENABLED",
    "browser_access": "ENABLED",
    "application_access": "ENABLED",
    "system_information": "ENABLED",
    "keyboard_control": "ENABLED",
    "mouse_control": "ENABLED",
    "power_commands": "CONFIRM",
    "file_deletion": "CONFIRM",
    "system_changes": "CONFIRM"
}

# Command levels
COMMAND_LEVELS = {
    "SAFE": 1,
    "MODERATE": 2,
    "HIGH_RISK": 3
}

# Application registry
KNOWN_APPS = {
    "chrome": ["chrome.exe", "google chrome"],
    "edge": ["msedge.exe", "microsoft edge"],
    "firefox": ["firefox.exe"],
    "brave": ["brave.exe"],
    "notepad": ["notepad.exe"],
    "vscode": ["code.cmd", "code.exe", "visual studio code"],
    "calculator": ["calc.exe", "calculator.exe"],
    "explorer": ["explorer.exe", "file explorer"],
    "file explorer": ["explorer.exe"],
    "task manager": ["taskmgr.exe"],
    "settings": ["ms-settings:"],
    "control panel": ["control.exe"],
    "command prompt": ["cmd.exe"],
    "cmd": ["cmd.exe"],
    "terminal": ["wt.exe", "cmd.exe"],
    "powershell": ["powershell.exe"],
    "paint": ["mspaint.exe"],
    "wordpad": ["write.exe"],
    "camera": ["microsoft.windows.camera:"],
    "spotify": ["spotify.exe", "spotify:"],
    "slack": ["slack.exe"],
    "discord": ["discord.exe"],
    "telegram": ["telegram.exe"],
    "whatsapp": ["whatsapp:"],
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "powerpoint": ["powerpnt.exe"],
    "outlook": ["outlook.exe"],
    "notion": ["notion.exe"],
    "obsidian": ["obsidian.exe"],
    "store": ["ms-windows-store:"],
    "photos": ["ms-photos:"],
}

# Browser settings
DEFAULT_BROWSER = "chrome"