import platform
import cv2
import time
from pose_detector import PoseDetector
from payload_builder import PayloadBuilder
from udp_json_sender import UdpJsonSender
from logger import Logger


class PoseLandmarkSender:
    WINDOW_NAME = "Pose landmark detection preview"

    def __init__(
        self, 
        udp_ip: str = "127.0.0.1", 
        udp_port: int = 5005, 
        cam_index: int = 0, 
        cam_requested_width: int = 640,
        cam_requested_height: int = 360,
        cam_requested_fps: int = 30,
        pose_model_complexity: int = 1,
        min_pose_detection_confidence: float = 0.5,
        min_landmark_tracking_confidence: float = 0.5,
        preview_mode = True,
    ):

        self.detector = PoseDetector(
            model_complexity = pose_model_complexity, 
            min_detection_confidence = min_pose_detection_confidence, 
            min_tracking_confidence = min_landmark_tracking_confidence,
        )
        
        self.payload_builder = PayloadBuilder(
            landmark_visibility_threshold = float(min_landmark_tracking_confidence)
        )

        self.sender = UdpJsonSender(udp_ip, udp_port)

        # choose backend depending on OS
        os_name = platform.system().lower()
        if os_name == "windows": self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        elif os_name == "darwin": self.cap = cv2.VideoCapture(cam_index, cv2.CAP_AVFOUNDATION)
        else: self.cap = cv2.VideoCapture(cam_index)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_requested_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_requested_height)
        self.cap.set(cv2.CAP_PROP_FPS, cam_requested_fps)

        self.preview_mode = preview_mode
        self.fps_counter_last_time = 0

        self.log = Logger.get()

    def run(self):
        if not self.cap.isOpened():
            self.log.error("Application start error: Cannot open camera!")
            return

        self.log.info(f"Application {'[Preview Mode]' if self.preview_mode else '[No Preview]'} started successfully")

        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    self.log.error("Camera frame is empty! Closing app...")
                    break

                landmarks, results = self.detector.process_frame(frame)

                # send payload
                landmarks_payload, frame_payload = self.payload_builder.build_payload(landmarks, frame)
                
                if landmarks_payload:
                    self.sender.send(landmarks_payload)
                else:
                    self.log.error()

                if frame_payload:
                    self.sender.send(frame_payload)
                else:
                    self.log.error()
                
                # preview
                if self.preview_mode:
                    show_landmarks = bool(results and results.pose_landmarks)
                    self._show_preview(frame, results, show_fps = True, show_landmarks = show_landmarks)
                    if self._close_preview_window():
                        break
        finally:
            self._cleanup()

    def _cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.detector.close()
        self.sender.close()
        self.log.info("Application closed successfully")

    def _show_preview(
        self, 
        frame, 
        results, 
        show_fps : bool, 
        show_landmarks : bool
    ):
        if show_fps:
            curr_time = time.time()
            fps = 1 / (curr_time - self.fps_counter_last_time) if self.fps_counter_last_time else 0
            self.fps_counter_last_time = curr_time
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if show_landmarks:
            frame = self.detector.draw_landmarks(frame, results)

        cv2.imshow(self.WINDOW_NAME, frame)

    def _close_preview_window(self) -> bool:
        key = cv2.waitKey(1) & 0xFF
        prop = cv2.getWindowProperty(self.WINDOW_NAME, cv2.WND_PROP_VISIBLE)
        return key == 27 or prop == 0