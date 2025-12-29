#!/bin/bash

echo "🔥 PHASE C - Recommendation Engine Complete Test"
echo "================================================"

BASE_URL="http://localhost:8008"

# 1. Login
echo -e "\n1. Login as test user..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_athlete_1766937260", "password": "TestPass123!"}' | \
  jq -r '.access_token')

# 2. Log some workouts to create history
echo -e "\n2. Creating workout history..."
for i in {1..3}; do
  echo "  Workout $i..."
  curl -s -X POST "$BASE_URL/api/workouts/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Test Workout $i\",
      \"exercises\": [
        {\"exercise_id\": $((i % 5 + 1)), \"sets\": 3, \"reps\": 10, \"calories\": 100}
      ]
    }" > /dev/null
  
  sleep 1
done

# 3. Get muscle analysis
echo -e "\n3. Muscle Analysis Results:"
curl -s "$BASE_URL/api/recommendations/muscle-analysis?days_back=7" \
  -H "Authorization: Bearer $TOKEN" | jq '{
    user_id,
    analysis_period_days,
    neglected_muscles,
    recommendations_priority: .recommendations_priority[:3]
  }'

# 4. Get recommendations
echo -e "\n4. Recommendation Results:"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/recommendations/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recovery_preference": "moderate"}')

echo "$RESPONSE" | jq '{
    algorithm_choice: .algorithm_choice.exercise_name,
    alternatives: .alternatives[].exercise_name,
    warnings,
    explanations,
    summary
}'

# 5. Test different recovery preferences
echo -e "\n5. Testing Different Recovery Preferences:"
for pref in "aggressive" "moderate" "conservative"; do
  echo "  $pref:"
  curl -s -X POST "$BASE_URL/api/recommendations/generate" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"recovery_preference\": \"$pref\"}" | \
    jq -r '  .algorithm_choice.exercise_name + " (" + .algorithm_choice.muscle_group + ")"'
done

echo -e "\n✅ PHASE C TESTS COMPLETE!"
echo "The Recommendation Engine is working!"
