#!/usr/bin/env python3
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.recommendation import ExerciseRecommender

db = SessionLocal()

# Test with user ID 4 (test_athlete)
try:
    print("Testing recommendation engine...")
    recommender = ExerciseRecommender(db, 4)
    result = recommender.generate_recommendation()
    print("✅ Recommendation generated successfully!")
    print(f"User: {result['username']}")
    if result['algorithm_choice']:
        print(f"Primary: {result['algorithm_choice']['exercise_name']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Explanations: {result['explanations']}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
