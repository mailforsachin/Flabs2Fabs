def calculate_volume(sets: int, reps_per_set: str, weight: float):
    reps = [int(r.strip()) for r in reps_per_set.split(",")]
    total_reps = sum(reps)
    avg_reps = total_reps / len(reps)
    volume = sets * avg_reps * weight
    return total_reps, round(volume, 2)
