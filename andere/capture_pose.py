import cv2
import mediapipe as mp
from pythonosc.udp_client import SimpleUDPClient

def extract_landmarks(raw):
    if raw is None:
        return []
    if hasattr(raw, "x") and hasattr(raw, "y"):
        return [raw]
    if isinstance(raw, list):
        if len(raw) == 0:
            return []
        if hasattr(raw[0], "x"):
            return raw
        if isinstance(raw[0], list) and hasattr(raw[0][0], "x"):
            return raw[0]
    return []

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

pose_model = PoseLandmarker.create_from_options(
    PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="dateien/pose_landmarker_full.task"),
        running_mode=VisionRunningMode.VIDEO
    )
)

hand_model = HandLandmarker.create_from_options(
    HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="dateien/hand_landmarker.task"),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2
    )
)

osc = SimpleUDPClient("127.0.0.1", 9000)

camera = cv2.VideoCapture(1)
frame_index = 0

while True:
    ok, frame = camera.read()
    if not ok:
        break

    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    timestamp = frame_index * 33

    pose_result = pose_model.detect_for_video(image, timestamp)
    lm_pose = extract_landmarks(pose_result.pose_landmarks)
    for i, p in enumerate(lm_pose):
        osc.send_message(f"/pose/{i}", [p.x, p.y, p.z])

    hand_result = hand_model.detect_for_video(image, timestamp)
    if hand_result.hand_landmarks:
        for h_id, hand in enumerate(hand_result.hand_landmarks):
            lm_hand = extract_landmarks(hand)
            for i, p in enumerate(lm_hand):
                osc.send_message(f"/hand/{h_id}/{i}", [p.x, p.y, p.z])

    cv2.imshow("Mediapipe Live", frame)
    frame_index += 1

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()
