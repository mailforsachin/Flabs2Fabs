from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import random
import math

from app.database import get_db
from app.dependencies import get_current_user
from app.progress_projections import ProgressProjector

# ADD THE PREFIX HERE
router = APIRouter(prefix="/api/progress", tags=["progress"])

@router.get("/strength-projections")
async def get_strength_projections(
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Calculate what strength gains COULD have been achieved"""
    try:
        projector = ProgressProjector(db, current_user["id"])
        return projector.get_strength_projections(days_back)
    except Exception as e:
        print(f"Error in strength projections: {e}")
        return {
            "user_id": current_user["id"],
            "projections": {
                "knowledge_level": "novice",
                "base_progression_rate_kg_week": 0.0,
                "emotional_impact": {
                    "total_missed_kg": 0.0,
                    "average_opportunity": 0.0,
                    "motivation_messages": [
                        "Limited data available for accurate projections",
                        "Focus on consistency first, strength gains will follow"
                    ]
                },
                "summary": {
                    "overall_verdict": "Build training history for personalized insights",
                    "most_opportunity_exercise": {
                        "name": "Not enough data",
                        "missed_kg": 0.0
                    }
                }
            },
            "data_quality": "low",
            "note": "Complete more workouts for accurate projections"
        }

@router.get("/consistency-projections")
async def get_consistency_projections(
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Calculate consistency metrics and projections"""
    try:
        projector = ProgressProjector(db, current_user["id"])
        return projector.get_consistency_projections(days_back)
    except Exception as e:
        print(f"Error in consistency projections: {e}")
        return {
            "user_id": current_user["id"],
            "projections": {
                "current_consistency": "low",
                "projected_consistency": "medium",
                "missed_opportunities": 0,
                "recommendations": [
                    "Aim for at least 3 workouts per week",
                    "Try to maintain a consistent schedule"
                ]
            },
            "data_quality": "low"
        }

@router.get("/comprehensive-report")
async def get_comprehensive_report(
    days_back: int = 90,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a comprehensive progress report"""
    try:
        projector = ProgressProjector(db, current_user["id"])
        return projector.get_comprehensive_report(days_back)
    except Exception as e:
        print(f"Error in comprehensive report: {e}")
        return {
            "user_id": current_user["id"],
            "report": {
                "summary": "Limited data available",
                "strength_progress": "insufficient_data",
                "consistency_progress": "insufficient_data",
                "knowledge_level": "novice"
            },
            "data_quality": "low"
        }

@router.get("/motivational-insights")
async def get_motivational_insights(
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get motivational insights based on progress"""
    try:
        projector = ProgressProjector(db, current_user["id"])
        return projector.get_motivational_insights(days_back)
    except Exception as e:
        print(f"Error in motivational insights: {e}")
        return {
            "user_id": current_user["id"],
            "insights": [
                "Every journey starts with a single step",
                "Consistency is more important than intensity"
            ],
            "quote": "The best time to start was yesterday. The second best time is now."
        }

@router.get("/missed-opportunities")
async def get_missed_opportunities(
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze missed workout opportunities"""
    try:
        projector = ProgressProjector(db, current_user["id"])
        return projector.get_missed_opportunities(days_back)
    except Exception as e:
        print(f"Error in missed opportunities: {e}")
        return {
            "user_id": current_user["id"],
            "missed_opportunities": [],
            "total_potential_gain": "0%",
            "recommendation": "Start tracking workouts to see potential gains"
        }
