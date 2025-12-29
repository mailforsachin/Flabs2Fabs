#!/bin/bash

echo "💔 PHASE D - PROGRESS PROJECTIONS & EMOTIONAL INSIGHTS"
echo "====================================================="

BASE_URL="http://localhost:8008"

# Get token
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_athlete_1766937260", "password": "TestPass123!"}' | \
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

echo "🔐 Authenticated"

echo -e "\n1. 📈 STRENGTH PROJECTIONS (What could have been):"
RESPONSE=$(curl -s "$BASE_URL/api/progress/strength-projections?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response from server"
else
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'projections' in data:
        projections = data['projections']
        
        # Safely extract data with defaults
        knowledge_level = projections.get('knowledge_level', 'NOVICE').upper()
        progression_rate = projections.get('base_progression_rate_kg_week', 0)
        
        print(f'Knowledge Level: {knowledge_level}')
        print(f'Progression Rate: {progression_rate}kg/week')
        
        # Emotional impact with safe access
        emotional = projections.get('emotional_impact', {})
        total_missed = emotional.get('total_missed_kg', 0)
        avg_opportunity = emotional.get('average_opportunity', 0)
        
        print(f'\n💔 EMOTIONAL IMPACT:')
        
        if total_missed == 0:
            print('Strength gains unavailable due to limited history.')
            print('Biggest opportunity: consistency and skill acquisition.')
        else:
            print(f'Total Missed Strength: {total_missed:.1f}kg')
            print(f'Average Opportunity: {avg_opportunity*100:.0f}%')
        
        # Motivation messages
        motivation_msgs = emotional.get('motivation_messages', [])
        if motivation_msgs:
            print(f'\n💡 MOTIVATION MESSAGES:')
            for msg in motivation_msgs[:2]:
                print(f' • {msg}')
        
        # Summary with safe access
        summary = projections.get('summary', {})
        overall_verdict = summary.get('overall_verdict', 'No verdict available')
        print(f'\n🎯 SUMMARY: {overall_verdict}')
        
        most_opp = summary.get('most_opportunity_exercise', {})
        if most_opp and most_opp.get('name'):
            print(f'Focus Area: {most_opp[\"name\"]} ({most_opp.get(\"missed_kg\", 0)}kg potential)')
            
    else:
        print('⚠️ No projections data available')
        print(f'Response: {data}')
        
except json.JSONDecodeError:
    print('❌ Invalid JSON response')
except Exception as e:
    print(f'❌ Error processing response: {e}')
"
fi

echo -e "\n2. 📅 CONSISTENCY PROJECTIONS:"
RESPONSE=$(curl -s "$BASE_URL/api/progress/consistency-projections?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'projections' in data:
        proj = data['projections']
        actual = proj.get('actual_workouts', 0)
        projected = proj.get('projected_workouts', 0)
        
        print(f'Actual: {actual} workouts ({actual/4 if actual>0 else 0:.1f}/week)')
        print(f'Projected: {projected} workouts ({projected/4:.1f}/week)')
        
        if projected > actual:
            print(f'📉 GAP ANALYSIS:')
            print(f'Missed Workouts: {projected - actual}')
            consistency_gap = ((projected - actual) / projected * 100) if projected > 0 else 0
            print(f'Consistency Gap: {consistency_gap:.0f}%')
        
        # Streaks
        print(f'\n🔥 STREAKS:')
        print(f'Best: {proj.get(\"best_streak_days\", 0)} days')
        print(f'Current: {proj.get(\"current_streak_days\", 0)} days')
        print(f'Projected Possible: {proj.get(\"projected_streak_days\", 0)} days')
    else:
        print('⚠️ No consistency data available')
except json.JSONDecodeError:
    print('❌ Invalid JSON')
except Exception as e:
    print(f'❌ Error: {e}')
"
fi

echo -e "\n3. 💔 MISSED OPPORTUNITIES (The Pain Point):"
RESPONSE=$(curl -s "$BASE_URL/api/progress/missed-opportunities?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    
    print('❌ WHAT YOU MISSED:')
    
    # Strength
    strength_missed = data.get('strength_missed_kg', 0)
    if strength_missed == 0:
        print('Strength: Limited data for accurate projection')
    else:
        print(f'Strength: {strength_missed}kg')
    
    # Workouts
    workouts_missed = data.get('workouts_missed', 0)
    print(f'Workouts: {workouts_missed} sessions')
    
    # Financial (if applicable)
    financial = data.get('financial_opportunity_cost', 0)
    if financial > 0:
        print(f'Financial Waste: ${financial:.1f}')
    
    # Emotional impact
    emotional = data.get('emotional_impact', {})
    if emotional:
        print(f'\n😔 EMOTIONAL IMPACT:')
        feelings = emotional.get('feelings', [])
        for feeling in feelings[:2]:
            print(f' • {feeling}')
    
    # Recovery plan
    recovery = data.get('recovery_plan', {})
    if recovery:
        print(f'\n🔄 RECOVERY PLAN:')
        time_to_recover = recovery.get('time_to_recover_days', 0)
        if time_to_recover > 0:
            print(f'Time to recover: {time_to_recover} days')
        
        first_step = recovery.get('first_step', '')
        if first_step:
            print(f'First step: \"{first_step}\"')
            
except json.JSONDecodeError:
    print('❌ Invalid JSON')
except Exception as e:
    print(f'❌ Error: {e}')
"
fi

echo -e "\n4. 🎯 COMPREHENSIVE PROGRESS REPORT:"
RESPONSE=$(curl -s "$BASE_URL/api/progress/comprehensive-report?days_back=30" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    
    # Overall score
    overall_score = data.get('overall_progress_score', 0)
    print(f'📊 OVERALL PROGRESS SCORE: {overall_score}/100')
    
    # Emotional state
    emotional = data.get('emotional_state', {})
    if emotional:
        print(f'\n🎯 EMOTIONAL STATE:')
        opportunity_msg = emotional.get('opportunity_message', '')
        if opportunity_msg:
            print(f'Opportunity Message: {opportunity_msg}')
        
        quote = emotional.get('motivational_quote', '')
        if quote:
            print(f'Quote: \"{quote}\"')
    
    # Top insights
    insights = data.get('top_insights', [])
    if insights:
        print(f'\n💡 TOP INSIGHTS:')
        for insight in insights[:3]:
            priority = insight.get('priority', 'MEDIUM')
            message = insight.get('message', '')
            action = insight.get('action', '')
            
            if message and action:
                print(f'{priority}: {message}')
                print(f'Action: {action}')
                print()
    
    # 30-day potential
    potential = data.get('thirty_day_potential', {})
    if potential:
        print(f'\n🚀 NEXT 30 DAY POTENTIAL:')
        strength_gain = potential.get('strength_gain_kg', 0)
        if strength_gain > 0:
            print(f'Strength: +{strength_gain}kg')
        
        workout_gain = potential.get('workout_gain', 0)
        if workout_gain > 0:
            print(f'Workouts: +{workout_gain} sessions')
        
        # Action items
        actions = potential.get('action_items', [])
        for action in actions[:2]:
            print(f' • {action}')
            
except json.JSONDecodeError:
    print('❌ Invalid JSON')
except Exception as e:
    print(f'❌ Error: {e}')
"
fi

echo -e "\n5. 💪 MOTIVATIONAL INSIGHTS (For Today):"
RESPONSE=$(curl -s "$BASE_URL/api/progress/motivational-insights" \
  -H "Authorization: Bearer $TOKEN")

if [ -z "$RESPONSE" ]; then
    echo "⚠️ Empty response"
else
    echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    
    # Emotional summary
    emotional = data.get('emotional_summary', {})
    if emotional:
        print('💖 DAILY MOTIVATION:')
        print(f'Message: {emotional.get(\"opportunity_message\", \"Start strong today!\")}')
        print(f'Quote: {emotional.get(\"motivational_quote\", \"You've got this!\")}')
    
    # Motivational messages
    messages = data.get('motivational_messages', [])
    if messages:
        print(f'\n🎯 TODAY\"S REMINDERS:')
        for msg in messages[:3]:
            print(f' • {msg}')
    
    # Training personality
    personality = data.get('training_personality', '')
    if personality:
        print(f'\n🧠 YOUR TRAINING STYLE: {personality}')
    
    # Today's focus
    focus = data.get('today_focus', '')
    if focus:
        print(f'\n🎯 TODAY\"S FOCUS: {focus}')
    
    # Milestones
    milestones = data.get('progress_milestones', [])
    if milestones:
        print(f'\n🏆 UPCOMING MILESTONES:')
        for milestone in milestones[:2]:
            name = milestone.get('milestone', '')
            progress = milestone.get('progress', '')
            if name and progress:
                print(f' • {name} ({progress})')
    
except json.JSONDecodeError:
    print('❌ Invalid JSON response')
    print(f'Raw response: {RESPONSE[:100]}...')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
fi

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
