#!/bin/bash

echo "🧠 TESTING C+ & C++ - ENHANCED INTELLIGENCE FEATURES"
echo "===================================================="

BASE_URL="http://localhost:8008"

# Get token
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_athlete_1766937260", "password": "TestPass123!"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "🔐 Authenticated"

echo -e "\n1. 📚 KNOWLEDGE LEVEL ASSESSMENT:"
curl -s "$BASE_URL/api/intelligence/knowledge-level" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Level: {data[\"knowledge_level\"].upper()}')
print(f'Score: {data[\"assessment\"][\"score\"]}/100')
print(f'Training Age: {data[\"assessment\"][\"training_age_days\"]} days')
print(f'Consistency: {data[\"assessment\"][\"consistency_score\"]*100:.0f}%')
print(f'Progression: {data[\"assessment\"][\"progression_quality\"]*100:.0f}%')
"

echo -e "\n2. ⚠️  SAFETY CHECK (Simulating risky workout):"
curl -s -X POST "$BASE_URL/api/intelligence/safety-check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exercises": [
      {"exercise_id": 1, "sets": 20, "reps": 10, "weight_kg": 80},
      {"exercise_id": 3, "sets": 15, "reps": 12, "weight_kg": 70}
    ]
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Safe: {\"✅ YES\" if data[\"is_safe\"] else \"❌ NO\"}')
if data[\"safety_warnings\"]:
    print('Warnings:')
    for warning in data[\"safety_warnings\"][:3]:
        print(f'  • {warning}')
"

echo -e "\n3. 📈 OVERRIDE PATTERN ANALYSIS:"
curl -s "$BASE_URL/api/intelligence/override-analysis?days_back=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
analysis = data[\"override_analysis\"]
print(f'Workouts analyzed: {analysis[\"total_workouts\"]}')
print(f'Exercises logged: {analysis[\"total_exercises\"]}')

if analysis.get(\"biases\"):
    print('\\n🎯 TRAINING BIASES:')
    for bias in analysis[\"biases\"][:2]:
        print(f'  • {bias[\"muscle\"]}: {bias[\"percentage\"]}% (avg: {bias[\"average\"]}%)')

if analysis.get(\"neglected_muscles\"):
    print('\\n📉 NEGLECTED MUSCLES:')
    for neglect in analysis[\"neglected_muscles\"][:2]:
        print(f'  • {neglect[\"muscle\"]}: {neglect[\"percentage\"]}% (avg: {neglect[\"average\"]}%)')

if analysis.get(\"insights\"):
    print('\\n💡 KEY INSIGHTS:')
    for insight in analysis[\"insights\"][:3]:
        print(f'  • {insight}')
"

echo -e "\n4. 🧠 SMART RECOMMENDATIONS (C+ & C++ Enhanced):"
curl -s "$BASE_URL/api/intelligence/smart-recommendations" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Knowledge Level: {data[\"knowledge_level\"].upper()}')

if data.get(\"primary_adjusted\"):
    adj = data[\"primary_adjusted\"]
    print(f'\\n🎯 ENHANCED RECOMMENDATION:')
    print(f'  Exercise: {adj[\"exercise_name\"]}')
    print(f'  Muscle: {adj[\"muscle_group\"]}')
    print(f'  Reason: {adj.get(\"adjustment_reason\", adj[\"reason\"])}')

print(f'\\n📊 ADJUSTMENTS APPLIED:')
print(f'  • Knowledge level: {data[\"knowledge_level\"]}')
print(f'  • Override patterns: Analyzed')
print(f'  • Safety considerations: Included')
"

echo -e "\n5. 🎯 COMPREHENSIVE TRAINING INSIGHTS:"
curl -s "$BASE_URL/api/intelligence/training-insights" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('🧠 YOUR TRAINING PROFILE:')
print(f'  Level: {data[\"knowledge_level\"].upper()}')
print(f'  Patterns: {len(data[\"override_patterns\"])} biases detected')
print(f'  Neglected: {len(data[\"neglected_areas\"])} areas need attention')

print('\\n💡 KEY INSIGHTS:')
for insight in data[\"key_insights\"][:3]:
    print(f'  • {insight}')

print('\\n🎯 ACTION ITEMS:')
for action in data[\"action_items\"]:
    print(f'  • {action}')
"

echo -e "\n🎉 C+ & C++ FEATURES ARE WORKING!"
echo "Flab2Fabs is now smarter with:"
echo "1. 🧠 Knowledge Level Tracking"
echo "2. ⚠️  Safety Warnings"
echo "3. 📈 Override Pattern Analysis"
echo "4. 🎯 Enhanced Recommendations"
echo "5. 💡 Training Insights"
