@echo off
echo Starting AI Caregiver Chatbot...
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo [2/3] Starting Backend Server...
cd backend
call venv\Scripts\activate.bat
start "Backend Server" cmd /k "call venv\\Scripts\\activate.bat && python run.py"
cd ..

echo.
echo [3/3] Starting Frontend...
cd caregiver-chatbot
start "Frontend Dev Server" cmd /k "npm run dev"
cd ..

echo.
echo 🚀 Both servers are starting...
echo.
echo 📍 Backend: http://localhost:8000
echo 📍 Frontend: http://localhost:5173
echo 📍 API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this launcher...
pause >nul 