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

def get_allowed_equipment(requested_equipment: str) -> List[str]:
    if requested_equipment == "gym":
        return ["gym", "dumbbells", "bodyweight", "bands"]
    elif requested_equipment == "dumbbells":
        return ["dumbbells", "bodyweight"]
    elif requested_equipment == "bands":
        return ["bands", "bodyweight"]
    else:
        return ["bodyweight"]

def get_alternative_exercise(db: Session, request: schemas.ReplaceExerciseRequest) -> models.Exercise:
    allowed_eq = get_allowed_equipment(request.equipment)
    # Szukamy ćwiczeń na tę samą partię, o tej samej kategorii i sprzęcie, ale o innym ID
    query = db.query(models.Exercise).filter(
        models.Exercise.muscle_group == request.muscle_group,
        models.Exercise.equipment.in_(allowed_eq),
        models.Exercise.id != request.current_exercise_id
    )
    
    if request.category:
        query = query.filter(models.Exercise.category == request.category)
        
    alternatives = query.all()
    
    if not alternatives:
        # Jeśli nie ma alternatywy w tej samej kategorii, spróbuj bez filtra kategorii
        alternatives = db.query(models.Exercise).filter(
            models.Exercise.muscle_group == request.muscle_group,
            models.Exercise.equipment.in_(allowed_eq),
            models.Exercise.id != request.current_exercise_id
        ).all()
        
    if not alternatives:
        return None
        
    return random.choice(alternatives)

