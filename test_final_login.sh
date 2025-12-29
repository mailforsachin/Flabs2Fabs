#!/bin/bash

echo "========================================="
echo "  FINAL LOGIN TEST"
echo "========================================="
echo

echo "🔍 1. CHECKING SERVICES..."
echo "------------------------"
echo "Backend (port 8008):"
if curl -s http://localhost:8008/health > /dev/null; then
    echo "✅ Backend running"
    echo "   Health: $(curl -s http://localhost:8008/health | jq -r '.status' 2>/dev/null || echo 'Unknown')"
else
    echo "❌ Backend NOT running"
    echo "   Starting backend..."
    cd ~/flabs2fabs/backend
    source venv/bin/activate
    pkill -f "uvicorn.*8008" 2>/dev/null
    sleep 2
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8008 > server.log 2>&1 &
    sleep 3
fi

echo
echo "Nginx:"
if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx running"
else
    echo "❌ Nginx NOT running"
    sudo systemctl start nginx
fi

echo
echo "🔍 2. TESTING LOGIN..."
echo "--------------------"
echo "Direct backend test:"
curl -s -X POST http://localhost:8008/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sashy","password":"Welcome2026!"}' \
  | jq -r '.access_token? // "No token"' | grep -q "." && echo "✅ Direct login works" || echo "❌ Direct login failed"

echo
echo "Nginx proxy test:"
RESPONSE=$(curl -k -s -X POST https://flabs2fabs.omchat.ovh/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: https://flabs2fabs.omchat.ovh" \
  -d '{"username":"sashy","password":"Welcome2026!"}')

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✅ Nginx login works"
    echo "   Token received"
else
    echo "❌ Nginx login failed"
    echo "   Response: ${RESPONSE:0:200}"
fi

echo
echo "🔍 3. CORS TEST..."
echo "----------------"
echo "OPTIONS preflight:"
curl -k -s -I -X OPTIONS https://flabs2fabs.omchat.ovh/api/auth/login \
  -H "Origin: https://flabs2fabs.omchat.ovh" \
  -H "Access-Control-Request-Method: POST" \
  | grep -i "access-control" | head -3 || echo "No CORS headers in preflight"

echo
echo "🔍 4. FRONTEND STATUS..."
echo "-----------------------"
cd ~/flabs2fabs/frontend
if [ -d "build" ]; then
    echo "✅ Frontend build exists"
    echo "   Checking nginx is serving it..."
    curl -k -s https://flabs2fabs.omchat.ovh | grep -q "Flab2Fabs\|React\|<!DOCTYPE" && echo "   ✅ Frontend being served" || echo "   ❌ Cannot fetch frontend"
else
    echo "❌ No frontend build"
    echo "   Run: cd ~/flabs2fabs/frontend && npm run build"
fi

echo
echo "========================================="
echo "  NEXT STEPS"
echo "========================================="
echo "1. Open https://flabs2fabs.omchat.ovh in browser"
echo "2. Open Developer Tools (F12)"
echo "3. Go to Console tab"
echo "4. Try to login with:"
echo "   Username: sashy"
echo "   Password: Welcome2026!"
echo "5. Check for errors in Console"
echo "6. Check Network tab for API calls"
echo
echo "Common issues to check:"
echo "• CORS errors → Backend CORS config"
echo "• 404 errors → Nginx proxy config"
echo "• Network errors → Backend not running"
