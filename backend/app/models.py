from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Text,
    Enum
)
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.database import Base

# --------------------------------------------------
# TIME HANDLING — SINGLE SOURCE OF TRUTH
# --------------------------------------------------
def utcnow():
    """
    Always return timezone-aware UTC datetime.
    This avoids negative durations and TZ drift bugs.
    """
    return datetime.now(timezone.utc)

# --------------------------------------------------
# USER MODEL
# --------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workouts = relationship(
        "Workout",
        back_populates="user",
        cascade="all, delete-orphan"
    )

# --------------------------------------------------
# EXERCISE TYPES
# --------------------------------------------------
class ExerciseType(str, enum.Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"

# --------------------------------------------------
# EXERCISE MODEL
# --------------------------------------------------
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    exercise_type = Column(Enum(ExerciseType))
    muscle_group = Column(String(100), nullable=True)
    equipment_required = Column(String(100), nullable=True)

    created_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    workout_exercises = relationship(
        "WorkoutExercise",
        back_populates="exercise"
    )

# --------------------------------------------------
# WORKOUT MODEL
# --------------------------------------------------
class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String(100))
    notes = Column(Text, nullable=True)

    # IMPORTANT: No server_default, always UTC from Python
    start_time = Column(DateTime(timezone=True), default=utcnow)
    end_time = Column(DateTime(timezone=True), nullable=True)

    total_duration_minutes = Column(Float, nullable=True)
    calories_burned = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="workouts")
    exercises = relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan"
    )

# --------------------------------------------------
# WORKOUT EXERCISE MODEL
# --------------------------------------------------
class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))

    # Exercise details
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight_kg = Column(Float, nullable=True)

    duration_minutes = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)
    calories = Column(Integer, nullable=True)

    # Relationships
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
