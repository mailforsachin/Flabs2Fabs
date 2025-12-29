#!/bin/bash
cd ~/flabs2fabs/backend

# Kill any existing server
pkill -f "uvicorn.*8008" 2>/dev/null || true
sleep 2

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# Start server
echo "🚀 Starting Flab2Fabs API on port 8008..."
echo "📊 Logs: server_output.log"
uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload > server_output.log 2>&1 &

# Wait for startup
sleep 5

# Check if started
if ps aux | grep -v grep | grep -q "uvicorn.*8008"; then
    echo "✅ Server started successfully!"
    echo "🌐 URL: http://localhost:8008"
    echo "📚 Docs: http://localhost:8008/docs"
    echo "📋 Logs: tail -f server_output.log"
    echo "🛑 Stop with: pkill -f 'uvicorn.*8008'"
    
    # Show first 10 lines of log
    echo ""
    echo "=== Server Log (first 10 lines) ==="
    head -10 server_output.log
else
    echo "❌ Server failed to start"
    echo "=== Error Log ==="
    tail -20 server_output.log
fi
