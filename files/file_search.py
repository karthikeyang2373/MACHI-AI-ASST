import os
from pathlib import Path
from typing import List, Tuple
from utils.paths import get_user_home, get_downloads_dir, get_desktop_dir, get_documents_dir
from utils.logger import logger
from memory.conversation_manager import conversation_manager

class FileSearchEngine:
    """Fast search engine for user files and documents across common directories."""

    def search(self, query: str, target_dir: Path = None, max_results: int = 10) -> Tuple[bool, List[Path], str]:
        """
        Searches for files matching query (extension or filename substring).
        """
        search_dirs = []
        if target_dir and target_dir.exists():
            search_dirs.append(target_dir)
        else:
            # Use contextual last_folder if available
            last_folder = conversation_manager.get_context("last_folder")
            if last_folder and Path(last_folder).exists():
                search_dirs.append(Path(last_folder))
            # Also search standard user locations
            search_dirs.extend([get_downloads_dir(), get_desktop_dir(), get_documents_dir(), Path.cwd()])

        matches: List[Path] = []
        query_lower = query.lower().strip()

        # Check for extension keywords e.g. "python files", "pdf files", "presentation files"
        ext_map = {
            "python": [".py"],
            "pdf": [".pdf"],
            "presentation": [".ppt", ".pptx"],
            "powerpoint": [".ppt", ".pptx"],
            "word": [".doc", ".docx"],
            "excel": [".xls", ".xlsx", ".csv"],
            "image": [".png", ".jpg", ".jpeg", ".gif"],
            "audio": [".mp3", ".wav"],
            "video": [".mp4", ".mkv", ".avi"],
            "zip": [".zip", ".tar", ".gz", ".7z", ".rar"]
        }

        target_exts = None
        for key, exts in ext_map.items():
            if key in query_lower:
                target_exts = exts
                break

        for sdir in search_dirs:
            try:
                # Top level search first for speed
                for root, dirs, files in os.walk(sdir):
                    # Limit scan depth to 3 levels max
                    depth = len(Path(root).relative_to(sdir).parts)
                    if depth > 3:
                        continue

                    for file in files:
                        file_lower = file.lower()
                        match_found = False

                        if target_exts:
                            if any(file_lower.endswith(ext) for ext in target_exts):
                                match_found = True
                        elif query_lower in file_lower:
                            match_found = True

                        if match_found:
                            file_path = Path(root) / file
                            if file_path not in matches:
                                matches.append(file_path)
                                if len(matches) >= max_results:
                                    break
                    if len(matches) >= max_results:
                        break
            except Exception as e:
                logger.error(f"Error walking directory '{sdir}' during search: {e}")

        if matches:
            first_match = str(matches[0])
            conversation_manager.update_context("last_file", first_match)
            count = len(matches)
            msg = f"I found {count} matching file{'s' if count > 1 else ''}."
            logger.info(f"File search for '{query}' found {count} results. Top: {first_match}")
            return True, matches, msg
        else:
            msg = f"No files matching '{query}' were found."
            logger.info(msg)
            return False, [], msg

file_search_engine = FileSearchEngine()
