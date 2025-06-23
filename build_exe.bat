@echo off

REM Make current folder the one where this script is located
cd /d "%~dp0"

.venv\Scripts\pyinstaller.exe --clean --onefile --collect-submodules=geoip2 --collect-data=geoip2 --hidden-import=sqlite3 src\request_flood_guard.py

REM Copy all .mmdb and .ini files from src to dist if newer
xcopy src\*.mmdb dist\ /D /Y
xcopy src\*.ini dist\ /D /Y
xcopy README.MD dist\ /D /Y
xcopy LICENSE dist\ /D /Y