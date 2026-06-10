from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, engine
import schemas
import generator
import models

app = FastAPI(title="Workout Generator API")

# Tworzenie tabel na starcie aplikacji
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate-plan", response_model=schemas.PlanResponse)
def create_plan(request: schemas.PlanRequest, db: Session = Depends(get_db)):
    return generator.generate_workout_plan(db, request)

@app.get("/api/exercises", response_model=list[schemas.ExerciseResponse])
def get_all_exercises(db: Session = Depends(get_db)):
    return db.query(models.Exercise).all()

@app.post("/api/exercises/replace", response_model=schemas.ExerciseResponse)
def replace_exercise(request: schemas.ReplaceExerciseRequest, db: Session = Depends(get_db)):
    alternative = generator.get_alternative_exercise(db, request)
    if not alternative:
        # Jeśli nie znaleziono żadnej alternatywy, zwróć błąd lub to samo ćwiczenie
        return db.query(models.Exercise).filter(models.Exercise.id == request.current_exercise_id).first()
    return alternative

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
