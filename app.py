import json
import cv2
import time
import platform
from pose_detector import PoseDetector
from udp_json_sender import UdpJsonSender


class PoseApp:
    LANDMARK_VISIBILITY_THRESHOLD = 0.5

    def __init__(self, udp_ip = "127.0.0.1", udp_port = 5005, cam_index = 0, previewMode = True):
        self.detector = PoseDetector()
        self.sender = UdpJsonSender(udp_ip, udp_port)

        # choose backend depending on OS
        os_name = platform.system().lower()
        match os_name:
            case "windows":
                self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
            case "darwin":
                self.cap = cv2.VideoCapture(cam_index, cv2.CAP_AVFOUNDATION)
            case _:
                self.cap = cv2.VideoCapture(cam_index)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.previewMode = previewMode
        self.fps_counter_last_time = 0

    def run(self):
        if  self.cap.isOpened():
            print(f"Application {'[preview mode]' if self.previewMode else ''} started successfuly")
        else:
            print("Application start error: Cannot open camera!")
            return

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Camera frame is empty")
                break
            
            landmarks, output_frame = self.detector.process_frame(frame, self.previewMode)
            if not landmarks:
                continue

            payload = self._format_landmarks_payload(landmarks)
            if payload:
                self.sender.send(payload)

            if self.previewMode:
                self._show_frame(output_frame, showfps = True)

            if cv2.waitKey(1) & 0xFF == 27: # ESC
                break

        self._cleanup()

    def _cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.detector.close()
        self.sender.close()

    def _format_landmarks_payload(self, landmarks):
        """Returns dict: {'pts': [[x,y,z], ...]} or None."""
        if not landmarks:
            return None
        
        pts = []
        for lm in landmarks:
            if float(lm.get("visibility", 1.0)) < self.LANDMARK_VISIBILITY_THRESHOLD:
                continue

            x = round(float(lm["x"]), 4)
            y = round(float(lm["y"]), 4)
            z = round(float(lm["z"]), 4)
            pts.append([x, y, z])
            
        return {"pts": pts} if pts else None

    def _show_frame(self, frame, showfps = True):
        cv2.imshow("PoseTrack (preview mode)", frame)

        if showfps:
            curr_time = time.time()
            fps = 1 / (curr_time - self.fps_counter_last_time) if self.fps_counter_last_time else 0
            self.fps_counter_last_time = curr_time
            cv2.putText(
                frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
            )


if __name__ == "__main__":
    with open("config.json", "r") as f:
        cfg = json.load(f)

    app = PoseApp(
        udp_ip=cfg.get("udp_ip", "127.0.0.1"),
        udp_port=cfg.get("udp_port", 5005),
        cam_index=cfg.get("cam_index", 0),
        previewMode=cfg.get("previewMode", True)
    )
    app.run()