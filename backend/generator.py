import random
from typing import List
from sqlalchemy.orm import Session
import models
import schemas

def generate_workout_plan(db: Session, request: schemas.PlanRequest) -> schemas.PlanResponse:
    # Pobranie wszystkich ćwiczeń, wykluczając te z zakazanych partii
    available_exercises = db.query(models.Exercise).filter(
        models.Exercise.muscle_group.notin_(request.contraindicated_muscles)
    ).all()

    # Grupowanie wg partii mięśniowej
    exercises_by_muscle = {}
    for ex in available_exercises:
        if ex.muscle_group not in exercises_by_muscle:
            exercises_by_muscle[ex.muscle_group] = []
        exercises_by_muscle[ex.muscle_group].append(ex)

    days_response = []
    
    if request.days_per_week <= 2:
        # Full Body Workout (FBW)
        for day in range(1, request.days_per_week + 1):
            day_exercises = []
            # Staramy się wylosować po 1 ćwiczeniu na każdą główną partię
            for group in ["Nogi", "Plecy", "Klatka", "Barki", "Biceps", "Triceps", "Brzuch"]:
                if group in exercises_by_muscle and exercises_by_muscle[group]:
                    chosen = random.choice(exercises_by_muscle[group])
                    day_exercises.append(schemas.ExerciseResponse.model_validate(chosen))
            days_response.append(schemas.WorkoutDayResponse(day=day, focus="Full Body Workout", exercises=day_exercises))

    elif request.days_per_week == 3:
        # Push / Pull / Legs
        splits = [
            {"name": "Push (Klatka, Barki, Triceps)", "muscles": ["Klatka", "Barki", "Triceps"]},
            {"name": "Pull (Plecy, Biceps, Brzuch)", "muscles": ["Plecy", "Biceps", "Brzuch"]},
            {"name": "Legs (Nogi)", "muscles": ["Nogi"]}
        ]
        for day in range(1, 4):
            split = splits[day-1]
            day_exercises = []
            for group in split["muscles"]:
                if group in exercises_by_muscle and exercises_by_muscle[group]:
                    available_for_group = exercises_by_muscle[group]
                    num_to_choose = min(2, len(available_for_group))
                    chosen = random.sample(available_for_group, num_to_choose)
                    for c in chosen:
                        day_exercises.append(schemas.ExerciseResponse.model_validate(c))
            days_response.append(schemas.WorkoutDayResponse(day=day, focus=split["name"], exercises=day_exercises))

    else:
        # 4-5 dni: Split
        splits = [
            {"name": "Klatka + Triceps", "muscles": ["Klatka", "Triceps"]},
            {"name": "Plecy + Biceps", "muscles": ["Plecy", "Biceps"]},
            {"name": "Nogi + Brzuch", "muscles": ["Nogi", "Brzuch"]},
            {"name": "Barki", "muscles": ["Barki"]},
            {"name": "Full Body (Uzupełniający)", "muscles": ["Klatka", "Plecy", "Nogi", "Barki", "Biceps", "Triceps"]}
        ]
        for day in range(1, request.days_per_week + 1):
            split = splits[(day - 1) % len(splits)]
            day_exercises = []
            for group in split["muscles"]:
                if group in exercises_by_muscle and exercises_by_muscle[group]:
                    available_for_group = exercises_by_muscle[group]
                    num_to_choose = min(3 if group in ["Plecy", "Nogi", "Klatka"] else 2, len(available_for_group))
                    chosen = random.sample(available_for_group, num_to_choose)
                    for c in chosen:
                        day_exercises.append(schemas.ExerciseResponse.model_validate(c))
            days_response.append(schemas.WorkoutDayResponse(day=day, focus=split["name"], exercises=day_exercises))

    return schemas.PlanResponse(days=days_response)
