from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, admin, system, exercise, workout, recommendation, intelligence
from app.routes.progress_simple import router as progress_simple_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Flab2Fabs API - Simple Test",
    description="Testing Phase D endpoints",
    version="3.0.0"
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(system.router)
app.include_router(exercise.router)
app.include_router(workout.router)
app.include_router(recommendation.router)
app.include_router(intelligence.router)
app.include_router(progress_simple_router, prefix="/api/progress", tags=["progress"])

@app.get("/")
def read_root():
    return {"message": "Flab2Fabs API - Simple Test Mode"}
