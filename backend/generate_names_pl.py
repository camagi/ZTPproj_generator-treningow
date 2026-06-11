import os
import json
import re

# Słownik ścisłych dopasowań (najwyższy priorytet)
EXACT_MATCHES = {
    "Barbell Bench Press - Medium Grip": "Wyciskanie Sztangi Na Ławce Płaskiej (Średni Chwyt)",
    "Hyperextensions (Back Extensions)": "Prostowanie Tułowia Na Ławce Rzymskiej",
    "Push Press - Behind the Neck": "Wyciskanie Żołnierskie Zza Karku",
    "Leg-over Floor Press": "Wyciskanie Z Podłogi Z Przełożeniem Nóg",
    "Two-arm Kettlebell Row": "Wiosłowanie Kettlebell Oburącz",
    "Lying Close-grip Bar Curl On High Pulley": "Uginanie Ramion Leżąc (Wyciąg Górny, Wąski Chwyt)",
    "Lying Close-grip Barbell Triceps Press To Chin": "Wyciskanie Francuskie Sztangi Do Brody Leżąc",
}

# 1. Bazy (Akcje)
ACTIONS = {
    "bench press": "Wyciskanie Na Ławce",
    "floor press": "Wyciskanie Z Podłogi",
    "shoulder press": "Wyciskanie Nad Głowę",
    "military press": "Wyciskanie Żołnierskie",
    "push press": "Wyciskanie Dynamiczne (Push Press)",
    "incline bench press": "Wyciskanie Na Ławce Skośnej",
    "decline bench press": "Wyciskanie Na Skosie Ujemnym",
    "deadlift": "Martwy Ciąg",
    "romanian deadlift": "Martwy Ciąg Na Prostych Nogach",
    "stiff-legged deadlift": "Martwy Ciąg Na Prostych Nogach",
    "squat": "Przysiad",
    "front squat": "Przysiad Przedni",
    "hack squat": "Przysiad Na Maszynie Hack",
    "box squat": "Przysiad Do Skrzyni",
    "split squat": "Przysiad Bułgarski",
    "lunge": "Wykroki",
    "step-up": "Wejścia Na Skrzynię",
    "leg press": "Wypychanie Nóg",
    "leg extension": "Prostowanie Nóg",
    "leg curl": "Uginanie Nóg",
    "calf raise": "Wspięcia Na Palce",
    "pull-up": "Podciąganie Na Drążku",
    "chin-up": "Podciąganie Podchwytem",
    "pulldown": "Ściąganie Drążka",
    "row": "Wiosłowanie",
    "upright row": "Podciąganie Wzdłuż Tułowia",
    "push-up": "Pompki",
    "dips": "Pompki Na Poręczach",
    "flye": "Rozpiętki",
    "flyes": "Rozpiętki",
    "curl": "Uginanie Ramion",
    "triceps extension": "Prostowanie Ramion",
    "skull crusher": "Wyciskanie Francuskie",
    "kickback": "Prostowanie Ramienia W Opadzie",
    "lateral raise": "Wznosy Bokiem",
    "front raise": "Wznosy Przodem",
    "rear delt raise": "Wznosy W Opadzie Tułowia",
    "shrug": "Szrugsy",
    "crunch": "Spięcia Brzucha",
    "sit-up": "Brzuszki",
    "plank": "Deska (Plank)",
    "russian twist": "Russian Twist",
    "wood chop": "Drwal",
    "snatch": "Rwanie",
    "clean": "Zarzut",
    "jerk": "Podrzut",
    "swing": "Wymachy",
    "good morning": "Dzień Dobry",
    "pullover": "Przenoszenie",
    "face pull": "Face Pull",
    "glute bridge": "Mostek Biodrowy",
    "hip thrust": "Wypychanie Bioder",
    "stretch": "Rozciąganie",
    "rollout": "Kółko (Ab Roller)",
}

# 2. Modyfikatory
MODIFIERS = {
    "seated": "Siedząc",
    "standing": "Stojąc",
    "lying": "Leżąc",
    "bent-over": "W Opadzie Tułowia",
    "bent over": "W Opadzie Tułowia",
    "incline": "Na Ławce Skośnej",
    "decline": "Na Skosie Ujemnym",
    "close-grip": "Wąskim Chwytem",
    "close grip": "Wąskim Chwytem",
    "wide-grip": "Szerokim Chwytem",
    "wide grip": "Szerokim Chwytem",
    "reverse-grip": "Podchwytem",
    "reverse grip": "Podchwytem",
    "neutral grip": "Chwytem Neutralnym",
    "underhand": "Podchwytem",
    "overhand": "Nachwytem",
    "one-arm": "Jednorącz",
    "one arm": "Jednorącz",
    "single-arm": "Jednorącz",
    "single arm": "Jednorącz",
    "two-arm": "Oburącz",
    "two arm": "Oburącz",
    "single-leg": "Jednonóż",
    "single leg": "Jednonóż",
    "alternating": "Naprzemiennie",
    "weighted": "Z Dodatkowym Obciążeniem",
    "behind the neck": "Zza Karku",
    "to chin": "Do Brody",
    "power": "Siłowe",
    "hang": "Ze Zwisem",
    "deficit": "Z Deficytu",
}

