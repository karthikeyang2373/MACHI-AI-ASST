import os
import re
import datetime
from pathlib import Path

def format_file_size(size_bytes: int) -> str:
    """Formats bytes into human readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def sanitize_filename(filename: str) -> str:
    """Removes invalid characters for Windows filenames."""
    return re.sub(r'[\\/*?:"<>|]', '_', filename).strip()

def get_timestamp_str() -> str:
    """Returns timestamp formatted string YYYY-MM-DD_HH-MM-SS."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def clean_speech_text(text: str) -> str:
    """Cleans up raw speech-to-text input string."""
    if not text:
        return ""
    cleaned = text.strip().lower()
    # Normalize punctuation and extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned