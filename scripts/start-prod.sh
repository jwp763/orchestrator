#!/bin/bash
# Production Environment Startup Script
# 
# ⚠️  DEPRECATED: This script is deprecated. Please use the npm script instead:
#    npm run prod:full
# 
# The npm script provides better cross-platform compatibility and process management.

echo "🚀 Starting Databricks Orchestrator - Production Environment"
echo "⚠️  NOTE: Consider using 'npm run prod:full' for improved experience"

# Load production environment using new Python environment loader
echo "📋 Loading environment configuration..."
eval $(python scripts/load-env.py production | grep "^export")

# Start backend in background (no reload in production)
echo "📦 Starting Backend (Port: $API_PORT)..."
cd backend && uvicorn src.main:app --host 0.0.0.0 --port $API_PORT &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend (production build)
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

echo "✅ Production environment started!"
echo "   Backend:  http://localhost:$API_PORT"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Database: orchestrator_prod.db"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait