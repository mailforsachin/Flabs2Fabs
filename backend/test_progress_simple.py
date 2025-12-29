#!/usr/bin/env python3
"""
Test progress endpoints directly without HTTP
"""
import sys
sys.path.append('.')

from app.database import SessionLocal, engine
from app.models import Base, User, Workout, Exercise, WorkoutExercise
from app.routes.progress_simple import get_mock_strength_projections, get_mock_consistency_projections
from datetime import datetime, timedelta
import random

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Get user
    user = db.query(User).filter(User.username == 'sashy').first()
    if not user:
        print("❌ User 'sashy' not found")
        exit(1)
    
    print(f"✅ Testing with user: {user.username} (ID: {user.id})")
    
    # Test the mock functions directly
    print("\n📊 Testing mock strength projections...")
    strength_data = get_mock_strength_projections(user.id, 30, db)
    print(f"✅ Strength projections: {strength_data}")
    
    print("\n📅 Testing mock consistency projections...")
    consistency_data = get_mock_consistency_projections(user.id, 30, db)
    print(f"✅ Consistency projections: {consistency_data}")
    
    # Let's also create some test workouts
    print("\n🏋️ Creating test workouts for more realistic data...")
    
    # Check if exercises exist
    exercises = db.query(Exercise).limit(3).all()
    if not exercises:
        print("⚠️ No exercises found, creating sample exercises...")
        exercises = [
            Exercise(name="Push-ups", muscle_group="chest", difficulty="beginner"),
            Exercise(name="Squats", muscle_group="legs", difficulty="beginner"),
            Exercise(name="Bicep Curls", muscle_group="arms", difficulty="beginner"),
        ]
        for ex in exercises:
            db.add(ex)
        db.commit()
        exercises = db.query(Exercise).limit(3).all()
    
    # Create workouts for last 7 days
    for i in range(7):
        workout_date = datetime.now() - timedelta(days=i)
        workout = Workout(
            user_id=user.id,
            date=workout_date,
            duration_minutes=random.randint(30, 60),
            notes=f"Test workout {i+1}"
        )
        db.add(workout)
        db.flush()  # Get the workout ID
        
        # Add exercises to workout
        for j, exercise in enumerate(exercises[:2]):  # Add 2 exercises per workout
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id,
                sets=random.randint(3, 5),
                reps=random.randint(8, 12),
                weight_kg=random.uniform(20, 50)
            )
            db.add(workout_exercise)
    
    db.commit()
    print(f"✅ Created 7 test workouts with exercises")
    
    # Test projections again with real data
    print("\n📊 Testing strength projections with real data...")
    real_strength = get_mock_strength_projections(user.id, 30, db)
    print(f"✅ Real strength projections: {real_strength}")
    
    print("\n📅 Testing consistency projections with real data...")
    real_consistency = get_mock_consistency_projections(user.id, 30, db)
    print(f"✅ Real consistency projections: {real_consistency}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
