#!/bin/bash

echo "💔 PHASE D - PROGRESS PROJECTIONS & EMOTIONAL INSIGHTS"
echo "====================================================="

BASE_URL="http://localhost:8008"

# Get token
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_athlete_1766937260", "password": "TestPass123!"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "🔐 Authenticated"

echo -e "\n1. 📈 STRENGTH PROJECTIONS (What could have been):"
curl -s "$BASE_URL/api/progress/strength-projections?days_back=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
projections = data[\"projections\"]

print(f'Knowledge Level: {projections[\"knowledge_level\"].upper()}')
print(f'Progression Rate: {projections[\"base_progression_rate_kg_week\"]}kg/week')

emotional = projections[\"emotional_impact\"]
print(f'\\n💔 EMOTIONAL IMPACT:')
print(f'Total Missed Strength: {emotional[\"total_missed_kg\"]:.1f}kg')
print(f'Average Opportunity: {emotional[\"average_opportunity\"]*100:.0f}%')

print(f'\\n💡 MOTIVATION MESSAGES:')
for msg in emotional[\"motivation_messages\"][:2]:
    print(f'  • {msg}')

summary = projections[\"summary\"]
print(f'\\n🎯 SUMMARY: {summary[\"overall_verdict\"]}')
if summary[\"most_opportunity_exercise\"][\"name\"]:
    ex = summary[\"most_opportunity_exercise\"]
    print(f'Focus Area: {ex[\"name\"]} ({ex[\"missed_kg\"]}kg potential)')
"

echo -e "\n2. 📅 CONSISTENCY PROJECTIONS:"
curl -s "$BASE_URL/api/progress/consistency-projections?days_back=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
proj = data[\"projections\"][\"consistency_projection\"]

print(f'Actual: {proj[\"actual\"][\"workouts\"]} workouts ({proj[\"actual\"][\"rate_per_week\"]}/week)')
print(f'Projected: {proj[\"projected\"][\"workouts\"]} workouts ({proj[\"projected\"][\"rate_per_week\"]}/week)')

gap = proj[\"gap_analysis\"]
print(f'\\n📉 GAP ANALYSIS:')
print(f'Missed Workouts: {gap[\"missed_workouts\"]}')
print(f'Consistency Gap: {gap[\"consistency_gap\"]*100:.0f}%')

print(f'\\n🔥 STREAKS:')
print(f'Best: {proj[\"actual\"][\"best_streak\"]} days')
print(f'Current: {proj[\"actual\"][\"current_streak\"]} days')
print(f'Projected Possible: {proj[\"projected\"][\"streak\"]} days')
"

echo -e "\n3. 💔 MISSED OPPORTUNITIES (The Pain Point):"
curl -s "$BASE_URL/api/progress/missed-opportunities?days_back=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
missed = data[\"total_missed_opportunity\"]

print(f'\\n❌ WHAT YOU MISSED:')
print(f'Strength: {missed[\"strength_kg\"]}kg')
print(f'Workouts: {missed[\"workouts\"]} sessions')
print(f'Financial Waste: \${missed[\"estimated_financial_waste\"]}')

print(f'\\n😔 EMOTIONAL IMPACT:')
for impact in data[\"emotional_impact\"]:
    print(f'  • {impact[\"message\"]}')
    print(f'    Feeling: {impact[\"feeling\"]}')

recovery = data[\"recovery_plan\"]
print(f'\\n🔄 RECOVERY PLAN:')
print(f'  Time to recover: {recovery[\"time_to_recover_days\"]} days')
print(f'  First step: \"{recovery[\"first_step\"]}\"')
"

echo -e "\n4. 🎯 COMPREHENSIVE PROGRESS REPORT:"
curl -s "$BASE_URL/api/progress/comprehensive-report?days_back=30" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
report = data[\"report\"]

print(f'\\n📊 OVERALL PROGRESS SCORE: {report[\"overall_progress_score\"]}/100')

emotional = report[\"emotional_summary\"]
print(f'\\n{emotional[\"icon\"]} EMOTIONAL STATE: {emotional[\"mood\"]}')
print(f'Message: {emotional[\"message\"]}')
print(f'Quote: \"{emotional[\"motivational_quote\"]}\"')

print(f'\\n💡 TOP INSIGHTS:')
for insight in report[\"actionable_insights\"][:2]:
    print(f'  {insight[\"priority\"].upper()}: {insight[\"message\"]}')
    print(f'    Action: {insight[\"action\"]}')

potential = report[\"next_30_day_potential\"]
print(f'\\n🚀 NEXT 30 DAY POTENTIAL:')
print(f'  Strength: +{potential[\"strength_potential_kg\"]}kg')
print(f'  Workouts: +{potential[\"consistency_potential_workouts\"]} sessions')
for goal in potential[\"achievable_goals\"][:2]:
    print(f'  • {goal}')
"

echo -e "\n5. 💪 MOTIVATIONAL INSIGHTS (For Today):"
curl -s "$BASE_URL/api/progress/motivational-insights" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)

print(f'\\n{data[\"icon\"]} TODAY\'S MOOD: {data[\"mood\"]}')
print(f'Message: {data[\"main_message\"]}')
print(f'Key Metric: {data[\"key_metric\"]}')
print(f'Quote: \"{data[\"motivational_quote\"]}\"')

print(f'\\n🎯 TODAY\'S FOCUS:')
for insight in data[\"top_insights\"]:
    print(f'  • {insight[\"message\"]}')

print(f'\\n📅 NEXT 30 DAYS:')
print(f'  Call to Action: {data[\"call_to_action\"]}')
print(f'  Potential: +{data[\"next_30_days\"][\"strength_potential_kg\"]}kg strength')
"

echo -e "\n🎉 PHASE D - COMPLETE!"
echo "====================================================="
echo "What we've built:"
echo "1. 💔 'What Could Have Been' Strength Projections"
echo "2. 📅 Consistency Gap Analysis"
echo "3. 😔 Missed Opportunity Pain Points"
echo "4. 🎯 Emotional State Detection"
echo "5. 💪 Motivational Insights Engine"
echo "6. 🚀 30-Day Potential Calculator"
echo ""
echo "Flab2Fabs is now an EMOTIONAL training partner!"
echo "It understands not just what you DID, but what you COULD HAVE DONE!"
