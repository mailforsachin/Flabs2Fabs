"""
🎯 Flab2Fabs Recommendation Engine v1
Mental Model: "Given what you've done recently, what is the most responsible thing to train today?"
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models import Workout, WorkoutExercise, Exercise, User

class RecoveryPreference:
    """Recovery preference mapping"""
    MINIMUM_REST_HOURS = {
        "aggressive": 24,    # 1 day
        "moderate": 48,      # 2 days
        "conservative": 72   # 3 days
    }
    
    @classmethod
    def get_min_rest_hours(cls, preference: str) -> int:
        return cls.MINIMUM_REST_HOURS.get(preference.lower(), 48)

class MuscleTracker:
    """Tracks muscle group training history"""
    
    # Muscle group mapping (simplified v1)
    MUSCLE_GROUPS = {
        "Chest": ["chest", "pectoral", "bench"],
        "Back": ["back", "lat", "pull", "row"],
        "Legs": ["leg", "quad", "hamstring", "calf", "squat"],
        "Shoulders": ["shoulder", "deltoid", "press"],
        "Arms": ["bicep", "tricep", "arm"],
        "Core": ["core", "abdominal", "abs", "oblique"],
        "Cardio": ["cardio", "endurance", "aerobic"]
    }
    
    @classmethod
    def classify_muscle_group(cls, muscle_str: str) -> str:
        """Classify exercise into a muscle group"""
        if not muscle_str:
            return "Unknown"
        
        muscle_lower = muscle_str.lower()
        for group, keywords in cls.MUSCLE_GROUPS.items():
            for keyword in keywords:
                if keyword in muscle_lower:
                    return group
        return "Other"

class WorkoutAnalyzer:
    """Analyzes user's workout history"""
    
    def __init__(self, db: Session, user_id: int, days_back: int = 7):
        self.db = db
        self.user_id = user_id
        self.days_back = days_back
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    def get_recent_workouts(self) -> List[Workout]:
        """Get workouts from last N days"""
        return self.db.query(Workout).filter(
            Workout.user_id == self.user_id,
            Workout.start_time >= self.cutoff_date,
            Workout.end_time.isnot(None)  # Only completed workouts
        ).order_by(Workout.start_time.desc()).all()
    
    def analyze_muscle_fatigue(self) -> Dict[str, Dict]:
        """
        Analyze muscle fatigue and recovery status
        """
        workouts = self.get_recent_workouts()
        muscle_data = {}
        now = datetime.now(timezone.utc)
        
        # Initialize all muscle groups
        for muscle_group in MuscleTracker.MUSCLE_GROUPS.keys():
            muscle_data[muscle_group] = {
                "session_count": 0,
                "last_trained": None,
                "hours_since_last": None,
                "fatigue_score": 0.0,
                "priority_score": 0.0
            }
        
        # Process each workout
        for workout in workouts:
            # Get workout time (prefer end_time, fallback to start_time)
            workout_time = workout.end_time or workout.start_time
            
            if workout_time:
                # Ensure workout_time is timezone-aware
                if workout_time.tzinfo is None:
                    # Assume UTC if no timezone info
                    workout_time = workout_time.replace(tzinfo=timezone.utc)
                else:
                    # Convert to UTC if it has timezone
                    workout_time = workout_time.astimezone(timezone.utc)
            
            for workout_ex in workout.exercises:
                exercise = workout_ex.exercise
                if exercise and exercise.muscle_group:
                    muscle_group = MuscleTracker.classify_muscle_group(exercise.muscle_group)
                    
                    if muscle_group in muscle_data:
                        data = muscle_data[muscle_group]
                        data["session_count"] += 1
                        
                        # Update last trained time
                        if workout_time:
                            # Ensure we have a datetime for comparison
                            if data["last_trained"] is None:
                                data["last_trained"] = workout_time
                                # Calculate hours since
                                hours_since = (now - workout_time).total_seconds() / 3600
                                data["hours_since_last"] = max(0, hours_since)  # Never negative
                            else:
                                # Check if this workout is more recent
                                if workout_time > data["last_trained"]:
                                    data["last_trained"] = workout_time
                                    # Recalculate hours since
                                    hours_since = (now - workout_time).total_seconds() / 3600
                                    data["hours_since_last"] = max(0, hours_since)
        
        # Calculate scores
        for muscle_group, data in muscle_data.items():
            # Fatigue score: higher with more recent sessions
            if data["session_count"] > 0:
                # Base fatigue from session count (0-1 scale)
                session_fatigue = min(data["session_count"] / 3.0, 1.0)
                
                # Recency factor: more recent = higher fatigue
                if data["hours_since_last"] is not None:
                    # Hours to days conversion for recency
                    recency_days = data["hours_since_last"] / 24
                    # More recent = higher factor (decays over 7 days)
                    recency_factor = max(0, 1 - (recency_days / 7))
                    data["fatigue_score"] = min(session_fatigue + recency_factor * 0.3, 1.0)
                else:
                    data["fatigue_score"] = session_fatigue
            
            # Priority score: inverse of fatigue, with neglect bonus
            if data["session_count"] == 0:
                # Neglected muscle: high priority
                data["priority_score"] = 0.9
            else:
                # Priority = 1 - fatigue, but never zero
                data["priority_score"] = max(0.1, 1 - data["fatigue_score"])
        
        return muscle_data
    
    def get_neglected_muscles(self, threshold_days: int = 7) -> List[str]:
        """Get muscles not trained in threshold days"""
        muscle_data = self.analyze_muscle_fatigue()
        neglected = []
        
        for muscle_group, data in muscle_data.items():
            if data["session_count"] == 0:
                neglected.append(muscle_group)
            elif data["hours_since_last"] and data["hours_since_last"] > (threshold_days * 24):
                neglected.append(muscle_group)
        
        return neglected
    
    def get_recovery_status(self, preference: str = "moderate") -> Dict[str, bool]:
        """
        Check which muscles have recovered enough based on preference
        Returns: {"Chest": True, "Back": False, ...}
        """
        min_rest_hours = RecoveryPreference.get_min_rest_hours(preference)
        muscle_data = self.analyze_muscle_fatigue()
        recovery_status = {}
        
        for muscle_group, data in muscle_data.items():
            if not data["hours_since_last"]:  # Never trained
                recovery_status[muscle_group] = True
            else:
                recovery_status[muscle_group] = data["hours_since_last"] >= min_rest_hours
        
        return recovery_status

