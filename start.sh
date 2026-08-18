#!/usr/bin/env bash

# ==============================================================================
# CARENET: Healthcare Provider Network Adequacy & Access Intelligence System
# One-Command Launch Script (macOS / Linux)
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=============================================================================="
echo "🏥 Starting CARENET Intelligence Platform..."
echo "=============================================================================="

# 1. Check Python Dependencies
echo "▶ Checking Python backend dependencies..."
python3 -m pip install -r backend/requirements.txt

# 2. Ingest Data into SQLite Database if needed
if [ ! -f "backend/carenet.db" ]; then
    echo "▶ Initializing database and calculating adequacy metrics..."
    python3 backend/data_processor.py
fi

# 3. Check and Install Frontend Node Modules
if [ ! -d "frontend/node_modules" ]; then
    echo "▶ Installing frontend packages..."
    cd frontend
    npm install
    cd ..
fi

# 4. Clean up any existing listeners on 8000 and 5173
echo "▶ Checking active ports (8000, 5173)..."
lsof -ti:8000 -ti:5173 | xargs kill -9 2>/dev/null || true

# 5. Launch Backend and Frontend concurrently
echo "=============================================================================="
echo "🚀 Launching Backend and Frontend Servers..."
echo "   - Backend REST API:  http://localhost:8000"
echo "   - Frontend Web App:  http://localhost:5173"
echo "=============================================================================="

trap 'echo "\nStopping CARENET servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' SIGINT SIGTERM

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!
cd ..

wait $BACKEND_PID $FRONTEND_PID
