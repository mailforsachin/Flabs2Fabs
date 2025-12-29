from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.schemas import WorkoutCreate, WorkoutResponse
from app.models import Workout, WorkoutExercise, Exercise
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/workouts", tags=["workouts"])

@router.get("/", response_model=List[WorkoutResponse])
def get_workouts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return workouts

@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@router.post("/", response_model=WorkoutResponse)
def create_workout(
    workout: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Validate all exercises exist
    for ex in workout.exercises:
        exercise = db.query(Exercise).filter(
            Exercise.id == ex.exercise_id,
            Exercise.is_active == True
        ).first()
        if not exercise:
            raise HTTPException(status_code=400, detail=f"Exercise with id {ex.exercise_id} not found")
    
    # Create workout
    db_workout = Workout(
        user_id=current_user.id,
        name=workout.name,
        notes=workout.notes
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    
    # Add exercises to workout
    total_calories = 0
    for ex in workout.exercises:
        workout_exercise = WorkoutExercise(
            workout_id=db_workout.id,
            exercise_id=ex.exercise_id,
            sets=ex.sets,
            reps=ex.reps,
            weight_kg=ex.weight_kg,
            duration_minutes=ex.duration_minutes,
            distance_km=ex.distance_km,
            calories=ex.calories
        )
        db.add(workout_exercise)
        
        if ex.calories:
            total_calories += ex.calories
    
    # Update workout totals
    db_workout.calories_burned = total_calories
    db.commit()
    db.refresh(db_workout)
    
    return db_workout

@router.post("/{workout_id}/complete")
def complete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    if workout.end_time:
        raise HTTPException(status_code=400, detail="Workout already completed")
    
    # Use timezone-aware datetime
    workout.end_time = datetime.now(timezone.utc)
    
    # Calculate duration if start_time exists
    if workout.start_time:
        # Ensure both datetimes are timezone-aware
        if workout.start_time.tzinfo is None:
            # Make start_time timezone-aware (assuming UTC)
            start_time_aware = workout.start_time.replace(tzinfo=timezone.utc)
        else:
            start_time_aware = workout.start_time
        
        # Calculate duration in minutes
        duration = (workout.end_time - start_time_aware).total_seconds() / 60
        workout.total_duration_minutes = round(duration, 2)
    
    db.commit()
    return {"status": "workout_completed", "workout_id": workout_id}
