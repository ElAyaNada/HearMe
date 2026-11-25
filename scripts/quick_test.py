import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

from core.recognition import LetterRecognizer

rec = LetterRecognizer()
cap = cv2.VideoCapture(0)
good, total = 0, 0

print("Tapez la lettre que vous allez signer (0 = aucune main). Entrée vide = terminer.")
while True:
    expected = input("\nLettre attendue : ").strip().upper()
    if not expected:
        break

    start = time.time()
    frame = None
    while time.time() - start < 4:
        ok, f = cap.read()
        if ok:
            frame = f
            view = f.copy()
            left = 4 - int(time.time() - start)
            cv2.putText(view, f"Signe {expected} : photo dans {left}", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow("Test", view)
            cv2.waitKey(1)

    if frame is None:
        print("Impossible de lire la camera.")
        break

    d = rec.predict(frame)
    expected_letter = None if expected == "0" else expected
    verdict = "OK" if d.letter == expected_letter else "ECHEC"
    print(f"Mains vues : {d.hands_count} | Lettre : {d.letter} | Attendu : {expected_letter} -> {verdict}")
    total += 1
    good += verdict == "OK"

cap.release()
cv2.destroyAllWindows()
rec.close()
print(f"\nResultat : {good}/{total}")
