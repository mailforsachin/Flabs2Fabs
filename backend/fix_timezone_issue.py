import sys
sys.path.append('.')
from app.database import SessionLocal
from app.models import Workout
from datetime import datetime, timezone

db = SessionLocal()

# Fix workout timestamps to be timezone-aware UTC
workouts = db.query(Workout).all()
fixed = 0

for workout in workouts:
    # Fix start_time
    if workout.start_time and workout.start_time.tzinfo is None:
        workout.start_time = workout.start_time.replace(tzinfo=timezone.utc)
        fixed += 1
    
    # Fix end_time  
    if workout.end_time and workout.end_time.tzinfo is None:
        workout.end_time = workout.end_time.replace(tzinfo=timezone.utc)
        fixed += 1

if fixed > 0:
    db.commit()
    print(f"✅ Fixed timezone for {fixed} workout timestamps")
else:
    print("✅ All timestamps already have timezone info")

db.close()
