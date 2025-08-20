import json
import sys
import os
import platform
import cv2
import time
from pose_detector import PoseDetector
from udp_json_sender import UdpJsonSender
from pose_payload_builder import PosePayloadBuilder


class PoseApp:
    def __init__(self, udp_ip = "127.0.0.1", udp_port = 5005, cam_index = 0, preview_mode = True):
        self.detector = PoseDetector()
        self.sender = UdpJsonSender(udp_ip, udp_port)
        self.payload_builder = PosePayloadBuilder()

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

        self.preview_Mode = preview_mode
        self.fps_counter_last_time = 0

    def run(self):
        if  self.cap.isOpened():
            print(f"Application {'[preview]' if self.preview_Mode else '[no preview]'} started successfuly")
        else:
            print("Application start error: Cannot open camera!")
            return

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Camera frame is empty")
                break

            landmarks, results = self.detector.process_frame(frame)
            has_landmarks = bool(landmarks)

            if has_landmarks:
                payload = self.payload_builder.build(landmarks, frame)
                if payload:
                    self.sender.send(payload)

            if self.preview_Mode:
                self._show_preview(frame, results, show_fps = True, show_landmarks = has_landmarks)

                # ESC - exit
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        self._cleanup()

    def _cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.detector.close()
        self.sender.close()

    def _show_preview(self, frame, results, show_fps : bool, show_landmarks : bool):
        if show_fps:
            curr_time = time.time()
            fps = 1 / (curr_time - self.fps_counter_last_time) if self.fps_counter_last_time else 0
            self.fps_counter_last_time = curr_time
            cv2.putText(
                frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
            )

        if show_landmarks:
            frame = self.detector.draw_landmarks(frame, results)

        cv2.imshow("Landmark detection", frame)


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(base_path, "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    app = PoseApp(
        udp_ip=cfg.get("udp_ip", "127.0.0.1"),
        udp_port=cfg.get("udp_port", 5005),
        cam_index=cfg.get("cam_index", 0),
        preview_mode=cfg.get("preview_mode", True)
    )
    app.run()