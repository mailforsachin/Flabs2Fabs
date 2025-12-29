"""
🎯 Recommendation Engine Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RecommendationRequest(BaseModel):
    """Request for recommendations"""
    recovery_preference: str = Field(
        default="moderate",
        description="Recovery preference: aggressive, moderate, conservative"
    )
    days_back: Optional[int] = Field(
        default=7,
        description="How many days to look back for analysis"
    )

class ExerciseRecommendation(BaseModel):
    """Individual exercise recommendation"""
    exercise_id: int
    exercise_name: str
    muscle_group: str
    reason: str
    sets_suggestion: Optional[int] = Field(default=3, description="Suggested sets")
    reps_suggestion: Optional[str] = Field(default="8-12", description="Suggested rep range")

class RecommendationResponse(BaseModel):
    """Complete recommendation response"""
    user_id: int
    username: str
    recovery_preference: str
    analysis_period_days: int
    timestamp: str
    
    algorithm_choice: Optional[ExerciseRecommendation]
    alternatives: List[ExerciseRecommendation] = []
    
    warnings: List[str] = []
    explanations: List[str] = []
    
    muscle_analysis: Dict[str, Dict[str, Any]] = Field(
        description="Detailed muscle group analysis"
    )
    
    summary: Optional[str] = Field(
        default=None,
        description="Human-readable summary"
    )

class MuscleAnalysisRequest(BaseModel):
    """Request for muscle analysis only"""
    days_back: Optional[int] = Field(default=7)

class MuscleAnalysisResponse(BaseModel):
    """Detailed muscle analysis response"""
    user_id: int
    analysis_period_days: int
    timestamp: str
    muscle_groups: Dict[str, Dict[str, Any]]
    neglected_muscles: List[str]
    recovery_status: Dict[str, bool]
    recommendations_priority: List[str]
