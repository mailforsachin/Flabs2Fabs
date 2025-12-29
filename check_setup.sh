#!/bin/bash
echo "🔍 Flab2Fabs Current Setup Diagnostic"
echo "====================================="

echo ""
echo "1. DOMAIN RESOLUTION"
echo "--------------------"
dig flab2fabs.omchat.ovh +short

echo ""
echo "2. PORT 8008 STATUS"
echo "-------------------"
if sudo netstat -tulpn | grep :8008; then
    echo "✅ Port 8008 is in use"
else
    echo "❌ Port 8008 is NOT in use"
fi

echo ""
echo "3. NGINX CONFIGURATION"
echo "----------------------"
if [ -f /etc/nginx/sites-available/flab2fabs ]; then
    echo "✅ Config file exists"
    echo "Contents:"
    head -20 /etc/nginx/sites-available/flab2fabs
else
    echo "❌ No flab2fabs config found"
fi

echo ""
echo "4. PROJECT STRUCTURE"
echo "-------------------"
if [ -d ~/flabs2fabs ]; then
    echo "✅ Project directory exists"
    find ~/flabs2fabs -type f -name "*.json" -o -name "*.tsx" -o -name "*.ts" | head -10
else
    echo "❌ Project directory not found"
fi

echo ""
echo "5. SSL CERTIFICATE STATUS"
echo "-------------------------"
if [ -d /etc/letsencrypt/live/flab2fabs.omchat.ovh ]; then
    echo "✅ SSL certificate directory exists"
    sudo certbot certificates | grep flab2fabs || echo "No certbot entry found"
else
    echo "❌ No SSL certificate found for flab2fabs.omchat.ovh"
fi

echo ""
echo "6. NODE/NPM VERSIONS"
echo "--------------------"
node --version 2>/dev/null || echo "Node.js not installed"
npm --version 2>/dev/null || echo "npm not installed"

echo ""
echo "====================================="
echo "Diagnostic complete!"
