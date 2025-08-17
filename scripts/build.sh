set -e

cd "$(dirname "$0")/.."

echo "==== Cleaning old build folders ===="
rm -rf build dist

echo "==== Building application with PyInstaller ===="
pyinstaller --onefile --noconsole app.py

echo "==== Copying config.json to dist ===="
cp config.json dist/config.json

echo ""
echo "======================================="
echo " Build finished successfully!"
echo " app (binary) is located in the 'dist' folder"
echo "======================================="