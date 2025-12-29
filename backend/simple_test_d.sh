#!/bin/bash

echo "🎯 TESTING PHASE D ENDPOINTS"
echo "============================="

BASE_URL="http://localhost:8008"

# Get admin token first (since test_athlete might not have data)
echo -e "\n🔐 Getting admin token..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "sashy", "password": "Welcome2026!"}' | \
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data['access_token'])
except:
    print('AUTH_FAILED')
")

if [ "$TOKEN" = "AUTH_FAILED" ]; then
    echo "❌ Authentication failed"
    exit 1
fi

echo "✅ Authenticated"

# Test each endpoint
echo -e "\n1. 📊 Testing Strength Projections:"
RESPONSE=$(curl -s "$BASE_URL/api/progress/strength-projections?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -50 || echo "Raw: ${RESPONSE:0:200}..."
fi

echo -e "\n2. 📅 Testing Consistency Projections:"
RESPONSE=$(curl -s "$BASE_URL/api/progress/consistency-projections?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -50 || echo "Raw: ${RESPONSE:0:200}..."
fi

echo -e "\n3. 📈 Testing Comprehensive Report:"
RESPONSE=$(curl -s "$BASE_URL/api/progress/comprehensive-report?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -50 || echo "Raw: ${RESPONSE:0:200}..."
fi

echo -e "\n4. 💪 Testing Motivational Insights:"
RESPONSE=$(curl -s "$BASE_URL/api/progress/motivational-insights?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -50 || echo "Raw: ${RESPONSE:0:200}..."
fi

echo -e "\n5. ❌ Testing Missed Opportunities:"
RESPONSE=$(curl -s "$BASE_URL/api/progress/missed-opportunities?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -50 || echo "Raw: ${RESPONSE:0:200}..."
fi

echo -e "\n✅ All Phase D endpoints tested!"
