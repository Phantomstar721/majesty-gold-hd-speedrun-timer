@echo off
setlocal
pushd "%~dp0"
python scripts\restore_speedrun_timer.py
echo.
pause
popd
