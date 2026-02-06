import cv2
import mediapipe as mp

def to_points(landmarks, w, h):
    if isinstance(landmarks[0], list):
        landmarks = landmarks[0]
    pts = []
    for p in landmarks:
        pts.append((int(p.x * w), int(p.y * h)))
    return pts

def count_fingers(pts):
    fingers = []
    if pts[4][0] < pts[3][0]:
        fingers.append(1)
    else:
        fingers.append(0)
    tip_ids = [8, 12, 16, 20]
    for i in tip_ids:
        if pts[i][1] < pts[i - 2][1]:
            fingers.append(1)
        else:
            fingers.append(0)
    return sum(fingers)

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions

hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="dateien/hand_landmarker.task"),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=5
)

face_options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="dateien/face_landmarker.task"),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=2
)

pose_options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="dateien/pose_landmarker_full.task"),
    running_mode=VisionRunningMode.VIDEO
)

hands = HandLandmarker.create_from_options(hand_options)
face = FaceLandmarker.create_from_options(face_options)
pose = PoseLandmarker.create_from_options(pose_options)

cap = cv2.VideoCapture(1)

finger_colors = {
    "thumb": (0, 0, 255),
    "index": (255, 0, 0),
    "middle": (0, 255, 255),
    "ring": (255, 0, 255),
    "pinky": (255, 255, 0)
}

finger_map = {
    "thumb": [1, 2, 3, 4],
    "index": [5, 6, 7, 8],
    "middle": [9, 10, 11, 12],
    "ring": [13, 14, 15, 16],
    "pinky": [17, 18, 19, 20]
}

#cv2.namedWindow("Multi Tracker", cv2.WND_PROP_FULLSCREEN)
cv2.namedWindow("Multi Tracker")
cv2.setWindowProperty("Multi Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))

    hand_result = hands.detect_for_video(mp_image, timestamp)
    face_result = face.detect_for_video(mp_image, timestamp)
    pose_result = pose.detect_for_video(mp_image, timestamp)

    if hand_result.hand_landmarks:
        for lm in hand_result.hand_landmarks:
            pts = to_points(lm, w, h)
            for finger, ids in finger_map.items():
                color = finger_colors[finger]
                for idx in ids:
                    x, y = pts[idx]
                    cv2.circle(frame, (x, y), 7, color, -1)
            finger_count = count_fingers(pts)
            cv2.putText(frame, f"Fingers: {finger_count}", (50, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)

    if face_result.face_landmarks:
        lm = face_result.face_landmarks[0]
        pts = to_points(lm, w, h)
        for x, y in pts:
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

    if pose_result.pose_landmarks:
        lm = pose_result.pose_landmarks
        pts = to_points(lm, w, h)
        for x, y in pts:
            cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)

    cv2.imshow("wer das liesst ist nicht erster", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()