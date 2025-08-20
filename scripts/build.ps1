$ErrorActionPreference = "Stop"

Set-Location -Path "$PSScriptRoot\.."

Write-Host "==== Cleaning old build folders ====" -ForegroundColor Yellow
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "==== Detecting mediapipe modules path ====" -ForegroundColor Yellow
$mpModules = & .\.venv\Scripts\python.exe -c "import mediapipe, pathlib; print(pathlib.Path(mediapipe.__file__).parent / 'modules')"
if (-not (Test-Path $mpModules)) {
    Write-Host "WARNING: mediapipe modules folder not found. Build may fail!" -ForegroundColor Red
}

Write-Host "==== Building application with PyInstaller ====" -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m PyInstaller --onefile --noconsole app.py `
    --add-data "$mpModules;mediapipe\modules"

Write-Host "==== Copying config.json to dist ====" -ForegroundColor Yellow
if (Test-Path "config.json") {
    Copy-Item -Path "config.json" -Destination "dist\config.json" -Force
} else {
    Write-Host "WARNING: config.json not found, skipping copy." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host " Build finished successfully!" -ForegroundColor Green
Write-Host " app.exe is located in the 'dist' folder" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green