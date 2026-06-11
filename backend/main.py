from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from database import get_db, engine
import schemas
import generator
import models

app = FastAPI(title="Workout Generator API")

# Mount static files for exercise images/gifs
# Assumes 'cwiczenia' directory is in the root of the project
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
candidate_paths = [
    os.path.join(parent_dir, "cwiczenia"),
    os.path.join(current_dir, "cwiczenia"),
]
cwiczenia_path = next((path for path in candidate_paths if os.path.exists(path)), None)

if cwiczenia_path:
    app.mount("/exercises-static", StaticFiles(directory=cwiczenia_path), name="exercises-static")

# Tworzenie tabel na starcie aplikacji
models.Base.metadata.create_all(bind=engine)

cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=(cors_origins != ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate-plan", response_model=schemas.PlanResponse)
def create_plan(request: schemas.PlanRequest, db: Session = Depends(get_db)):
    try:
        return generator.generate_workout_plan(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/api/exercises", response_model=list[schemas.ExerciseResponse])
def get_all_exercises(db: Session = Depends(get_db)):
    return db.query(models.Exercise).all()

@app.post("/api/exercises/replace", response_model=schemas.ExerciseResponse)
def replace_exercise(request: schemas.ReplaceExerciseRequest, db: Session = Depends(get_db)):
    alternative = generator.get_alternative_exercise(db, request)
    if not alternative:
        raise HTTPException(status_code=404, detail="No alternative exercise found")
    return alternative

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
