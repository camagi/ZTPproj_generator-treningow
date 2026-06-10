import re

# Słownik nazw ćwiczeń dla ścisłego dopasowania
EXERCISE_NAMES_PL = {
    "Barbell Bench Press": "Wyciskanie Sztangi Na Ławce Poziomej",
    "Dumbbell Bench Press": "Wyciskanie Hantli Na Ławce Poziomej",
    "Barbell Squat": "Przysiad Ze Sztangą",
    "Barbell Full Squat": "Pełny Przysiad Ze Sztangą",
    "Deadlift": "Martwy Ciąg",
    "Barbell Deadlift": "Martwy Ciąg Ze Sztangą",
    "Pull-Up": "Podciąganie Na Drążku",
    "Push-Up": "Pompki Klasyczne",
    "Dumbbell Curl": "Uginanie Ramion Z Hantlami",
    "Barbell Curl": "Uginanie Ramion Ze Sztangą",
    "Bicep Curl": "Uginanie Przedramion",
    "Tricep Extension": "Prostowanie Przedramion",
    "Lateral Raise": "Wznosy Bokiem",
    "Front Raise": "Wznosy Przodem",
    "Shoulder Press": "Wyciskanie Nad Głowę",
    "Military Press": "Wyciskanie Żołnierskie",
    "Bent Over Row": "Wiosłowanie W Opadzie Tułowia",
    "Lat Pulldown": "Ściąganie Drążka Wyciągu Górnego",
    "Leg Press": "Wypychanie Na Maszynie",
    "Leg Extension": "Prostowanie Nóg Na Maszynie",
    "Leg Curl": "Uginanie Nóg Na Maszynie",
    "Calf Raise": "Wspięcia Na Palce",
    "Crunch": "Spięcia Brzucha",
    "Plank": "Deska (Plank)",
    "Lunge": "Wykroki",
    "Dips": "Pompki Na Poręczach",
    "Flyes": "Rozpiętki",
}

WORDS_PL = {
    "barbell": "Sztanga",
    "dumbbell": "Hantle",
    "cable": "Wyciąg",
    "machine": "Maszyna",
    "press": "Wyciskanie",
    "squat": "Przysiad",
    "row": "Wiosłowanie",
    "curl": "Uginanie",
    "extension": "Prostowanie",
    "raise": "Wznosy",
    "deadlift": "Martwy Ciąg",
    "flyes": "Rozpiętki",
    "lunge": "Wykroki",
}

