#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start Backend
echo "Starting Backend on port 8000..."
uvicorn backend.main:app --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready (naive wait)
sleep 2

# Start Frontend
echo "Starting Frontend on port 6004..."
python frontend/app.py &
FRONTEND_PID=$!

echo "Application started."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "To expose to public via Cloudflare Quick Tunnel, run:"
echo "cloudflared tunnel --url http://localhost:6004"

# Trap SIGINT to kill child processes
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT

wait
