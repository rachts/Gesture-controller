import time
from collections import deque
from typing import Tuple, Optional
import numpy as np


class MovingAverageFilter:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.x_history = deque(maxlen=window_size)
        self.y_history = deque(maxlen=window_size)
    
    def update(self, x: float, y: float) -> Tuple[float, float]:
        self.x_history.append(x)
        self.y_history.append(y)
        smoothed_x = sum(self.x_history) / len(self.x_history)
        smoothed_y = sum(self.y_history) / len(self.y_history)
        return smoothed_x, smoothed_y
    
    def reset(self):
        self.x_history.clear()
        self.y_history.clear()


class GestureCooldown:
    def __init__(self, default_cooldown: float = 0.8):
        self.default_cooldown = default_cooldown
        self.last_trigger_times = {}
        self.cooldowns = {
            "swipe_right": 1.0,
            "swipe_left": 1.0,
            "pinch": 0.8,
            "volume_up": 0.3,
            "volume_down": 0.3,
            "fist": 1.0,
            "open_palm": 1.0,
        }
    
    def can_trigger(self, gesture: str) -> bool:
        current_time = time.time()
        last_time = self.last_trigger_times.get(gesture, 0)
        cooldown = self.cooldowns.get(gesture, self.default_cooldown)
        return (current_time - last_time) >= cooldown
    
    def trigger(self, gesture: str):
        self.last_trigger_times[gesture] = time.time()
    
    def reset(self, gesture: Optional[str] = None):
        if gesture:
            self.last_trigger_times.pop(gesture, None)
        else:
            self.last_trigger_times.clear()


class FPSCounter:
    def __init__(self, avg_frames: int = 30):
        self.avg_frames = avg_frames
        self.frame_times = deque(maxlen=avg_frames)
        self.last_time = time.time()
    
    def update(self) -> float:
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time
        if delta > 0:
            self.frame_times.append(1.0 / delta)
        if len(self.frame_times) > 0:
            return sum(self.frame_times) / len(self.frame_times)
        return 0.0


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def calculate_angle(point1: Tuple[float, float], point2: Tuple[float, float], 
                    point3: Tuple[float, float]) -> float:
    vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
    vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
    cos_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2) + 1e-6)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))
