import mediapipe as mp
from logger import Logger


class PoseBoundsChecker:
    def __init__(
        self, 
        landmark_visibility_threshold : float = 0.5,
        bound_left: float = 0.25,
        bound_right: float = 0.75,
        feet_bound_top: float = 0.1,
        feet_bound_bottom: float = 0.2
    ):
        self.landmark_visibility_threshold = landmark_visibility_threshold
        self.bound_left = bound_left
        self.bound_right = bound_right
        self.feet_bound_top = feet_bound_top
        self.feet_bound_bottom = feet_bound_bottom

        self.mp_pose = mp.solutions.pose.PoseLandmark

        self.logger = Logger.get()
        self.logger.info(f"{PoseBoundsChecker.__name__} initialized successfully")
        
    def pose_inside_horizontal_bounds(self, pose_landmarks) -> bool:
        if pose_landmarks is None:
            return False

        landmarks = pose_landmarks.landmark
        mid_shoulders_x = (landmarks[self.mp_pose.LEFT_SHOULDER].x + landmarks[self.mp_pose.RIGHT_SHOULDER].x) * 0.5
        return self.bound_left <= mid_shoulders_x <= self.bound_right

    def pose_inside_vertical_bounds(self, pose_landmarks) -> bool:
        if pose_landmarks is None:
            return False

        landmarks = pose_landmarks.landmark
        left_foot = landmarks[self.mp_pose.LEFT_FOOT_INDEX]
        right_foot = landmarks[self.mp_pose.RIGHT_FOOT_INDEX]

        visible_feet = []
        if left_foot.visibility > self.landmark_visibility_threshold: visible_feet.append(left_foot)
        if right_foot.visibility > self.landmark_visibility_threshold: visible_feet.append(right_foot)

        if visible_feet:
            lower_foot = max(visible_feet, key = lambda f: f.y)
            return (1.0 - self.feet_bound_bottom) >= lower_foot.y >= (1.0 - self.feet_bound_top)

        return False