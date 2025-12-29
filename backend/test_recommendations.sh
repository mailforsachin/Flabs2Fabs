#!/bin/bash

echo "🧠 Testing Flab2Fabs Recommendation Engine v1"
echo "============================================="

BASE_URL="http://localhost:8008"

# Get user token
echo -e "\n1. Getting user token..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_athlete_1766937260", "password": "TestPass123!"}' | \
  jq -r '.access_token')

echo "Token: ${TOKEN:0:30}..."

# Test 1: Muscle Analysis
echo -e "\n2. Testing Muscle Analysis..."
curl -s "$BASE_URL/api/recommendations/muscle-analysis" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Test 2: Quick Recommendation
echo -e "\n3. Testing Quick Recommendation..."
curl -s "$BASE_URL/api/recommendations/quick" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# Test 3: Full Recommendation
echo -e "\n4. Testing Full Recommendation (Conservative Recovery)..."
curl -s -X POST "$BASE_URL/api/recommendations/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recovery_preference": "conservative", "days_back": 7}' | jq '.'

# Test 4: Aggressive Recommendation
echo -e "\n5. Testing Aggressive Recommendation..."
curl -s -X POST "$BASE_URL/api/recommendations/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recovery_preference": "aggressive", "days_back": 3}' | jq '.'

echo -e "\n🎯 Recommendation Engine Tests Complete!"
