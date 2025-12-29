"""
🧠 C+ - Knowledge Level Reassessment Logic
Detect: Novice → Learner → Practitioner → Expert drift
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum
from sqlalchemy.orm import Session
from app.models import Workout, User, WorkoutExercise, Exercise

class KnowledgeLevel(str, Enum):
    NOVICE = "novice"        # < 30 days, inconsistent
    LEARNER = "learner"      # 30-90 days, building consistency  
    PRACTITIONER = "practitioner"  # 90-180 days, consistent
    EXPERT = "expert"        # > 180 days, advanced patterns

class KnowledgeAssessor:
    """Assesses user's fitness knowledge level"""
    
    # Level thresholds (days of consistent training)
    LEVEL_THRESHOLDS = {
        KnowledgeLevel.NOVICE: 0,
        KnowledgeLevel.LEARNER: 30,
        KnowledgeLevel.PRACTITIONER: 90,
        KnowledgeLevel.EXPERT: 180
    }
    
    # Safety thresholds for warnings
    SAFETY_THRESHOLDS = {
        KnowledgeLevel.NOVICE: {
            "max_sessions_per_week": 4,
            "max_sets_per_muscle": 12,
            "min_rest_days": 2,
            "max_weight_increase": 2.5  # kg
        },
        KnowledgeLevel.LEARNER: {
            "max_sessions_per_week": 5,
            "max_sets_per_muscle": 15,
            "min_rest_days": 1,
            "max_weight_increase": 5.0  # kg
        },
        KnowledgeLevel.PRACTITIONER: {
            "max_sessions_per_week": 6,
            "max_sets_per_muscle": 20,
            "min_rest_days": 1,
            "max_weight_increase": 7.5  # kg
        },
        KnowledgeLevel.EXPERT: {
            "max_sessions_per_week": 7,
            "max_sets_per_muscle": 25,
            "min_rest_days": 0,  # Can train daily if programmed
            "max_weight_increase": 10.0  # kg
        }
    }
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.now = datetime.now(timezone.utc)
    
    def get_user_training_age_days(self) -> int:
        """How many days since first workout"""
        first_workout = self.db.query(Workout).filter(
            Workout.user_id == self.user_id,
            Workout.end_time.isnot(None)
        ).order_by(Workout.start_time.asc()).first()
        
        if not first_workout:
            return 0
        
        first_date = first_workout.start_time or first_workout.end_time
        if first_date.tzinfo is None:
            first_date = first_date.replace(tzinfo=timezone.utc)
        
        days = (self.now - first_date).days
        return max(0, days)
    
    def get_consistency_score(self, days_lookback: int = 90) -> float:
        """
        Calculate training consistency (0-1)
        1.0 = trained every possible day
        0.0 = never trained
        """
        cutoff = self.now - timedelta(days=days_lookback)
        
        # Get all completed workouts in period
        workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user_id,
            Workout.end_time.isnot(None),
            Workout.start_time >= cutoff
        ).all()
        
        if not workouts:
            return 0.0
        
        # Count unique training days
        training_days = set()
        for workout in workouts:
            if workout.start_time:
                date = workout.start_time.date()
                training_days.add(date)
        
        consistency = len(training_days) / days_lookback
        return min(consistency, 1.0)
    
    def get_progression_quality(self) -> float:
        """
        Assess quality of progressive overload (0-1)
        Looks at weight increases over time
        """
        # Get all strength exercises with weight tracking
        strength_workouts = self.db.query(WorkoutExercise).join(Workout).join(Exercise).filter(
            Workout.user_id == self.user_id,
            Workout.end_time.isnot(None),
            Exercise.exercise_type == "strength",
            WorkoutExercise.weight_kg.isnot(None),
            WorkoutExercise.weight_kg > 0
        ).order_by(Workout.start_time.asc()).all()
        
        if len(strength_workouts) < 4:  # Need enough data
            return 0.5  # Neutral
        
        # Group by exercise and track progression
        exercise_progress = {}
        for w_ex in strength_workouts:
            if w_ex.exercise_id not in exercise_progress:
                exercise_progress[w_ex.exercise_id] = []
            exercise_progress[w_ex.exercise_id].append(w_ex.weight_kg)
        
        # Calculate progression scores
        progression_scores = []
        for ex_id, weights in exercise_progress.items():
            if len(weights) >= 3:
                # Check if generally increasing
                increasing = 0
                for i in range(1, len(weights)):
                    if weights[i] > weights[i-1]:
                        increasing += 1
                
                progression_ratio = increasing / (len(weights) - 1)
                progression_scores.append(progression_ratio)
        
        if not progression_scores:
            return 0.5
        
        return sum(progression_scores) / len(progression_scores)
    
    def assess_knowledge_level(self) -> Tuple[KnowledgeLevel, Dict]:
        """
        Assess user's current knowledge level
        Returns: (level, assessment_details)
        """
        training_age = self.get_user_training_age_days()
        consistency = self.get_consistency_score()
        progression = self.get_progression_quality()
        
        # Calculate level score (0-100)
        age_score = min(training_age / 180, 1.0) * 40  # Max 40 points
        consistency_score = consistency * 40           # Max 40 points  
        progression_score = progression * 20           # Max 20 points
        
        total_score = age_score + consistency_score + progression_score
        
        # Determine level
        if total_score >= 80:
            level = KnowledgeLevel.EXPERT
        elif total_score >= 60:
            level = KnowledgeLevel.PRACTITIONER
        elif total_score >= 30:
            level = KnowledgeLevel.LEARNER
        else:
            level = KnowledgeLevel.NOVICE
        
        assessment = {
            "level": level,
            "score": round(total_score, 1),
            "training_age_days": training_age,
            "consistency_score": round(consistency, 2),
            "progression_quality": round(progression, 2),
            "breakdown": {
                "age_score": round(age_score, 1),
                "consistency_score": round(consistency_score, 1),
                "progression_score": round(progression_score, 1)
            },
            "safety_thresholds": self.SAFETY_THRESHOLDS[level]
        }
        
        return level, assessment
    
    def generate_safety_warnings(self, planned_workout: Dict) -> List[str]:
        """
        Generate safety warnings based on knowledge level
        planned_workout: {
            "exercises": [
                {"exercise_id": 1, "sets": 3, "reps": 10, "weight_kg": 60},
                ...
            ]
        }
        """
        level, assessment = self.assess_knowledge_level()
        thresholds = self.SAFETY_THRESHOLDS[level]
        warnings = []
        
        # Check weekly frequency (simplified)
        recent_workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user_id,
            Workout.end_time.isnot(None),
            Workout.start_time >= self.now - timedelta(days=7)
        ).count()
        
        if recent_workouts >= thresholds["max_sessions_per_week"]:
            warnings.append(f"High frequency: {recent_workouts} sessions this week (max: {thresholds['max_sessions_per_week']})")
        
        # Check muscle group volume in planned workout
        muscle_sets = {}
        for ex in planned_workout.get("exercises", []):
            exercise = self.db.query(Exercise).filter(Exercise.id == ex["exercise_id"]).first()
            if exercise and exercise.muscle_group:
                from app.recommendation import MuscleTracker
                muscle = MuscleTracker.classify_muscle_group(exercise.muscle_group)
                muscle_sets[muscle] = muscle_sets.get(muscle, 0) + ex.get("sets", 0)
        
        for muscle, sets in muscle_sets.items():
            if sets > thresholds["max_sets_per_muscle"]:
                warnings.append(f"High volume for {muscle}: {sets} sets (max: {thresholds['max_sets_per_muscle']})")
        
        # Check weight jumps
        for ex in planned_workout.get("exercises", []):
            if ex.get("weight_kg"):
                # Get last weight for this exercise
                last_workout = self.db.query(WorkoutExercise).join(Workout).filter(
                    Workout.user_id == self.user_id,
                    WorkoutExercise.exercise_id == ex["exercise_id"],
                    WorkoutExercise.weight_kg.isnot(None)
                ).order_by(Workout.start_time.desc()).first()
                
                if last_workout and last_workout.weight_kg:
                    weight_increase = ex["weight_kg"] - last_workout.weight_kg
                    if weight_increase > thresholds["max_weight_increase"]:
                        warnings.append(f"Large weight jump: +{weight_increase:.1f}kg (max: {thresholds['max_weight_increase']}kg)")
        
        # Level-specific advice
        if level == KnowledgeLevel.NOVICE:
            warnings.append("Novice tip: Focus on form over weight. Consider a trainer.")
        elif level == KnowledgeLevel.LEARNER:
            warnings.append("Learner tip: Build consistency before increasing intensity.")
        
        return warnings
    
    def get_level_based_recommendations(self) -> Dict:
        """
        Get recommendations tailored to knowledge level
        """
        level, assessment = self.assess_knowledge_level()
        
        recommendations = {
            "level": level,
            "description": self._get_level_description(level),
            "focus_areas": self._get_focus_areas(level),
            "common_mistakes": self._get_common_mistakes(level),
            "next_level_goals": self._get_next_level_goals(level, assessment),
            "safety_limits": assessment["safety_thresholds"]
        }
        
        return recommendations
    
    def _get_level_description(self, level: KnowledgeLevel) -> str:
        descriptions = {
            KnowledgeLevel.NOVICE: "Just starting out. Focus on learning form and building consistency.",
            KnowledgeLevel.LEARNER: "Building foundations. Working on consistency and basic programming.",
            KnowledgeLevel.PRACTITIONER: "Consistent training. Refining technique and programming.",
            KnowledgeLevel.EXPERT: "Advanced training. Sophisticated programming and self-regulation."
        }
        return descriptions.get(level, "")
    
    def _get_focus_areas(self, level: KnowledgeLevel) -> List[str]:
        focus = {
            KnowledgeLevel.NOVICE: [
                "Learn proper form for basic exercises",
                "Establish 2-3 workouts per week consistency",
                "Focus on full-body workouts",
                "Track workouts consistently"
            ],
            KnowledgeLevel.LEARNER: [
                "Improve exercise technique",
                "Introduce progressive overload",
                "Experiment with different exercises",
                "Learn about recovery needs"
            ],
            KnowledgeLevel.PRACTITIONER: [
                "Optimize training splits",
                "Periodize training cycles",
                "Refine nutrition for goals",
                "Manage fatigue effectively"
            ],
            KnowledgeLevel.EXPERT: [
                "Advanced programming techniques",
                "Peaking for specific events",
                "Injury prevention strategies",
                "Mentoring others"
            ]
        }
        return focus.get(level, [])
    
    def _get_common_mistakes(self, level: KnowledgeLevel) -> List[str]:
        mistakes = {
            KnowledgeLevel.NOVICE: [
                "Skipping warm-ups",
                "Using too much weight too soon",
                "Inconsistent training schedule",
                "Not tracking progress"
            ],
            KnowledgeLevel.LEARNER: [
                "Neglecting recovery",
                "Chasing weight over form",
                "Overtraining certain muscles",
                "Not deloading when needed"
            ],
            KnowledgeLevel.PRACTITIONER: [
                "Plateauing from lack of variation",
                "Ignoring mobility work",
                "Underestimating sleep importance",
                "Neglecting weak points"
            ],
            KnowledgeLevel.EXPERT: [
                "Overcomplicating programming",
                "Ignoring new research",
                "Neglecting fundamentals",
                "Burnout from excessive intensity"
            ]
        }
        return mistakes.get(level, [])
    
    def _get_next_level_goals(self, level: KnowledgeLevel, assessment: Dict) -> List[str]:
        if level == KnowledgeLevel.EXPERT:
            return ["Maintain expert status", "Help others learn", "Set new personal records"]
        
        next_level = {
            KnowledgeLevel.NOVICE: KnowledgeLevel.LEARNER,
            KnowledgeLevel.LEARNER: KnowledgeLevel.PRACTITIONER,
            KnowledgeLevel.PRACTITIONER: KnowledgeLevel.EXPERT
        }.get(level)
        
        goals = []
        if assessment["consistency_score"] < 0.7:
            goals.append(f"Increase consistency to {int(assessment['consistency_score']*100)}% → 70%")
        
        if assessment["progression_quality"] < 0.6:
            goals.append(f"Improve progression quality to {int(assessment['progression_quality']*100)}% → 60%")
        
        days_needed = self.LEVEL_THRESHOLDS[next_level] - assessment["training_age_days"]
        if days_needed > 0:
            goals.append(f"Continue training for {days_needed} more days")
        
        return goals
