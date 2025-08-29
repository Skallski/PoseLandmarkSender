import sys
import json
import os
from pose_landmark_sender import PoseLandmarkSender


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(base_path, "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    app = PoseLandmarkSender(
        udp_ip = cfg.get("udp_ip", "127.0.0.1"),
        udp_port = cfg.get("udp_port", 5005),
        cam_index = cfg.get("cam_index", 0),
        cam_requested_width = cfg.get("cam_requested_width", 640),
        cam_requested_height = cfg.get("cam_requested_height", 360),
        cam_requested_fps = cfg.get("cam_requested_fps", 30),
        pose_model_complexity = cfg.get("pose_model_complexity", 1),
        min_pose_detection_confidence = cfg.get("min_pose_detection_confidence", 0.5),
        min_landmark_tracking_confidence = cfg.get("min_landmark_tracking_confidence", 0.5),
        preview_mode = cfg.get("preview_mode", True)
    )
    app.run()