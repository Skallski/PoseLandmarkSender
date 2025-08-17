$ErrorActionPreference = "Stop"

Set-Location -Path "$PSScriptRoot\.."

Write-Host "==== Cleaning old build folders ====" -ForegroundColor Yellow
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "==== Building application with PyInstaller ====" -ForegroundColor Yellow
pyinstaller --onefile --noconsole app.py

Write-Host "==== Copying config.json to dist ====" -ForegroundColor Yellow
Copy-Item -Path "config.json" -Destination "dist\config.json" -Force

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host " Build finished successfully!" -ForegroundColor Green
Write-Host " app.exe is located in the 'dist' folder" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green