#!/bin/bash

echo "Starting development environment..."

# Start Flask backend in background
echo "Starting Flask backend on port 8000..."
cd app
python main.py &
FLASK_PID=$!
cd ..

# Wait a moment for Flask to start
sleep 2

# Start React frontend
echo "Starting React frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Development servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8000/api/dashboard"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $FLASK_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
