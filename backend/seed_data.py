from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models

# Inicjalizacja bazy
Base.metadata.drop_all(bind=engine) # Usuwamy stare tabele, bo zmieniliśmy schemat
Base.metadata.create_all(bind=engine)

INITIAL_EXERCISES = [
    # GYM (Siłownia)
    {"name": "Wyciskanie sztangi na ławce poziomej", "muscle_group": "Klatka", "category": "Złożone", "equipment": "gym"},
    {"name": "Wyciskanie hantli na ławce skośnej dodatniej", "muscle_group": "Klatka", "category": "Złożone", "equipment": "gym"},
    {"name": "Rozpiętki na maszynie", "muscle_group": "Klatka", "category": "Izolowane", "equipment": "gym"},
    {"name": "Martwy ciąg", "muscle_group": "Plecy", "category": "Złożone", "equipment": "gym"},
    {"name": "Wiosłowanie sztangą w opadzie tułowia", "muscle_group": "Plecy", "category": "Złożone", "equipment": "gym"},
    {"name": "Ściąganie drążka wyciągu górnego", "muscle_group": "Plecy", "category": "Izolowane", "equipment": "gym"},
    {"name": "Przysiady ze sztangą na karku", "muscle_group": "Nogi", "category": "Złożone", "equipment": "gym"},
    {"name": "Wyciskanie na suwnicy", "muscle_group": "Nogi", "category": "Złożone", "equipment": "gym"},
    {"name": "Prostowanie nóg na maszynie", "muscle_group": "Nogi", "category": "Izolowane", "equipment": "gym"},
    {"name": "Wyciskanie żołnierskie sztangi", "muscle_group": "Barki", "category": "Złożone", "equipment": "gym"},
    {"name": "Wznosy ramion bokiem na wyciągu", "muscle_group": "Barki", "category": "Izolowane", "equipment": "gym"},
    {"name": "Uginanie przedramion ze sztangą", "muscle_group": "Biceps", "category": "Izolowane", "equipment": "gym"},
    {"name": "Prostowanie ramion na wyciągu górnym", "muscle_group": "Triceps", "category": "Izolowane", "equipment": "gym"},
    {"name": "Allahy (skłony na wyciągu)", "muscle_group": "Brzuch", "category": "Izolowane", "equipment": "gym"},

    # DUMBBELLS (Tylko hantle)
    {"name": "Wyciskanie hantli na ławce poziomej", "muscle_group": "Klatka", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Wyciskanie hantli na ławce skośnej", "muscle_group": "Klatka", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Rozpiętki z hantlami", "muscle_group": "Klatka", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Wiosłowanie hantlem w oparciu o ławkę", "muscle_group": "Plecy", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Wiosłowanie hantlami w opadzie tułowia", "muscle_group": "Plecy", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Przenoszenie hantla za głowę (Pullover)", "muscle_group": "Plecy", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Przysiady pucharowe (Goblet Squat)", "muscle_group": "Nogi", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Wykroki z hantlami", "muscle_group": "Nogi", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Martwy ciąg na prostych nogach z hantlami", "muscle_group": "Nogi", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Wspięcia na palce z hantlami", "muscle_group": "Nogi", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Wyciskanie hantli siedząc", "muscle_group": "Barki", "category": "Złożone", "equipment": "dumbbells"},
    {"name": "Wznosy ramion bokiem z hantlami", "muscle_group": "Barki", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Wznosy hantli w opadzie tułowia", "muscle_group": "Barki", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Uginanie przedramion z hantlami (supinacja)", "muscle_group": "Biceps", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Uginanie przedramion chwytem młotkowym", "muscle_group": "Biceps", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Wyciskanie francuskie hantla leżąc", "muscle_group": "Triceps", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Prostowanie ramienia z hantlem w opadzie", "muscle_group": "Triceps", "category": "Izolowane", "equipment": "dumbbells"},
    {"name": "Spięcia brzucha z obciążeniem (hantlem)", "muscle_group": "Brzuch", "category": "Izolowane", "equipment": "dumbbells"},

    # BODYWEIGHT (Kalistenika)
    {"name": "Pompki klasyczne", "muscle_group": "Klatka", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Pompki szerokie", "muscle_group": "Klatka", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Dipy (pompki na poręczach)", "muscle_group": "Klatka", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Podciąganie na drążku (nachwyt)", "muscle_group": "Plecy", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Podciąganie na drążku (podchwyt)", "muscle_group": "Plecy", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Podciąganie australijskie", "muscle_group": "Plecy", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Przysiady klasyczne", "muscle_group": "Nogi", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Przysiady bułgarskie (bez obciążenia)", "muscle_group": "Nogi", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Wykroki w miejscu", "muscle_group": "Nogi", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Mostki biodrowe (Glute Bridge)", "muscle_group": "Nogi", "category": "Izolowane", "equipment": "bodyweight"},
    {"name": "Pompki szczupakowe (Pike Pushups)", "muscle_group": "Barki", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Stanie na rękach przy ścianie", "muscle_group": "Barki", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Uginanie ramion (opór własny/drążek niski)", "muscle_group": "Biceps", "category": "Izolowane", "equipment": "bodyweight"},
    {"name": "Pompki diamentowe", "muscle_group": "Triceps", "category": "Złożone", "equipment": "bodyweight"},
    {"name": "Dipy na ławce/krześle", "muscle_group": "Triceps", "category": "Izolowane", "equipment": "bodyweight"},
    {"name": "Plank (deska)", "muscle_group": "Brzuch", "category": "Izolowane", "equipment": "bodyweight"},
    {"name": "Wznosy nóg w leżeniu", "muscle_group": "Brzuch", "category": "Izolowane", "equipment": "bodyweight"},
    {"name": "Wznosy nóg w zwisie na drążku", "muscle_group": "Brzuch", "category": "Izolowane", "equipment": "bodyweight"},

    # BANDS (Gumy oporowe)
    {"name": "Wyciskanie gumy przed klatkę", "muscle_group": "Klatka", "category": "Złożone", "equipment": "bands"},
    {"name": "Rozpiętki z gumą stojąc", "muscle_group": "Klatka", "category": "Izolowane", "equipment": "bands"},
    {"name": "Wiosłowanie gumą siedząc", "muscle_group": "Plecy", "category": "Złożone", "equipment": "bands"},
    {"name": "Przyciąganie gumy do twarzy (Facepulls)", "muscle_group": "Plecy", "category": "Izolowane", "equipment": "bands"},
    {"name": "Przysiady z gumą oporową", "muscle_group": "Nogi", "category": "Złożone", "equipment": "bands"},
    {"name": "Odwodzenie nogi z gumą", "muscle_group": "Nogi", "category": "Izolowane", "equipment": "bands"},
    {"name": "Wyciskanie gumy nad głowę", "muscle_group": "Barki", "category": "Złożone", "equipment": "bands"},
    {"name": "Wznosy ramion bokiem z gumą", "muscle_group": "Barki", "category": "Izolowane", "equipment": "bands"},
    {"name": "Uginanie ramion z gumą oporową", "muscle_group": "Biceps", "category": "Izolowane", "equipment": "bands"},
    {"name": "Prostowanie ramion z gumą (Triceps Extensions)", "muscle_group": "Triceps", "category": "Izolowane", "equipment": "bands"},
    {"name": "Spięcia brzucha z gumą", "muscle_group": "Brzuch", "category": "Izolowane", "equipment": "bands"},
]

def seed():
    db = SessionLocal()
    try:
        if db.query(models.Exercise).count() == 0:
            print("Wypełnianie bazy danymi początkowymi (Sprzęt)...")
            for ex_data in INITIAL_EXERCISES:
                exercise = models.Exercise(**ex_data)
                db.add(exercise)
            db.commit()
            print("Zakończono wypełnianie bazy.")
        else:
            print("Baza danych zawiera już ćwiczenia. Pomijam seedowanie.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
