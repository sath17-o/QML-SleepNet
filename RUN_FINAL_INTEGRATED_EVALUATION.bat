@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo QML-SleepNet final integrated evaluation reproduction
echo ============================================================

py -3.11 --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.11 is required. Install Python 3.11 and ensure the Windows py launcher is available.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python 3.11 virtual environment...
  py -3.11 -m venv .venv
  if errorlevel 1 exit /b 1
)

.venv\Scripts\python.exe -c "import numpy, sklearn" >nul 2>&1
if errorlevel 1 (
  echo Installing final-evaluation dependencies...
  .venv\Scripts\python.exe -m pip install --upgrade pip
  if errorlevel 1 exit /b 1
  .venv\Scripts\python.exe -m pip install -r requirements-final-evaluation.txt
  if errorlevel 1 exit /b 1
)

echo.
echo Reproducing fixed 25%% physiology + 75%% QML project-level fusion...
.venv\Scripts\python.exe scripts\run_final_integrated_evaluation.py
if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo FINAL INTEGRATED EVALUATION PASS
 echo ============================================================
exit /b 0
