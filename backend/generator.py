import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import models
import schemas
import generator_templates

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

    # Zbiór ID ćwiczeń już użytych w całym planie
    used_exercise_ids = set()

    # Rodziny ruchów zapobiegające dublowaniu tego samego wzorca na jednej sesji
    MOVEMENT_FAMILIES = {
        "row": ["row", "wiosło"],
        "pulldown": ["pulldown", "pull-up", "chin-up", "ściąg"],
        "deadlift": ["deadlift", "good morning", "martw"],
        "horizontal_press": ["bench press", "floor press", "fly", "push-up", "rozpiętk", "pompk"],
        "vertical_press": ["shoulder press", "military press", "push press", "wyciskanie nad"],
        "squat": ["squat", "leg press", "przysiad", "suwnic"],
        "lunge": ["lunge", "split squat", "step-up", "wykrok"],
        "curl": ["curl", "uginan"],
        "extension": ["extension", "pushdown", "skull crusher", "kickback", "prostowan"],
        "raise": ["raise", "shrug", "wznos", "szrugs"],
        "dip": ["dip", "poręcz"]
    }

    def get_movement_family(name: str, name_pl: str) -> str:
        name_low = f"{name} {name_pl}".lower()
        family_base = "other"
        for family, keywords in MOVEMENT_FAMILIES.items():
            if any(kw in name_low for kw in keywords):
                family_base = family
                break
                
        # Sub-kategoryzacja na podstawie chwytu
        if "reverse" in name_low or "underhand" in name_low or "podchwyt" in name_low:
            family_base += "_underhand"
        elif "close" in name_low or "narrow" in name_low or "wąsk" in name_low:
            family_base += "_close"
        elif "wide" in name_low or "szerok" in name_low:
            family_base += "_wide"
            
        return family_base

    def find_best_exercise_for_slot(slot_dict, available_exs, used_families_this_session):
        target_muscle = slot_dict["muscle"]
        keywords = slot_dict.get("kw", [])
        
        candidates = [e for e in available_exs if e.muscle_group == target_muscle]
        
        # Jeśli użytkownik wykluczył tę partię mięśniową, nie dobieramy niczego zastępczego z innych partii
        if not candidates:
            return None
            
        def score(ex):
            s = 0
            name_low = ex.name.lower()
            name_pl_low = ex.name_pl.lower() if ex.name_pl else ""
            text_to_search = f"{name_low} {name_pl_low} {ex.sub_muscle} {ex.category}".lower()
            
            # Wyrzucamy ćwiczenia typu rozciąganie, joga, dziwne mobilnościowe
            if "stretch" in name_low or "rozciąg" in name_pl_low or "90/90" in name_low or "mobility" in name_low or "yoga" in name_low:
                s -= 5000
            
            # Dopasowanie słów kluczowych z szablonu
            matched_kws = 0
            for kw in keywords:
                if kw.lower() in text_to_search:
                    s += 60
                    matched_kws += 1
                    # Bonus za ścisłe dopasowanie w samej nazwie
                    if kw.lower() in name_low or kw.lower() in name_pl_low:
                        s += 30 
                        
            # Jeśli ćwiczenie nie spełnia wymagań szablonu, spychamy je w dół
            if keywords and matched_kws == 0:
                s -= 150
            
            # Preferuj wielostawowe jeśli slot tego wymaga
            if slot_dict.get("comp") and ex.category == "Złożone":
                s += 40
                
            # WSPARCIE SPRZĘTU (Priorytetyzacja głównego wyboru)
            # Jeśli użytkownik wybrał Siłownię, chcemy sztangi i maszyny, a nie pompki (chyba że to dipy/pullupy)
            is_great_bodyweight = "pull-up" in name_low or "dip" in name_low or "podciąg" in name_pl_low or "poręcz" in name_pl_low
            
            if request.equipment == schemas.EquipmentType.gym:
                if ex.equipment == "gym": s += 50
                elif ex.equipment == "dumbbells": s += 30
                elif ex.equipment == "bodyweight":
                    if is_great_bodyweight: s += 50
                    elif "plank" in name_low or "crunch" in name_low: s += 20 # ok dla brzucha
                    else: s -= 20 # Odrzucamy bodyweight squat jeśli są sztangi!
                    
            elif request.equipment == schemas.EquipmentType.dumbbells:
                if ex.equipment == "dumbbells": s += 60
                elif ex.equipment == "bodyweight":
                    if is_great_bodyweight: s += 50
                    elif "plank" in name_low or "crunch" in name_low: s += 20
                    else: s -= 10
            
            # Ogólna kara za dziwne ćwiczenia
            if any(banned in name_low for banned in BANNED_KEYWORDS):
                s -= 2000
                
            # Filtrowanie zaawansowania
            if request.experience_level == schemas.ExperienceLevel.beginner:
                if any(adv in name_low for adv in ADVANCED_KEYWORDS) or any(inter in name_low for inter in INTERMEDIATE_KEYWORDS):
                    s -= 2000
            elif request.experience_level == schemas.ExperienceLevel.intermediate:
                if any(adv in name_low for adv in ADVANCED_KEYWORDS):
                    s -= 2000
                    
            # Bardzo surowa kara za całkowity duplikat
            if ex.id in used_exercise_ids:
                s -= 10000
                
            # Zróżnicowanie ruchu na sesji (nie robimy 3 wiosłowań pod rząd)
            fam = get_movement_family(ex.name, ex.name_pl)
            if fam != "other" and fam in used_families_this_session:
                s -= 800
                
            # Promocja ogólnie świetnych ćwiczeń
            for okw in OPTIMAL_KEYWORDS:
                if okw in name_low:
                    s += 15
                    break
                    
            return s
            
        candidates.sort(key=score, reverse=True)
        
        # Nawet jeśli znaleźliśmy kandydatów, najlepszy może mieć tragiczny wynik (np. same duplikaty lub rozciągania). 
        # Zwracamy pierwszego, chyba że baza jest skrajnie pusta.
        best_ex = candidates[0]
        used_exercise_ids.add(best_ex.id)
        
        fam = get_movement_family(best_ex.name, best_ex.name_pl)
        if fam != "other":
            used_families_this_session.add(fam)
            
        return best_ex

    # Pobranie odpowiedniego szablonu dla danego poziomu i typu
    workout_templates = generator_templates.TEMPLATES.get(workout_type, {}).get(request.experience_level, [])
    
    # Jeśli z jakiegoś powodu nie ma szablonu, fallback do PPL Beginner
    if not workout_templates:
        workout_templates = generator_templates.TEMPLATES[schemas.WorkoutType.ppl][schemas.ExperienceLevel.beginner]

    # Budowanie planu na podstawie szablonów (powtarzamy szablony, jeśli dni > ilości szablonów)
    for day in range(1, request.days_per_week + 1):
        template = workout_templates[(day - 1) % len(workout_templates)]
        day_exercises = []
        used_families_this_session = set()
        
        for slot in template["slots"]:
            # Krótki trening - omijamy niektóre ćwiczenia (np. z końca) by skrócić objętość
            if request.duration == schemas.WorkoutDuration.short and len(day_exercises) >= 4:
                 # Skracamy do max 4-5 kluczowych ćwiczeń
                 if slot["muscle"] in ["Biceps", "Triceps", "Brzuch", "Barki"] and len(day_exercises) > 4:
                     continue

            best_ex = find_best_exercise_for_slot(slot, available_exercises, used_families_this_session)
            if best_ex:
                volume = assign_volume(best_ex, request.goal, request.duration)
                ex_resp = schemas.ExerciseResponse.model_validate(best_ex)
                ex_resp.sets = volume["sets"]
                ex_resp.reps = volume["reps"]
                ex_resp.rest_time = volume["rest_time"]
                day_exercises.append(ex_resp)
                
        days_response.append(schemas.WorkoutDayResponse(day=day, focus=template["focus"], exercises=day_exercises))

    # 4. Obliczanie sugestii dietetycznych
    nutrition = calculate_suggested_nutrition(
        request.weight, 
        request.height, 
        request.goal, 
        request.days_per_week
    )

    return schemas.PlanResponse(days=days_response, nutrition=nutrition)
