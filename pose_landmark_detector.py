import cv2
import mediapipe as mp
from logger import Logger


class PoseLandmarkDetector:
    def __init__(
        self, 
        model_complexity : int = 1, 
        min_detection_confidence : float = 0.5, 
        min_tracking_confidence : float = 0.5
    ):
        self.logger = Logger.get()

        self.mp_pose = mp.solutions.pose

        try:
            model_complexity_valid = int(float(model_complexity))
        except (TypeError, ValueError):
            self.logger.warning("Model complexity value is not valid! Falling back to 0. (Allowed: 0, 1, 2)")
            model_complexity_valid = 0
        if model_complexity_valid not in (0, 1, 2): model_complexity_valid = 0
        
        self.pose = self.mp_pose.Pose(
            static_image_mode = False,
            model_complexity = model_complexity_valid,
            enable_segmentation = False,
            min_detection_confidence = self.max(0.0, min(1.0, float(min_detection_confidence))),
            min_tracking_confidence = self.max(0.0, min(1.0, float(min_tracking_confidence)))
        )

        self.logger.info(f"{PoseLandmarkDetector.__name__} initialized successfully")

    def get_landmarks(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        return results.pose_landmarks

    def close(self):
        self.pose.close()
        self.logger.info(f"{PoseLandmarkDetector.__name__} closed successfully")
