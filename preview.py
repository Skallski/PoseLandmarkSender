import cv2
import time
import mediapipe as mp
from logger import Logger


class Preview:
    PREVIWEW_WINDOW_NAME = "Pose Landmark Sender"

    def __init__(self, show_fps: bool = True):
        self.show_fps = show_fps
        self.fps_counter_last_time = 0
        self.logger = Logger.get()
        self.logger.info(f"{Preview.__name__} initialized successfully")

    def show_preview(self, frame, landmarks):
        if frame is None:
            return

        if self.show_fps:
            curr_time = time.time()
            fps = 1 / (curr_time - self.fps_counter_last_time) if self.fps_counter_last_time else 0
            self.fps_counter_last_time = curr_time
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if landmarks is not None:
            frame = self._get_frame_with_landmarks_drawn(frame, landmarks)

        cv2.imshow(self.PREVIWEW_WINDOW_NAME, frame)

    def _get_frame_with_landmarks_drawn(self, frame, landmarks):
        if landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                landmarks,
                mp.solutions.pose.POSE_CONNECTIONS
            )
        return frame

    def trigger_close_window(self) -> bool:
        key = cv2.waitKey(1) & 0xFF
        prop = cv2.getWindowProperty(self.PREVIWEW_WINDOW_NAME, cv2.WND_PROP_VISIBLE)
        return key == 27 or prop == 0
    
    def close(self):
        cv2.destroyAllWindows()
        self.logger.info(f"{Preview.__name__} closed successfully")
