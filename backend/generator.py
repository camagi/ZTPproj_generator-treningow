import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import models
import schemas

def get_exercises_by_category(exercises: List[models.Exercise], category: str) -> List[models.Exercise]:
    return [ex for ex in exercises if ex.category == category]

def assign_volume(exercise: models.Exercise, goal: schemas.TrainingGoal) -> Dict[str, Any]:
    if goal == schemas.TrainingGoal.strength:
        if exercise.category == "Złożone":
            return {"sets": 5, "reps": "5"}
        else:
            return {"sets": 3, "reps": "8-10"}
    elif goal == schemas.TrainingGoal.reduction:
        if exercise.category == "Złożone":
            return {"sets": 3, "reps": "12-15"}
        else:
            return {"sets": 3, "reps": "15-20"}
    else:  # hypertrophy
        if exercise.category == "Złożone":
            return {"sets": 4, "reps": "8-10"}
        else:
            return {"sets": 3, "reps": "10-12"}

def generate_workout_plan(db: Session, request: schemas.PlanRequest) -> schemas.PlanResponse:
    available_exercises = db.query(models.Exercise).filter(
        models.Exercise.muscle_group.notin_(request.contraindicated_muscles)
    ).all()

    exercises_by_muscle = {}
    for ex in available_exercises:
        if ex.muscle_group not in exercises_by_muscle:
            exercises_by_muscle[ex.muscle_group] = []
        exercises_by_muscle[ex.muscle_group].append(ex)

    days_response = []
    
    # 1. Ustalenie typu treningu
    workout_type = request.workout_type
    
    if not workout_type:
        if request.experience_level == schemas.ExperienceLevel.beginner:
            # Początkujący zawsze dostają FBW lub ewentualnie podział góra/dół (ale tu uprościmy do FBW dla bezpieczeństwa)
            workout_type = schemas.WorkoutType.fbw
        else:
            if request.days_per_week <= 2:
                workout_type = schemas.WorkoutType.fbw
            elif request.days_per_week == 3:
                workout_type = schemas.WorkoutType.ppl
            else:
                workout_type = schemas.WorkoutType.split

    # 2. Ustalenie mnożnika objętości (ile ćwiczeń na partię)
    volume_multiplier = 1
    if request.experience_level == schemas.ExperienceLevel.beginner:
        volume_multiplier = 1 # Mało ćwiczeń, głównie złożone
    elif request.experience_level == schemas.ExperienceLevel.intermediate:
        volume_multiplier = 2
    elif request.experience_level == schemas.ExperienceLevel.advanced:
        volume_multiplier = 3

    # Funkcja pomocnicza do wybierania ćwiczeń
    def pick_exercises(muscle: str, count: int, prefer_compound: bool = False) -> List[models.Exercise]:
        if muscle not in exercises_by_muscle or not exercises_by_muscle[muscle]:
            return []
        
        available = exercises_by_muscle[muscle]
        chosen = []
        
        if prefer_compound:
            compounds = get_exercises_by_category(available, "Złożone")
            if compounds:
                # Wybierz przynajmniej jedno złożone jeśli to możliwe
                chosen.append(random.choice(compounds))
                available = [ex for ex in available if ex not in chosen]
                count -= 1
                
        # Dobierz resztę
        num_to_choose = min(count, len(available))
        if num_to_choose > 0:
            chosen.extend(random.sample(available, num_to_choose))
            
        return chosen

    # 3. Generowanie w zależności od typu
    if workout_type == schemas.WorkoutType.fbw:
        for day in range(1, request.days_per_week + 1):
            day_exercises = []
            # FBW - po 1-2 ćwiczenia na główną partię
            muscles_order = ["Nogi", "Plecy", "Klatka", "Barki", "Biceps", "Triceps", "Brzuch"]
            for group in muscles_order:
                # Dla początkujących 1 ćwiczenie, dla zaawansowanych może być 2 dla dużych partii
                ex_count = 1 if request.experience_level == schemas.ExperienceLevel.beginner else (2 if group in ["Nogi", "Plecy", "Klatka"] and volume_multiplier > 1 else 1)
                prefer_comp = request.experience_level == schemas.ExperienceLevel.beginner
                
                picked = pick_exercises(group, ex_count, prefer_compound=prefer_comp)
                for ex in picked:
                    volume = assign_volume(ex, request.goal)
                    ex_resp = schemas.ExerciseResponse.model_validate(ex)
                    ex_resp.sets = volume["sets"]
                    ex_resp.reps = volume["reps"]
                    day_exercises.append(ex_resp)
            
            days_response.append(schemas.WorkoutDayResponse(day=day, focus="Full Body Workout", exercises=day_exercises))

    elif workout_type == schemas.WorkoutType.ppl:
        splits = [
            {"name": "Push (Klatka, Barki, Triceps)", "muscles": ["Klatka", "Barki", "Triceps"]},
            {"name": "Pull (Plecy, Biceps, Brzuch)", "muscles": ["Plecy", "Biceps", "Brzuch"]},
            {"name": "Legs (Nogi)", "muscles": ["Nogi"]}
        ]
        # Pętla przez ilość dni, powtarzając split
        for day in range(1, request.days_per_week + 1):
            split = splits[(day - 1) % len(splits)]
            day_exercises = []
            
            for group in split["muscles"]:
                ex_count = volume_multiplier if group in ["Klatka", "Plecy", "Nogi"] else max(1, volume_multiplier - 1)
                prefer_comp = request.experience_level != schemas.ExperienceLevel.advanced # Zaawansowani mają już dużo izolacji
                
                picked = pick_exercises(group, ex_count, prefer_compound=prefer_comp)
                for ex in picked:
                    volume = assign_volume(ex, request.goal)
                    ex_resp = schemas.ExerciseResponse.model_validate(ex)
                    ex_resp.sets = volume["sets"]
                    ex_resp.reps = volume["reps"]
                    day_exercises.append(ex_resp)
                    
            days_response.append(schemas.WorkoutDayResponse(day=day, focus=split["name"], exercises=day_exercises))

    elif workout_type == schemas.WorkoutType.split:
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
                # W splicie objętość na partię jest zazwyczaj największa, bo trenujemy ją raz w tygodniu
                base_count = 3 if group in ["Klatka", "Plecy", "Nogi", "Barki"] else 2
                # Skalujemy przez mnożnik zaawansowania (ale pilnujemy maksimum)
                ex_count = min(base_count + (volume_multiplier - 1), 5) 
                if split["name"] == "Full Body (Uzupełniający)":
                     ex_count = 1
                     
                picked = pick_exercises(group, ex_count, prefer_compound=True)
                for ex in picked:
                    volume = assign_volume(ex, request.goal)
                    ex_resp = schemas.ExerciseResponse.model_validate(ex)
                    ex_resp.sets = volume["sets"]
                    ex_resp.reps = volume["reps"]
                    day_exercises.append(ex_resp)
                    
            days_response.append(schemas.WorkoutDayResponse(day=day, focus=split["name"], exercises=day_exercises))

    return schemas.PlanResponse(days=days_response)
