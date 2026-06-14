@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~dp0NCWHTD_Credits_Trainer.exe' -Verb RunAs"