class ExerciseRecommender:
    """Generates exercise recommendations"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.analyzer = WorkoutAnalyzer(db, user_id)
    
    def get_available_exercises(self, muscle_group: Optional[str] = None) -> List[Exercise]:
        """Get exercises filtered by muscle group"""
        query = self.db.query(Exercise).filter(Exercise.is_active == True)
        
        if muscle_group:
            # Find exercises that match the muscle group
            matching_exercises = []
            all_exercises = query.all()
            
            for exercise in all_exercises:
                if exercise.muscle_group:
                    classified = MuscleTracker.classify_muscle_group(exercise.muscle_group)
                    if classified == muscle_group:
                        matching_exercises.append(exercise)
            
            return matching_exercises
        
        return query.all()
    
    def generate_recommendation(self, 
                               recovery_preference: str = "moderate",
                               max_recommendations: int = 4) -> Dict:
        """
        Generate workout recommendation
        Returns structure matching RecommendationResponse schema
        """
        # Get user info
        user = self.db.query(User).filter(User.id == self.user_id).first()
        
        # Analyze muscle state
        muscle_data = self.analyzer.analyze_muscle_fatigue()
        neglected = self.analyzer.get_neglected_muscles()
        recovery_status = self.analyzer.get_recovery_status(recovery_preference)
        
        # Sort muscles by priority score
        prioritized_muscles = sorted(
            [(mg, data["priority_score"]) for mg, data in muscle_data.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Filter for recovered muscles only
        available_muscles = [
            muscle for muscle, score in prioritized_muscles
            if recovery_status.get(muscle, True)  # True if never trained
        ]
        
        # Build recommendations
        recommendations = []
        warnings = []
        explanations = []
        
        # Algorithm's primary choice
        if available_muscles:
            primary_muscle = available_muscles[0]
            primary_exercises = self.get_available_exercises(primary_muscle)
            
            if primary_exercises:
                primary_exercise = primary_exercises[0]
                recommendations.append({
                    "exercise_id": primary_exercise.id,
                    "exercise_name": primary_exercise.name,
                    "muscle_group": primary_muscle,
                    "reason": f"High priority: {primary_muscle} has priority score {muscle_data[primary_muscle]['priority_score']:.2f}"
                })
                
                # Add alternatives from same muscle group
                alt_count = min(3, len(primary_exercises) - 1)
                for i in range(1, alt_count + 1):
                    alt_exercise = primary_exercises[i]
                    recommendations.append({
                        "exercise_id": alt_exercise.id,
                        "exercise_name": alt_exercise.name,
                        "muscle_group": primary_muscle,
                        "reason": f"Alternative {primary_muscle} exercise"
                    })
        
        # Add recommendations from other high-priority muscles
        other_muscles = available_muscles[1:3] if len(available_muscles) > 1 else []
        for muscle in other_muscles:
            exercises = self.get_available_exercises(muscle)
            if exercises:
                recommendations.append({
                    "exercise_id": exercises[0].id,
                    "exercise_name": exercises[0].name,
                    "muscle_group": muscle,
                    "reason": f"Balancing: {muscle} needs attention"
                })
        
        # Generate warnings
        # 1. Overtraining warning
        high_fatigue_muscles = [
            mg for mg, data in muscle_data.items()
            if data["fatigue_score"] > 0.8
        ]
        if high_fatigue_muscles:
            warnings.append(f"Overtraining risk: {', '.join(high_fatigue_muscles)}")
        
        # 2. Neglect warning
        if neglected:
            warnings.append(f"Neglected muscles: {', '.join(neglected[:3])}")
        
        # 3. Recovery warning
        non_recovered = [
            mg for mg, recovered in recovery_status.items()
            if not recovered
        ]
        if non_recovered:
            warnings.append(f"Muscles need rest: {', '.join(non_recovered[:3])}")
        
        # Generate explanations
        explanations.append(f"Based on last {self.analyzer.days_back} days of training")
        
        if available_muscles:
            top_muscle = available_muscles[0]
            explanations.append(f"Primary focus: {top_muscle} (priority: {muscle_data[top_muscle]['priority_score']:.2f})")
        
        if neglected:
            explanations.append(f"Consider adding: {neglected[0]} to address imbalance")
        
        # Build final response
        return {
            "user_id": self.user_id,
            "username": user.username if user else "Unknown",
            "recovery_preference": recovery_preference,
            "analysis_period_days": self.analyzer.days_back,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "algorithm_choice": recommendations[0] if recommendations else None,
            "alternatives": recommendations[1:] if len(recommendations) > 1 else [],
            "warnings": warnings,
            "explanations": explanations,
            "muscle_analysis": {
                mg: {
                    "priority": data["priority_score"],
                    "fatigue": data["fatigue_score"],
                    "session_count": data["session_count"],
                    "recovered": recovery_status.get(mg, True),
                    "last_trained_hours_ago": data.get("hours_since_last")
                }
                for mg, data in muscle_data.items()
            }
        }
