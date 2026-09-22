import speech_recognition as sr
from typing import Tuple
from voice.microphone import microphone_manager
from utils.logger import logger
from utils.helpers import clean_speech_text

class SpeechToTextEngine:
    """Speech recognition engine translating spoken audio to text."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 100
        self.recognizer.dynamic_energy_threshold = True

    def listen_once(self, timeout: float = 6.0, phrase_time_limit: float = 12.0) -> Tuple[bool, str]:
        """
        Listens for a single speech command from microphone.
        Returns: (success_boolean, transcribed_text_or_error_message)
        """
        if not microphone_manager.is_available():
            return False, "Microphone is unavailable."

        try:
            logger.info("Listening for voice input...")
            audio = microphone_manager.record_speech_audio(timeout=timeout, phrase_time_limit=phrase_time_limit)

            if audio is None:
                return False, "No speech detected."

            logger.info("Processing speech recognition...")
            text = self.recognizer.recognize_google(audio)
            cleaned = clean_speech_text(text)
            logger.info(f"Transcribed speech: '{cleaned}'")
            return True, cleaned

        except sr.WaitTimeoutError:
            logger.debug("Speech recognition timed out.")
            return False, "No speech detected."
        except sr.UnknownValueError:
            logger.info("Speech was unintelligible.")
            return False, "I didn't hear that clearly. Please try again."
        except sr.RequestError as e:
            logger.error(f"Speech recognition service request error: {e}")
            return False, "Speech recognition service is currently unavailable."
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return False, f"Speech error: {e}"

stt_engine = SpeechToTextEngine()
