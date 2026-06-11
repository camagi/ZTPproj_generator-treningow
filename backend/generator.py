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

    if duration == schemas.WorkoutDuration.short:
        sets = max(2, sets - 1)
        if goal != schemas.TrainingGoal.strength:
            if "90" in rest: rest = "60s"
            elif "60" in rest: rest = "45s"
    elif duration == schemas.WorkoutDuration.long:
        if exercise.category == "Izolowane":
            sets += 1 

    return {"sets": sets, "reps": reps, "rest_time": rest}

def calculate_suggested_nutrition(weight: float, height: float, goal: schemas.TrainingGoal, days_per_week: int) -> schemas.NutritionResponse:
    bmr = (10 * weight) + (6.25 * height) - (5 * 30)
    if days_per_week <= 2: multiplier = 1.3
    elif days_per_week == 3: multiplier = 1.5
    else: multiplier = 1.7
    tdee = bmr * multiplier
    
    if goal == schemas.TrainingGoal.reduction: target_calories = tdee - 400
    elif goal == schemas.TrainingGoal.hypertrophy: target_calories = tdee + 300
    else: target_calories = tdee + 100
        
    protein_g = int(weight * 2.0)
    fat_g = int(weight * 0.9)
    remaining_calories = target_calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = int(max(0, remaining_calories / 4))
    
    return schemas.NutritionResponse(target_calories=int(target_calories), protein_g=protein_g, fat_g=fat_g, carbs_g=carbs_g)

def get_allowed_equipment(requested_equipment: str) -> List[str]:
    if requested_equipment == "gym": return ["gym", "dumbbells", "bodyweight", "bands"]
    elif requested_equipment == "dumbbells": return ["dumbbells", "bodyweight"]
    elif requested_equipment == "bands": return ["bands", "bodyweight"]
    else: return ["bodyweight"]

def get_alternative_exercise(db: Session, request: schemas.ReplaceExerciseRequest) -> models.Exercise:
    allowed_eq = get_allowed_equipment(request.equipment)
    # Bazowe zapytanie: ta sama partia, dozwolony sprzęt, inne ID, nie rozgrzewka
    base_query = db.query(models.Exercise).filter(
        models.Exercise.muscle_group == request.muscle_group,
        models.Exercise.equipment.in_(allowed_eq),
        models.Exercise.id != request.current_exercise_id,
        models.Exercise.is_warmup == 0
    )
    
    # Próba 1: Ta sama kategoria (Złożone/Izolowane)
    query = base_query
    if request.category:
        query = query.filter(models.Exercise.category == request.category)
    
    alternatives = query.all()
    
    # Próba 2: Jeśli nie ma, szukaj w dowolnej kategorii na tę partię
    if not alternatives:
        alternatives = base_query.all()
        
    # Próba 3: Jeśli nadal nie ma, szukaj w CAŁEJ bazie dla tej partii (nawet inny sprzęt)
    if not alternatives:
        alternatives = db.query(models.Exercise).filter(
            models.Exercise.muscle_group == request.muscle_group,
            models.Exercise.id != request.current_exercise_id,
            models.Exercise.is_warmup == 0
        ).all()
        
    return random.choice(alternatives) if alternatives else None

