import sys
import time

import cv2

name = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"
cap = cv2.VideoCapture(0)
print("Placez votre main, photo dans 4 secondes...")
start = time.time()
frame = None
while time.time() - start < 4:
    ok, frame = cap.read()   # on lit en continu pour que la caméra se stabilise
cap.release()
if frame is None:
    sys.exit("Impossible de lire la caméra.")
cv2.imwrite(name, frame)
print("Photo enregistrée :", name)