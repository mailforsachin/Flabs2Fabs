import sys
sys.path.append('.')
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, admin, system, exercise, workout, recommendation, intelligence, progress

app = FastAPI()

# Include WITHOUT prefixes first to see what they are
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(system.router)
app.include_router(exercise.router)
app.include_router(workout.router)
app.include_router(recommendation.router)
app.include_router(intelligence.router)
app.include_router(progress.router)

print("All routes WITHOUT prefixes:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"  {route.path}")