# 3. Sprzęt
EQUIPMENT = {
    "barbell": "Sztangą",
    "dumbbell": "Hantlami",
    "dumbbells": "Hantlami",
    "cable": "Na Wyciągu",
    "machine": "Na Maszynie",
    "smith machine": "Na Maszynie Smitha",
    "kettlebell": "Z Kettlebell",
    "band": "Z Gumą Oporową",
    "bands": "Z Gumą Oporową",
    "chains": "Z Łańcuchami",
    "plate": "Z Talerzem",
    "bodyweight": "Ciężarem Ciała",
    "medicine ball": "Z Piłką Lekarską",
    "stability ball": "Na Piłce Stabilizacyjnej",
    "bosu": "Na Bosu",
    "trx": "Na TRX",
    "rope": "Ze Sznurem",
}

def translate_name_heuristics(name_en):
    if name_en in EXACT_MATCHES:
        return EXACT_MATCHES[name_en]
        
    name_lower = name_en.lower()
    
    found_action = ""
    found_modifiers = []
    found_equipment = ""
    
    # Znajdź najdłuższą akcję
    for eng_act, pl_act in sorted(ACTIONS.items(), key=lambda x: len(x[0]), reverse=True):
        if eng_act in name_lower:
            found_action = pl_act
            # Usuń akcję by nie nadpisywała modyfikatorów
            name_lower = name_lower.replace(eng_act, "")
            break
            
    # Znajdź modyfikatory
    for eng_mod, pl_mod in sorted(MODIFIERS.items(), key=lambda x: len(x[0]), reverse=True):
        if eng_mod in name_lower:
            found_modifiers.append(pl_mod)
            name_lower = name_lower.replace(eng_mod, "")
            
    # Znajdź sprzęt
    for eng_eq, pl_eq in sorted(EQUIPMENT.items(), key=lambda x: len(x[0]), reverse=True):
        if eng_eq in name_lower:
            found_equipment = pl_eq
            name_lower = name_lower.replace(eng_eq, "")
            break
            
    # Budowanie nazwy
    parts = []
    if found_action:
        parts.append(found_action)
    else:
        # Jeśli nie znaleziono głównej akcji, zwracamy oryginał lub próbujemy chociaż sprzęt przetłumaczyć
        return name_en
        
    if found_equipment:
        if found_equipment in ["Na Wyciągu", "Na Maszynie", "Na Maszynie Smitha", "Na Piłce Stabilizacyjnej"]:
            parts.append(found_equipment)
        else:
            parts.append(f"Ze {found_equipment}" if found_equipment == "Sztangą" else f"Z {found_equipment}")
            
    for mod in found_modifiers:
        if mod not in parts: # Uniknij duplikatów np. Na Ławce Skośnej jeśli akcja już to ma
            parts.append(mod)
            
    result = " ".join(parts)
    
    # Drobne poprawki gramatyczne
    result = result.replace("Z Z ", "Z ").replace("Ze Ze ", "Ze ").replace("Na Na ", "Na ")
    
    # Jeśli wynik jest identyczny z akcją, lepiej zwrócić przetłumaczoną akcję, niż nic.
    return result.strip()

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    exercises_dir = os.path.join(parent_dir, "cwiczenia", "exercises")
    
    names_to_translate = set()
    
    for filename in os.listdir(exercises_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(exercises_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                names_to_translate.add(data.get("name", filename.replace(".json", "").replace("_", " ")))
                
    # Dodaj gify
    try:
        from gif_data import GIF_EXERCISES
        for item in GIF_EXERCISES:
            names_to_translate.add(item.get("name", ""))
    except:
        pass
        
    names_to_translate = { " ".join([w.capitalize() for w in n.split()]) for n in names_to_translate if n }
    
    translations = {}
    for name in names_to_translate:
        pl_name = translate_name_heuristics(name)
        if pl_name and pl_name != name:
             translations[name] = pl_name
             
    output_path = os.path.join(current_dir, "generated_names_pl.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=4)
        
    print(f"Wygenerowano {len(translations)} tłumaczeń nazw do {output_path}")

if __name__ == "__main__":
    main()