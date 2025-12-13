from typing import Optional, Tuple, List
from collections import deque
from hand_tracker import HandTracker, HandLandmarks
from utils import calculate_distance


class GestureRecognizer:
    NONE = "none"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_LEFT = "swipe_left"
    PINCH = "pinch"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    FIST = "fist"
    OPEN_PALM = "open_palm"
    
    def __init__(self, 
                 swipe_threshold: float = 80,
                 pinch_threshold: float = 40,
                 volume_y_threshold: float = 0.03,
                 history_size: int = 10):
        self.swipe_threshold = swipe_threshold
        self.pinch_threshold = pinch_threshold
        self.volume_y_threshold = volume_y_threshold
        self.wrist_history: deque = deque(maxlen=history_size)
        self.palm_center_history: deque = deque(maxlen=history_size)
        self.was_pinching = False
        self.last_gesture = self.NONE
        self.last_wrist_y: Optional[float] = None
    
    def _is_finger_extended(self, landmarks: List[Tuple[float, float, float]], 
                           finger_tip_idx: int, finger_pip_idx: int, 
                           finger_mcp_idx: int) -> bool:
        tip = landmarks[finger_tip_idx]
        pip = landmarks[finger_pip_idx]
        mcp = landmarks[finger_mcp_idx]
        return tip[1] < pip[1] and pip[1] < mcp[1]
    
    def _is_thumb_extended(self, landmarks: List[Tuple[float, float, float]], 
                          handedness: str) -> bool:
        thumb_tip = landmarks[HandTracker.THUMB_TIP]
        thumb_mcp = landmarks[HandTracker.THUMB_MCP]
        if handedness == "Right":
            return thumb_tip[0] < thumb_mcp[0]
        else:
            return thumb_tip[0] > thumb_mcp[0]
    
    def _get_finger_states(self, hand_data: HandLandmarks) -> List[int]:
        landmarks = hand_data.landmarks
        states = []
        states.append(1 if self._is_thumb_extended(landmarks, hand_data.handedness) else 0)
        finger_indices = [
            (HandTracker.INDEX_TIP, HandTracker.INDEX_PIP, HandTracker.INDEX_MCP),
            (HandTracker.MIDDLE_TIP, HandTracker.MIDDLE_PIP, HandTracker.MIDDLE_MCP),
            (HandTracker.RING_TIP, HandTracker.RING_PIP, HandTracker.RING_MCP),
            (HandTracker.PINKY_TIP, HandTracker.PINKY_PIP, HandTracker.PINKY_MCP),
        ]
        for tip_idx, pip_idx, mcp_idx in finger_indices:
            if self._is_finger_extended(landmarks, tip_idx, pip_idx, mcp_idx):
                states.append(1)
            else:
                states.append(0)
        return states
    
    def _count_extended_fingers(self, hand_data: HandLandmarks) -> int:
        return sum(self._get_finger_states(hand_data))
    
    def _is_volume_mode(self, hand_data: HandLandmarks) -> bool:
        fingers = self._get_finger_states(hand_data)
        return (
            fingers[0] == 1 and  # Thumb up
            fingers[1] == 1 and  # Index up
            fingers[2] == 1 and  # Middle up
            fingers[3] == 0 and  # Ring down
            fingers[4] == 0      # Pinky down
        )
    
    def _detect_pinch(self, hand_data: HandLandmarks) -> bool:
        landmarks = hand_data.landmarks
        thumb_tip = (landmarks[HandTracker.THUMB_TIP][0], landmarks[HandTracker.THUMB_TIP][1])
        index_tip = (landmarks[HandTracker.INDEX_TIP][0], landmarks[HandTracker.INDEX_TIP][1])
        distance = calculate_distance(thumb_tip, index_tip)
        return distance < self.pinch_threshold
    
    def _detect_fist(self, hand_data: HandLandmarks) -> bool:
        return self._count_extended_fingers(hand_data) == 0
    
    def _detect_open_palm(self, hand_data: HandLandmarks) -> bool:
        return self._count_extended_fingers(hand_data) == 5
    
    def _get_palm_center(self, landmarks: List[Tuple[float, float, float]]) -> Tuple[float, float]:
        palm_indices = [
            HandTracker.WRIST,
            HandTracker.INDEX_MCP,
            HandTracker.MIDDLE_MCP,
            HandTracker.RING_MCP,
            HandTracker.PINKY_MCP
        ]
        x_sum = sum(landmarks[i][0] for i in palm_indices)
        y_sum = sum(landmarks[i][1] for i in palm_indices)
        return x_sum / len(palm_indices), y_sum / len(palm_indices)
    
    def _detect_swipe(self, hand_data: HandLandmarks) -> Optional[str]:
        landmarks = hand_data.landmarks
        palm_center = self._get_palm_center(landmarks)
        self.palm_center_history.append(palm_center)
        if len(self.palm_center_history) < 5:
            return None
        start_x = self.palm_center_history[0][0]
        end_x = self.palm_center_history[-1][0]
        delta_x = end_x - start_x
        if abs(delta_x) > self.swipe_threshold:
            self.palm_center_history.clear()
            if delta_x > 0:
                return self.SWIPE_RIGHT
            else:
                return self.SWIPE_LEFT
        return None
    
    def _detect_volume_gesture(self, hand_data: HandLandmarks) -> Optional[str]:
        if not self._is_volume_mode(hand_data):
            self.last_wrist_y = None
            return None
        
        landmarks = hand_data.landmarks
        current_y = landmarks[HandTracker.WRIST][1]
        
        if self.last_wrist_y is None:
            self.last_wrist_y = current_y
            return None
        
        delta_y = current_y - self.last_wrist_y
        
        if delta_y < -self.volume_y_threshold:
            self.last_wrist_y = current_y
            return self.VOLUME_UP
        elif delta_y > self.volume_y_threshold:
            self.last_wrist_y = current_y
            return self.VOLUME_DOWN
        
        return None
    
    def recognize(self, hand_data: Optional[HandLandmarks]) -> str:
        if hand_data is None:
            self.wrist_history.clear()
            self.palm_center_history.clear()
            self.was_pinching = False
            self.last_wrist_y = None
            return self.NONE
        
        volume = self._detect_volume_gesture(hand_data)
        if volume:
            return volume
        
        is_pinching = self._detect_pinch(hand_data)
        if is_pinching and not self.was_pinching:
            self.was_pinching = True
            return self.PINCH
        elif not is_pinching:
            self.was_pinching = False
        
        if self._detect_fist(hand_data):
            return self.FIST
        
        if self._detect_open_palm(hand_data):
            return self.OPEN_PALM
        
        swipe = self._detect_swipe(hand_data)
        if swipe:
            return swipe
        
        return self.NONE
    
    def get_gesture_name(self, gesture: str) -> str:
        names = {
            self.NONE: "None",
            self.SWIPE_RIGHT: "Swipe Right - Next Track",
            self.SWIPE_LEFT: "Swipe Left - Previous Track",
            self.PINCH: "Pinch - Play/Pause",
            self.VOLUME_UP: "Volume Up (3 Fingers + Move Up)",
            self.VOLUME_DOWN: "Volume Down (3 Fingers + Move Down)",
            self.FIST: "Fist - Mute",
            self.OPEN_PALM: "Open Palm - Resume",
        }
        return names.get(gesture, "Unknown")
