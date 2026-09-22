import webbrowser
import subprocess
import urllib.parse
from typing import Tuple
from config import DEFAULT_BROWSER
from utils.logger import logger


SITE_SHORTCUTS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "reddit": "https://www.reddit.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "chatgpt": "https://chat.openai.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "linkedin": "https://www.linkedin.com",
    "stackoverflow": "https://stackoverflow.com",
}

SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q={}",
    "youtube": "https://www.youtube.com/results?search_query={}",
    "bing": "https://www.bing.com/search?q={}",
    "duckduckgo": "https://duckduckgo.com/?q={}",
}


class WebHandler:
    """Handles browser navigation and web search commands."""

    def open_website(self, site: str) -> Tuple[bool, str]:
        """Opens a website by name or URL."""
        site_lower = site.strip().lower().rstrip(".com").rstrip(".org")

        url = SITE_SHORTCUTS.get(site_lower)
        if not url:
            # Try as raw URL
            if site.startswith("http://") or site.startswith("https://"):
                url = site
            else:
                url = f"https://www.{site}.com"

        try:
            webbrowser.open(url)
            logger.info(f"Opened website: {url}")
            return True, f"Opening {site}."
        except Exception as e:
            logger.error(f"Failed to open website '{url}': {e}")
            return False, f"Could not open {site}."

    def search_web(self, query: str, engine: str = "google") -> Tuple[bool, str]:
        """Searches the web using the specified search engine."""
        engine_lower = engine.strip().lower()
        template = SEARCH_ENGINES.get(engine_lower, SEARCH_ENGINES["google"])
        encoded_query = urllib.parse.quote_plus(query)
        url = template.format(encoded_query)

        try:
            webbrowser.open(url)
            logger.info(f"Web search [{engine}]: {query}")
            return True, f"Searching {engine} for {query}."
        except Exception as e:
            logger.error(f"Failed to search web: {e}")
            return False, "Could not open browser for search."


web_handler = WebHandler()
