import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import models
import schemas

def get_exercises_by_category(exercises: List[models.Exercise], category: str) -> List[models.Exercise]:
    return [ex for ex in exercises if ex.category == category]

def assign_volume(exercise: models.Exercise, goal: schemas.TrainingGoal, duration: schemas.WorkoutDuration) -> Dict[str, Any]:
    sets = 3
    reps = "10-12"
    rest = "60-90s"

    # Podstawowe przypisanie na podstawie celu
    if goal == schemas.TrainingGoal.strength:
        if exercise.category == "Złożone":
            sets, reps, rest = 5, "5", "180s"
        else:
            sets, reps, rest = 3, "8-10", "120s"
    elif goal == schemas.TrainingGoal.reduction:
        if exercise.category == "Złożone":
            sets, reps, rest = 3, "12-15", "60s"
        else:
            sets, reps, rest = 3, "15-20", "45s"
    else:  # hypertrophy
        if exercise.category == "Złożone":
            sets, reps, rest = 4, "8-10", "90-120s"
        else:
            sets, reps, rest = 3, "10-12", "60-90s"

    # Korekta na podstawie czasu trwania (duration)
    if duration == schemas.WorkoutDuration.short:
        sets = max(2, sets - 1)
        # Skracamy przerwy jeśli to nie jest trening siłowy
        if goal != schemas.TrainingGoal.strength:
            if "90" in rest: rest = "60s"
            elif "60" in rest: rest = "45s"
    elif duration == schemas.WorkoutDuration.long:
        if exercise.category == "Izolowane":
            sets += 1 # Więcej pracy nad detalami przy długim treningu

    return {"sets": sets, "reps": reps, "rest_time": rest}

def calculate_suggested_nutrition(weight: float, height: float, goal: schemas.TrainingGoal, days_per_week: int) -> schemas.NutritionResponse:
    # Uproszczony wzór BMR (średnia dla dorosłego, wiek ~30, neutralny płciowo)
    bmr = (10 * weight) + (6.25 * height) - (5 * 30)
    
    # Mnożnik aktywności TDEE
    if days_per_week <= 2:
        multiplier = 1.3
    elif days_per_week == 3:
        multiplier = 1.5
    else:
        multiplier = 1.7
        
    tdee = bmr * multiplier
    
    # Dostosowanie do celu
    if goal == schemas.TrainingGoal.reduction:
        target_calories = tdee - 400
    elif goal == schemas.TrainingGoal.hypertrophy:
        target_calories = tdee + 300
    else: # strength
        target_calories = tdee + 100
        
    # Makroskładniki
    protein_g = int(weight * 2.0)
    fat_g = int(weight * 0.9)
    # 1g B = 4 kcal, 1g T = 9 kcal, 1g W = 4 kcal
    remaining_calories = target_calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = int(max(0, remaining_calories / 4))
    
    return schemas.NutritionResponse(
        target_calories=int(target_calories),
        protein_g=protein_g,
        fat_g=fat_g,
        carbs_g=carbs_g
    )

def get_alternative_exercise(db: Session, request: schemas.ReplaceExerciseRequest) -> models.Exercise:
    # Szukamy ćwiczeń na tę samą partię, o tej samej kategorii i sprzęcie, ale o innym ID
    query = db.query(models.Exercise).filter(
        models.Exercise.muscle_group == request.muscle_group,
        models.Exercise.equipment == request.equipment,
        models.Exercise.id != request.current_exercise_id
    )
    
    if request.category:
        query = query.filter(models.Exercise.category == request.category)
        
    alternatives = query.all()
    
    if not alternatives:
        # Jeśli nie ma alternatywy w tej samej kategorii, spróbuj bez filtra kategorii
        alternatives = db.query(models.Exercise).filter(
            models.Exercise.muscle_group == request.muscle_group,
            models.Exercise.equipment == request.equipment,
            models.Exercise.id != request.current_exercise_id
        ).all()
        
    if not alternatives:
        return None
        
    return random.choice(alternatives)

