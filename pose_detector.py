import cv2
import mediapipe as mp


class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode = False,
            model_complexity = 1,
            enable_segmentation = False,
            min_detection_confidence = 0.5,
            min_tracking_confidence = 0.5
        )

        self.drawer = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        landmarks_data = []
        if results.pose_landmarks:
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