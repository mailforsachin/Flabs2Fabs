#!/bin/bash

echo "========================================="
echo "  FRONTEND CONTENT ANALYSIS"
echo "========================================="
echo

cd ~/flabs2fabs/frontend

echo "🔍 1. APP.TSX ANALYSIS..."
echo "-----------------------"
if [ -f "src/App.tsx" ]; then
    echo "File size: $(wc -l < src/App.tsx) lines"
    echo "First 50 lines:"
    head -50 src/App.tsx
    echo "..."
    echo "Last 50 lines:"
    tail -50 src/App.tsx
    echo
    echo "Looking for functional components:"
    grep -n "function\|const.*=\|return\|<div" src/App.tsx | head -20
else
    echo "App.tsx not found!"
fi

echo
echo "🔍 2. LOGIN.TSX ANALYSIS..."
echo "-------------------------"
if [ -f "src/Login.tsx" ]; then
    echo "File size: $(wc -l < src/Login.tsx) lines"
    echo "First 100 lines:"
    head -100 src/Login.tsx
    echo "..."
    echo "Looking for form elements and handlers:"
    grep -n "form\|input\|button\|onSubmit\|onClick\|handle" src/Login.tsx | head -20
else
    echo "Login.tsx not found!"
fi

echo
echo "🔍 3. PACKAGE.JSON ANALYSIS..."
echo "----------------------------"
echo "Dependencies:"
grep -A20 '"dependencies"' package.json
echo
echo "Scripts:"
grep -A10 '"scripts"' package.json

echo
echo "🔍 4. CHECKING FOR HARDCODED API URLS..."
echo "--------------------------------------"
echo "Searching source files for API URLs:"
find src -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.js" \) -exec grep -H "http://\|https://\|localhost\|:800" {} \;

echo
echo "🔍 5. QUICK REBUILD TEST..."
echo "-------------------------"
echo "Checking if we can build the app:"
if [ -f "package.json" ]; then
    echo "npm version: $(npm --version 2>/dev/null || echo 'npm not available')"
    echo "node version: $(node --version 2>/dev/null || echo 'node not available')"
    
    # Check if dependencies are installed
    if [ -d "node_modules" ]; then
        echo "node_modules exists: $(du -sh node_modules)"
    else
        echo "node_modules NOT found - need to run npm install"
    fi
fi