def generate_workout_plan(db: Session, request: schemas.PlanRequest) -> schemas.PlanResponse:
    available_exercises = db.query(models.Exercise).filter(
        models.Exercise.muscle_group.notin_(request.contraindicated_muscles),
        models.Exercise.equipment == request.equipment.value
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

    # Korekta ilości ćwiczeń pod kątem czasu trwania
    if request.duration == schemas.WorkoutDuration.short:
        volume_multiplier = max(1, volume_multiplier - 1)

    OPTIMAL_KEYWORDS = [
        "barbell bench press", "barbell squat", "barbell deadlift", "pull-up", "push-up",
        "military press", "shoulder press", "bent over row", "lat pulldown", "dips",
        "lunge", "barbell curl", "triceps pushdown", "plank", "crunch", "leg press",
        "dumbbell bench press", "lateral raise", "calf raise", "romanian deadlift",
        "dumbbell curl", "leg extension", "leg curl", "dumbbell row"
    ]

    def score_exercise(ex: models.Exercise) -> int:
        score = 0
        name_low = ex.name.lower()
        
        if ex.category == "Złożone":
            score += 20
            
        # Promuj "najlepsze" podstawowe ćwiczenia
        for kw in OPTIMAL_KEYWORDS:
            if kw in name_low:
                score += 50
                # Ścisłe dopasowanie dostaje jeszcze więcej punktów
                if kw == name_low:
                    score += 20
                break
                
        # Deklasuj udziwnienia w generowaniu
        if "smith machine" in name_low or "band" in name_low or "cable" in name_low or "stability ball" in name_low or "one-arm" in name_low or "single" in name_low or "seated" in name_low:
            score -= 15
            
        # Niewielki element losowości, żeby plany nie były identyczne w 100% każdego dnia, ale w 90%
        # Nie dajemy tu random, bo chcemy pełnej standaryzacji przy pierwszym generowaniu
            
        return score

    # Zbiór ID ćwiczeń już użytych w całym planie
    used_exercise_ids = set()

    # Funkcja pomocnicza do wybierania ćwiczeń
    def pick_exercises(muscle: str, count: int, prefer_compound: bool = False) -> List[models.Exercise]:
        if muscle not in exercises_by_muscle or not exercises_by_muscle[muscle]:
            return []
        
        available = exercises_by_muscle[muscle].copy()
        
        # Sortowanie: najpierw po ocenie (malejąco), potem odrzucamy użyte (na koniec listy)
        available.sort(key=lambda ex: (0 if ex.id in used_exercise_ids else 1, score_exercise(ex)), reverse=True)
        
        chosen = []
        
        if prefer_compound:
            compounds = [ex for ex in available if ex.category == "Złożone"]
            if compounds:
                best_compound = compounds[0]
                chosen.append(best_compound)
                available.remove(best_compound)
                used_exercise_ids.add(best_compound.id)
                count -= 1
                
        # Dobierz resztę
        num_to_choose = min(count, len(available))
        if num_to_choose > 0:
            selected = available[:num_to_choose]
            chosen.extend(selected)
            for ex in selected:
                used_exercise_ids.add(ex.id)
            
        return chosen

    # 3. Generowanie w zależności od typu
    if workout_type == schemas.WorkoutType.fbw:
        for day in range(1, request.days_per_week + 1):
            day_exercises = []
            # FBW - po 1-2 ćwiczenia na główną partię
            muscles_order = ["Nogi", "Plecy", "Klatka", "Barki", "Biceps", "Triceps", "Brzuch"]
            for group in muscles_order:
                # Krótki trening: tylko po 1 ćwiczeniu na mniejsze partie
                if request.duration == schemas.WorkoutDuration.short and group in ["Biceps", "Triceps", "Brzuch"]:
                    ex_count = 1
                else:
                    ex_count = 1 if request.experience_level == schemas.ExperienceLevel.beginner else (2 if group in ["Nogi", "Plecy", "Klatka"] and volume_multiplier > 1 else 1)
                
                prefer_comp = request.experience_level == schemas.ExperienceLevel.beginner or request.duration == schemas.WorkoutDuration.short
                
                picked = pick_exercises(group, ex_count, prefer_compound=prefer_comp)
                for ex in picked:
                    volume = assign_volume(ex, request.goal, request.duration)
                    ex_resp = schemas.ExerciseResponse.model_validate(ex)
                    ex_resp.sets = volume["sets"]
                    ex_resp.reps = volume["reps"]
                    ex_resp.rest_time = volume["rest_time"]
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
                    volume = assign_volume(ex, request.goal, request.duration)
                    ex_resp = schemas.ExerciseResponse.model_validate(ex)
                    ex_resp.sets = volume["sets"]
                    ex_resp.reps = volume["reps"]
                    ex_resp.rest_time = volume["rest_time"]
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
                
                if request.duration == schemas.WorkoutDuration.short:
                    ex_count = max(2, ex_count - 1)

                if split["name"] == "Full Body (Uzupełniający)":
                     ex_count = 1
                     
                picked = pick_exercises(group, ex_count, prefer_compound=True)
                for ex in picked:
                    volume = assign_volume(ex, request.goal, request.duration)
                    ex_resp = schemas.ExerciseResponse.model_validate(ex)
                    ex_resp.sets = volume["sets"]
                    ex_resp.reps = volume["reps"]
                    ex_resp.rest_time = volume["rest_time"]
                    day_exercises.append(ex_resp)
                    
            days_response.append(schemas.WorkoutDayResponse(day=day, focus=split["name"], exercises=day_exercises))

    # 4. Obliczanie sugestii dietetycznych
    nutrition = calculate_suggested_nutrition(
        request.weight, 
        request.height, 
        request.goal, 
        request.days_per_week
    )

    return schemas.PlanResponse(days=days_response, nutrition=nutrition)
