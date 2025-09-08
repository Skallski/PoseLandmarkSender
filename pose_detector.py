import cv2
import mediapipe as mp
from logger import Logger


class PoseDetector:
    def __init__(
        self, 
        model_complexity : int = 1, 
        min_detection_confidence : float = 0.5, 
        min_tracking_confidence : float = 0.5,
    ):
        self.log = Logger.get()

        self.mp_pose = mp.solutions.pose

        try:
            model_complexity_valid = int(float(model_complexity))
        except (TypeError, ValueError):
            self.log.warning("Model complexity value is not valid! Falling back to 0. (Allowed: 0, 1, 2)")
            model_complexity_valid = 0
        if model_complexity_valid not in (0, 1, 2): model_complexity_valid = 0
        
        self.pose = self.mp_pose.Pose(
            static_image_mode = False,
            model_complexity = model_complexity_valid,
            enable_segmentation = False,
            min_detection_confidence = max(0.0, min(1.0, float(min_detection_confidence))),
            min_tracking_confidence = max(0.0, min(1.0, float(min_tracking_confidence)))
        )

        self.drawer = mp.solutions.drawing_utils
        self.log.info(f"{PoseDetector.__name__} initialized successfully")

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if not (results and results.pose_landmarks):
            return [], results
        
        landmarks_data = []
        for landmark in results.pose_landmarks.landmark:
            landmarks_data.append({
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            })

        return landmarks_data, results
    
    def draw_landmarks(self, frame, results):
        if results:
            self.drawer.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

        return frame

    def close(self):
        self.pose.close()
        self.log.info(f"{PoseDetector.__name__} closed successfully")
