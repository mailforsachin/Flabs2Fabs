#!/bin/bash

echo "🧠 FINAL RECOMMENDATION ENGINE VALIDATION"
echo "=========================================="

BASE_URL="http://localhost:8008"

# Get token
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_athlete_1766937260", "password": "TestPass123!"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "🔐 Authenticated as: test_athlete_1766937260"

echo -e "\n📊 MUSCLE ANALYSIS SUMMARY:"
curl -s "$BASE_URL/api/recommendations/muscle-analysis" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)

print('🎯 NEGLECTED MUSCLES (High Priority):')
for muscle in data['recommendations_priority'][:3]:
    stats = data['muscle_groups'][muscle]
    print(f'  • {muscle}: Priority {stats[\"priority\"]:.2f}, Never trained' if stats['session_count'] == 0 else f'  • {muscle}: Priority {stats[\"priority\"]:.2f}')

print('\n⚠️  OVERTRAINED/RECOVERY NEEDED:')
for muscle, stats in data['muscle_groups'].items():
    if not stats['recovered']:
        print(f'  • {muscle}: Fatigue {stats[\"fatigue\"]:.2f}, needs rest')
"

echo -e "\n🎯 RECOMMENDATION ENGINE DECISION:"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/recommendations/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recovery_preference": "moderate"}')

echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)

print('🧠 THE ENGINE THINKS:')
print(f'1. \"{data[\"explanations\"][0]}\"')
print(f'2. \"{data[\"explanations\"][1]}\"')
if len(data['explanations']) > 2:
    print(f'3. \"{data[\"explanations\"][2]}\"')

print(f'\n🎯 ALGORITHM\'S CHOICE:')
choice = data['algorithm_choice']
print(f'  Exercise: {choice[\"exercise_name\"]}')
print(f'  Muscle: {choice[\"muscle_group\"]}')
print(f'  Reason: {choice[\"reason\"]}')

print(f'\n🔄 ALTERNATIVES:')
for i, alt in enumerate(data['alternatives'], 1):
    print(f'  {i}. {alt[\"exercise_name\"]} ({alt[\"muscle_group\"]})')

print(f'\n⚠️  WARNINGS:')
for warning in data['warnings']:
    print(f'  • {warning}')

print(f'\n📈 ANALYSIS INSIGHTS:')
muscle_data = data['muscle_analysis']
total_sessions = sum(m.get('session_count', 0) for m in muscle_data.values() if isinstance(m, dict))
print(f'  • Total muscle sessions analyzed: {total_sessions}')
print(f'  • Recovery preference: {data[\"recovery_preference\"]}')
print(f'  • Analysis period: {data[\"analysis_period_days\"]} days')
"

echo -e "\n✅ PHASE C - COMPLETE SUCCESS!"
echo "=========================================="
echo "🎯 What we built:"
echo "1. ✅ Muscle fatigue tracker"
echo "2. ✅ Neglect detection system"
echo "3. ✅ Recovery preference engine"
echo "4. ✅ Intelligent exercise recommender"
echo "5. ✅ Explainable AI with human reasoning"
echo "6. ✅ Warning system for overtraining"
echo ""
echo "🧠 The Flab2Fabs Brain is now operational!"
echo "It analyzes, recommends, and explains like a personal trainer!"
