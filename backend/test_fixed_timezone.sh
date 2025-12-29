#!/bin/bash

echo "🧪 TESTING FIXED TIMEZONE CALCULATIONS"
echo "======================================"

BASE_URL="http://localhost:8008"

# Get token
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_athlete_1766937260", "password": "TestPass123!"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "🔐 Token obtained"

# Test muscle analysis
echo -e "\n📊 MUSCLE ANALYSIS (Checking for negative hours):"
RESPONSE=$(curl -s "$BASE_URL/api/recommendations/muscle-analysis" \
  -H "Authorization: Bearer $TOKEN")

echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)

print('Muscle Group | Sessions | Hours Ago | Recovered')
print('------------|----------|-----------|-----------')
negative_found = False

for muscle, stats in data['muscle_groups'].items():
    hours = stats.get('last_trained_hours_ago')
    if hours is not None:
        if hours < 0:
            negative_found = True
            print(f'{muscle:11} | {stats[\"session_count\"]:8} | {hours:9.2f} ⚠️ NEGATIVE! | {stats[\"recovered\"]}')
        else:
            print(f'{muscle:11} | {stats[\"session_count\"]:8} | {hours:9.2f} | {stats[\"recovered\"]}')
    else:
        print(f'{muscle:11} | {stats[\"session_count\"]:8} | Never      | {stats[\"recovered\"]}')

if negative_found:
    print('\n❌ STILL HAVE NEGATIVE HOURS ISSUE!')
else:
    print('\n✅ ALL HOURS ARE POSITIVE! FIX WORKED!')
"

# Test recommendation
echo -e "\n🎯 RECOMMENDATION ENGINE TEST:"
curl -s -X POST "$BASE_URL/api/recommendations/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recovery_preference": "moderate"}' | python3 -c "
import sys, json
data = json.load(sys.stdin)

print('Engine Decision:')
if data.get('algorithm_choice'):
    choice = data['algorithm_choice']
    print(f'  🎯 {choice[\"exercise_name\"]} ({choice[\"muscle_group\"]})')
    print(f'  📝 {choice[\"reason\"]}')

print(f'\nAnalysis Summary:')
print(f'  📅 Period: {data[\"analysis_period_days\"]} days')
print(f'  ⚖️ Recovery: {data[\"recovery_preference\"]}')

# Check muscle data
print(f'\nMuscle State:')
for muscle, stats in data['muscle_analysis'].items():
    hours = stats.get('last_trained_hours_ago')
    if hours is not None:
        status = '✅ OK' if hours >= 0 else '❌ NEGATIVE'
        print(f'  {muscle:10}: {hours:6.1f}h ago {status}')
"
