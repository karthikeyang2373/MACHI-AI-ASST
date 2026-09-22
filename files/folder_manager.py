import os
from pathlib import Path
from typing import Tuple
from utils.paths import resolve_known_folder, get_user_home, get_downloads_dir
from utils.logger import logger
from memory.conversation_manager import conversation_manager

class FolderManager:
    """Manages opening and navigating Windows folders via voice commands."""

    def open_folder(self, folder_alias_or_path: str) -> Tuple[bool, str]:
        """
        Opens a folder in Windows File Explorer.
        """
        target_path: Path = None

        # Check if folder is a known alias (e.g. "downloads", "desktop", "project folder")
        resolved = resolve_known_folder(folder_alias_or_path)
        if resolved:
            target_path = resolved
        elif "project" in folder_alias_or_path.lower():
            # Check user project folder or current directory
            target_path = Path.cwd()
        else:
            # Check direct path
            p = Path(folder_alias_or_path)
            if p.exists() and p.is_dir():
                target_path = p
            else:
                # Check inside user home directory
                home_p = get_user_home() / folder_alias_or_path
                if home_p.exists() and home_p.is_dir():
                    target_path = home_p

        if target_path and target_path.exists():
            try:
                os.startfile(str(target_path))
                conversation_manager.update_context("last_folder", str(target_path))
                logger.info(f"Opened folder in File Explorer: {target_path}")
                return True, f"Opening {target_path.name}."
            except Exception as e:
                logger.error(f"Error opening folder '{target_path}': {e}")
                return False, f"Could not open folder: {e}"
        else:
            return False, f"I couldn't find the folder '{folder_alias_or_path}'."

folder_manager = FolderManager()
