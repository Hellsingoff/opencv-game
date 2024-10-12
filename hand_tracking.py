import time

import cv2
import math

from mediapipe.python.solutions.hands import Hands
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from Finger import Finger
from shared_data import shared_data
from enums.finger import FingerName, FingerState
from enums.gesture import GestureType
from typing import Dict, Tuple, Optional

hands = Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

selected_landmarks: Dict[FingerName, Tuple[int, int]] = {
    FingerName.INDEX: (5, 8),
    FingerName.MIDDLE: (9, 12),
    FingerName.RING: (13, 16),
    FingerName.PINKY: (17, 20)
}


def calculate_distance(point1: NormalizedLandmark, point2: NormalizedLandmark) -> float:
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def determine_finger_position(wrist_to_mcp: float, wrist_to_tip: float) -> FingerState:
    if wrist_to_tip > wrist_to_mcp * 1.60:
        return FingerState.STRAIGHT
    elif wrist_to_tip < wrist_to_mcp * 1.30:
        return FingerState.BENT
    else:
        return FingerState.INTERMEDIATE


def determine_gesture(fingers: Dict[FingerName, Finger]) -> Optional[GestureType]:
    straight_count = sum(1 for finger in fingers.values() if finger.state == FingerState.STRAIGHT)
    bent_count = sum(1 for finger in fingers.values() if finger.state == FingerState.BENT)

    if straight_count == 4:
        return GestureType.PAPER
    if fingers[FingerName.INDEX].state == FingerState.STRAIGHT and \
            fingers[FingerName.MIDDLE].state == FingerState.STRAIGHT and \
            fingers[FingerName.RING].state == FingerState.BENT and \
            fingers[FingerName.PINKY].state == FingerState.BENT:
        return GestureType.SCISSORS
    if bent_count == 4:
        return GestureType.ROCK
    return None


def process_hand() -> None:
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        with shared_data.lock:
            shared_data.frame = frame.copy()

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                wrist = hand_landmarks.landmark[0]
                fingers: Dict[FingerName, Finger] = {}

                for finger_name, (mcp_index, tip_index) in selected_landmarks.items():
                    mcp_landmark = hand_landmarks.landmark[mcp_index]
                    tip_landmark = hand_landmarks.landmark[tip_index]
                    wrist_to_mcp = calculate_distance(wrist, mcp_landmark)
                    wrist_to_tip = calculate_distance(wrist, tip_landmark)
                    position = determine_finger_position(wrist_to_mcp, wrist_to_tip)
                    tip_x = int(tip_landmark.x * frame.shape[1])
                    tip_y = int(tip_landmark.y * frame.shape[0])
                    fingers[finger_name] = Finger(tip_x, tip_y, position)

                current_gesture = determine_gesture(fingers)
                shared_data.gesture = current_gesture

                if current_gesture is not None:
                    shared_data.last_valid_gesture = current_gesture

                shared_data.fingers = fingers
            else:
                shared_data.gesture = None
                shared_data.fingers = {}
        time.sleep(0.02)
    cap.release()
