import time
import math
import numpy as np
from typing import Optional, Tuple
from utils.logger import logger
from config import SAMPLE_RATE, CHUNK_SIZE

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import sounddevice as sd
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False


class MicrophoneManager:
    """
    Dual-backend microphone manager.
    Supports PyAudio when available, with an automatic, highly robust
    sounddevice + numpy fallback with Voice Activity Detection (VAD).
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self.mic = None
        self.use_sounddevice = False
        self._available = False
        self.ambient_energy = 300.0
        self._init_microphone()

    def _init_microphone(self):
        """Initializes microphone backend (PyAudio or SoundDevice)."""
        # Try PyAudio first if present
        if SR_AVAILABLE:
            try:
                self.mic = sr.Microphone(sample_rate=self.sample_rate)
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                self.use_sounddevice = False
                self._available = True
                logger.info("Microphone initialized with PyAudio backend.")
                return
            except Exception as e:
                logger.info(f"PyAudio mic not available ({e}), falling back to SoundDevice backend.")

        # Fallback to SoundDevice
        if SD_AVAILABLE:
            try:
                # Test query input devices
                devices = sd.query_devices()
                default_input = sd.default.device[0]
                if default_input is not None and default_input >= 0:
                    self.use_sounddevice = True
                    self._available = True
                    self._calibrate_ambient_noise()
                    logger.info("Microphone initialized with SoundDevice backend.")
                    return
                else:
                    # Search for any input device
                    for idx, dev in enumerate(devices):
                        if dev.get('max_input_channels', 0) > 0:
                            sd.default.device = (idx, sd.default.device[1])
                            self.use_sounddevice = True
                            self._available = True
                            self._calibrate_ambient_noise()
                            logger.info(f"Microphone initialized on device {idx}: {dev['name']}.")
                            return
            except Exception as e:
                logger.error(f"SoundDevice mic initialization failed: {e}")

        logger.warning("No working microphone backend found.")
        self._available = False

    def _calibrate_ambient_noise(self, duration: float = 0.4):
        """Measures background noise RMS using sounddevice."""
        if not self.use_sounddevice:
            return
        try:
            samples = int(self.sample_rate * duration)
            recording = sd.rec(samples, samplerate=self.sample_rate, channels=1, dtype='int16')
            sd.wait()
            data = recording.flatten().astype(np.float32)
            rms = math.sqrt(np.mean(data ** 2)) if len(data) > 0 else 50.0
            self.ambient_energy = max(30.0, min(rms * 1.2, 100.0))
            logger.info(f"Calibrated ambient energy threshold: {self.ambient_energy:.1f}")
        except Exception as e:
            logger.debug(f"Ambient noise calibration error: {e}")
            self.ambient_energy = 40.0

    def is_available(self) -> bool:
        return self._available

    def record_speech_audio(self, timeout: float = 6.0, phrase_time_limit: float = 12.0) -> Optional[sr.AudioData]:
        """
        Captures speech audio from the microphone.
        Uses adaptive energy thresholding and pre-buffering to ensure no speech is lost.
        Returns sr.AudioData object ready for speech recognition.
        """
        if not self._available:
            return None

        # 1. PyAudio path
        if not self.use_sounddevice and self.mic:
            try:
                with self.mic as source:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    return audio
            except Exception as e:
                logger.error(f"PyAudio listen error: {e}")
                return None

        # 2. SoundDevice path with Voice Activity Detection
        if self.use_sounddevice and SD_AVAILABLE:
            try:
                chunk_duration = 0.1  # 100ms chunks
                chunk_samples = int(self.sample_rate * chunk_duration)
                silence_threshold = max(35.0, min(self.ambient_energy, 90.0))
                speech_detected = False
                silence_chunks = 0
                max_silence_chunks = int(1.4 / chunk_duration)  # 1.4s of silence stops recording
                recorded_frames = []
                start_time = time.time()
                speech_start_time = None

                with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16', blocksize=chunk_samples) as stream:
                    while True:
                        now = time.time()
                        chunk, overflow = stream.read(chunk_samples)
                        chunk_flat = chunk.flatten()
                        recorded_frames.append(chunk_flat)

                        # Calculate RMS energy
                        float_chunk = chunk_flat.astype(np.float32)
                        rms = math.sqrt(np.mean(float_chunk ** 2)) if len(float_chunk) > 0 else 0

                        if rms >= silence_threshold:
                            if not speech_detected:
                                speech_detected = True
                                speech_start_time = now
                                logger.info(f"Speech activity detected (RMS: {rms:.1f})")
                            silence_chunks = 0
                        else:
                            if speech_detected:
                                silence_chunks += 1
                                if silence_chunks >= max_silence_chunks:
                                    logger.info("Speech finished (silence detected).")
                                    break

                        # Timeout if no speech started after timeout seconds
                        if not speech_detected and (now - start_time) > timeout:
                            logger.info("Listening window ended.")
                            break

                        # Max phrase time limit
                        if speech_detected and speech_start_time and (now - speech_start_time) > phrase_time_limit:
                            logger.info("Phrase time limit reached.")
                            break

                if recorded_frames:
                    full_audio = np.concatenate(recorded_frames, axis=0)
                    # Only return if we actually captured valid non-empty audio
                    if len(full_audio) >= self.sample_rate * 0.4:
                        raw_bytes = full_audio.tobytes()
                        return sr.AudioData(raw_bytes, self.sample_rate, 2)
                return None

            except Exception as e:
                logger.error(f"SoundDevice recording error: {e}")
                return None

        return None



microphone_manager = MicrophoneManager(sample_rate=SAMPLE_RATE)
