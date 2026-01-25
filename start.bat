@echo off
REM Startup script for Hybrid Attendance Management System (Windows)

echo Starting Hybrid Attendance Management System...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python init_db.py

REM Start the server
echo Starting server...
python app/main.py

pause
