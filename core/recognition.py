"""Reconnaissance des lettres ASL à partir d'une image.

Même prétraitement que model/app.py : 21 points de la main, x et y diminués
du minimum de la main -> 42 nombres envoyés au modèle.
"""
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "assets" / "model.p"


@dataclass
class Detection:
    letter: Optional[str]    # None si aucune prédiction possible
    bbox: Optional[tuple]    # (x1, y1, x2, y2) en pixels, None si aucune main
    hands_count: int         # nombre de mains vues
    landmarks: list          # points MediaPipe, pour le dessin


class LetterRecognizer:
    def __init__(self, model_path: Path = MODEL_PATH):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)["model"]
        self._mp_hands = mp.solutions.hands
        self._drawing = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            static_image_mode=True, min_detection_confidence=0.3
        )

    def predict(self, frame_bgr: np.ndarray) -> Detection:
        """frame_bgr : image OpenCV (BGR). Renvoie une Detection."""
        h, w, _ = frame_bgr.shape
        results = self._hands.process(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))

        if not results.multi_hand_landmarks:
            return Detection(None, None, 0, [])

        hands = results.multi_hand_landmarks
        xs = [lm.x for hand in hands for lm in hand.landmark]
        ys = [lm.y for hand in hands for lm in hand.landmark]
        min_x, min_y = min(xs), min(ys)

        data = []
        for hand in hands:
            for lm in hand.landmark:
                data.append(lm.x - min_x)
                data.append(lm.y - min_y)

        bbox = (
            max(int(min_x * w) - 10, 0),
            max(int(min_y * h) - 10, 0),
            min(int(max(xs) * w) + 10, w),
            min(int(max(ys) * h) + 10, h),
        )

        # Le modèle attend exactement 42 nombres = une seule main
        letter = None
        if len(data) == 42:
            letter = str(self.model.predict([np.asarray(data)])[0])

        return Detection(letter, bbox, len(hands), list(hands))

    def draw(self, frame_bgr: np.ndarray, detection: Detection) -> np.ndarray:
        """Dessine les points de la main, le cadre et la lettre sur l'image."""
        for hand in detection.landmarks:
            self._drawing.draw_landmarks(
                frame_bgr, hand, self._mp_hands.HAND_CONNECTIONS
            )
        if detection.bbox:
            x1, y1, x2, y2 = detection.bbox
            cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (255, 255, 255), 3)
            if detection.letter:
                cv2.putText(frame_bgr, detection.letter, (x1, max(y1 - 10, 30)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3, cv2.LINE_AA)
        return frame_bgr

    def close(self):
        self._hands.close()