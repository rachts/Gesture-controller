import cv2
import sys
import time

from hand_tracker import HandTracker
from gesture_recognition import GestureRecognizer
from media_controls import MediaController
from utils import GestureCooldown, FPSCounter

__author__ = "Rachit"
__version__ = "1.0.0"


class GestureMediaPlayer:
    def __init__(self, camera_id: int = 0, window_name: str = "Gesture Media Controller"):
        self.window_name = window_name
        self.camera_id = camera_id
        self.hand_tracker = HandTracker(
            max_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            smoothing_window=5
        )
        self.gesture_recognizer = GestureRecognizer(
            swipe_threshold=80,
            pinch_threshold=40,
            volume_y_threshold=0.03
        )
        self.media_controller = MediaController(verbose=True)
        self.cooldown = GestureCooldown()
        self.fps_counter = FPSCounter()
        self.current_gesture = "none"
        self.last_action = ""
        self.action_display_time = 0
        self.action_display_duration = 1.5
        self.colors = {
            "primary": (0, 255, 100),
            "secondary": (255, 200, 0),
            "accent": (0, 165, 255),
            "text": (255, 255, 255),
            "background": (40, 40, 40),
            "success": (0, 255, 0),
            "warning": (0, 255, 255),
        }
    
    def _draw_ui(self, frame, fps: float, hand_detected: bool):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 70), self.colors["background"], -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "Gesture Media Controller", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors["text"], 2)
        fps_color = self.colors["success"] if fps >= 20 else self.colors["warning"]
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 120, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2)
        status_text = "Hand Detected" if hand_detected else "No Hand"
        status_color = self.colors["success"] if hand_detected else self.colors["warning"]
        cv2.putText(frame, status_text, (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        media_status = self.media_controller.get_status()
        cv2.putText(frame, media_status, (w - 200, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors["secondary"], 2)
        if self.current_gesture != "none":
            gesture_name = self.gesture_recognizer.get_gesture_name(self.current_gesture)
            cv2.rectangle(overlay, (0, h - 60), (w, h), self.colors["background"], -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            cv2.putText(frame, f"Gesture: {gesture_name}", (10, h - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors["accent"], 2)
        current_time = time.time()
        if self.last_action and (current_time - self.action_display_time) < self.action_display_duration:
            elapsed = current_time - self.action_display_time
            alpha = 1.0 - (elapsed / self.action_display_duration)
            text_size = cv2.getTextSize(self.last_action, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h // 2
            padding = 20
            cv2.rectangle(frame, 
                         (text_x - padding, text_y - text_size[1] - padding),
                         (text_x + text_size[0] + padding, text_y + padding),
                         self.colors["background"], -1)
            color = tuple(int(c * alpha) for c in self.colors["primary"])
            cv2.putText(frame, self.last_action, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        cv2.putText(frame, "Press 'Q' to quit", (w - 180, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors["text"], 1)
    
    def _show_action(self, action: str):
        self.last_action = action
        self.action_display_time = time.time()
    
    def run(self):
        print("\n" + "="*50)
        print("  Gesture Media Controller")
        print(f"  Developed by {__author__}")
        print("="*50)
        print("\nInitializing webcam...")
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            print("Please check if your webcam is connected and not in use by another application.")
            sys.exit(1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        print("Webcam initialized successfully!")
        print("\nGesture Controls:")
        print("  - Pinch (Thumb + Index) -> Play/Pause")
        print("  - Swipe Right -> Next Track")
        print("  - Swipe Left -> Previous Track")
        print("  - 3 Fingers (Thumb+Index+Middle) + Move Up -> Volume Up")
        print("  - 3 Fingers (Thumb+Index+Middle) + Move Down -> Volume Down")
        print("  - Fist -> Mute")
        print("  - Open Palm -> Resume/Unmute")
        print("\nPress 'Q' to quit\n")
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                frame = cv2.flip(frame, 1)
                fps = self.fps_counter.update()
                hand_data = self.hand_tracker.process_frame(frame)
                if hand_data:
                    self.hand_tracker.draw_landmarks(frame, hand_data, self.colors["primary"])
                gesture = self.gesture_recognizer.recognize(hand_data)
                self.current_gesture = gesture
                if gesture != GestureRecognizer.NONE:
                    if self.cooldown.can_trigger(gesture):
                        if self.media_controller.execute_gesture(gesture):
                            self.cooldown.trigger(gesture)
                            action_name = self.gesture_recognizer.get_gesture_name(gesture)
                            self._show_action(action_name)
                self._draw_ui(frame, fps, hand_data is not None)
                cv2.imshow(self.window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\nExiting...")
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.hand_tracker.release()
            print("Goodbye!")


def main():
    app = GestureMediaPlayer(camera_id=0)
    app.run()


if __name__ == "__main__":
    main()
