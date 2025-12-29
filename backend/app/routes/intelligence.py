"""
🧠 C+ & C++ - Enhanced Intelligence Routes
Knowledge Level + Override Tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.knowledge_level import KnowledgeAssessor
from app.override_tracking import OverrideTracker
from app.recommendation import ExerciseRecommender

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

@router.get("/knowledge-level")
def get_knowledge_level(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's fitness knowledge level assessment
    """
    assessor = KnowledgeAssessor(db, current_user.id)
    level, assessment = assessor.assess_knowledge_level()
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "knowledge_level": level,
        "assessment": assessment,
        "timestamp": assessment.get("timestamp")  # Will be added by assessor
    }

@router.post("/safety-check")
def safety_check_workout(
    planned_workout: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check planned workout for safety issues based on knowledge level
    """
    assessor = KnowledgeAssessor(db, current_user.id)
    warnings = assessor.generate_safety_warnings(planned_workout)
    
    # Also get knowledge level context
    level, assessment = assessor.assess_knowledge_level()
    
    return {
        "user_id": current_user.id,
        "knowledge_level": level,
        "planned_workout": planned_workout,
        "safety_warnings": warnings,
        "safety_thresholds": assessment.get("safety_thresholds", {}),
        "is_safe": len(warnings) == 0,
        "recommendations": assessor.get_level_based_recommendations() if warnings else None
    }

@router.get("/override-analysis")
def get_override_analysis(
    days_back: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze user's override patterns and biases
    """
    tracker = OverrideTracker(db, current_user.id)
    analysis = tracker.analyze_override_patterns(days_back)
    
    return {
        "user_id": current_user.id,
        "analysis_period_days": days_back,
        "override_analysis": analysis
    }

@router.get("/override-report")
def get_override_report(
    days_back: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive override report with recommendations
    """
    tracker = OverrideTracker(db, current_user.id)
    report = tracker.generate_override_report(days_back)
    
    return {
        "user_id": current_user.id,
        "report": report
    }

@router.get("/smart-recommendations")
def get_smart_recommendations(
    recovery_preference: str = "moderate",
    days_back: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recommendations enhanced with knowledge level and override analysis
    """
    # Get base recommendations
    recommender = ExerciseRecommender(db, current_user.id)
    base_result = recommender.generate_recommendation(recovery_preference)
    
    # Get knowledge level context
    assessor = KnowledgeAssessor(db, current_user.id)
    level, assessment = assessor.assess_knowledge_level()
    
    # Get override adjustments
    tracker = OverrideTracker(db, 30)  # 30 days for override analysis
    base_recs = []
    if base_result.get("algorithm_choice"):
        base_recs.append(base_result["algorithm_choice"])
    base_recs.extend(base_result.get("alternatives", []))
    
    adjusted_recs = tracker.get_override_adjusted_recommendations(base_recs)
    
    # Enhance response with intelligence data
    enhanced_result = {
        **base_result,
        "intelligence_enhanced": True,
        "knowledge_level": level,
        "level_based_advice": assessor.get_level_based_recommendations(),
        "original_recommendations": base_recs,
        "adjusted_recommendations": adjusted_recs,
        "primary_adjusted": adjusted_recs[0] if adjusted_recs else None
    }
    
    return enhanced_result

@router.get("/training-insights")
def get_training_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive training insights combining all intelligence modules
    """
    # Knowledge level
    assessor = KnowledgeAssessor(db, current_user.id)
    level, level_assessment = assessor.assess_knowledge_level()
    
    # Override analysis
    tracker = OverrideTracker(db, current_user.id)
    override_analysis = tracker.analyze_override_patterns(90)
    
    # Recommendations
    recommender = ExerciseRecommender(db, current_user.id)
    recommendations = recommender.generate_recommendation()
    
    # Generate insights
    insights = []
    
    # Knowledge level insights
    insights.append(f"You're at {level.value} level with score {level_assessment['score']}/100")
    insights.extend(assessor.get_level_based_recommendations().get("next_level_goals", []))
    
    # Override insights
    insights.extend(override_analysis.get("insights", []))
    
    # Recommendation insights
    if recommendations.get("algorithm_choice"):
        choice = recommendations["algorithm_choice"]
        insights.append(f"Today's focus: {choice['muscle_group']} - {choice['exercise_name']}")
    
    # Warning insights
    insights.extend(recommendations.get("warnings", []))
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "knowledge_level": level.value,
        "level_assessment": level_assessment,
        "override_patterns": override_analysis.get("biases", [])[:3],
        "neglected_areas": override_analysis.get("neglected_muscles", [])[:3],
        "primary_recommendation": recommendations.get("algorithm_choice"),
        "key_insights": insights[:5],  # Top 5 insights
        "action_items": [
            f"Follow {level.value} safety guidelines",
            "Balance your exercise selection",
            "Track progress consistently",
            "Adjust based on recovery"
        ]
    }
