@echo off
echo Starting Task Management Application Setup...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.x
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python init_db.py

REM Run the application
echo Starting Flask application...
echo Access the application at http://localhost:5000
echo Default admin credentials:
echo Username: admin
echo Password: admin123
python app.py 