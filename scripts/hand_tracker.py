import cv2
import mediapipe as mp
from typing import Optional, List, Tuple, NamedTuple
from utils import MovingAverageFilter


class HandLandmarks(NamedTuple):
    landmarks: List[Tuple[float, float, float]]
    handedness: str
    confidence: float


class HandTracker:
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20
    
    def __init__(self, 
                 max_hands: int = 1,
                 min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.6,
                 smoothing_window: int = 5):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.smoothers = [MovingAverageFilter(smoothing_window) for _ in range(21)]
        self.prev_landmarks: Optional[List[Tuple[float, float, float]]] = None
    
    def process_frame(self, frame) -> Optional[HandLandmarks]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        if not results.multi_hand_landmarks:
            self.prev_landmarks = None
            return None
        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0].classification[0]
        h, w, _ = frame.shape
        landmarks = []
        for i, lm in enumerate(hand_landmarks.landmark):
            px, py = int(lm.x * w), int(lm.y * h)
            smoothed_x, smoothed_y = self.smoothers[i].update(px, py)
            landmarks.append((smoothed_x, smoothed_y, lm.z))
        self.prev_landmarks = landmarks
        return HandLandmarks(
            landmarks=landmarks,
            handedness=handedness.label,
            confidence=handedness.score
        )
    
    def draw_landmarks(self, frame, hand_data: Optional[HandLandmarks], 
                       color: Tuple[int, int, int] = (0, 255, 0)) -> None:
        if hand_data is None:
            return
        landmarks = hand_data.landmarks
        connections = self.mp_hands.HAND_CONNECTIONS
        for connection in connections:
            start_idx, end_idx = connection
            start_point = (int(landmarks[start_idx][0]), int(landmarks[start_idx][1]))
            end_point = (int(landmarks[end_idx][0]), int(landmarks[end_idx][1]))
            cv2.line(frame, start_point, end_point, color, 2)
        for i, (x, y, z) in enumerate(landmarks):
            radius = 8 if i in [4, 8, 12, 16, 20] else 5
            cv2.circle(frame, (int(x), int(y)), radius, color, -1)
            cv2.circle(frame, (int(x), int(y)), radius, (255, 255, 255), 1)
    
    def get_fingertip_positions(self, hand_data: HandLandmarks) -> dict:
        landmarks = hand_data.landmarks
        return {
            "thumb": landmarks[self.THUMB_TIP],
            "index": landmarks[self.INDEX_TIP],
            "middle": landmarks[self.MIDDLE_TIP],
            "ring": landmarks[self.RING_TIP],
            "pinky": landmarks[self.PINKY_TIP],
            "wrist": landmarks[self.WRIST]
        }
    
    def release(self):
        self.hands.close()
