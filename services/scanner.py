# services/scanner.py
import cv2
import mediapipe as mp
import numpy as np           #don't know but for some reason i cant install cv,mp,np 
import json
import time
from pathlib import Path

# Predefined reference colors
SKIN_TONES = {
    "Very Light": (220, 220, 245),
    "Light": (180, 170, 220),
    "Medium": (150, 140, 190),
    "Tan": (120, 110, 160),
    "Dark": (80, 70, 120),
    "Very Dark": (50, 40, 80)
}

def run_scan(user_data: dict):
    """
    Run body type and skin tone detection.
    Accepts user_data (dict) from the API.
    Returns structured JSON result.
    """

    mp_pose = mp.solutions.pose
    mp_face = mp.solutions.face_mesh
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    face = mp_face.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)

    body_type = "Detecting..."
    skin_tone = "Detecting..."
    stable_frames = 0
    result_time = None
    data = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pose_results = pose.process(rgb)
        face_results = face.process(rgb)
        h, w = frame.shape[:2]

        # ---------- BODY TYPE DETECTION ----------
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            try:
                l_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                r_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                l_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
                r_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

                shoulder_width = abs(r_shoulder.x - l_shoulder.x)
                hip_width = abs(r_hip.x - l_hip.x)
                waist_x_left = l_shoulder.x + (l_hip.x - l_shoulder.x) * 0.5
                waist_x_right = r_shoulder.x + (r_hip.x - r_shoulder.x) * 0.5
                waist_width = abs(waist_x_right - waist_x_left)

                new_type = "Unknown"
                if abs(shoulder_width - hip_width) < 0.05 and waist_width < shoulder_width * 0.75:
                    new_type = "Hourglass"
                elif hip_width > shoulder_width + 0.05:
                    new_type = "Pear"
                elif shoulder_width > hip_width + 0.05:
                    if waist_width < shoulder_width * 0.75:
                        new_type = "Inverted Triangle"
                    else:
                        new_type = "Apple"
                elif abs(shoulder_width - hip_width) < 0.05:
                    new_type = "Rectangle"
                else:
                    new_type = "Average"

                if new_type == body_type:
                    stable_frames += 1
                else:
                    stable_frames = 0
                    body_type = new_type
            except Exception:
                body_type = "Error"

        # ---------- SKIN TONE DETECTION ----------
        if face_results.multi_face_landmarks:
            try:
                face_landmarks = face_results.multi_face_landmarks[0].landmark
                pts = [face_landmarks[i] for i in [10, 151, 337, 332]]
                x_coords = [int(pt.x * w) for pt in pts]
                y_coords = [int(pt.y * h) for pt in pts]
                x1, y1 = max(0, min(x_coords)), max(0, min(y_coords))
                x2, y2 = min(w, max(x_coords)), min(h, max(y_coords))

                if x2 > x1 and y2 > y1:
                    roi = frame[y1:y2, x1:x2]
                    avg_color = np.mean(roi, axis=(0, 1))
                    min_dist = float('inf')
                    for tone, ref_color in SKIN_TONES.items():
                        dist = np.linalg.norm(avg_color - ref_color)
                        if dist < min_dist:
                            min_dist = dist
                            skin_tone = tone
            except Exception:
                skin_tone = "Detecting..."

        # ---------- STOP CONDITION ----------
        result_ready = stable_frames > 8 and skin_tone != "Detecting..."
        if result_ready:
            data = {
                "style": user_data.get("style", "Unspecified"),
                "body_type": body_type,
                "skin_tone": skin_tone,
                "life_stage": user_data.get("life_stage"),
                "occasion": user_data.get("occasion"),
                "price_range": user_data.get("price_range"),
                "season": user_data.get("season"),
                "unisex_preference": user_data.get("unisex_preference")
            }
            break

    cap.release()
    cv2.destroyAllWindows()

    # Save result JSON
    save_path = Path(__file__).resolve().parent.parent / "fitme_result.json"
    with open(save_path, "w") as f:
        json.dump(data, f, indent=2)

    return data
