from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import ExerciseCreate, ExerciseResponse
from app.models import Exercise
from app.dependencies import admin_required

router = APIRouter(prefix="/api/exercises", tags=["exercises"])

@router.get("/", response_model=List[ExerciseResponse])
def get_exercises(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    exercises = db.query(Exercise).filter(Exercise.is_active == True).offset(skip).limit(limit).all()
    return exercises

@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id, Exercise.is_active == True).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.post("/", response_model=ExerciseResponse)
def create_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(admin_required)
):
    # Check if exercise already exists
    existing = db.query(Exercise).filter(Exercise.name == exercise.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Exercise already exists")
    
    db_exercise = Exercise(
        name=exercise.name,
        description=exercise.description,
        exercise_type=exercise.exercise_type,
        muscle_group=exercise.muscle_group,
        equipment_required=exercise.equipment_required,
        created_by_admin_id=admin_user.id
    )
    
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(admin_required)
):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    exercise.is_active = False
    db.commit()
    return {"status": "exercise_deleted"}
