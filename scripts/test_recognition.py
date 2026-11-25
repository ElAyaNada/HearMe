import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

from core.recognition import LetterRecognizer

if len(sys.argv) < 2:
    sys.exit("Usage : python scripts/test_recognition.py image.jpg")

frame = cv2.imread(sys.argv[1])
if frame is None:
    sys.exit("Image introuvable.")

rec = LetterRecognizer()
d = rec.predict(frame)
print("Mains vues :", d.hands_count)
print("Lettre     :", d.letter)
print("Cadre      :", d.bbox)
rec.close()