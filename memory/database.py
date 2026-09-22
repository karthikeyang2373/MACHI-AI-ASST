import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import DATABASE_PATH, DATA_DIR
from utils.logger import logger

class DatabaseManager:
    """Manages SQLite database storage for MACHI."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection to SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes SQLite tables if they do not exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Table: command_logs
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        raw_input TEXT NOT NULL,
                        intent TEXT,
                        status TEXT NOT NULL,
                        result_summary TEXT,
                        safety_level INTEGER DEFAULT 1
                    )
                """)

                # Table: user_preferences
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)

                # Table: app_aliases
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_aliases (
                        alias TEXT PRIMARY KEY,
                        target TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)

                # Table: conversation_history
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        sender TEXT NOT NULL,
                        message TEXT NOT NULL,
                        intent TEXT
                    )
                """)

                conn.commit()
                logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    def log_command(self, raw_input: str, intent: str, status: str, result_summary: str, safety_level: int = 1):
        """Logs a command execution to database."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO command_logs (timestamp, raw_input, intent, status, result_summary, safety_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (timestamp, raw_input, intent, status, result_summary, safety_level))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging command to DB: {e}")

    def get_recent_commands(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent logged commands."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, timestamp, raw_input, intent, status, result_summary, safety_level
                    FROM command_logs ORDER BY id DESC LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching recent commands: {e}")
            return []

    def set_preference(self, key: str, value: str):
        """Sets a user preference in DB."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, value, timestamp))
                conn.commit()
        except Exception as e:
            logger.error(f"Error setting preference '{key}': {e}")

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Gets a user preference from DB."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row["value"] if row else default
        except Exception as e:
            logger.error(f"Error getting preference '{key}': {e}")
            return default

    def set_alias(self, alias: str, target: str):
        """Stores a custom application or path alias."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO app_aliases (alias, target, created_at)
                    VALUES (?, ?, ?)
                """, (alias.lower().strip(), target, timestamp))
                conn.commit()
        except Exception as e:
            logger.error(f"Error setting alias '{alias}': {e}")

    def get_alias(self, alias: str) -> Optional[str]:
        """Retrieves target for a custom alias."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT target FROM app_aliases WHERE alias = ?", (alias.lower().strip(),))
                row = cursor.fetchone()
                return row["target"] if row else None
        except Exception as e:
            logger.error(f"Error getting alias '{alias}': {e}")
            return None

    def log_chat(self, sender: str, message: str, intent: Optional[str] = None):
        """Logs chat message."""
        try:
            timestamp = datetime.datetime.now().isoformat()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversation_history (timestamp, sender, message, intent)
                    VALUES (?, ?, ?, ?)
                """, (timestamp, sender, message, intent))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging chat message: {e}")

    def get_chat_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent chat messages."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, timestamp, sender, message, intent
                    FROM conversation_history ORDER BY id DESC LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                # Return in chronological order
                return list(reversed([dict(row) for row in rows]))
        except Exception as e:
            logger.error(f"Error fetching chat history: {e}")
            return []

db_manager = DatabaseManager()
