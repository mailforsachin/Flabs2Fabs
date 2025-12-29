from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Auth schemas - Keep original ones
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AdminCreateUser(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False

class AdminResetPassword(BaseModel):
    user_id: int
    new_password: str

# Exercise schemas
class ExerciseType(str, Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"

class ExerciseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    exercise_type: ExerciseType
    muscle_group: Optional[str] = None
    equipment_required: Optional[str] = None

class ExerciseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    exercise_type: ExerciseType
    muscle_group: Optional[str]
    equipment_required: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Workout schemas
class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_minutes: Optional[float] = None
    distance_km: Optional[float] = None
    calories: Optional[int] = None

class WorkoutCreate(BaseModel):
    name: str
    notes: Optional[str] = None
    exercises: List[WorkoutExerciseCreate]

class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    name: str
    notes: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    total_duration_minutes: Optional[float]
    calories_burned: Optional[int]
    
    class Config:
        from_attributes = True
