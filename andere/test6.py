import cv2
import numpy as np

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # verkleinern für mehr FPS
    small = cv2.resize(frame, None, fx=0.7, fy=0.7)

    # Kanten extrahieren
    edges = cv2.Canny(small, 80, 160)

    # Glitch-Effekt: RGB-Kanäle gegeneinander verschieben
    b, g, r = cv2.split(small)
    glitch = cv2.merge([
        np.roll(b, 5, axis=1),
        np.roll(g, -5, axis=0),
        np.roll(r, 8, axis=1)
    ])

    # Kanten invertieren und als Maske nutzen
    mask = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    mask = cv2.bitwise_not(mask)

    # Mischung aus Original + Glitch + Kanten
    combined = cv2.addWeighted(glitch, 0.6, mask, 0.4, 0)

    cv2.imshow("Glitch Edge Vision", combined)

    if cv2.waitKey(1) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
