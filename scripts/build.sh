#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

echo "==== Cleaning old build folders ===="
rm -rf build dist

echo "==== Detecting mediapipe modules path ===="
mpModules=$(./.venv/bin/python3 -c "import mediapipe, pathlib; print(pathlib.Path(mediapipe.__file__).parent / 'modules')")
if [ ! -d "$mpModules" ]; then
    echo "WARNING: mediapipe modules folder not found. Build may fail!"
fi

echo "==== Building application with PyInstaller ===="
./.venv/bin/python3 -m PyInstaller --onefile --noconsole app.py \
    --add-data "$mpModules:mediapipe/modules"

echo "==== Copying config.json to dist ===="
if [ -f "config.json" ]; then
    cp config.json dist/config.json
else
    echo "WARNING: config.json not found, skipping copy."
fi

echo ""
echo "======================================="
echo " Build finished successfully!"
echo " app executable is located in the 'dist' folder"
echo "======================================="