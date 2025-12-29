"""
📈 C++ - Override Impact Tracking
Track: "You chose chest over back 5 times"
Use: Feed into projections, adjust recommendations
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from app.models import Workout, WorkoutExercise, Exercise, User
from app.recommendation import MuscleTracker

class OverrideTracker:
    """Tracks when users override recommendations"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def analyze_override_patterns(self, days_back: int = 90) -> Dict:
        """
        Analyze patterns in user's exercise choices vs recommendations
        Returns override tendencies and biases
        """
        # Get all workouts
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user_id,
            Workout.end_time.isnot(None),
            Workout.start_time >= cutoff
        ).order_by(Workout.start_time.asc()).all()
        
        if not workouts:
            return {"no_data": True, "message": "No workout history to analyze"}
        
        # Analyze muscle group distribution
        muscle_counts = Counter()
        muscle_preferences = defaultdict(list)
        
        for workout in workouts:
            for w_ex in workout.exercises:
                exercise = w_ex.exercise
                if exercise and exercise.muscle_group:
                    muscle = MuscleTracker.classify_muscle_group(exercise.muscle_group)
                    muscle_counts[muscle] += 1
                    muscle_preferences[muscle].append({
                        "date": workout.start_time.date().isoformat() if workout.start_time else None,
                        "exercise": exercise.name,
                        "sets": w_ex.sets,
                        "reps": w_ex.reps,
                        "weight": w_ex.weight_kg
                    })
        
        # Calculate distribution percentages
        total_exercises = sum(muscle_counts.values())
        muscle_percentages = {
            muscle: (count / total_exercises * 100)
            for muscle, count in muscle_counts.items()
        }
        
        # Identify biases (muscles trained >20% more than others)
        avg_percentage = 100 / len(muscle_counts) if muscle_counts else 0
        biases = []
        
        for muscle, percentage in muscle_percentages.items():
            if percentage > avg_percentage * 1.2:  # 20% above average
                biases.append({
                    "muscle": muscle,
                    "percentage": round(percentage, 1),
                    "average": round(avg_percentage, 1),
                    "over_trained_by": round(percentage - avg_percentage, 1)
                })
        
        # Identify neglected muscles (<50% of average)
        neglected = []
        for muscle in MuscleTracker.MUSCLE_GROUPS.keys():
            percentage = muscle_percentages.get(muscle, 0)
            if percentage < avg_percentage * 0.5 and percentage > 0:
                neglected.append({
                    "muscle": muscle,
                    "percentage": round(percentage, 1),
                    "average": round(avg_percentage, 1),
                    "under_trained_by": round(avg_percentage - percentage, 1)
                })
        
        # Track progression patterns
        progression_analysis = self._analyze_progression_patterns(workouts)
        
        # Get most frequent exercises
        exercise_frequency = self._get_exercise_frequency(workouts)
        
        return {
            "analysis_period_days": days_back,
            "total_workouts": len(workouts),
            "total_exercises": total_exercises,
            "muscle_distribution": {
                "counts": dict(muscle_counts),
                "percentages": muscle_percentages,
                "average_percentage": round(avg_percentage, 1)
            },
            "biases": biases,
            "neglected_muscles": neglected,
            "progression_patterns": progression_analysis,
            "favorite_exercises": exercise_frequency[:5],
            "insights": self._generate_insights(biases, neglected, progression_analysis)
        }
    
    def _analyze_progression_patterns(self, workouts: List[Workout]) -> Dict:
        """Analyze how user progresses in exercises"""
        progression_data = defaultdict(list)
        
        for workout in workouts:
            for w_ex in workout.exercises:
                if w_ex.exercise and w_ex.weight_kg:
                    progression_data[w_ex.exercise.name].append({
                        "date": workout.start_time.date().isoformat() if workout.start_time else None,
                        "weight": w_ex.weight_kg,
                        "sets": w_ex.sets,
                        "reps": w_ex.reps
                    })
        
        # Calculate progression rates
        progression_rates = {}
        for exercise, records in progression_data.items():
            if len(records) >= 3:
                records.sort(key=lambda x: x["date"] or "")
                weights = [r["weight"] for r in records if r["weight"]]
                
                if len(weights) >= 2:
                    # Calculate average weekly increase
                    first_weight = weights[0]
                    last_weight = weights[-1]
                    
                    # Estimate weeks between first and last
                    if records[0]["date"] and records[-1]["date"]:
                        from datetime import datetime
                        first_date = datetime.fromisoformat(records[0]["date"]).date()
                        last_date = datetime.fromisoformat(records[-1]["date"]).date()
                        weeks = max(1, (last_date - first_date).days / 7)
                        
                        weekly_increase = (last_weight - first_weight) / weeks
                        progression_rates[exercise] = {
                            "weekly_increase_kg": round(weekly_increase, 2),
                            "total_increase_kg": round(last_weight - first_weight, 1),
                            "records_count": len(records),
                            "trend": "increasing" if weekly_increase > 0 else "stable" if weekly_increase == 0 else "decreasing"
                        }
        
        return {
            "exercises_tracked": len(progression_data),
            "exercises_with_progression": len(progression_rates),
            "progression_rates": progression_rates,
            "summary": self._summarize_progression(progression_rates)
        }
    
    def _summarize_progression(self, progression_rates: Dict) -> Dict:
        """Summarize progression patterns"""
        if not progression_rates:
            return {"message": "No progression data available"}
        
        increasing = [e for e, d in progression_rates.items() if d["trend"] == "increasing"]
        stable = [e for e, d in progression_rates.items() if d["trend"] == "stable"]
        decreasing = [e for e, d in progression_rates.items() if d["trend"] == "decreasing"]
        
        avg_increase = sum(d["weekly_increase_kg"] for d in progression_rates.values()) / len(progression_rates)
        
        return {
            "increasing_exercises": increasing[:3],
            "stable_exercises": stable[:3],
            "decreasing_exercises": decreasing[:3],
            "average_weekly_increase_kg": round(avg_increase, 2),
            "fastest_progressing": max(progression_rates.items(), key=lambda x: x[1]["weekly_increase_kg"])[0] if progression_rates else None,
            "slowest_progressing": min(progression_rates.items(), key=lambda x: x[1]["weekly_increase_kg"])[0] if progression_rates else None
        }
    
    def _get_exercise_frequency(self, workouts: List[Workout]) -> List[Dict]:
        """Get most frequently performed exercises"""
        exercise_counter = Counter()
        
        for workout in workouts:
            for w_ex in workout.exercises:
                if w_ex.exercise:
                    exercise_counter[w_ex.exercise.name] += 1
        
        return [
            {"exercise": exercise, "count": count}
            for exercise, count in exercise_counter.most_common(10)
        ]
    
    def _generate_insights(self, biases: List, neglected: List, progression: Dict) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        # Bias insights
        for bias in biases[:2]:  # Top 2 biases
            insights.append(f"You train {bias['muscle']} {bias['over_trained_by']}% more than average")
        
        # Neglect insights
        for neglect in neglected[:2]:  # Top 2 neglected
            insights.append(f"{neglect['muscle']} gets {neglect['under_trained_by']}% less attention than average")
        
        # Progression insights
        prog_summary = progression.get("summary", {})
        if prog_summary.get("average_weekly_increase_kg", 0) > 0.5:
            insights.append(f"Great progress! Adding {prog_summary['average_weekly_increase_kg']}kg/week on average")
        
        if prog_summary.get("decreasing_exercises"):
            insights.append(f"Watch out: {', '.join(prog_summary['decreasing_exercises'][:2])} trending down")
        
        # General insights
        if biases and not neglected:
            insights.append("You have clear favorites but maintain good overall balance")
        elif neglected and not biases:
            insights.append("Good variety but some muscles need more attention")
        elif biases and neglected:
            insights.append("You have strong preferences leading to muscle imbalances")
        else:
            insights.append("Excellent balanced training approach")
        
        return insights
    
    def get_override_adjusted_recommendations(self, 
                                           base_recommendations: List[Dict],
                                           days_back: int = 30) -> List[Dict]:
        """
        Adjust recommendations based on override history
        """
        analysis = self.analyze_override_patterns(days_back)
        
        # Adjust based on biases
        biases = {b["muscle"]: b for b in analysis.get("biases", [])}
        neglected = {n["muscle"]: n for n in analysis.get("neglected_muscles", [])}
        
        adjusted = []
        for rec in base_recommendations:
            muscle = rec.get("muscle_group")
            
            # Demote biased muscles
            if muscle in biases:
                rec["adjusted_priority"] = rec.get("priority", 1) * 0.7
                rec["adjustment_reason"] = f"Frequently trained ({biases[muscle]['percentage']:.1f}% of workouts)"
            
            # Promote neglected muscles
            elif muscle in neglected:
                rec["adjusted_priority"] = rec.get("priority", 1) * 1.3
                rec["adjustment_reason"] = f"Needs attention ({neglected[muscle]['percentage']:.1f}% of workouts)"
            
            else:
                rec["adjusted_priority"] = rec.get("priority", 1)
                rec["adjustment_reason"] = "Balanced training history"
            
            adjusted.append(rec)
        
        # Sort by adjusted priority
        adjusted.sort(key=lambda x: x.get("adjusted_priority", 0), reverse=True)
        
        return adjusted
    
    def generate_override_report(self, days_back: int = 90) -> Dict:
        """
        Generate comprehensive override report
        """
        analysis = self.analyze_override_patterns(days_back)
        
        report = {
            "period_analyzed_days": days_back,
            "summary": self._generate_report_summary(analysis),
            "key_findings": analysis.get("insights", []),
            "recommendations": self._generate_report_recommendations(analysis),
            "detailed_analysis": {
                "muscle_balance": analysis.get("muscle_distribution", {}),
                "biases": analysis.get("biases", []),
                "neglected": analysis.get("neglected_muscles", []),
                "progression": analysis.get("progression_patterns", {}),
                "favorites": analysis.get("favorite_exercises", [])
            }
        }
        
        return report
    
    def _generate_report_summary(self, analysis: Dict) -> str:
        """Generate report summary"""
        biases = analysis.get("biases", [])
        neglected = analysis.get("neglected_muscles", [])
        
        if biases and neglected:
            return "Mixed training patterns with clear favorites and some neglect"
        elif biases:
            return "Strong exercise preferences leading to focused training"
        elif neglected:
            return "Balanced overall but some muscles need more attention"
        else:
            return "Well-balanced training approach"
    
    def _generate_report_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        # Address biases
        for bias in analysis.get("biases", [])[:2]:
            recs.append(f"Reduce {bias['muscle']} frequency from {bias['percentage']:.1f}% to under {bias['average']:.1f}%")
        
        # Address neglect
        for neglect in analysis.get("neglected_muscles", [])[:2]:
            recs.append(f"Increase {neglect['muscle']} training from {neglect['percentage']:.1f}% to at least {neglect['average'] * 0.8:.1f}%")
        
        # Progression recommendations
        prog = analysis.get("progression_patterns", {}).get("summary", {})
        if prog.get("decreasing_exercises"):
            recs.append(f"Re-evaluate programming for: {', '.join(prog['decreasing_exercises'][:2])}")
        
        # Variety recommendation
        favorites = analysis.get("favorite_exercises", [])
        if len(favorites) > 0 and favorites[0]["count"] > 10:
            recs.append(f"Try alternatives to your most frequent exercise: {favorites[0]['exercise']}")
        
        # Add general recommendations if few specific ones
        if len(recs) < 3:
            recs.append("Consider a deload week if feeling fatigued")
            recs.append("Track weight and reps consistently for better insights")
            recs.append("Listen to your body - adjust intensity based on recovery")
        
        return recs
