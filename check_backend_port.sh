#!/bin/bash

echo "========================================="
echo "  FINDING ACTUAL BACKEND PORT"
echo "========================================="
echo

echo "🔍 1. CHECKING ALL PORTS 8000-8010..."
echo "-----------------------------------"
for port in {8000..8010}; do
    if sudo ss -tulpn | grep -q ":$port "; then
        echo "   ✅ Port $port is IN USE:"
        sudo ss -tulpn | grep ":$port " | sed 's/^/     /'
        
        # Get process info
        PID=$(sudo lsof -ti:$port 2>/dev/null | head -1)
        if [ -n "$PID" ]; then
            echo "     Process ID: $PID"
            echo "     Command: $(ps -p $PID -o command= 2>/dev/null || echo 'Cannot get process info')"
            
            # Check if it's our flabs2fabs backend
            if ps -p $PID -o command= 2>/dev/null | grep -q "flabs2fabs\|main.py"; then
                echo "     🎯 THIS IS FLABS2FABS BACKEND!"
            fi
        fi
        echo
    fi
done

echo
echo "🔍 2. CHECKING ALL PYTHON PROCESSES..."
echo "------------------------------------"
ps aux | grep python | grep -v grep | while read line; do
    echo "   $line"
    # Extract PID
    PID=$(echo $line | awk '{print $2}')
    # Check what files it's using
    echo "     Open files:"
    sudo lsof -p $PID 2>/dev/null | grep "TCP.*LISTEN" | sed 's/^/       /' || echo "       No listening sockets"
    echo
done

echo
echo "🔍 3. CHECKING SPECIFICALLY FOR FLABS2FABS..."
echo "-------------------------------------------"
echo "Checking for any process with 'flabs2fabs' in command:"
ps aux | grep -i flabs2fabs | grep -v grep | sed 's/^/   /'
echo

echo "Checking backend directory for running processes:"
cd ~/flabs2fabs/backend
# Check if any process is running from this directory
for pid in $(ps aux | grep python | grep -v grep | awk '{print $2}'); do
    if sudo ls -la /proc/$pid/cwd 2>/dev/null | grep -q "flabs2fabs"; then
        echo "   Process $pid is running from flabs2fabs directory"
        echo "   Command: $(ps -p $pid -o command= 2>/dev/null)"
        echo "   CWD: $(sudo readlink /proc/$pid/cwd 2>/dev/null)"
        echo
    fi
done

echo
echo "🔍 4. CHECKING BACKEND LOGS..."
echo "----------------------------"
echo "Recent backend logs:"
ls -la ~/flabs2fabs/backend/*.log 2>/dev/null | head -5
echo
echo "Checking for port mentions in logs:"
grep -i "port\|800\|start\|listen" ~/flabs2fabs/backend/*.log 2>/dev/null | tail -10 | sed 's/^/   /'

echo
echo "🔍 5. CHECKING STARTUP SCRIPTS..."
echo "-------------------------------"
echo "Looking for startup scripts in backend:"
ls -la ~/flabs2fabs/backend/*.sh 2>/dev/null
echo
echo "Checking start_server.sh:"
if [ -f ~/flabs2fabs/backend/start_server.sh ]; then
    cat ~/flabs2fabs/backend/start_server.sh | grep -i port
fi

echo
echo "🔍 6. MANUAL PORT TESTING..."
echo "--------------------------"
echo "Testing each port for FastAPI response:"
for port in 8000 8001 8008 8009 8010 8080; do
    echo -n "   Testing port $port... "
    if timeout 2 curl -s http://localhost:$port/health > /dev/null; then
        echo "✅ RESPONDS with /health"
        echo "     Testing /api/auth/status..."
        curl -s http://localhost:$port/api/auth/status | head -2 | sed 's/^/       /'
    elif timeout 2 curl -s http://localhost:$port > /dev/null; then
        echo "✅ RESPONDS (no /health endpoint)"
    else
        echo "❌ No response"
    fi
done

echo
echo "🔍 7. CHECKING NGINX CONFIG FOR PROXY..."
echo "--------------------------------------"
echo "Looking for proxy_pass in flabs2fabs config:"
sudo grep -n "proxy_pass" /etc/nginx/sites-available/flabs2fabs
echo
echo "Full flabs2fabs nginx config:"
sudo cat /etc/nginx/sites-available/flabs2fabs
