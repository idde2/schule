import cv2
import mediapipe as mp
import math
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# -----------------------------
# 1. MODEL LADEN
# -----------------------------
base_options = python.BaseOptions(
    model_asset_path="dateien/hand_landmarker.task"
)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)
detector = vision.HandLandmarker.create_from_options(options)

# -----------------------------
# 2. KALIBRIERUNG
# -----------------------------
# Beispiel: 2-Euro-Münze = 2.575 cm Durchmesser
REAL_SIZE_CM = 2.575

calibration_factor = None  # cm pro Pixel

def calibrate(px_distance):
    return REAL_SIZE_CM / px_distance


# -----------------------------
# 3. VIDEO LOOP
# -----------------------------
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        h, w, _ = frame.shape
        lm = result.hand_landmarks[0]

        # Daumen- und Zeigefinger-Spitze
        x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
        x2, y2 = int(lm[8].x * w), int(lm[8].y * h)

        # Pixelabstand
        px_dist = math.hypot(x2 - x1, y2 - y1)

        # Falls noch nicht kalibriert → Benutzer soll Münze zeigen
        if calibration_factor is None:
            cv2.putText(frame, "Halte eine 2-Euro-Muenze ins Bild!",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Pixel: {int(px_dist)}",
                        (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # Wenn Münze erkannt → ENTER druecken
            if cv2.waitKey(1) & 0xFF == 13:
                calibration_factor = calibrate(px_dist)
            cv2.imshow("HandLandmarker", frame)
            continue

        # Umrechnung in cm
        cm_dist = px_dist * calibration_factor

        # Visualisierung
        cv2.circle(frame, (x1, y1), 10, (0, 255, 0), -1)
        cv2.circle(frame, (x2, y2), 10, (0, 255, 0), -1)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)

        cv2.putText(frame, f"{cm_dist:.2f} cm",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

    cv2.imshow("HandLandmarker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
