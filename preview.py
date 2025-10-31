import cv2
import time
import mediapipe as mp
from logger import Logger


class Preview:
    PREVIWEW_WINDOW_NAME = "Pose Landmark Sender"

    def __init__(
        self, 
        show_fps: bool = True,
        bound_left: float = 0.25,
        bound_right: float = 0.75,
        bound_feet_top: float = 0.1,
        bound_feet_bottom: float = 0.2
    ):
        self.show_fps = show_fps
        self.fps_counter_last_time = 0

        self.bound_left = bound_left
        self.bound_right = bound_right
        self.bound_feet_top = bound_feet_top
        self.bound_feet_bottom = bound_feet_bottom

        self.logger = Logger.get()
        self.logger.info(f"{Preview.__name__} initialized successfully")

    def show_preview(
        self, 
        frame, 
        landmarks, 
        pose_inside_horizontal_bounds, 
        pose_inside_vertical_bounds
    ):
        if frame is None:
            return

        if self.show_fps:
            curr_time = time.time()
            fps = 1 / (curr_time - self.fps_counter_last_time) if self.fps_counter_last_time else 0
            self.fps_counter_last_time = curr_time
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        frame = self._get_frame_with_bounds_drawn(
            frame, 
            landmarks,
            pose_inside_horizontal_bounds,
            pose_inside_vertical_bounds
        )

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
    
    def _get_frame_with_bounds_drawn(
        self, 
        frame, 
        pose_inside_horizontal_bounds, 
        pose_inside_vertical_bounds
    ):
        thickness = 2
        height, width, _ = frame.shape

        # horizontal bounds
        left_x = int(self.bound_left * width)
        right_x = int(self.bound_right * width)

        color_horizontal_bounds = (0, 255, 0) if pose_inside_horizontal_bounds else (0, 0, 255)
        cv2.line(frame, (left_x, 0), (left_x, height), color_horizontal_bounds, thickness)
        cv2.line(frame, (right_x, 0), (right_x, height), color_horizontal_bounds, thickness)

        # vertical bounds
        top_y = int((1.0 - self.bound_feet_top) * height)
        bottom_y = int((1.0 - self.bound_feet_bottom) * height)

        color_vertical_bounds = (0, 255, 0) if pose_inside_vertical_bounds else (0, 0, 255)
        cv2.line(frame, (0, top_y), (width, top_y), color_vertical_bounds, thickness)
        cv2.line(frame, (0, bottom_y), (width, bottom_y), color_vertical_bounds, thickness)

        return frame

    def trigger_close_window(self) -> bool:
        key = cv2.waitKey(1) & 0xFF
        prop = cv2.getWindowProperty(self.PREVIWEW_WINDOW_NAME, cv2.WND_PROP_VISIBLE)
        return key == 27 or prop == 0
    
    def close(self):
        cv2.destroyAllWindows()
        self.logger.info(f"{Preview.__name__} closed successfully")
