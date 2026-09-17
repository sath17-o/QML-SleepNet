@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo QML-SleepNet full evaluator reproduction - x01 through x35
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

.venv\Scripts\python.exe -c "import numpy, torch" >nul 2>&1
if errorlevel 1 (
  echo Installing inference dependencies...
  .venv\Scripts\python.exe -m pip install --upgrade pip
  if errorlevel 1 exit /b 1
  .venv\Scripts\python.exe -m pip install -r requirements-inference.txt
  if errorlevel 1 exit /b 1
)

echo.
echo Verifying all 35 bundled Stage02 evaluator records...
.venv\Scripts\python.exe scripts\setup_evaluator_data.py --mode full
if errorlevel 1 exit /b 1

echo.
echo Running the published Stage06 checkpoint on x01 through x35...
.venv\Scripts\python.exe scripts\run_pipeline.py --mode inference --stage02-dir "data\stage02_official_x" --device cpu --compare-reference
if errorlevel 1 exit /b 1

echo.
echo ============================================================
echo FULL EVALUATION PASS: all official-x reference probabilities reproduced within tolerance.
echo ============================================================
exit /b 0
