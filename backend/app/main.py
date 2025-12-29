from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import auth, admin, system, exercise, workout, recommendation, intelligence
# Use the simple working version
from app.routes.progress_simple_working import router as progress_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Flab2Fabs API",
    description="Intelligent fitness tracking with emotional insights",
    version="3.0.0"
)

# Add CORS middleware - THIS IS THE KEY FIX!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://flabs2fabs.omchat.ovh",
        "http://flabs2fabs.omchat.ovh",
        "https://www.flabs2fabs.omchat.ovh",
        "http://www.flabs2fabs.omchat.ovh",
        "http://localhost:8008",  # For direct API access
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(system.router)
app.include_router(exercise.router)
app.include_router(workout.router)
app.include_router(recommendation.router)
app.include_router(intelligence.router)
app.include_router(progress_router)

@app.get("/")
def read_root():
    return {
        "message": "Flab2Fabs API v3.0 - The Emotional Training Partner",
        "version": "3.0.0",
        "docs": "/docs",
        "features": [
            "✅ Basic API (Auth, Exercises, Workouts)",
            "✅ Recommendation Engine (Phase C)",
            "🧠 Knowledge Level Tracking (C+)",
            "📈 Override Pattern Analysis (C++)",
            "💔 Progress Projections (Phase D)",
            "🎯 Emotional Insights & Motivation",
            "📊 'What Could Have Been' Analysis"
        ]
    }

@app.get("/health")
def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}
