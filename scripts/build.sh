#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

YELLOW="\033[33m"; GREEN="\033[32m"; RED="\033[31m"; RESET="\033[0m"

echo -e "${YELLOW}==== Cleaning old build folders ====${RESET}"
rm -rf build dist || true

echo -e "${YELLOW}==== Detecting mediapipe modules path ====${RESET}"
PYTHON="./.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="python3"
fi

mpModules="$($PYTHON -c 'import mediapipe, pathlib; print(pathlib.Path(mediapipe.__file__).parent / "modules")' || true)"
if [[ -z "${mpModules:-}" || ! -d "$mpModules" ]]; then
  echo -e "${RED}WARNING: mediapipe modules folder not found. Build may fail!${RESET}"
fi

echo -e "${YELLOW}==== Building application with PyInstaller ====${RESET}"
"$PYTHON" -m PyInstaller --onefile --windowed --name PoseLandmarkSender app.py \
  --add-data "$mpModules:mediapipe/modules"

echo -e "${YELLOW}==== Copying config.json to dist ====${RESET}"
if [[ -f "config.json" ]]; then
  mkdir -p dist
  cp -f "config.json" "dist/config.json"
else
  echo -e "${YELLOW}WARNING: config.json not found, skipping copy.${RESET}"
fi

echo
echo -e "${GREEN}=======================================${RESET}"
echo -e "${GREEN} Build finished successfully!${RESET}"

if [[ -d "dist/PoseLandmarkSender.app" ]]; then
  echo -e "${GREEN} PoseLandmarkSender.app is located in the 'dist' folder${RESET}"
elif [[ -f "dist/PoseLandmarkSender" ]]; then
  echo -e "${GREEN} PoseLandmarkSender is located in the 'dist' folder${RESET}"
else
  echo -e "${YELLOW} Build done, but no known artifact found. Check the 'dist' folder.${RESET}"
fi
echo -e "${GREEN}=======================================${RESET}"