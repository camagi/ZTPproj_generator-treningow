import json
import os
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models
from gif_data import GIF_EXERCISES

# Wczytaj cache tłumaczeń
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "translation_cache.json"), 'r', encoding='utf-8') as f:
        TRANSLATION_CACHE = json.load(f)
except Exception as e:
    print(f"Nie udało się załadować cache tłumaczeń instrukcji: {e}")
    TRANSLATION_CACHE = {}

# Wczytaj wygenerowane polskie nazwy ćwiczeń
try:
    with open(os.path.join(current_dir, "generated_names_pl.json"), 'r', encoding='utf-8') as f:
        NAMES_CACHE = json.load(f)
except Exception as e:
    print(f"Nie udało się załadować cache nazw ćwiczeń: {e}")
    NAMES_CACHE = {}

def get_pl_translation(text, default=""):
    """Zwraca tłumaczenie z cache, lub wartość domyślną."""
    if not text: return default
    return TRANSLATION_CACHE.get(text, default)

def get_pl_name(name_en):
    """Zwraca polską nazwę z wygenerowanego słownika lub oryginał."""
    return NAMES_CACHE.get(name_en, name_en)

def determine_sub_muscle(name_en, muscle_group, original_primary):
    name_low = name_en.lower()
    orig_low = original_primary.lower() if original_primary else ""
    
    if muscle_group == "Klatka":
        if "incline" in name_low: return "Góra klatki"
        if "decline" in name_low or "dip" in name_low: return "Dół klatki"
        return "Środek klatki"
    elif muscle_group == "Plecy":
        if "pulldown" in name_low or "pull-up" in name_low or "chin-up" in name_low or "lats" in orig_low: return "Szerokość pleców"
        if "deadlift" in name_low or "hyperextension" in name_low or "good morning" in name_low or "lower back" in orig_low or "spine" in orig_low: return "Dół pleców"
        return "Grubość i górny grzbiet"
    elif muscle_group == "Nogi":
        if "calf" in name_low or "calves" in orig_low:
            if "seated" in name_low: return "Łydki - dolna część"
            return "Łydki - górna część"
        if "glute" in name_low or "glutes" in orig_low or "hip thrust" in name_low: return "Pośladki"
        if "hamstring" in name_low or "hamstrings" in orig_low or "romanian" in name_low or "stiff" in name_low or "leg curl" in name_low: return "Tył uda"
        if "adductor" in name_low or "adductors" in orig_low or "groin" in name_low: return "Wewnętrzna strona ud"
        if "abductor" in name_low or "abductors" in orig_low: return "Zewnętrzna strona ud"
        return "Przód uda"
    elif muscle_group == "Barki":
        if "rear" in name_low or "face pull" in name_low: return "Tylny akton"
        if "lateral" in name_low or "side" in name_low: return "Boczny akton"
        if "front" in name_low: return "Przedni akton"
        return "Przedni akton"
    elif muscle_group == "Biceps":
        if "forearm" in orig_low or "brachialis" in orig_low or "reverse" in name_low or "hammer" in name_low: return "Góra przedramienia"
        if "wrist" in name_low: return "Dół przedramienia"
        if "incline" in name_low or "drag" in name_low: return "Biceps - głowa długa"
        if "preacher" in name_low or "concentration" in name_low: return "Biceps - głowa krótka"
        return "Biceps - ogólnie"
    elif muscle_group == "Triceps":
        if "overhead" in name_low or "skull crusher" in name_low or "french" in name_low: return "Triceps - głowa długa"
        if "pushdown" in name_low or "kickback" in name_low or "dip" in name_low or "close-grip" in name_low or "close grip" in name_low: return "Triceps - głowa boczna i przyśrodkowa"
        return "Triceps - głowa boczna i przyśrodkowa"
    elif muscle_group == "Brzuch":
        if "oblique" in name_low or "obliques" in orig_low or "twist" in name_low or "side" in name_low: return "Boki brzucha"
        if "leg raise" in name_low or "lower abs" in orig_low: return "Dół brzucha"
        if "plank" in name_low or "rollout" in name_low or "core" in orig_low: return "Głęboka stabilizacja"
        return "Góra brzucha"
    
    return None

MUSCLE_MAPPING = {
    "chest": "Klatka",
    "pectorals": "Klatka",
    "middle back": "Plecy",
    "lats": "Plecy",
    "lower back": "Plecy",
    "traps": "Plecy",
    "trapezius": "Plecy",
    "upper back": "Plecy",
    "spine": "Plecy",
    "quadriceps": "Nogi",
    "quads": "Nogi",
    "hamstrings": "Nogi",
    "glutes": "Nogi",
    "calves": "Nogi",
    "adductors": "Nogi",
    "abductors": "Nogi",
    "shoulders": "Barki",
    "delts": "Barki",
    "deltoids": "Barki",
    "biceps": "Biceps",
    "triceps": "Triceps",
    "abdominals": "Brzuch",
    "abs": "Brzuch",
    "lower abs": "Brzuch",
    "obliques": "Brzuch",
    "forearms": "Biceps",
    "brachialis": "Biceps",
    "soleus": "Nogi",
    "inner thighs": "Nogi",
    "latissimus dorsi": "Plecy",
    "rhomboids": "Plecy",
    "upper chest": "Klatka",
    "cardiovascular system": "Inne"
}

EQUIPMENT_MAPPING = {
    "body only": "bodyweight",
    "body weight": "bodyweight",
    "dumbbell": "dumbbells",
    "dumbbells": "dumbbells",
    "bands": "bands",
    "band": "bands",
    "resistance band": "bands",
    "barbell": "gym",
    "olympic barbell": "gym",
    "ez barbell": "gym",
    "trap bar": "gym",
    "machine": "gym",
    "cable": "gym",
    "kettlebells": "gym",
    "kettlebell": "gym",
    "smith machine": "gym",
    "sled machine": "gym",
    "leverage machine": "gym",
    "weighted": "gym",
    "assisted": "gym",
    "stability ball": "gym",
    "bosu ball": "gym",
    "medicine ball": "gym",
    "roller": "gym",
    "wheel roller": "gym",
    "stationary bike": "gym",
    "elliptical machine": "gym",
    "stepmill machine": "gym",
}

def upsert_exercise(db: Session, exercise: models.Exercise) -> bool:
    existing = db.query(models.Exercise).filter(models.Exercise.name == exercise.name).first()
    if not existing:
        db.add(exercise)
        return True

    for field in [
        "name_pl",
        "muscle_group",
        "sub_muscle",
        "category",
        "equipment",
        "description",
        "images",
        "gif_url",
        "instructions",
        "instructions_pl",
        "is_warmup",
    ]:
        setattr(existing, field, getattr(exercise, field))
    return False


def seed(reset: bool = False, skip_if_populated: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if reset:
        db.query(models.Exercise).delete()
        db.commit()
    elif skip_if_populated and db.query(models.Exercise.id).first():
        print("Baza zawiera już ćwiczenia. Pomijam seed.")
        db.close()
        return
    
    # Ćwiczenia całkowicie usuwane (strongman, niebezpieczne, dziwne)
    BANNED_KEYWORDS = [
        "atlas", "stone", "tire", "sled", "battling rope", "yoke", "sandbag", "prowler",
        "rickshaw", "car deadlift", "sledgehammer", "chain", "chains", "band ", "bands ",
        "stability ball", "bosu", "neck", "suspension", "trx", "board press", "guillotine",
        "floor press", "power snatch", "clean and jerk", "rocky", "otiz", "zercher", "spell caster", "yoke walk"
    ]
    
    # Słowa kluczowe sugerujące rozgrzewkę / mobilność
    WARMUP_KEYWORDS = [
        "circle", "drill", "warm up", "warm-up", "mobility", "stretch", "yoga", "rotation", 
        "clench", "breathing", "dynamic", "ankle circle", "arm circle", "elbow circle"
    ]
    
    BANNED_INSTRUCTION_KEYWORDS = [
        "partner", "someone", "assistant", "third person", "coach"
    ]
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        candidate_dirs = [
            os.path.join(parent_dir, "cwiczenia", "exercises"),
            os.path.join(current_dir, "cwiczenia", "exercises"),
        ]
        exercises_dir = next((path for path in candidate_dirs if os.path.exists(path)), None)
        
        if not exercises_dir:
            print(f"Exercises directory not found. Checked: {candidate_dirs}")
            return

        print("Wypełnianie bazy danymi z plików JSON...")
        count = 0
        for filename in os.listdir(exercises_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(exercises_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        
                        name_en_raw = data.get("name", filename.replace(".json", "").replace("_", " "))
                        name_en = " ".join([w.capitalize() for w in name_en_raw.split()])
                        name_low = name_en.lower()

                        # 1. Sprawdź czy ćwiczenie jest na czarnej liście (strongman itp)
                        if any(banned in name_low for banned in BANNED_KEYWORDS):
                            continue
                            
                        # 2. Sprawdź czy instrukcje wymagają partnera
                        raw_instructions = data.get("instructions", [])
                        concise_instructions = raw_instructions[:3]
                        instructions_text = " ".join(concise_instructions).lower()
                        if any(banned in instructions_text for banned in BANNED_INSTRUCTION_KEYWORDS):
                            continue

                        # 3. Kategoryzacja rozgrzewki
                        is_warmup = 0
                        json_cat = data.get("category", "").lower()
                        if json_cat in ["stretching", "warm up", "mobility"] or any(w in name_low for w in WARMUP_KEYWORDS):
                            is_warmup = 1

                        name_pl = get_pl_name(name_en)
                        primary_muscle = data.get("primaryMuscles", [""])[0]
                        muscle_group = MUSCLE_MAPPING.get(primary_muscle, "Inne")
                        
                        # Ręczne poprawki na błędne tagowanie
                        if "lunge" in name_low or "squat" in name_low or "leg press" in name_low:
                            muscle_group = "Nogi"
                        if "pushdown" in name_low or "triceps" in name_low:
                            muscle_group = "Triceps"
                        if "curl" in name_low and "leg" not in name_low:
                            muscle_group = "Biceps"
                            
                        equipment_raw = data.get("equipment", "gym")
                        if equipment_raw is None: equipment_raw = "body only"
                        equipment = EQUIPMENT_MAPPING.get(equipment_raw, "gym")
                        
                        mechanic = data.get("mechanic")
                        category = "Złożone" if mechanic == "compound" else "Izolowane"
                        
                        instructions = json.dumps(concise_instructions)
                        
                        # Tłumaczenie przez Google Translate z cache
                        instructions_pl = []
                        for i, instr in enumerate(concise_instructions):
                            translated = get_pl_translation(instr, instr)
                            instructions_pl.append(f"Krok {i+1}: {translated}")
                        instructions_pl = json.dumps(instructions_pl)
                        
                        images = json.dumps([f"exercises/{img}" for img in data.get("images", [])])
                        sub_muscle = determine_sub_muscle(name_en, muscle_group, primary_muscle)
                        
                        exercise = models.Exercise(
                            name=name_en,
                            name_pl=name_pl,
                            muscle_group=muscle_group,
                            sub_muscle=sub_muscle,
                            category=category,
                            equipment=equipment,
                            description=raw_instructions[0] if raw_instructions else "",
                            instructions=instructions,
                            instructions_pl=instructions_pl,
                            images=images,
                            is_warmup=is_warmup
                        )
                        if upsert_exercise(db, exercise):
                            count += 1
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
        
        db.commit()
        print(f"Dodano {count} ćwiczeń z plików JSON.")

        # Dodawanie ćwiczeń z GIFami
        print("Wypełnianie bazy danymi z GIFami (z gif_data.py)...")
        gif_count = 0
        for item in GIF_EXERCISES:
            name_en_raw = item.get("name")
            name_en = " ".join([w.capitalize() for w in name_en_raw.split()])
            name_low = name_en.lower()
            
            if any(banned in name_low for banned in BANNED_KEYWORDS):
                continue
                
            raw_instructions = item.get("instructions", [])
            concise_instructions = raw_instructions[:3]
            instructions_text = " ".join(concise_instructions).lower()
            if any(banned in instructions_text for banned in BANNED_INSTRUCTION_KEYWORDS):
                continue

            is_warmup = 0
            if any(w in name_low for w in WARMUP_KEYWORDS):
                is_warmup = 1
                
            name_pl = get_pl_name(name_en)
            target_muscle = item.get("targetMuscles", [""])[0]
            muscle_group = MUSCLE_MAPPING.get(target_muscle, "Inne")
            equip_raw = item.get("equipments", ["gym"])[0]
            equipment = EQUIPMENT_MAPPING.get(equip_raw, "gym")
            
            category = "Izolowane"
            if any(word in name_low for word in ["squat", "press", "deadlift", "row", "lunge"]):
                category = "Złożone"
            
            instructions = json.dumps(concise_instructions)
            
            instructions_pl = []
            for i, instr in enumerate(concise_instructions):
                translated = get_pl_translation(instr, instr)
                instructions_pl.append(f"Krok {i+1}: {translated}")
            instructions_pl = json.dumps(instructions_pl)
            
            gif_url = f"gifs_720x720/{item.get('gifUrl')}"
            sub_muscle = determine_sub_muscle(name_en, muscle_group, target_muscle)
            
            db.flush()
            existing = db.query(models.Exercise).filter(models.Exercise.name == name_en).first()
            
            if existing:
                existing.gif_url = gif_url
                existing.name_pl = name_pl
                existing.instructions_pl = instructions_pl
                existing.muscle_group = muscle_group
                existing.sub_muscle = sub_muscle
                existing.equipment = equipment
                existing.category = category
                existing.is_warmup = is_warmup
            else:
                exercise = models.Exercise(
                    name=name_en,
                    name_pl=name_pl,
                    muscle_group=muscle_group,
                    sub_muscle=sub_muscle,
                    category=category,
                    equipment=equipment,
                    description=raw_instructions[0] if raw_instructions else "",
                    instructions=instructions,
                    instructions_pl=instructions_pl,
                    images=json.dumps([]),
                    gif_url=gif_url,
                    is_warmup=is_warmup
                )
                db.add(exercise)
                gif_count += 1
        
        db.commit()
        print(f"Dodano {gif_count} nowych ćwiczeń z GIFami.")
        count += gif_count
        
        print(f"Zakończono wypełnianie bazy. Łącznie: {count} ćwiczeń.")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed workout exercises database.")
    parser.add_argument("--reset", action="store_true", help="Delete existing exercises before seeding.")
    parser.add_argument("--skip-if-populated", action="store_true", help="Do nothing when exercises already exist.")
    args = parser.parse_args()

    seed(reset=args.reset, skip_if_populated=args.skip_if_populated)
