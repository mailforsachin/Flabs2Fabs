"""
🎯 Recommendation Engine Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.recommendation import ExerciseRecommender, WorkoutAnalyzer
from app.schemas_recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    MuscleAnalysisRequest,
    MuscleAnalysisResponse
)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("/muscle-analysis", response_model=MuscleAnalysisResponse)
def get_muscle_analysis(
    days_back: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed muscle group analysis
    """
    analyzer = WorkoutAnalyzer(db, current_user.id, days_back)
    muscle_data = analyzer.analyze_muscle_fatigue()
    neglected = analyzer.get_neglected_muscles(days_back)
    recovery_status = analyzer.get_recovery_status("moderate")
    
    # Sort muscles by priority
    prioritized = sorted(
        [(mg, data["priority_score"]) for mg, data in muscle_data.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    from datetime import datetime, timezone
    return MuscleAnalysisResponse(
        user_id=current_user.id,
        analysis_period_days=days_back,
        timestamp=datetime.now(timezone.utc).isoformat(),
        muscle_groups={
            mg: {
                "priority": data["priority_score"],
                "fatigue": data["fatigue_score"],
                "session_count": data["session_count"],
                "last_trained_hours_ago": data.get("hours_since_last"),
                "recovered": recovery_status.get(mg, True)
            }
            for mg, data in muscle_data.items()
        },
        neglected_muscles=neglected,
        recovery_status=recovery_status,
        recommendations_priority=[mg for mg, _ in prioritized[:5]]
    )

@router.post("/generate", response_model=RecommendationResponse)
def generate_recommendation(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate workout recommendations based on training history
    """
    try:
        recommender = ExerciseRecommender(db, current_user.id)
        result = recommender.generate_recommendation(
            recovery_preference=request.recovery_preference,
            max_recommendations=4
        )
        
        # Add summary
        if result["algorithm_choice"]:
            choice = result["algorithm_choice"]
            result["summary"] = (
                f"Today's focus: {choice['muscle_group']}. "
                f"Recommended: {choice['exercise_name']}. "
            )
            
            if result["warnings"]:
                result["summary"] += f"Note: {result['warnings'][0]}"
        
        return RecommendationResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation generation failed: {str(e)}"
        )

@router.get("/quick")
def quick_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick recommendation (default settings)
    """
    recommender = ExerciseRecommender(db, current_user.id)
    result = recommender.generate_recommendation()
    
    # Simplified response for quick view
    return {
        "user": current_user.username,
        "timestamp": result["timestamp"],
        "primary_recommendation": result.get("algorithm_choice"),
        "warnings": result.get("warnings", []),
        "explanation": result.get("explanations", [])[0] if result.get("explanations") else None
    }
