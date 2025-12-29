from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta
import random

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Workout

router = APIRouter()

@router.get("/strength-projections-simple")
async def get_strength_projections_simple(
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Simple strength projections without complex dependencies"""
    try:
        # Get workout count
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        workout_count = db.query(Workout).filter(
            Workout.user_id == current_user["id"],
            Workout.start_time >= start_date,
            Workout.start_time <= end_date
        ).count()
        
        # Simple projection logic
        if workout_count == 0:
            knowledge_level = "novice"
            missed_kg = 12.5  # Estimated novice gains in 30 days
            message = "Start training to unlock newbie gains!"
        elif workout_count < 4:
            knowledge_level = "beginner"
            missed_kg = workout_count * 2.5
            message = f"You've started! {4-workout_count} more workouts for better insights."
        else:
            knowledge_level = "intermediate"
            missed_kg = max(0, 12.5 - (workout_count * 2))
            message = f"Good consistency! {workout_count} workouts completed."
        
        return {
            "user_id": current_user["id"],
            "projections": {
                "knowledge_level": knowledge_level,
                "base_progression_rate_kg_week": 1.0,
                "emotional_impact": {
                    "total_missed_kg": missed_kg,
                    "average_opportunity": 0.5,
                    "motivation_messages": [
                        message,
                        "Consistency is key for strength gains!",
                        "Every workout makes you stronger!"
                    ]
                },
                "summary": {
                    "overall_verdict": "Good progress with room for improvement",
                    "most_opportunity_exercise": {
                        "name": "Compound lifts",
                        "missed_kg": missed_kg
                    }
                }
            },
            "workouts_analyzed": workout_count,
            "period_days": days_back
        }
        
    except Exception as e:
        return {
            "user_id": current_user["id"],
            "error": str(e),
            "projections": {
                "knowledge_level": "novice",
                "base_progression_rate_kg_week": 0.0,
                "emotional_impact": {
                    "total_missed_kg": 0.0,
                    "average_opportunity": 0.0,
                    "motivation_messages": ["Complete a workout to see projections"]
                }
            }
        }

@router.get("/consistency-projections-simple")
async def get_consistency_projections_simple(
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Simple consistency projections"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        workouts = db.query(Workout).filter(
            Workout.user_id == current_user["id"],
            Workout.start_time >= start_date,
            Workout.start_time <= end_date
        ).all()
        
        actual = len(workouts)
        projected = int((days_back / 7) * 3)  # 3 workouts/week target
        
        return {
            "user_id": current_user["id"],
            "projections": {
                "actual_workouts": actual,
                "projected_workouts": projected,
                "missed_workouts": max(0, projected - actual),
                "consistency_score": min(100, (actual / projected * 100) if projected > 0 else 0),
                "current_streak_days": 1 if actual > 0 else 0,
                "best_streak_days": 1 if actual > 0 else 0,
                "projected_streak_days": 7 if actual > 0 else 0
            },
            "period_days": days_back
        }
        
    except Exception as e:
        return {
            "user_id": current_user["id"],
            "error": str(e),
            "projections": {
                "actual_workouts": 0,
                "projected_workouts": 0,
                "missed_workouts": 0,
                "consistency_score": 0
            }
        }
