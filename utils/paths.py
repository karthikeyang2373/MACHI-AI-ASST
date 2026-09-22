import os
from pathlib import Path

def get_user_home() -> Path:
    """Returns the user's home directory path."""
    return Path(os.path.expanduser("~"))

def get_downloads_dir() -> Path:
    """Returns the user's Downloads directory."""
    home = get_user_home()
    return home / "Downloads"

def get_desktop_dir() -> Path:
    """Returns the user's Desktop directory."""
    home = get_user_home()
    return home / "Desktop"

def get_documents_dir() -> Path:
    """Returns the user's Documents directory."""
    home = get_user_home()
    return home / "Documents"

def get_pictures_dir() -> Path:
    """Returns the user's Pictures directory."""
    home = get_user_home()
    return home / "Pictures"

def get_videos_dir() -> Path:
    """Returns the user's Videos directory."""
    home = get_user_home()
    return home / "Videos"

def get_music_dir() -> Path:
    """Returns the user's Music directory."""
    home = get_user_home()
    return home / "Music"

def get_screenshots_dir() -> Path:
    """Returns the MACHI Screenshots directory in Pictures."""
    screenshots_dir = get_pictures_dir() / "MACHI_Screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    return screenshots_dir

def resolve_known_folder(folder_alias: str) -> Path | None:
    """Resolves a friendly folder alias to its actual Path."""
    alias_map = {
        "downloads": get_downloads_dir(),
        "download": get_downloads_dir(),
        "desktop": get_desktop_dir(),
        "documents": get_documents_dir(),
        "document": get_documents_dir(),
        "pictures": get_pictures_dir(),
        "picture": get_pictures_dir(),
        "photos": get_pictures_dir(),
        "images": get_pictures_dir(),
        "videos": get_videos_dir(),
        "video": get_videos_dir(),
        "movies": get_videos_dir(),
        "music": get_music_dir(),
        "audio": get_music_dir(),
        "songs": get_music_dir(),
        "screenshots": get_screenshots_dir(),
    }
    return alias_map.get(folder_alias.lower().strip())