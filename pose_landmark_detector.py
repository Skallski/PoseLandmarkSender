import cv2
import mediapipe as mp
from logger import Logger


class PoseLandmarkDetector:
    def __init__(
        self, 
        model_complexity : int = 1, 
        min_detection_confidence : float = 0.5, 
        min_tracking_confidence : float = 0.5,
        pose_detection_bound_left: float = 0.25,
        pose_detection_bound_right: float = 0.75,
        pose_detection_feet_bound_top: float = 0.1,
        pose_detection_feet_bound_bottom: float = 0.2
    ):
        self.logger = Logger.get()

        self.mp_pose = mp.solutions.pose

        try:
            model_complexity_valid = int(float(model_complexity))
        except (TypeError, ValueError):
            self.logger.warning("Model complexity value is not valid! Falling back to 0. (Allowed: 0, 1, 2)")
            model_complexity_valid = 0
        if model_complexity_valid not in (0, 1, 2): model_complexity_valid = 0
        
        self.min_detection_confidence = max(0.0, min(1.0, float(min_detection_confidence)))
        self.min_tracking_confidence = max(0.0, min(1.0, float(min_tracking_confidence)))

        self.pose = self.mp_pose.Pose(
            static_image_mode = False,
            model_complexity = model_complexity_valid,
            enable_segmentation = False,
            min_detection_confidence = self.min_detection_confidence,
            min_tracking_confidence = self.min_tracking_confidence
        )

        # bounds
        self.pose_detection_bound_left = pose_detection_bound_left
        self.pose_detection_bound_right = pose_detection_bound_right
        self.pose_detection_feet_bound_top = pose_detection_feet_bound_top
        self.pose_detection_feet_bound_bottom = pose_detection_feet_bound_bottom

        self.logger.info(f"{PoseLandmarkDetector.__name__} initialized successfully")
        
    def _pose_inside_horizontal_bounds(self, landmarks) -> bool:
        mp_pose = self.mp_pose.PoseLandmark
        mid_shoulders_x = (landmarks[mp_pose.LEFT_SHOULDER].x + landmarks[mp_pose.RIGHT_SHOULDER].x) * 0.5
        return self.pose_detection_bound_left <= mid_shoulders_x <= self.pose_detection_bound_right

    def _pose_inside_vertical_bounds(self, landmarks) -> bool:
        mp_pose = self.mp_pose.PoseLandmark
        left_foot = landmarks[mp_pose.LEFT_FOOT_INDEX]
        right_foot = landmarks[mp_pose.RIGHT_FOOT_INDEX]

        visible_feet = []
        if left_foot.visibility > self.min_tracking_confidence: visible_feet.append(left_foot)
        if right_foot.visibility > self.min_tracking_confidence: visible_feet.append(right_foot)

        if visible_feet:
            lower_foot = max(visible_feet, key = lambda f: f.y)
            bound_top = 1.0 - self.pose_detection_feet_bound_top
            bound_bottom = 1.0 - self.pose_detection_feet_bound_bottom
            return bound_bottom >= lower_foot.y >= bound_top

        return False

    def get_landmarks(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if not results.pose_landmarks:
            return None
        
        landmarks = results.pose_landmarks.landmark
        pose_inside_horizontal_bounds = self._pose_inside_horizontal_bounds(landmarks)
        pose_inside_vertical_bounds = self._pose_inside_vertical_bounds(landmarks)
        if pose_inside_horizontal_bounds and pose_inside_vertical_bounds:
            return results.pose_landmarks
        else:
            return None

    def close(self):
        self.pose.close()
        self.logger.info(f"{PoseLandmarkDetector.__name__} closed successfully")
