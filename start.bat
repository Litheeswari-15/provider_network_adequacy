@echo off
echo ==============================================================================
echo 🏥 Starting CARENET Healthcare Provider Network Intelligence System...
echo ==============================================================================

cd %~dp0

echo ▶ Checking Python dependencies...
python -m pip install -r backend\requirements.txt

if not exist backend\carenet.db (
    echo ▶ Initializing database and calculating adequacy metrics...
    python backend\data_processor.py
)

if not exist frontend\node_modules (
    echo ▶ Installing frontend packages...
    cd frontend
    call npm install
    cd ..
)

echo ==============================================================================
echo 🚀 Launching Backend and Frontend Servers...
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:5173
echo ==============================================================================

start "CARENET Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
start "CARENET Frontend" cmd /k "cd frontend && npm run dev -- --host 0.0.0.0 --port 5173"
