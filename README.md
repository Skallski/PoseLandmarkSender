# Pose Landmark Sender
Real-time pose landmark detection and transmission over UDP

<p align="center">
	<img alt="package.json version" src="https://img.shields.io/badge/version-v1.2-blue" />
	<a href="https://github.com/Skallski/PoseLandmarkSender/issues">
		<img alt="GitHub issues" src ="https://img.shields.io/github/issues/Skallski/PoseLandmarkSender" />
	</a>
	<a href="https://github.com/Skallu0711/PoseLandmarkSender/pulls">
		<img alt="GitHub pull requests" src ="https://img.shields.io/github/issues-pr/Skallski/PoseLandmarkSender" />
	</a>
	<a href="https://github.com/Skallu0711/PoseLandmarkSender/blob/master/LICENSE">
		<img alt="GitHub license" src ="https://img.shields.io/github/license/Skallski/PoseLandmarkSender" />
	</a>
	<img alt="GitHub last commit" src ="https://img.shields.io/github/last-commit/Skallski/PoseLandmarkSender" />
</p>

---

### Introduction
Pose Landmark Sender performs **real-time pose landmark detection** from webcam input using [MediaPipe Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker?hl=en).  

- Runs entirely on **CPU**  
- Outputs **detected landmarks** + lightweight frame metadata  
- Data is serialized to **JSON** and streamed via **UDP**  

---

### Platforms:
<p align="center">
	<img alt="Windows" src="https://img.shields.io/badge/Windows-Stable-28a745?style=for-the-badge&logo=windows&logoColor=white" />
	<img alt="macOS" src="https://img.shields.io/badge/macOS-In%20Progress-FFD700?style=for-the-badge&logo=apple&logoColor=white" />
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

# macOS/Linux
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
py -m PyInstaller --onefile --console --clean --name PoseLandmarkSender app.py
copy config.json dist\

# macOS/Linux
python -m PyInstaller --onefile --windowed --clean --name PoseLandmarkSender app.py
cp config.json dist/
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

  "preview_mode": true
}
```
| Parameter                       | Description                                                           |
|---------------------------------|-----------------------------------------------------------------------|
| `udp_ip`                        | Target IP address for UDP packets                                     |
| `udp_port`                      | Target port for UDP packets                                           |
| `cam_index`                     | OS camera index (0 = default webcam)                                  |
| `cam_requested_width`           | Requested capture width (may be capped by the camera)                  |
| `cam_requested_height`          | Requested capture height (may be capped by the camera)                 |
| `cam_requested_fps`             | Requested capture FPS (may be capped by the camera)                    |
| `pose_model_complexity`         | Model size/accuracy trade-off: 0 (fastest), 1 (default), 2 (most accurate) |
| `min_pose_detection_confidence` | Minimum confidence threshold to accept a person detection              |
| `min_landmark_tracking_confidence` | Minimum confidence threshold to accept landmark tracking updates    |
| `preview_mode`                  | Show a local preview window when `true`                               |

---

### UDP payload
The payload contains pose landmarks (`pts`) - an array of (`x`, `y`, `z`) coordinates - and per-frame metadata (`frame_b64`) - a Base64-encoded JPEG of the current frame.  

Landmark coordinates follow MediaPipe’s image-normalized convention (`x`, `y` ∈ `[0, 1]`; `z` is normalized depth, negative in front of the camera).
If a landmark is not visible, the sender returns `-1` for `x`, `y`, and `z`.  

**Example**
```json
{
  "pts": [
    { "x": 0.5123, "y": 0.4132, "z": -0.0123 },
    { "x": 0.5234, "y": 0.4021, "z": -0.0156 },
    { "x": 0.5401, "y": 0.3950, "z": -0.0180 },
    { "x": 0.5589, "y": 0.3921, "z": -0.0205 },
    { "x": 0.5776, "y": 0.3942, "z": -0.0230 },
    { "x": 0.5950, "y": 0.4018, "z": -0.0257 },
    { "x": -1,     "y": -1,     "z": -1 },
	...
  ],
  "frame_b64": "/9j/4AAQSkZJRgABAQAAAQABAAD/..."
}
```