# Reguły tłumaczeniowe (uporządkowane od najdłuższych fraz do pojedynczych słów)
# Zostaną posortowane automatycznie w kodzie, ale trzymamy je tutaj dla czytelności.
TRANSLATION_RULES = {
    "this exercise is best performed inside a squat rack for safety purposes": "to ćwiczenie najlepiej wykonywać w klatce do przysiadów dla bezpieczeństwa",
    "hold on to the bar using both arms at each side and lift it off the rack by first pushing with your legs and at the same time straightening your torso": "trzymaj sztangę oburącz po bokach i zdejmij ją ze stojaka, wypychając ją najpierw nogami, jednocześnie prostując tułów",
    "step away from the rack and position your legs using a shoulder width medium stance with the toes slightly pointed out": "odejdź od stojaka i ustaw nogi na szerokość barków ze stopami skierowanymi lekko na zewnątrz",
    "sit down on a pull down machine with a wide bar attached to the top pulley": "usiądź na maszynie wyciągu górnego z zamocowanym szerokim drążkiem",
    "grab the bar with the palms facing forward using the prescribed grip": "chwyć drążek nachwytem (dłonie skierowane do przodu), używając wskazanego chwytu",
    "as you have both arms extended in front of you holding the bar at the chosen grip width, bring your torso back around 30 degrees or so while creating a curvature on your lower back and sticking your chest out": "mając wyprostowane ręce przed sobą i trzymając drążek, odchyl tułów do tyłu o około 30 stopni, zachowując naturalną krzywiznę dolnego odcinka pleców i wypinając klatkę piersiową",
    "from the starting position, breathe in and begin coming down slowly until the bar touches your middle chest": "z pozycji startowej weź wdech i zacznij powoli opuszczać ciężar, aż sztanga dotknie środkowej części klatki piersiowej",
    "after a brief pause, push the bar back to the starting position as you breathe out": "po krótkiej pauzie wypchnij sztangę z powrotem do pozycji startowej, robiąc wydech",
    "focus on pushing the bar using your chest muscles": "skup się na wypychaniu sztangi przy użyciu mięśni klatki piersiowej",
    "lock your arms and squeeze your chest in the contracted position at the top of the motion, hold for a second and then start coming down slowly again": "zablokuj ramiona i napnij klatkę piersiową w górnej fazie ruchu, przytrzymaj przez sekundę, a następnie zacznij ponownie powoli opuszczać ciężar",
    "ideally, lowering the weight should take about twice as long as raising it": "najlepiej, aby opuszczanie ciężaru trwało dwa razy dłużej niż podnoszenie",
    "repeat the movement for the prescribed amount of repetitions": "powtórz ruch określoną ilość razy",
    "when you are done, place the bar back in the rack": "po zakończeniu odłóż sztangę na stojak",
    "stand up straight with your feet shoulder width apart": "stań prosto ze stopami na szerokość barków",
    "lower the weight slowly towards your chest": "opuszczaj ciężar powoli w stronę klatki piersiowej",
    "push the weight back to the starting position": "wypchnij ciężar z powrotem do pozycji startowej",
    "exhale as you perform the movement": "wykonuj wydech podczas wykonywania ruchu",
    "inhale as you return to the start": "rób wdech podczas powrotu do pozycji startowej",
    "repeat for the desired number of repetitions": "powtórz zadaną ilość razy",
    "keep your back straight throughout the exercise": "trzymaj proste plecy przez cały czas trwania ćwiczenia",
    "contract your muscles at the top of the movement": "napnij mięśnie w końcowej fazie ruchu",
    "hold the bar with your palms facing forward": "trzymaj sztangę nachwytem (palce do przodu)",
    "position your feet firmly on the floor": "postaw stopy stabilnie na podłodze",
    "lower your hips back until your thighs are parallel to the floor": "opuszczaj biodra, aż uda znajdą się równolegle do podłogi",
    "lift it off the rack by first pushing with your legs": "zdejmij sztangę ze stojaka, wypychając ją nogami",
    "lie back on a flat bench": "połóż się na ławce płaskiej",
    "sit down on a bench": "usiądź na ławce",
    "starting position": "pozycja startowa",
    "return to the starting position": "wróć do pozycji startowej",
    "shoulder width apart": "na szerokość barków",
    "shoulder-width apart": "na szerokość barków",
    "shoulder width": "szerokość barków",
    "overhand grip": "nachwyt",
    "underhand grip": "podchwyt",
    "neutral grip": "chwyt neutralny",
    "breathe out": "zrób wydech",
    "breathe in": "zrób wdech",
    "exhale": "zrób wydech",
    "inhale": "zrób wdech",
    "push the": "wypchnij",
    "pull the": "pociągnij",
    "lower the": "opuść",
    "raise the": "unieś",
    "lift the": "podnieś",
    "hold the": "trzymaj",
    "grab the": "chwyć",
    "squeeze your": "napnij",
    "contract your": "napnij",
    "keep your back straight": "trzymaj proste plecy",
    "palms facing forward": "dłonie skierowane do przodu",
    "palms facing you": "dłonie skierowane do ciebie",
    "for safety purposes": "dla bezpieczeństwa",
    "step away from": "odejdź od",
    "pause for a second": "zatrzymaj ruch na sekundę",
    "brief pause": "krótka pauza",
    "flat bench": "płaska ławka",
    "incline bench": "ławka skośna",
    "decline bench": "ławka ze skosem ujemnym",
    "barbell": "sztangę",
    "dumbbells": "hantle",
    "dumbbell": "hantel",
    "bar": "gryf",
    "weights": "ciężary",
    "weight": "ciężar",
    "machine": "maszynę",
    "cable": "wyciąg",
    "pulley": "wyciąg",
    "chest": "klatkę piersiową",
    "back": "plecy",
    "legs": "nogi",
    "arms": "ramiona",
    "knees": "kolana",
    "elbows": "łokcie",
    "shoulders": "barki",
    "feet": "stopy",
    "hands": "dłonie",
    "floor": "podłogę",
    "ground": "ziemię",
    "slowly": "powoli",
    "straight": "prosto",
    "grab": "chwyć",
    "hold": "trzymaj",
    "push": "wypchnij",
    "pull": "pociągnij",
    "lift": "podnieś",
    "lower": "opuść",
    "extend": "wyprostuj",
    "bend": "ugnij",
    "squeeze": "napnij",
    "contract": "napnij",
    "sit": "usiądź",
    "stand": "stań",
    "lie": "leż",
    "step": "krok",
    "with": "z",
    "your": "swoje",
    "the": "",
    "a": "",
    "an": "",
    "to": "do",
    "on": "na",
    "in": "w",
    "and": "i",
}

# Sort the dictionary by length of the key descending to ensure longer phrases are replaced first
SORTED_RULES = sorted(TRANSLATION_RULES.items(), key=lambda item: len(item[0]), reverse=True)

def translate_instruction_pro(instruction_en):
    # 1. Usuń numerację z początku
    clean = instruction_en.strip().lower()
    
    # 2. Zastosuj wszystkie reguły z posortowanego słownika
    for en_phrase, pl_phrase in SORTED_RULES:
        # Używamy prostego replace, ale można by też użyć regex z \b dla pełnych słów
        # Replace radzi sobie dobrze, jeśli zachowujemy ostrożność ze spacjami dla krótkich słów.
        # Dla słów krótszych niż 4 znaki, dodajemy spacje wokół, żeby uniknąć podmiany części wyrazu.
        if len(en_phrase) <= 4:
            clean = re.sub(r'\b' + re.escape(en_phrase) + r'\b', pl_phrase, clean)
        else:
            clean = clean.replace(en_phrase, pl_phrase)
            
    # 3. Usuń wielokrotne spacje i popraw typografię
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # 4. Kapitalizacja pierwszego znaku
    if clean:
        clean = clean[0].upper() + clean[1:]
        
    return clean

def translate_name_pro(name_en):
    # 1. Sprawdź dokładne dopasowanie
    if name_en in EXERCISE_NAMES_PL:
        return EXERCISE_NAMES_PL[name_en]
    
    # 2. Próba inteligentnego złożenia nazwy
    parts = name_en.replace("-", " ").replace("_", " ").split()
    translated_parts = []
    
    equipment = ""
    action = ""
    
    for p in parts:
        p_low = p.lower()
        if p_low in WORDS_PL:
            val = WORDS_PL[p_low]
            if p_low in ["barbell", "dumbbell", "cable", "machine"]:
                equipment = val
            elif p_low in ["press", "squat", "row", "curl", "extension", "raise", "deadlift"]:
                action = val
            else:
                translated_parts.append(val)
        else:
            translated_parts.append(p)
            
    final_name = " ".join(translated_parts)
    if action:
        final_name = f"{action} {final_name}"
    if equipment:
        final_name = f"{final_name} ({equipment})"
        
    return final_name.strip().title()