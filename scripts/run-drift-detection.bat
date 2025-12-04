@echo off
REM Drift Detection Windows Task Scheduler Script

REM Configuration
set PROJECT_DIR=C:\Project\drift-detection-system
set BUCKET=drift-detection-drift-detection-dev-026bfe5b
set SNS_TOPIC=arn:aws:sns:us-east-1:900317037265:vprofile-pipeline-notifications
set LOG_FILE=C:\temp\drift-detection.log

REM Create temp directory if it doesn't exist
if not exist C:\temp mkdir C:\temp

REM Change to project directory
cd /d %PROJECT_DIR%

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set UTF-8 encoding for emoji support
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

REM Set AWS region
set AWS_REGION=us-east-1

REM Log start time
echo === Drift Detection Run: %date% %time% === >> %LOG_FILE%

REM Run drift detection
drift-detect --bucket %BUCKET% --sns-topic %SNS_TOPIC% detect-all >> %LOG_FILE% 2>&1

REM Log completion
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Drift detection completed >> %LOG_FILE%
) else (
    echo [ERROR] Drift detection failed >> %LOG_FILE%
)

echo. >> %LOG_FILE%
