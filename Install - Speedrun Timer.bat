@echo off
setlocal
pushd "%~dp0"
python scripts\install_speedrun_timer.py
echo.
pause
popd