def generate_workout_plan(db: Session, request: schemas.PlanRequest) -> schemas.PlanResponse:
    allowed_eq = get_allowed_equipment(request.equipment.value)
    available_exercises = db.query(models.Exercise).filter(
        models.Exercise.muscle_group.notin_(request.contraindicated_muscles),
        models.Exercise.equipment.in_(allowed_eq)
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
        "dumbbell curl", "leg extension", "leg curl", "dumbbell row", "face pull",
        "overhead press", "bulgarian split squat", "front squat"
    ]
    
    BANNED_KEYWORDS = [
        "atlas", "stone", "tire", "sled", "battling rope", "yoke", "sandbag", "prowler",
        "rickshaw", "car deadlift", "sledgehammer", "chain", "chains", "band ", "bands ",
        "stability ball", "bosu", "neck", "suspension", "trx", "board press", "guillotine",
        "floor press", "power snatch", "clean and jerk", "rocky", "otiz", "zercher"
    ]
    
    ADVANCED_KEYWORDS = [
        "muscle up", "muscle-up", "snatch", "clean", "jerk", "front lever", "back lever",
        "planche", "human flag", "pistol squat", "handstand", "dragon flag", "kipping"
    ]
    
    INTERMEDIATE_KEYWORDS = [
        "deadlift", "front squat", "overhead squat", "good morning", "bulgarian",
        "hanging leg raise", "ab wheel", "rollout"
    ]

    def score_exercise(ex: models.Exercise) -> int:
        score = 0
        name_low = ex.name.lower()
        
        # Odrzuć dziwne ćwiczenia strongman/crossfit jeśli szukamy standardowego planu na siłownię
        if any(banned in name_low for banned in BANNED_KEYWORDS):
            return -1000 # Gwarancja, że nie wylosuje się jako domyślne
            
        # Odrzucanie zaawansowanych ćwiczeń dla początkujących
        if request.experience_level == schemas.ExperienceLevel.beginner:
            if any(adv in name_low for adv in ADVANCED_KEYWORDS) or any(inter in name_low for inter in INTERMEDIATE_KEYWORDS):
                return -1000
                
        # Odrzucanie bardzo zaawansowanych ćwiczeń dla średniozaawansowanych
        if request.experience_level == schemas.ExperienceLevel.intermediate:
            if any(adv in name_low for adv in ADVANCED_KEYWORDS):
                return -1000
        
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
                
        # Deklasuj nieoptymalne modyfikatory (np. ćwiczenia jednorącz na maszynie zamiast klasyki)
        if "smith machine" in name_low or "one-arm" in name_low or "single" in name_low or "behind the neck" in name_low:
            score -= 25
            
        # Promuj klasyczny sprzęt jeśli użytkownik wybrał siłownię
        if request.equipment == schemas.EquipmentType.gym:
            if "barbell" in name_low or "dumbbell" in name_low or "cable" in name_low or "machine" in name_low:
                score += 10
            
        return score

    # Zbiór ID ćwiczeń już użytych w całym planie
    used_exercise_ids = set()

    # Rodziny ruchów zapobiegające dublowaniu tego samego wzorca na jednej sesji
    MOVEMENT_FAMILIES = {
        "row": ["row"],
        "pulldown": ["pulldown", "pull-up", "chin-up"],
        "deadlift": ["deadlift", "good morning"],
        "horizontal_press": ["bench press", "floor press", "fly", "push-up"],
        "vertical_press": ["shoulder press", "military press", "push press"],
        "squat": ["squat", "leg press"],
        "lunge": ["lunge", "split squat", "step-up"],
        "curl": ["curl"],
        "extension": ["extension", "pushdown", "skull crusher", "kickback"],
        "raise": ["raise", "shrug"],
        "dip": ["dip"]
    }

    def get_movement_family(name: str) -> str:
        name_low = name.lower()
        family_base = "other"
        for family, keywords in MOVEMENT_FAMILIES.items():
            if any(kw in name_low for kw in keywords):
                family_base = family
                break
                
        # Sub-kategoryzacja na podstawie chwytu, aby zróżnicować np. wiosłowanie nachwytem od podchwytu
        if "reverse" in name_low or "underhand" in name_low or "podchwyt" in name_low:
            family_base += "_underhand"
        elif "close" in name_low or "narrow" in name_low or "wąsk" in name_low:
            family_base += "_close"
        elif "wide" in name_low or "szerok" in name_low:
            family_base += "_wide"
            
        return family_base

    # Funkcja pomocnicza do wybierania ćwiczeń
    def pick_exercises(muscle: str, count: int, prefer_compound: bool = False) -> List[models.Exercise]:
        if muscle not in exercises_by_muscle or not exercises_by_muscle[muscle]:
            return []
        
        # Filtrujemy na wstępie te skrajnie niechciane
        available = [ex for ex in exercises_by_muscle[muscle] if score_exercise(ex) > -500]
        
        if not available: # Fallback jeśli na daną partię zostały same dziwne ćwiczenia
             available = exercises_by_muscle[muscle].copy()
        
        chosen = []
        used_families_this_session = set()
        
        # Wewnętrzna funkcja sortująca, która dodatkowo karze za duplikaty ruchów
        def dynamic_score(ex: models.Exercise) -> tuple:
            # Tupla sortująca:
            # 1. Nie użyto nigdy w planie (1) vs użyto (0)
            # 2. Nie użyto rodziny ruchu w TEJ SESJI na TĄ PARTIĘ (1) vs użyto (0) - Drastyczna kara
            # 3. Bazowy wynik punktowy
            is_new = 0 if ex.id in used_exercise_ids else 1
            family = get_movement_family(ex.name)
            
            # Wymuszamy, by priorytetem był CAŁKIEM NOWY RUCH (np. po wyciskaniu nie bierzemy znowu wyciskania, tylko rozpiętki/dipsy)
            is_new_family = 0 if family in used_families_this_session else 1000
            
            # Jeśli rodzina jest zajęta, to ma ujemny priorytet, aby ustąpić miejsca innym
            family_score = is_new_family
            
            return (is_new, family_score, score_exercise(ex))

        # Dobieramy po jednym ćwiczeniu odświeżając sortowanie
        while count > 0 and available:
            available.sort(key=dynamic_score, reverse=True)
            
            # Jeśli potrzebujemy złożeń, upewnijmy się, że na start bierzemy złożone
            best_ex = None
            if prefer_compound:
                for ex in available:
                    if ex.category == "Złożone":
                        best_ex = ex
                        break
            
            if not best_ex:
                best_ex = available[0]
                
            chosen.append(best_ex)
            available.remove(best_ex)
            used_exercise_ids.add(best_ex.id)
            
            fam = get_movement_family(best_ex.name)
            if fam != "other":
                used_families_this_session.add(fam)
                
            count -= 1
            prefer_compound = False # Tylko pierwsze musiało być złożone
            
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
