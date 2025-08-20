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

### Introduction
Real-time pose landmark detection from webcam input using [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker?hl=en).
Detected landmarks and captured frames are transmitted as JSON over UDP.

### Platforms:
<p align="center">
	<img alt="Windows" src="https://img.shields.io/badge/Windows-Stable-28a745?style=for-the-badge&logo=windows&logoColor=white" />
	<img alt="macOS" src="https://img.shields.io/badge/macOS-In%20Progress-FFD700?style=for-the-badge&logo=apple&logoColor=white" />
	<img alt="Linux" src="https://img.shields.io/badge/Linux-Not%20Supported-CC0000?style=for-the-badge&logo=linux&logoColor=white" />
</p>

### Instalation
You can either **download a prebuilt release** from the [Releases](../../releases) page  
or **build from source**:

1. Install the required libraries from the `requirements.txt` file  
2. Build the project using the appropriate script:  
   - On **Windows**, run `build.ps1`  
   - On **macOS**, run `build.sh`
