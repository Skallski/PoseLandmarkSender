import sys
import cv2
import platform
from logger import Logger
from config_loader import ConfigLoader
from pose_landmark_detector import PoseLandmarkDetector
from payload_builder import PayloadBuilder
from udp_json_sender import UdpJsonSender
from preview import Preview

if __name__ == "__main__":

    logger = Logger.get()

    # load config
    try:
        cfg = ConfigLoader.load_config()
        logger.info("Config loaded successfully")
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit(1)

    # initialize scripts
    pose_detection_bound_left = cfg.get("pose_detection_bound_left", 0.25)
    pose_detection_bound_right = cfg.get("pose_detection_bound_right", 0.75)

    pose_landmark_detector = PoseLandmarkDetector(
        model_complexity = cfg.get("pose_model_complexity", 1),
        min_detection_confidence = cfg.get("min_pose_detection_confidence", 0.5),
        min_tracking_confidence = cfg.get("min_pose_landmark_tracking_confidence", 0.5),
        pose_detection_bound_left = pose_detection_bound_left,
        pose_detection_bound_right = pose_detection_bound_right
    )

    send_frame_payload = cfg.get("send_frame_payload", False)

    payload_builder = PayloadBuilder()

    sender = UdpJsonSender(
        ip = cfg.get("udp_ip", "127.0.0.1"), 
        port = cfg.get("udp_port", 5005)
    )

    if cfg.get("preview_mode", True):
        preview = Preview(
            show_fps = True,
            pose_detection_bound_left = pose_detection_bound_left,
            pose_detection_bound_right = pose_detection_bound_right
        )
    else:
        preview = None

    # initialize webcam
    cam_index = cfg.get("cam_index", 0)

    os_name = platform.system().lower()
    if os_name == "windows": cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    elif os_name == "darwin": cap = cv2.VideoCapture(cam_index, cv2.CAP_AVFOUNDATION)
    else: cap = cv2.VideoCapture(cam_index)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.get("cam_requested_width", 640))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.get("cam_requested_height", 360))
    cap.set(cv2.CAP_PROP_FPS, cfg.get("cam_requested_fps", 30))

    # main loop
    if not cap.isOpened():
        logger.error("Application start error: Cannot open camera!")
        sys.exit(1)

    logger.info(f"Application started successfully")

    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                logger.error("Camera frame is empty! Closing app...")
                break

            pose_landmarks = pose_landmark_detector.get_landmarks(frame)

            # build & send payloads
            landmarks_payload = payload_builder.build_pose_landmarks_payload(pose_landmarks)
            if landmarks_payload:
                sender.send(landmarks_payload)

            if send_frame_payload:
                frame_payload = payload_builder.build_payload(frame)
                if frame_payload:
                    sender.send(frame_payload)

            # preview
            if preview is not None:
                preview.show_preview(frame, pose_landmarks)
                if preview.trigger_close_window():
                    break

    except Exception as e:
        logger.error(e)
    finally:
        cap.release()

        if preview is not None:
            preview.close()

        pose_landmark_detector.close()
        sender.close()
        logger.info("Application closed successfully")