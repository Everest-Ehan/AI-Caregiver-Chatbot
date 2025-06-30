@echo off
echo ========================================
echo AI Caregiver Chatbot - Python 3.11 Setup
echo ========================================
echo.

echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Setting up backend...
cd backend

echo Running Python 3.11 setup script...
python setup_python311.py
if %errorlevel% neq 0 (
    echo ERROR: Backend setup failed
    pause
    exit /b 1
)

echo.
echo Backend setup completed successfully!
echo.
echo Next steps:
echo 1. Update the OPENAI_API_KEY in backend/.env file
echo 2. Run: python backend/run.py
echo 3. Open http://localhost:8000 in your browser
echo.
pause 