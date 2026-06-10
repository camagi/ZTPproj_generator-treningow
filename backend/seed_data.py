import json
import os
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models

# Inicjalizacja bazy
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

MUSCLE_MAPPING = {
    "chest": "Klatka",
    "middle back": "Plecy",
    "lats": "Plecy",
    "lower back": "Plecy",
    "traps": "Plecy",
    "quadriceps": "Nogi",
    "hamstrings": "Nogi",
    "glutes": "Nogi",
    "calves": "Nogi",
    "adductors": "Nogi",
    "abductors": "Nogi",
    "shoulders": "Barki",
    "biceps": "Biceps",
    "triceps": "Triceps",
    "abdominals": "Brzuch",
    "forearms": "Biceps" # Uproszczenie
}

EQUIPMENT_MAPPING = {
    "body only": "bodyweight",
    "dumbbell": "dumbbells",
    "bands": "bands",
}

def seed():
    db = SessionLocal()
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        exercises_dir = os.path.join(parent_dir, "cwiczenia", "exercises")
        
        if not os.path.exists(exercises_dir):
            print(f"Directory not found: {exercises_dir}")
            return

        print("Wypełnianie bazy danymi z plików JSON...")
        count = 0
        for filename in os.listdir(exercises_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(exercises_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        
                        # Mapowanie grupy mięśniowej
                        primary_muscle = data.get("primaryMuscles", [""])[0]
                        muscle_group = MUSCLE_MAPPING.get(primary_muscle, "Inne")
                        
                        # Mapowanie sprzętu
                        equipment_raw = data.get("equipment", "gym")
                        if equipment_raw is None: equipment_raw = "body only"
                        equipment = EQUIPMENT_MAPPING.get(equipment_raw, "gym")
                        
                        # Mapowanie kategorii
                        mechanic = data.get("mechanic")
                        category = "Złożone" if mechanic == "compound" else "Izolowane"
                        
                        # Instrukcje i zdjęcia jako JSON
                        instructions = json.dumps(data.get("instructions", []))
                        images = json.dumps([f"exercises/{img}" for ex_img in data.get("images", []) for img in [ex_img]])
                        # Wait, the images in JSON are relative to 'exercises/' folder?
                        # Example: "3_4_Sit-Up/0.jpg"
                        # My mount is app.mount("/exercises-static", StaticFiles(directory=cwiczenia_path))
                        # So the URL should be /exercises-static/exercises/3_4_Sit-Up/0.jpg
                        images = json.dumps([f"exercises/{img}" for img in data.get("images", [])])
                        
                        exercise = models.Exercise(
                            name=data.get("name", filename),
                            muscle_group=muscle_group,
                            category=category,
                            equipment=equipment,
                            description=data.get("instructions", [""])[0] if data.get("instructions") else "",
                            instructions=instructions,
                            images=images
                        )
                        db.add(exercise)
                        count += 1
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        
        db.commit()
        print(f"Zakończono wypełnianie bazy. Dodano {count} ćwiczeń.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
