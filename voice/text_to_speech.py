import pyttsx3
import queue
import threading
import time
from typing import Callable, Optional
from utils.logger import logger

class TextToSpeechEngine:
    """Thread-safe, non-blocking Text-To-Speech engine using pyttsx3."""

    def __init__(self, rate: int = 190, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.muted = False
        self.speech_queue = queue.Queue()
        self._on_speaking_start: Optional[Callable] = None
        self._on_speaking_stop: Optional[Callable] = None
        self._is_speaking = False

        # Worker thread for speech processing
        self._thread = threading.Thread(target=self._speech_worker, daemon=True)
        self._thread.start()

    def set_callbacks(self, on_start: Callable = None, on_stop: Callable = None):
        """Sets callbacks for speaking start and stop events."""
        self._on_speaking_start = on_start
        self._on_speaking_stop = on_stop

    def is_speaking(self) -> bool:
        """Returns True if MACHI is currently speaking."""
        return self._is_speaking

    def set_muted(self, muted: bool):
        """Mutes or unmutes speech output."""
        self.muted = muted

    def set_rate(self, rate: int):
        """Sets speaking rate (speed)."""
        self.rate = max(100, min(300, rate))

    def set_volume(self, volume: float):
        """Sets TTS volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))

    def speak(self, text: str):
        """Enqueues text to be spoken asynchronously."""
        if not text or self.muted:
            return
        self.speech_queue.put(text)

    def _speech_worker(self):
        """Worker thread executing speech queued items safely in single COM context."""
        try:
            engine = pyttsx3.init()
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 TTS engine: {e}")
            engine = None

        while True:
            text = self.speech_queue.get()
            if text is None:
                break

            if engine and not self.muted:
                try:
                    self._is_speaking = True
                    if self._on_speaking_start:
                        self._on_speaking_start(text)

                    engine.setProperty('rate', self.rate)
                    engine.setProperty('volume', self.volume)
                    
                    logger.info(f"MACHI Speaking: '{text}'")
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    logger.error(f"TTS Speech error: {e}")
                finally:
                    self._is_speaking = False
                    if self._on_speaking_stop:
                        self._on_speaking_stop()
            else:
                logger.info(f"MACHI (Muted/No-TTS): '{text}'")

            self.speech_queue.task_done()

tts_engine = TextToSpeechEngine()
