#!/bin/bash

# Start the FastAPI backend
echo "Starting FastAPI backend..."
uvicorn app.main:app --port 8000 --reload --reload-dir=app &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Streamlit frontend
echo "Starting Streamlit frontend..."
streamlit run streamlit_app.py --server.port 8501

# Clean up backend when script exits
trap "kill $BACKEND_PID" EXIT
