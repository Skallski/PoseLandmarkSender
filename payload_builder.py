import base64
import cv2
from typing import Optional


class PayloadBuilder:
    NUM_LANDMARKS = 33

    def __init__(
        self,
        landmark_visibility_threshold: float = 0.5,
        jpeg_quality: int = 70,
        max_size: int = 60 * 1024,
        quality_floor: int = 20,
        scales: tuple[float, ...] = (0.75, 0.5, 0.35, 0.25),
        quality_steps: tuple[int, ...] = (70, 60, 50, 40, 30)
    ):        
        self.landmark_visibility_threshold = landmark_visibility_threshold
        self.jpeg_quality = jpeg_quality
        self.max_size = max_size
        self.quality_floor = quality_floor
        self.scales = scales
        self.quality_steps = quality_steps

    def _format_landmarks(self, landmarks):
        """
        Format landmarks into format: {"pts":[{x,y,z},...]}
        
        Always emit a fixed-length array (num_landmarks). For any landmark that is
        missing or has visibility below threshold, output (-1, -1, -1).
        The order matches MediaPipe's PoseLandmark index order.
        """
        pts = []
        for i in range(self.NUM_LANDMARKS):
            if landmarks and i < len(landmarks):
                lm = landmarks[i]
                vis = float(lm.get("visibility", 0.0))
                if vis >= self.landmark_visibility_threshold:
                    x = round(float(lm.get("x", -1)), 4)
                    y = round(float(lm.get("y", -1)), 4)
                    z = round(float(lm.get("z", -1)), 4)
                else:
                    x = y = z = -1
            else:
                x = y = z = -1
            pts.append({"x": x, "y": y, "z": z})

        return {"pts": pts}

    def _encode_frame_b64(self, frame) -> Optional[str]:
        """Encode an OpenCV frame to Base64 JPEG with iterative fallback on size."""

        def _try_encode(img, q):
            """Try encoding a frame to JPEG at given quality, return bytes or None."""
            ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), int(q)])
            return buf if ok else None

        # Try with og image with default quality
        buf = _try_encode(frame, self.jpeg_quality)
        if buf is not None and buf.nbytes <= self.max_size:
            return base64.b64encode(buf).decode("utf-8")

        # Fallback: downscale iteratively
        h, w = frame.shape[:2]
        for scale in self.scales:
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            for q in self.quality_steps:
                if q < self.quality_floor:
                    continue

                buf = _try_encode(resized, q)
                if buf is not None and buf.nbytes <= self.max_size:
                    return base64.b64encode(buf).decode("utf-8")

        return None

    def build(self, landmarks, frame = None):
        payload = self._format_landmarks(landmarks or [])

        if frame is not None:
            b64 = self._encode_frame_b64(frame)
            if b64 is not None:
                payload["frame_b64"] = b64

        return payload