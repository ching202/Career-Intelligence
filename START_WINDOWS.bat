@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto dependencies
py -3.12 -m venv .venv
if errorlevel 1 goto setup_failed
:dependencies
".venv\Scripts\python.exe" -c "import importlib.metadata as m; assert m.version('pandas') == '2.2.3'; assert m.version('streamlit') == '1.51.0'; assert m.version('plotly') == '6.3.1'" >nul 2>&1
if not errorlevel 1 goto launch
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto setup_failed
:launch
echo Opening Career Intelligence. Keep this window open. Press Ctrl+C to stop.
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto setup_failed
exit /b 0
:setup_failed
echo Setup or launch failed. Install Python 3.12 and follow README.md.
echo For installation, internet access is required. No API keys are needed.
pause
exit /b 1
