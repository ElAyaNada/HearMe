import threading
import time

import av
from streamlit_webrtc import VideoProcessorBase

from core.recognition import LetterRecognizer

HOLD_SECONDS = 1.0          # lettre tenue 1 seconde pour être validée
AUTO_SPACE_SECONDS = 2.0    # main absente pendant ce délai -> espace
MAX_LENGTH = 200


class SignProcessor(VideoProcessorBase):
    """Traite chaque image de la webcam (dans un thread séparé de Streamlit)."""

    def __init__(self):
        self.recognizer = LetterRecognizer()
        self.auto_space = True
        self.space_delay = AUTO_SPACE_SECONDS
        self._lock = threading.Lock()
        self._text = ""
        self._candidate = ""
        self._since = time.time()
        self._shown = ""
        self._no_hand_since = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        detection = self.recognizer.predict(img)
        letter = detection.letter
        now = time.time()

        with self._lock:
            # Espace automatique quand la main disparaît
            if detection.hands_count == 0:
                if self._no_hand_since is None:
                    self._no_hand_since = now
                elif (
                    self.auto_space
                    and now - self._no_hand_since > self.space_delay
                    and self._text
                    and not self._text.endswith(" ")
                    and len(self._text) < MAX_LENGTH
                ):
                    self._text += " "
            else:
                self._no_hand_since = None

            # Validation d'une lettre tenue 1 seconde
            if letter is None:
                self._candidate = ""
                self._since = now
            elif letter != self._candidate:
                self._candidate = letter
                self._since = now
            elif now - self._since > HOLD_SECONDS and len(self._text) < MAX_LENGTH:
                self._text += letter
                self._since = now
            self._shown = letter or ""

        img = self.recognizer.draw(img, detection)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    # Méthodes appelées par la page (autre thread) : toujours sous verrou
    def get_text(self) -> str:
        with self._lock:
            return self._text

    def get_letter(self) -> str:
        with self._lock:
            return self._shown

    def add_space(self):
        with self._lock:
            if self._text and not self._text.endswith(" ") and len(self._text) < MAX_LENGTH:
                self._text += " "

    def delete_last(self):
        with self._lock:
            if self._text.endswith(" "):
                # Espace final : on retire l'espace et la lettre qui le précède
                self._text = self._text.rstrip(" ")[:-1]
            else:
                self._text = self._text[:-1]
            self._candidate = ""
            self._since = time.time()
            self._no_hand_since = None   # relance le délai de l'espace automatique

    def clear(self):
        with self._lock:
            self._text = ""
            self._candidate = ""
            self._since = time.time()