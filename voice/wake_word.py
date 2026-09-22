import threading
import time
from typing import Callable, Optional
from voice.speech_to_text import stt_engine
from voice.microphone import microphone_manager
from config import WAKE_WORD
from utils.logger import logger

class WakeWordListener:
    """Continuous background wake-word detector ("Hey Machi", "Machi", "OK Machi")."""

    def __init__(self, wake_word: str = WAKE_WORD):
        self.wake_word = wake_word.lower()
        self.is_running = False
        self._on_wake_detected: Optional[Callable] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, callback: Callable):
        """Starts continuous wake word monitoring in a background thread."""
        if self.is_running:
            return

        self._on_wake_detected = callback
        self.is_running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info(f"Wake word listener started for: '{self.wake_word}'")

    def stop(self):
        """Stops wake word monitoring thread."""
        self.is_running = False
        logger.info("Wake word listener stopped.")

    def _listen_loop(self):
        """Background loop constantly listening for wake word phrase."""
        while self.is_running:
            if not microphone_manager.is_available():
                time.sleep(2.0)
                continue

            try:
                success, text = stt_engine.listen_once(timeout=3.0, phrase_time_limit=4.0)
                if success and text:
                    text_lower = text.lower()
                    wake_phrases = [self.wake_word, "machi", "hey match", "hey makhi", "ok machi", "hi machi"]
                    if any(p in text_lower for p in wake_phrases):
                        logger.info(f"Wake word detected in input: '{text}'")
                        if self._on_wake_detected:
                            self._on_wake_detected()
                        time.sleep(1.0)
            except Exception as e:
                logger.debug(f"Wake word loop error: {e}")
                time.sleep(0.5)

wake_word_listener = WakeWordListener()
