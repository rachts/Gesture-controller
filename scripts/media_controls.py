import os
if os.getenv("DISPLAY"):
    import pyautogui
else:
    pyautogui = None

from typing import Callable, Dict


class MediaController:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.is_muted = False
        self.is_playing = True
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        self.gesture_actions: Dict[str, Callable] = {
            "swipe_right": self.next_track,
            "swipe_left": self.previous_track,
            "pinch": self.play_pause,
            "volume_up": self.volume_up,
            "volume_down": self.volume_down,
            "fist": self.mute,
            "open_palm": self.unmute,
        }
    
    def _log(self, message: str):
        if self.verbose:
            print(f"[Media Control] {message}")
    
    def play_pause(self):
        pyautogui.press('playpause')
        self.is_playing = not self.is_playing
        status = "Playing" if self.is_playing else "Paused"
        self._log(f"Play/Pause toggled - {status}")
    
    def next_track(self):
        pyautogui.press('nexttrack')
        self._log("Next track")
    
    def previous_track(self):
        pyautogui.press('prevtrack')
        self._log("Previous track")
    
    def volume_up(self, steps: int = 2):
        for _ in range(steps):
            pyautogui.press('volumeup')
        self._log(f"Volume up (+{steps})")
    
    def volume_down(self, steps: int = 2):
        for _ in range(steps):
            pyautogui.press('volumedown')
        self._log(f"Volume down (-{steps})")
    
    def mute(self):
        if not self.is_muted:
            pyautogui.press('volumemute')
            self.is_muted = True
            self._log("Muted")
    
    def unmute(self):
        if self.is_muted:
            pyautogui.press('volumemute')
            self.is_muted = False
            self._log("Unmuted")
    
    def execute_gesture(self, gesture: str) -> bool:
        if gesture in self.gesture_actions:
            self.gesture_actions[gesture]()
            return True
        return False
    
    def get_status(self) -> str:
        play_status = "Playing" if self.is_playing else "Paused"
        mute_status = "Muted" if self.is_muted else "Unmuted"
        return f"{play_status} | {mute_status}"