def generate_workout_plan(db: Session, request: schemas.PlanRequest) -> schemas.PlanResponse:
    allowed_eq = get_allowed_equipment(request.equipment.value)
    
    # Podział na bazę główną i rozgrzewkową
    available_exercises = db.query(models.Exercise).filter(
        models.Exercise.muscle_group.notin_(request.contraindicated_muscles),
        models.Exercise.equipment.in_(allowed_eq),
        models.Exercise.is_warmup == 0
    ).all()

    if not available_exercises:
        raise ValueError("No exercises available for the selected constraints.")

    warmup_pool = db.query(models.Exercise).filter(
        models.Exercise.is_warmup == 1,
        models.Exercise.equipment.in_(allowed_eq)
    ).all()

    exercises_by_muscle = {}
    for ex in available_exercises:
        if ex.muscle_group not in exercises_by_muscle: exercises_by_muscle[ex.muscle_group] = []
        exercises_by_muscle[ex.muscle_group].append(ex)

    days_response = []
    workout_type = request.workout_type or (schemas.WorkoutType.fbw if request.experience_level == schemas.ExperienceLevel.beginner or request.days_per_week <= 2 else (schemas.WorkoutType.ppl if request.days_per_week == 3 else schemas.WorkoutType.split))

    BANNED_KEYWORDS = ["atlas", "stone", "tire", "sled", "battling rope", "yoke", "sandbag", "prowler", "rickshaw", "car deadlift", "sledgehammer", "chain", "chains", "stability ball", "bosu", "neck", "suspension", "trx", "board press", "guillotine", "floor press", "power snatch", "clean and jerk", "rocky", "otiz", "zercher", "handstand"]
    ADVANCED_KEYWORDS = ["muscle up", "muscle-up", "snatch", "clean", "jerk", "front lever", "back lever", "planche", "human flag", "pistol squat", "handstand", "dragon flag", "kipping", "vertical pushup"]
    INTERMEDIATE_KEYWORDS = ["deadlift", "front squat", "overhead squat", "good morning", "bulgarian", "hanging leg raise", "ab wheel", "rollout"]
    OPTIMAL_KEYWORDS = ["barbell bench press", "barbell squat", "barbell deadlift", "pull-up", "push-up", "military press", "shoulder press", "bent over row", "lat pulldown", "dips", "lunge", "barbell curl", "triceps pushdown", "plank", "crunch", "leg press", "dumbbell bench press", "lateral raise", "calf raise", "romanian deadlift", "dumbbell curl", "leg extension", "leg curl", "dumbbell row", "face pull", "overhead press", "bulgarian split squat", "front squat"]

    used_exercise_ids = set()
    MOVEMENT_FAMILIES = {"row": ["row", "wiosło"], "pulldown": ["pulldown", "pull-up", "chin-up", "ściąg"], "deadlift": ["deadlift", "good morning", "martw"], "horizontal_press": ["bench press", "floor press", "fly", "push-up", "rozpiętk", "pompk"], "vertical_press": ["shoulder press", "military press", "push press", "wyciskanie nad"], "squat": ["squat", "leg press", "przysiad", "suwnic"], "lunge": ["lunge", "split squat", "step-up", "wykrok"], "curl": ["curl", "uginan"], "extension": ["extension", "pushdown", "skull crusher", "kickback", "prostowan"], "raise": ["raise", "shrug", "wznos", "szrugs"], "dip": ["dip", "poręcz"]}

    def get_movement_family(name: str, name_pl: str) -> str:
        name_low = f"{name} {name_pl}".lower()
        family_base = "other"
        for family, keywords in MOVEMENT_FAMILIES.items():
            if any(kw in name_low for kw in keywords):
                family_base = family
                break
        if "reverse" in name_low or "underhand" in name_low or "podchwyt" in name_low: family_base += "_underhand"
        elif "close" in name_low or "narrow" in name_low or "wąsk" in name_low: family_base += "_close"
        elif "wide" in name_low or "szerok" in name_low: family_base += "_wide"
        return family_base

    def is_exercise_disallowed(ex: models.Exercise) -> bool:
        name_low = ex.name.lower()
        if any(banned in name_low for banned in BANNED_KEYWORDS):
            return True
        if request.experience_level == schemas.ExperienceLevel.beginner:
            return any(adv in name_low for adv in ADVANCED_KEYWORDS) or any(inter in name_low for inter in INTERMEDIATE_KEYWORDS)
        if request.experience_level == schemas.ExperienceLevel.intermediate:
            return any(adv in name_low for adv in ADVANCED_KEYWORDS)
        return False

    def find_best_exercise_for_slot(slot_dict, available_exs, used_families_this_session):
        target_muscle = slot_dict["muscle"]
        keywords = slot_dict.get("kw", [])
        candidates = [
            e for e in available_exs
            if e.muscle_group == target_muscle
            and e.id not in used_exercise_ids
            and not is_exercise_disallowed(e)
        ]
        if not candidates: return None
            
        def score(ex):
            s = 0
            name_low, name_pl_low = ex.name.lower(), (ex.name_pl.lower() if ex.name_pl else "")
            text_to_search = f"{name_low} {name_pl_low} {ex.sub_muscle} {ex.category}".lower()
            
            matched_kws = 0
            for kw in keywords:
                if kw.lower() in text_to_search:
                    s += 60
                    matched_kws += 1
                    if kw.lower() in name_low or kw.lower() in name_pl_low: s += 30 
            if keywords and matched_kws == 0: s -= 150
            if slot_dict.get("comp") and ex.category == "Złożone": s += 40
                
            is_great_bodyweight = "pull-up" in name_low or "dip" in name_low or "podciąg" in name_pl_low or "poręcz" in name_pl_low
            if request.equipment == schemas.EquipmentType.gym:
                if ex.equipment == "gym": s += 50
                elif ex.equipment == "dumbbells": s += 30
                elif ex.equipment in ["cable", "machine"]: s += 50
                elif ex.equipment == "bodyweight":
                    if is_great_bodyweight: s += 50
                    elif "plank" in name_low or "crunch" in name_low: s += 20
                    else: s -= 40
            elif request.equipment == schemas.EquipmentType.dumbbells:
                if ex.equipment == "dumbbells": s += 60
                elif ex.equipment == "bodyweight":
                    if is_great_bodyweight: s += 50
                    elif "plank" in name_low or "crunch" in name_low: s += 20
                    else: s -= 10
            
            fam = get_movement_family(ex.name, ex.name_pl)
            if fam != "other" and fam in used_families_this_session: s -= 1500
            for okw in OPTIMAL_KEYWORDS:
                if okw in name_low: s += 15; break
            return s
            
        candidates.sort(key=score, reverse=True)
        best_ex = candidates[0]
        used_exercise_ids.add(best_ex.id)
        fam = get_movement_family(best_ex.name, best_ex.name_pl)
        if fam != "other": used_families_this_session.add(fam)
        return best_ex

    workout_templates = generator_templates.TEMPLATES.get(workout_type, {}).get(request.experience_level, [])
    if not workout_templates: workout_templates = generator_templates.TEMPLATES[schemas.WorkoutType.ppl][schemas.ExperienceLevel.beginner]

    for day in range(1, request.days_per_week + 1):
        template = workout_templates[(day - 1) % len(workout_templates)]
        day_exercises, used_families_this_session, day_warmup = [], set(), []
        
        if request.include_warmup and warmup_pool:
            focus_words = template["focus"].lower().split()
            day_warmup_pool = warmup_pool.copy()
            def score_warmup(w):
                ws = 0
                w_text = f"{w.name} {w.name_pl} {w.muscle_group}".lower()
                for fw in focus_words:
                    if fw in w_text: ws += 10
                return ws
            day_warmup_pool.sort(key=score_warmup, reverse=True)
            sample_size = min(15, len(day_warmup_pool))
            selected_warmup = random.sample(day_warmup_pool[:sample_size], min(3, sample_size))
            for w in selected_warmup:
                w_resp = schemas.ExerciseResponse.model_validate(w)
                w_resp.sets, w_resp.reps, w_resp.rest_time = 1, "12-15", "30s"
                day_warmup.append(w_resp)

        for slot in template["slots"]:
            if request.duration == schemas.WorkoutDuration.short and len(day_exercises) >= 4:
                break
            best_ex = find_best_exercise_for_slot(slot, available_exercises, used_families_this_session)
            if best_ex:
                volume = assign_volume(best_ex, request.goal, request.duration)
                ex_resp = schemas.ExerciseResponse.model_validate(best_ex)
                ex_resp.sets, ex_resp.reps, ex_resp.rest_time = volume["sets"], volume["reps"], volume["rest_time"]
                day_exercises.append(ex_resp)
                
        days_response.append(schemas.WorkoutDayResponse(day=day, focus=template["focus"], exercises=day_exercises, warmup=day_warmup))

    if not any(day.exercises for day in days_response):
        raise ValueError("The selected constraints do not allow a useful workout plan.")

    nutrition = calculate_suggested_nutrition(request.weight, request.height, request.goal, request.days_per_week)
    return schemas.PlanResponse(days=days_response, nutrition=nutrition)
