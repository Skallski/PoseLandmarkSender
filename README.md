# Pose Landmark Sender
Real-time pose landmark detection and transmission over UDP

<p align="center">
	<a href="https://github.com/Skallski/PoseLandmarkSender/releases/latest">
  		<img alt="latest release" src="https://img.shields.io/github/v/release/Skallski/PoseLandmarkSender?sort=semver&label=latest%20release" />
	</a>
		<img alt="GitHub last commit" src ="https://img.shields.io/github/last-commit/Skallski/PoseLandmarkSender" />
	<a href="https://github.com/Skallu0711/PoseLandmarkSender/blob/master/LICENSE">
		<img alt="GitHub license" src ="https://img.shields.io/github/license/Skallski/PoseLandmarkSender" />
	</a>
</p>

---

### Introduction
Pose Landmark Sender performs **real-time pose landmark detection** from webcam input using [MediaPipe Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker?hl=en).  

- Runs entirely on **CPU**  
- Outputs **detected landmarks** and optional **base64 encoded frame**
- Data is serialized to **JSON** and streamed via **UDP**  

---

### Platforms:
<p align="center">
	<img alt="Windows" src="https://img.shields.io/badge/Windows-Stable-28a745?style=for-the-badge&logo=windows&logoColor=white" />
  <img alt="macOS" src="https://img.shields.io/badge/macOS-Stable-28a745?style=for-the-badge&logo=apple&logoColor=white" />
	<img alt="Linux" src="https://img.shields.io/badge/Linux-Not%20Supported-CC0000?style=for-the-badge&logo=linux&logoColor=white" />
</p>

---

### Instalation
You can either download a prebuilt release from the [Releases](../../releases) page or build from source:

#### Building from source
**Prerequisites**
- `Python 3.8+` and `pip` on your PATH

**(Recommended) Create a virtual environment**
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS
source .venv/bin/activate
```

**Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Build a standalone binary (Pyinstaller)**
```bash
# Windows
py -m PyInstaller --onefile --noconsole --clean \
  --name PoseLandmarkSender app.py \
  --add-data ".venv\Lib\site-packages\mediapipe\modules;mediapipe\modules"
copy config.json dist\

# macOS
python -m PyInstaller --onedir --clean \
  --target-arch arm64 \
  --name PoseLandmarkSender app.py \
  --add-data ".venv/lib/python3.11/site-packages/mediapipe/modules:mediapipe/modules"
cp config.json "dist/PoseLandmarkSender.app/Contents/MacOS/"
xattr -dr com.apple.quarantine "dist/PoseLandmarkSender.app"
```

---

### Configuration (config.json)
> **Note:** `config.json` must be placed in the same directory as the executable.
```json
{
  "udp_ip": "127.0.0.1",
  "udp_port": 5005,

  "cam_index": 0,
  "cam_requested_width": 640,
  "cam_requested_height": 360,
  "cam_requested_fps": 30,

  "pose_model_complexity": 1,
  "min_pose_detection_confidence": 0.5,
  "min_landmark_tracking_confidence": 0.5,
  "pose_detection_bound_left": 0.25,
  "pose_detection_bound_right": 0.75,
  "pose_detection_feet_bound_top": 0.1,
  "pose_detection_feet_bound_bottom": 0.3,

  "send_frame_payload": false,

  "preview_mode": true
}
```
| Parameter                          | Description                                                                |
|------------------------------------|----------------------------------------------------------------------------|
| `udp_ip`                           | Target IP address for UDP packets                                          |
| `udp_port`                         | Target port for UDP packets                                                |
| `cam_index`                        | OS camera index (0 = default webcam)                                       |
| `cam_requested_width`              | Requested capture width (may be capped by the camera)                      |
| `cam_requested_height`             | Requested capture height (may be capped by the camera)                     |
| `cam_requested_fps`                | Requested capture FPS (may be capped by the camera)                        |
| `pose_model_complexity`            | Model size/accuracy trade-off: 0 (fastest), 1 (default), 2 (most accurate) |
| `min_pose_detection_confidence`    | Minimum confidence threshold to accept a person detection                  |
| `min_landmark_tracking_confidence` | Minimum confidence threshold to accept landmark tracking updates           |
| `pose_detection_bound_left`        | Normalized left boundary (0–1) for the pose detection area                 |
| `pose_detection_bound_right`       | Normalized right boundary (0–1) for the pose detection area                |
| `pose_detection_feet_bound_top` | Normalized top boundary (0–1) for feet — helps estimate user distance from the camera <br> (the farther the user stays, the higher their feet appear in the frame) |
| `pose_detection_feet_bound_bottom` | Normalized bottom boundary (0–1) for feet — helps estimate user distance from the camera <br> (the farther the user stays, the higher their feet appear in the frame)   |
| `send_frame_payload` 			     | Build and send frame data payload when `true` (useful for debugging, increases bandwidth usage)   |
| `preview_mode`                     | Show a local preview window when `true`                                    |

---

### UDP payload
Sender emits *two independent JSON packets per iteration*: one with *landmarks* and optional one with the *frame*.
* 33 pose *Landmarks*: `{"pts": [{x, y, z}, ...]}` in MediaPipe , image-normalized convention (`x, y ∈ [0, 1]`. `z` is normalized depth, negative in front of the camera). If a landmark is not visible, the sender returns `-1` for `x`, `y`, and `z`.  
* *Frame* metadata `{"frame_b64":"<base64 JPEG>"}` - a Base64-encoded JPEG of the current frame.  

**Landmarks payload example**
```json
{
  "pts": [
    {"x":0.5123,"y":0.4132,"z":-0.0123},
    {"x":0.5234,"y":0.4021,"z":-0.0156},
    {"x":-1,"y":-1,"z":-1}
    ...
  ]
}
```

**Frame payload example**
```json
{"frame_b64":"/9j/4AAQSkZJRgABAQAAAQABAAD/..."}
```
