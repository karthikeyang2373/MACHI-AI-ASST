import logging
import os
import re
from pathlib import Path
from config import LOG_FILE, LOGS_DIR

# Ensure log directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class MaskingFormatter(logging.Formatter):
    """Custom log formatter to redact API keys and sensitive tokens."""
    PATTERNS = [
        (re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'), '[REDACTED_GEMINI_KEY]'),
        (re.compile(r'GEMINI_API_KEY=[\'"]?([^\'"\s]+)[\'"]?'), 'GEMINI_API_KEY=[REDACTED]'),
        (re.compile(r'password[\'"]?\s*:\s*[\'"]?([^\'"\s]+)[\'"]?', re.IGNORECASE), 'password: [REDACTED]'),
    ]

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        for pattern, replacement in self.PATTERNS:
            formatted = pattern.sub(replacement, formatted)
        return formatted

def setup_logger(name: str = "MACHI") -> logging.Logger:
    """Sets up and returns a configured logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # File Handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = MaskingFormatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = MaskingFormatter(
            fmt='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()