#!/bin/bash
# Staging Environment Startup Script
# 
# ⚠️  DEPRECATED: This script is deprecated. Please use the npm script instead:
#    npm run staging:full
# 
# The npm script provides better cross-platform compatibility and process management.

echo "🚀 Starting Databricks Orchestrator - Staging Environment"
echo "⚠️  NOTE: Consider using 'npm run staging:full' for improved experience"

# Load staging environment using new Python environment loader
echo "📋 Loading environment configuration..."
eval $(python scripts/load-env.py staging | grep "^export")

# Start backend in background
echo "📦 Starting Backend (Port: $API_PORT)..."
cd backend && uvicorn src.main:app --host 0.0.0.0 --port $API_PORT --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🌐 Starting Frontend (Port: $FRONTEND_PORT)..."
cd ../frontend && npm run build && npm run preview -- --port $FRONTEND_PORT &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Setup trap for cleanup
trap cleanup SIGINT SIGTERM

echo "✅ Staging environment started!"
echo "   Backend:  http://localhost:$API_PORT"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Database: orchestrator_staging.db"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait