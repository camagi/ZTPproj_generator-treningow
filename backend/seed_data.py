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

# Inicjalizacja bazy
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

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

def seed():
    db = SessionLocal()
    
    BANNED_KEYWORDS = [
        "atlas", "stone", "tire", "sled", "battling rope", "yoke", "sandbag", "prowler",
        "rickshaw", "car deadlift", "sledgehammer", "chain", "chains", "band ", "bands ",
        "stability ball", "bosu", "neck", "suspension", "trx", "board press", "guillotine",
        "floor press", "power snatch", "clean and jerk", "rocky", "otiz", "zercher", "spell caster", "yoke walk"
    ]
    
    BANNED_INSTRUCTION_KEYWORDS = [
        "partner", "someone", "assistant", "third person"
    ]
    
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
                        
                        name_en_raw = data.get("name", filename.replace(".json", "").replace("_", " "))
                        name_en = " ".join([w.capitalize() for w in name_en_raw.split()])
                        
                        if any(banned in name_en.lower() for banned in BANNED_KEYWORDS):
                            continue
                            
                        raw_instructions = data.get("instructions", [])
                        concise_instructions = raw_instructions[:3]
                        
                        # Filtrowanie po instrukcjach (partner, osoba trzecia)
                        instructions_text = " ".join(concise_instructions).lower()
                        if any(banned in instructions_text for banned in BANNED_INSTRUCTION_KEYWORDS):
                            continue
                            
                        name_pl = get_pl_name(name_en)
                        
                        primary_muscle = data.get("primaryMuscles", [""])[0]
                        muscle_group = MUSCLE_MAPPING.get(primary_muscle, "Inne")
                        
                        equipment_raw = data.get("equipment", "gym")
                        if equipment_raw is None: equipment_raw = "body only"
                        equipment = EQUIPMENT_MAPPING.get(equipment_raw, "gym")
                        
                        mechanic = data.get("mechanic")
                        category = "Złożone" if mechanic == "compound" else "Izolowane"
                        
                        raw_instructions = data.get("instructions", [])
                        concise_instructions = raw_instructions[:3]
                        
                        instructions = json.dumps(concise_instructions)
                        
                        # Tłumaczenie przez Google Translate z cache
                        instructions_pl = []
                        for i, instr in enumerate(concise_instructions):
                            translated = get_pl_translation(instr, instr)
                            instructions_pl.append(f"Krok {i+1}: {translated}")
                        instructions_pl = json.dumps(instructions_pl)
                        
                        images = json.dumps([f"exercises/{img}" for img in data.get("images", [])])
                        
                        exercise = models.Exercise(
                            name=name_en,
                            name_pl=name_pl,
                            muscle_group=muscle_group,
                            category=category,
                            equipment=equipment,
                            description=raw_instructions[0] if raw_instructions else "",
                            instructions=instructions,
                            instructions_pl=instructions_pl,
                            images=images
                        )
                        db.add(exercise)
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
            
            if any(banned in name_en.lower() for banned in BANNED_KEYWORDS):
                continue
                
            raw_instructions = item.get("instructions", [])
            concise_instructions = raw_instructions[:3]
            
            instructions_text = " ".join(concise_instructions).lower()
            if any(banned in instructions_text for banned in BANNED_INSTRUCTION_KEYWORDS):
                continue
                
            name_pl = get_pl_name(name_en)
            
            target_muscle = item.get("targetMuscles", [""])[0]
            muscle_group = MUSCLE_MAPPING.get(target_muscle, "Inne")
            
            equip_raw = item.get("equipments", ["gym"])[0]
            equipment = EQUIPMENT_MAPPING.get(equip_raw, "gym")
            
            category = "Izolowane"
            if any(word in name_en.lower() for word in ["squat", "press", "deadlift", "row", "lunge"]):
                category = "Złożone"
            
            raw_instructions = item.get("instructions", [])
            concise_instructions = raw_instructions[:3]
            instructions = json.dumps(concise_instructions)
            
            # Tłumaczenie przez Google Translate z cache
            instructions_pl = []
            for i, instr in enumerate(concise_instructions):
                translated = get_pl_translation(instr, instr)
                instructions_pl.append(f"Krok {i+1}: {translated}")
            instructions_pl = json.dumps(instructions_pl)
            
            gif_url = f"gifs_720x720/{item.get('gifUrl')}"
            
            db.flush()
            existing = db.query(models.Exercise).filter(models.Exercise.name == name_en).first()
            
            if existing:
                existing.gif_url = gif_url
                existing.name_pl = name_pl
                existing.instructions_pl = instructions_pl
                existing.muscle_group = muscle_group
                existing.equipment = equipment
                existing.category = category
            else:
                exercise = models.Exercise(
                    name=name_en,
                    name_pl=name_pl,
                    muscle_group=muscle_group,
                    category=category,
                    equipment=equipment,
                    description=raw_instructions[0] if raw_instructions else "",
                    instructions=instructions,
                    instructions_pl=instructions_pl,
                    images=json.dumps([]),
                    gif_url=gif_url
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
    seed()
