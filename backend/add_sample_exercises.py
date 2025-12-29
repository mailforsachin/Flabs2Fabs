import sys
sys.path.append('.')
from app.database import SessionLocal
from app.models import Exercise
from app.recommendation import MuscleTracker

db = SessionLocal()

exercises_data = [
    # Chest
    {"name": "Barbell Bench Press", "muscle_group": "Chest", "exercise_type": "strength"},
    {"name": "Dumbbell Flyes", "muscle_group": "Chest", "exercise_type": "strength"},
    {"name": "Push-ups", "muscle_group": "Chest", "exercise_type": "strength"},
    {"name": "Incline Bench Press", "muscle_group": "Upper Chest", "exercise_type": "strength"},
    
    # Back
    {"name": "Pull-ups", "muscle_group": "Back", "exercise_type": "strength"},
    {"name": "Barbell Rows", "muscle_group": "Back", "exercise_type": "strength"},
    {"name": "Lat Pulldowns", "muscle_group": "Back", "exercise_type": "strength"},
    {"name": "Deadlifts", "muscle_group": "Back", "exercise_type": "strength"},
    
    # Legs
    {"name": "Barbell Squats", "muscle_group": "Legs", "exercise_type": "strength"},
    {"name": "Leg Press", "muscle_group": "Legs", "exercise_type": "strength"},
    {"name": "Lunges", "muscle_group": "Legs", "exercise_type": "strength"},
    {"name": "Calf Raises", "muscle_group": "Calves", "exercise_type": "strength"},
    
    # Shoulders
    {"name": "Overhead Press", "muscle_group": "Shoulders", "exercise_type": "strength"},
    {"name": "Lateral Raises", "muscle_group": "Shoulders", "exercise_type": "strength"},
    {"name": "Front Raises", "muscle_group": "Shoulders", "exercise_type": "strength"},
    
    # Arms
    {"name": "Bicep Curls", "muscle_group": "Biceps", "exercise_type": "strength"},
    {"name": "Tricep Extensions", "muscle_group": "Triceps", "exercise_type": "strength"},
    {"name": "Hammer Curls", "muscle_group": "Biceps", "exercise_type": "strength"},
    
    # Core
    {"name": "Plank", "muscle_group": "Core", "exercise_type": "strength"},
    {"name": "Russian Twists", "muscle_group": "Core", "exercise_type": "strength"},
    {"name": "Leg Raises", "muscle_group": "Core", "exercise_type": "strength"},
    
    # Cardio
    {"name": "Running", "muscle_group": "Cardio", "exercise_type": "cardio"},
    {"name": "Cycling", "muscle_group": "Cardio", "exercise_type": "cardio"},
    {"name": "Jump Rope", "muscle_group": "Cardio", "exercise_type": "cardio"},
]

for ex_data in exercises_data:
    # Check if exercise already exists
    existing = db.query(Exercise).filter(Exercise.name == ex_data["name"]).first()
    if not existing:
        exercise = Exercise(
            name=ex_data["name"],
            description=f"Standard {ex_data['muscle_group'].lower()} exercise",
            exercise_type=ex_data["exercise_type"],
            muscle_group=ex_data["muscle_group"],
            equipment_required="Various",
            created_by_admin_id=1,
            is_active=True
        )
        db.add(exercise)

db.commit()
print(f"Added/updated {len(exercises_data)} exercises")
db.close()
