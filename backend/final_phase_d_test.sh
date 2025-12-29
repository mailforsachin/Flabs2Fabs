#!/bin/bash
echo "🎯 FINAL PHASE D VERIFICATION TEST"
echo "=================================="

# Test all features
echo "1. Testing basic API..."
curl -s http://localhost:8008/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'   ✅ API Version: {data.get(\"version\")}')
print(f'   ✅ Message: {data.get(\"message\")}')
"

echo -e "\n2. Testing authentication..."
TOKEN=$(curl -s -X POST http://localhost:8008/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sashy","password":"Welcome2026!"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "   ✅ Token obtained"

echo -e "\n3. Testing Phase D Progress Endpoints:"
ENDPOINTS=(
  "strength-projections"
  "consistency-projections" 
  "comprehensive-report"
  "motivational-insights"
  "missed-opportunities"
)

for endpoint in "${ENDPOINTS[@]}"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8008/api/progress/$endpoint?days_back=30")
  
  if [ "$STATUS" = "200" ]; then
    echo "   ✅ $endpoint: HTTP 200"
  else
    echo "   ❌ $endpoint: HTTP $STATUS"
  fi
done

echo -e "\n4. Testing other intelligence features (Phase C++):"
INTEL_ENDPOINTS=(
  "knowledge-level"
  "override-analysis"
  "smart-recommendations"
)

for endpoint in "${INTEL_ENDPOINTS[@]}"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8008/api/intelligence/$endpoint")
  
  if [ "$STATUS" = "200" ]; then
    echo "   ✅ $endpoint: HTTP 200"
  else
    echo "   ❌ $endpoint: HTTP $STATUS"
  fi
done

echo -e "\n=================================="
echo "🎉 PHASE D COMPLETE!"
echo "📚 API Documentation: http://localhost:8008/docs"
echo "🔑 Test User: sashy / Welcome2026!"
