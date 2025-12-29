"""
📈 D - Progress Projections Engine
The emotional hook of Flab2Fabs: "What could have been?"
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.models import Workout, WorkoutExercise, Exercise, User
from app.recommendation import MuscleTracker
from app.knowledge_level import KnowledgeAssessor, KnowledgeLevel
from app.override_tracking import OverrideTracker
import math

@dataclass
class StrengthProjection:
    """Strength projection for a single exercise"""
    exercise_id: int
    exercise_name: str
    muscle_group: str
    
    # Actual performance
    actual_current_weight: float  # Current 1RM (kg)
    actual_start_weight: float   # Starting weight (kg)
    actual_sessions: int         # Number of sessions
    actual_consistency: float    # 0-1 consistency score
    
    # Projected performance
    projected_current_weight: float  # What weight could be at
    projected_weekly_gain: float     # Projected kg/week gain
    projected_days_ahead: int        # Days ahead/behind schedule
    
    # Emotional metrics
    missed_opportunity_kg: float     # How much stronger you could be
    opportunity_percentage: float    # % of potential achieved
    motivation_score: float          # 0-100 motivation score
    
    # Timeline
    projection_start_date: str
    projection_end_date: str
    actual_timeline: List[Dict]      # Actual weight history
    projected_timeline: List[Dict]   # Projected weight history

@dataclass
class ConsistencyProjection:
    """Consistency projection"""
    period_days: int
    actual_workouts: int
    projected_workouts: int
    actual_consistency_rate: float  # workouts/week
    projected_consistency_rate: float
    missed_workouts: int
    consistency_gap: float  # 0-1 gap
    
    best_streak: int
    current_streak: int
    projected_streak: int

@dataclass
class MuscleBalanceProjection:
    """Muscle balance projection"""
    period_days: int
    actual_balance_score: float  # 0-1 (1 = perfect balance)
    projected_balance_score: float
    imbalance_gap: float
    
    most_biased_muscle: str
    most_neglected_muscle: str
    balance_improvement_potential: float

class ProgressProjector:
    """
    Projects "what could have been" based on:
    1. Actual training history
    2. Knowledge level appropriate progression
    3. Recommendation adherence
    4. Consistency patterns
    """
    
    # Progression rates by knowledge level (kg/week)
    PROGRESSION_RATES = {
        KnowledgeLevel.NOVICE: 1.0,      # 1kg/week
        KnowledgeLevel.LEARNER: 0.75,    # 0.75kg/week  
        KnowledgeLevel.PRACTITIONER: 0.5,  # 0.5kg/week
        KnowledgeLevel.EXPERT: 0.25       # 0.25kg/week
    }
    
    # Consistency targets by level (workouts/week)
    CONSISTENCY_TARGETS = {
        KnowledgeLevel.NOVICE: 2.5,
        KnowledgeLevel.LEARNER: 3.0,
        KnowledgeLevel.PRACTITIONER: 3.5,
        KnowledgeLevel.EXPERT: 4.0
    }
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.now = datetime.now(timezone.utc)
        
        # Initialize other modules
        self.knowledge_assessor = KnowledgeAssessor(db, user_id)
        self.override_tracker = OverrideTracker(db, user_id)
    
    def get_strength_projections(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Get strength projections for all exercises
        Shows actual vs what could have been
        """
        # Get knowledge level
        level, _ = self.knowledge_assessor.assess_knowledge_level()
        base_progression_rate = self.PROGRESSION_RATES.get(level, 0.5)
        
        # Get exercise history
        strength_exercises = self._get_strength_exercise_history(days_back)
        
        projections = []
        emotional_impact = {
            "total_missed_kg": 0,
            "average_opportunity": 0,
            "best_opportunity": None,
            "worse_opportunity": None,
            "motivation_messages": []
        }
        
        for ex_id, history in strength_exercises.items():
            if len(history) < 2:  # Need at least 2 data points
                continue
                
            projection = self._calculate_exercise_projection(
                ex_id, history, base_progression_rate, days_back, level
            )
            
            if projection:
                projections.append(projection)
                
                # Update emotional impact
                emotional_impact["total_missed_kg"] += projection.missed_opportunity_kg
                
                # Track best/worst opportunities
                if not emotional_impact["best_opportunity"] or \
                   projection.opportunity_percentage > emotional_impact["best_opportunity"]["percentage"]:
                    emotional_impact["best_opportunity"] = {
                        "exercise": projection.exercise_name,
                        "percentage": projection.opportunity_percentage,
                        "missed_kg": projection.missed_opportunity_kg
                    }
                
                if not emotional_impact["worse_opportunity"] or \
                   projection.opportunity_percentage < emotional_impact["worse_opportunity"]["percentage"]:
                    emotional_impact["worse_opportunity"] = {
                        "exercise": projection.exercise_name,
                        "percentage": projection.opportunity_percentage,
                        "missed_kg": projection.missed_opportunity_kg
                    }
        
        # Calculate averages
        if projections:
            emotional_impact["average_opportunity"] = sum(
                p.opportunity_percentage for p in projections
            ) / len(projections)
            
            # Generate motivation messages
            emotional_impact["motivation_messages"] = self._generate_motivation_messages(
                projections, emotional_impact
            )
        
        return {
            "period_days": days_back,
            "knowledge_level": level,
            "base_progression_rate_kg_week": base_progression_rate,
            "projections": [self._projection_to_dict(p) for p in projections],
            "emotional_impact": emotional_impact,
            "summary": self._generate_strength_summary(projections, emotional_impact)
        }
    
    def _get_strength_exercise_history(self, days_back: int) -> Dict[int, List[Dict]]:
        """Get strength exercise history with weights"""
        cutoff = self.now - timedelta(days=days_back)
        
        workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user_id,
            Workout.end_time.isnot(None),
            Workout.start_time >= cutoff,
            Workout.start_time.isnot(None)
        ).order_by(Workout.start_time.asc()).all()
        
        exercise_history = {}
        
        for workout in workouts:
            for w_ex in workout.exercises:
                if w_ex.exercise and w_ex.weight_kg and w_ex.exercise.exercise_type == "strength":
                    ex_id = w_ex.exercise_id
                    
                    if ex_id not in exercise_history:
                        exercise_history[ex_id] = {
                            "exercise_name": w_ex.exercise.name,
                            "muscle_group": w_ex.exercise.muscle_group,
                            "history": []
                        }
                    
                    # Calculate estimated 1RM using Epley formula
                    reps = w_ex.reps or 1
                    weight = w_ex.weight_kg
                    estimated_1rm = weight * (1 + reps / 30)  # Simplified Epley
                    
                    exercise_history[ex_id]["history"].append({
                        "date": workout.start_time.date().isoformat(),
                        "workout_id": workout.id,
                        "weight_kg": weight,
                        "reps": reps,
                        "sets": w_ex.sets or 0,
                        "estimated_1rm": round(estimated_1rm, 1),
                        "actual_1rm": weight if reps == 1 else None
                    })
        
        return exercise_history
    
    def _calculate_exercise_projection(self, 
                                     ex_id: int,
                                     history_data: Dict,
                                     base_rate: float,
                                     days_back: int,
                                     level: KnowledgeLevel) -> Optional[StrengthProjection]:
        """Calculate projection for a single exercise"""
        history = history_data["history"]
        if len(history) < 2:
            return None
        
        # Calculate actual progression
        start_weight = history[0]["estimated_1rm"]
        current_weight = history[-1]["estimated_1rm"]
        actual_gain = current_weight - start_weight
        
        # Calculate actual weekly rate
        try:
            start_date = datetime.fromisoformat(history[0]["date"]).date()
            end_date = datetime.fromisoformat(history[-1]["date"]).date()
            weeks = max(1, (end_date - start_date).days / 7)
            actual_weekly_rate = actual_gain / weeks
        except:
            actual_weekly_rate = 0
        
        # Calculate consistency for this exercise
        unique_days = len(set(h["date"] for h in history))
        total_days = days_back
        exercise_consistency = unique_days / total_days if total_days > 0 else 0
        
        # Calculate projected weight (if followed optimal progression)
        projected_gain = base_rate * weeks * (1 + exercise_consistency)  # Consistency bonus
        projected_current = start_weight + projected_gain
        
        # Calculate missed opportunity
        missed_kg = max(0, projected_current - current_weight)
        opportunity_pct = (current_weight - start_weight) / (projected_current - start_weight) if projected_current > start_weight else 0
        
        # Calculate motivation score (higher is better)
        motivation_score = min(100, opportunity_pct * 100 * (1 + exercise_consistency))
        
        # Generate timelines
        actual_timeline = self._generate_actual_timeline(history)
        projected_timeline = self._generate_projected_timeline(
            start_weight, base_rate, exercise_consistency, 
            start_date, end_date, len(history)
        )
        
        return StrengthProjection(
            exercise_id=ex_id,
            exercise_name=history_data["exercise_name"],
            muscle_group=history_data.get("muscle_group", "Unknown"),
            
            actual_current_weight=round(current_weight, 1),
            actual_start_weight=round(start_weight, 1),
            actual_sessions=len(history),
            actual_consistency=round(exercise_consistency, 2),
            
            projected_current_weight=round(projected_current, 1),
            projected_weekly_gain=round(base_rate * (1 + exercise_consistency), 2),
            projected_days_ahead=self._calculate_days_ahead(
                current_weight, projected_current, base_rate
            ),
            
            missed_opportunity_kg=round(missed_kg, 1),
            opportunity_percentage=round(min(1.0, opportunity_pct), 2),
            motivation_score=round(motivation_score, 1),
            
            projection_start_date=start_date.isoformat(),
            projection_end_date=end_date.isoformat(),
            actual_timeline=actual_timeline,
            projected_timeline=projected_timeline
        )
    
    def _generate_actual_timeline(self, history: List[Dict]) -> List[Dict]:
        """Generate actual weight timeline"""
        timeline = []
        for i, h in enumerate(history):
            timeline.append({
                "week": i + 1,
                "date": h["date"],
                "weight_kg": h["estimated_1rm"],
                "reps": h["reps"],
                "sets": h["sets"]
            })
        return timeline
    
    def _generate_projected_timeline(self, 
                                   start_weight: float,
                                   weekly_rate: float,
                                   consistency: float,
                                   start_date: datetime.date,
                                   end_date: datetime.date,
                                   actual_sessions: int) -> List[Dict]:
        """Generate projected weight timeline"""
        from datetime import timedelta
        
        timeline = []
        weeks = max(1, (end_date - start_date).days / 7)
        projected_sessions = int(actual_sessions * (1 + consistency))  # Consistency bonus
        
        for week in range(int(weeks) + 1):
            date = (start_date + timedelta(days=week*7)).isoformat()
            projected_weight = start_weight + (weekly_rate * week * (1 + consistency))
            
            timeline.append({
                "week": week + 1,
                "date": date,
                "weight_kg": round(projected_weight, 1),
                "sessions_this_week": 1 if week < projected_sessions else 0,
                "note": "Projected" if week > 0 else "Starting point"
            })
        
        return timeline
    
    def _calculate_days_ahead(self, 
                            current_weight: float, 
                            projected_weight: float,
                            weekly_rate: float) -> int:
        """Calculate how many days ahead/behind schedule"""
        weight_gap = projected_weight - current_weight
        if weekly_rate <= 0:
            return 0
        
        days = (weight_gap / weekly_rate) * 7
        return int(days)
    
    def _generate_motivation_messages(self, 
                                    projections: List[StrengthProjection],
                                    emotional_impact: Dict) -> List[str]:
        """Generate motivational messages based on projections"""
        messages = []
        
        if not projections:
            return ["Start tracking strength exercises to see projections!"]
        
        # Calculate overall metrics
        avg_opportunity = emotional_impact["average_opportunity"]
        total_missed = emotional_impact["total_missed_kg"]
        best = emotional_impact.get("best_opportunity")
        worst = emotional_impact.get("worse_opportunity")
        
        if avg_opportunity > 0.8:
            messages.append("🎯 Amazing consistency! You're capturing over 80% of your strength potential.")
        elif avg_opportunity > 0.6:
            messages.append("💪 Good progress! You're on track for about 60-80% of optimal gains.")
        else:
            messages.append("📈 Room for growth: You could be significantly stronger with more consistency.")
        
        if total_missed > 20:
            messages.append(f"⚡ Potential unlock: You could be {total_missed:.0f}kg stronger across all lifts!")
        
        if best and best["percentage"] > 0.9:
            messages.append(f"🌟 Star performer: Your {best['exercise']} is near optimal!")
        
        if worst and worst["percentage"] < 0.4:
            messages.append(f"🎯 Focus area: {worst['exercise']} has the most room for improvement.")
        
        # Add level-specific advice
        level, _ = self.knowledge_assessor.assess_knowledge_level()
        if level == KnowledgeLevel.NOVICE:
            messages.append("👶 Beginner tip: Focus on consistency over weight. The gains will come!")
        elif level == KnowledgeLevel.LEARNER:
            messages.append("📚 Learning phase: Perfect your form as you increase weight.")
        
        return messages[:3]  # Return top 3 messages
    
    def _generate_strength_summary(self, 
                                 projections: List[StrengthProjection],
                                 emotional_impact: Dict) -> Dict:
        """Generate strength projection summary"""
        if not projections:
            return {"message": "No strength data available for projections"}
        
        # Calculate overall metrics
        total_missed = emotional_impact["total_missed_kg"]
        avg_opportunity = emotional_impact["average_opportunity"]
        
        # Find best and worst exercises
        best_exercise = None
        worst_exercise = None
        
        for proj in projections:
            if not best_exercise or proj.opportunity_percentage > best_exercise.opportunity_percentage:
                best_exercise = proj
            if not worst_exercise or proj.opportunity_percentage < worst_exercise.opportunity_percentage:
                worst_exercise = proj
        
        return {
            "total_exercises_projected": len(projections),
            "average_opportunity_percentage": round(avg_opportunity * 100, 1),
            "total_missed_strength_kg": round(total_missed, 1),
            "best_performing_exercise": {
                "name": best_exercise.exercise_name if best_exercise else None,
                "opportunity": round(best_exercise.opportunity_percentage * 100, 1) if best_exercise else None,
                "missed_kg": round(best_exercise.missed_opportunity_kg, 1) if best_exercise else None
            },
            "most_opportunity_exercise": {
                "name": worst_exercise.exercise_name if worst_exercise else None,
                "opportunity": round(worst_exercise.opportunity_percentage * 100, 1) if worst_exercise else None,
                "missed_kg": round(worst_exercise.missed_opportunity_kg, 1) if worst_exercise else None
            },
            "overall_verdict": self._get_overall_verdict(avg_opportunity),
            "recommended_focus": worst_exercise.exercise_name if worst_exercise else None
        }
    
    def _get_overall_verdict(self, avg_opportunity: float) -> str:
        """Get overall verdict based on opportunity percentage"""
        if avg_opportunity > 0.85:
            return "Exceptional: You're capturing most of your strength potential!"
        elif avg_opportunity > 0.70:
            return "Great: Strong progress with room for optimization."
        elif avg_opportunity > 0.50:
            return "Good: Solid foundation with significant opportunity."
        else:
            return "Potential: Consider focusing on consistency for greater gains."
    
    def _projection_to_dict(self, projection: StrengthProjection) -> Dict:
        """Convert projection dataclass to dict"""
        return {
            "exercise_id": projection.exercise_id,
            "exercise_name": projection.exercise_name,
            "muscle_group": projection.muscle_group,
            
            "actual": {
                "current_weight_kg": projection.actual_current_weight,
                "start_weight_kg": projection.actual_start_weight,
                "sessions": projection.actual_sessions,
                "consistency": projection.actual_consistency
            },
            
            "projected": {
                "current_weight_kg": projection.projected_current_weight,
                "weekly_gain_kg": projection.projected_weekly_gain,
                "days_ahead": projection.projected_days_ahead
            },
            
            "opportunity_analysis": {
                "missed_kg": projection.missed_opportunity_kg,
                "opportunity_percentage": projection.opportunity_percentage,
                "motivation_score": projection.motivation_score
            },
            
            "timeline": {
                "start_date": projection.projection_start_date,
                "end_date": projection.projection_end_date,
                "actual_points": len(projection.actual_timeline),
                "projected_points": len(projection.projected_timeline)
            }
        }
    
    def get_consistency_projections(self, days_back: int = 90) -> Dict:
        """
        Project consistency "what if" scenarios
        """
        cutoff = self.now - timedelta(days=days_back)
        
        # Get actual workouts
        workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user_id,
            Workout.end_time.isnot(None),
            Workout.start_time >= cutoff,
            Workout.start_time.isnot(None)
        ).order_by(Workout.start_time.asc()).all()
        
        if not workouts:
            return {"message": "No workout data available"}
        
        # Calculate actual consistency
        workout_dates = set()
        for workout in workouts:
            if workout.start_time:
                workout_dates.add(workout.start_time.date())
        
        actual_workouts = len(workout_dates)
        actual_consistency_rate = (actual_workouts / days_back) * 7  # workouts/week
        
        # Get knowledge level for projected target
        level, _ = self.knowledge_assessor.assess_knowledge_level()
        projected_rate = self.CONSISTENCY_TARGETS.get(level, 3.0)
        projected_workouts = int((projected_rate / 7) * days_back)
        
        # Calculate streaks
        best_streak, current_streak = self._calculate_streaks(list(workout_dates))
        projected_streak = int(best_streak * 1.5)  # Optimistic projection
        
        consistency_gap = max(0, projected_rate - actual_consistency_rate) / projected_rate
        
        projection = ConsistencyProjection(
            period_days=days_back,
            actual_workouts=actual_workouts,
            projected_workouts=projected_workouts,
            actual_consistency_rate=round(actual_consistency_rate, 1),
            projected_consistency_rate=projected_rate,
            missed_workouts=max(0, projected_workouts - actual_workouts),
            consistency_gap=round(consistency_gap, 2),
            best_streak=best_streak,
            current_streak=current_streak,
            projected_streak=projected_streak
        )
        
        return {
            "period_days": days_back,
            "knowledge_level": level,
            "consistency_projection": {
                "actual": {
                    "workouts": projection.actual_workouts,
                    "rate_per_week": projection.actual_consistency_rate,
                    "best_streak": projection.best_streak,
                    "current_streak": projection.current_streak
                },
                "projected": {
                    "workouts": projection.projected_workouts,
                    "rate_per_week": projection.projected_consistency_rate,
                    "streak": projection.projected_streak
                },
                "gap_analysis": {
                    "missed_workouts": projection.missed_workouts,
                    "consistency_gap": projection.consistency_gap,
                    "potential_extra_sessions": projection.missed_workouts
                }
            },
            "consistency_messages": self._generate_consistency_messages(projection, level)
        }
    
    def _calculate_streaks(self, workout_dates: List[datetime.date]) -> Tuple[int, int]:
        """Calculate best and current streaks"""
        if not workout_dates:
            return 0, 0
        
        # Sort dates
        dates = sorted(workout_dates)
        
        # Calculate streaks
        best_streak = 1
        current_streak = 1
        temp_streak = 1
        
        for i in range(1, len(dates)):
            days_diff = (dates[i] - dates[i-1]).days
            
            if days_diff == 1:  # Consecutive days
                temp_streak += 1
                best_streak = max(best_streak, temp_streak)
            elif days_diff <= 3:  # Allow small gaps for "streak"
                temp_streak += 1  # Count as streak with rest days
                best_streak = max(best_streak, temp_streak)
            else:
                temp_streak = 1
        
        # Calculate current streak (from most recent date)
        today = self.now.date()
        current_streak = 0
        
        for i in range(len(dates)-1, -1, -1):
            if i == len(dates)-1:
                # Check if last workout was recent
                if (today - dates[i]).days <= 3:
                    current_streak = 1
                else:
                    break
            else:
                days_diff = (dates[i+1] - dates[i]).days
                if days_diff <= 3:
                    current_streak += 1
                else:
                    break
        
        return best_streak, current_streak
    
    def _generate_consistency_messages(self, 
                                     projection: ConsistencyProjection,
                                     level: KnowledgeLevel) -> List[str]:
        """Generate consistency-related messages"""
        messages = []
        
        gap = projection.consistency_gap
        missed = projection.missed_workouts
        
        if gap < 0.1:
            messages.append("🎯 Consistency champion! You're hitting your target frequency.")
        elif gap < 0.3:
            messages.append("💪 Solid consistency! Small improvements could yield big results.")
        else:
            messages.append(f"📅 Opportunity: You missed ~{missed} workouts vs target.")
        
        if projection.current_streak >= 7:
            messages.append(f"🔥 Hot streak! {projection.current_streak} days in a row!")
        elif projection.current_streak == 0:
            messages.append("🔄 Time to restart your streak! Even short workouts count.")
        
        if projection.best_streak > 14:
            messages.append(f"🌟 Record streak: You've done {projection.best_streak} days before!")
        
        # Level-specific advice
        if level == KnowledgeLevel.NOVICE:
            messages.append("👶 Beginner focus: Build the habit with 2-3 sessions/week.")
        elif level == KnowledgeLevel.LEARNER:
            messages.append("📚 Learning phase: Consistency builds skill and strength.")
        
        return messages[:3]
    
    def get_comprehensive_progress_report(self, days_back: int = 90) -> Dict:
        """
        Get comprehensive progress report combining all projections
        """
        strength = self.get_strength_projections(days_back)
        consistency = self.get_consistency_projections(days_back)
        
        # Get knowledge level
        level, level_assessment = self.knowledge_assessor.assess_knowledge_level()
        
        # Calculate overall progress score (0-100)
        strength_score = strength.get("emotional_impact", {}).get("average_opportunity", 0.5) * 50
        consistency_gap = consistency.get("consistency_projection", {}).get("gap_analysis", {}).get("consistency_gap", 0.5)
        consistency_score = (1 - consistency_gap) * 50
        
        overall_score = strength_score + consistency_score
        
        # Generate emotional impact summary
        emotional_summary = self._generate_emotional_summary(strength, consistency, overall_score)
        
        return {
            "period_days": days_back,
            "knowledge_level": level,
            "overall_progress_score": round(overall_score, 1),
            "score_breakdown": {
                "strength_progress": round(strength_score, 1),
                "consistency_progress": round(consistency_score, 1),
                "max_possible": 100
            },
            "strength_projections": strength,
            "consistency_projections": consistency,
            "emotional_summary": emotional_summary,
            "actionable_insights": self._generate_actionable_insights(strength, consistency, level),
            "next_30_day_potential": self._calculate_30_day_potential(strength, consistency)
        }
    
    def _generate_emotional_summary(self, 
                                  strength: Dict, 
                                  consistency: Dict,
                                  overall_score: float) -> Dict:
        """Generate emotional summary of progress"""
        strength_missed = strength.get("emotional_impact", {}).get("total_missed_kg", 0)
        consistency_missed = consistency.get("consistency_projection", {}).get("gap_analysis", {}).get("missed_workouts", 0)
        
        if overall_score > 80:
            mood = "Exceptional"
            icon = "🏆"
            message = "You're performing at an elite level! Keep up the amazing work."
        elif overall_score > 65:
            mood = "Great"
            icon = "🚀"
            message = "Strong progress! You're well on your way to your goals."
        elif overall_score > 50:
            mood = "Good"
            icon = "💪"
            message = "Solid foundation with clear opportunities for growth."
        else:
            mood = "Opportunity"
            icon = "🎯"
            message = "Significant potential waiting to be unlocked!"
        
        return {
            "mood": mood,
            "icon": icon,
            "message": message,
            "key_metric": f"{overall_score:.0f}/100 progress score",
            "motivational_quote": self._get_motivational_quote(overall_score),
            "potential_unlock": {
                "strength_kg": round(strength_missed, 1),
                "workouts": consistency_missed,
                "summary": f"Potential: {strength_missed:.0f}kg stronger, {consistency_missed} more workouts"
            }
        }
    
    def _get_motivational_quote(self, score: float) -> str:
        """Get motivational quote based on score"""
        quotes = {
            "high": [
                "The only bad workout is the one that didn't happen.",
                "Success isn't always about greatness. It's about consistency.",
                "Don't stop when you're tired. Stop when you're done."
            ],
            "medium": [
                "It's not about having time, it's about making time.",
                "The hardest lift of all is lifting your butt off the couch.",
                "Small steps every day lead to big results over time."
            ],
            "low": [
                "The best time to start was yesterday. The second best time is now.",
                "You don't have to be great to start, but you have to start to be great.",
                "Your only limit is you. What are you waiting for?"
            ]
        }
        
        import random
        if score > 70:
            return random.choice(quotes["high"])
        elif score > 40:
            return random.choice(quotes["medium"])
        else:
            return random.choice(quotes["low"])
    
    def _generate_actionable_insights(self, 
                                    strength: Dict, 
                                    consistency: Dict,
                                    level: KnowledgeLevel) -> List[Dict]:
        """Generate actionable insights from projections"""
        insights = []
        
        # Strength insights
        strength_summary = strength.get("summary", {})
        worst_exercise = strength_summary.get("most_opportunity_exercise", {})
        
        if worst_exercise.get("name"):
            insights.append({
                "type": "strength",
                "priority": "high",
                "message": f"Focus on {worst_exercise['name']} - {worst_exercise['missed_kg']}kg potential",
                "action": f"Add 1-2 extra sessions for {worst_exercise['name']} this month"
            })
        
        # Consistency insights
        consistency_gap = consistency.get("consistency_projection", {}).get("gap_analysis", {}).get("consistency_gap", 0)
        if consistency_gap > 0.2:
            target = consistency.get("consistency_projection", {}).get("projected", {}).get("rate_per_week", 3)
            insights.append({
                "type": "consistency",
                "priority": "medium",
                "message": f"Aim for {target} workouts/week (currently below target)",
                "action": "Schedule workouts in your calendar like appointments"
            })
        
        # Level-specific insights
        if level == KnowledgeLevel.NOVICE:
            insights.append({
                "type": "education",
                "priority": "medium",
                "message": "Focus on learning proper form for 3-5 key exercises",
                "action": "Watch tutorial videos for your main lifts"
            })
        elif level == KnowledgeLevel.LEARNER:
            insights.append({
                "type": "progression",
                "priority": "medium",
                "message": "Start tracking weights and aiming for small weekly increases",
                "action": "Add 1.25-2.5kg to one exercise each week"
            })
        
        # General insights
        insights.append({
            "type": "general",
            "priority": "low",
            "message": "Review your progress monthly to stay motivated",
            "action": "Set a calendar reminder for monthly progress review"
        })
        
        return insights[:3]  # Return top 3 insights
    
    def _calculate_30_day_potential(self, strength: Dict, consistency: Dict) -> Dict:
        """Calculate potential gains in next 30 days"""
        strength_missed = strength.get("emotional_impact", {}).get("total_missed_kg", 0)
        consistency_gap = consistency.get("consistency_projection", {}).get("gap_analysis", {}).get("consistency_gap", 0.5)
        
        # Estimate 30-day potential (scaled down from total missed)
        monthly_potential_kg = strength_missed * 0.3  # 30% of total missed in 30 days
        monthly_extra_workouts = int(consistency_gap * 8)  # ~2 workouts/week gap
        
        level, _ = self.knowledge_assessor.assess_knowledge_level()
        
        return {
            "timeframe_days": 30,
            "strength_potential_kg": round(monthly_potential_kg, 1),
            "consistency_potential_workouts": monthly_extra_workouts,
            "knowledge_level": level,
            "achievable_goals": [
                f"Add {monthly_potential_kg:.1f}kg to your lifts",
                f"Complete {monthly_extra_workouts} extra workouts",
                f"Improve one exercise by 5-10%"
            ],
            "commitment_required": {
                "weekly_sessions": monthly_extra_workouts // 4 + 2,  # Extra + base
                "focus_minutes": 30 * monthly_extra_workouts,  # 30 min per extra session
                "consistency_days": 20  # Aim for 20/30 days of some activity
            }
        }
