from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models

# Inicjalizacja bazy
Base.metadata.create_all(bind=engine)

INITIAL_EXERCISES = [
    {"name": "Wyciskanie sztangi na ławce poziomej", "muscle_group": "Klatka", "category": "Złożone"},
    {"name": "Wyciskanie hantli na ławce skośnej dodatniej", "muscle_group": "Klatka", "category": "Złożone"},
    {"name": "Wyciskanie hantli na ławce poziomej", "muscle_group": "Klatka", "category": "Złożone"},
    {"name": "Rozpiętki z hantlami", "muscle_group": "Klatka", "category": "Izolowane"},
    {"name": "Pompki na poręczach (Dipy)", "muscle_group": "Klatka", "category": "Złożone"},
    {"name": "Krzyżowanie linek wyciągu (High-to-Low)", "muscle_group": "Klatka", "category": "Izolowane"},
    {"name": "Martwy ciąg", "muscle_group": "Plecy", "category": "Złożone"},
    {"name": "Podciąganie na drążku", "muscle_group": "Plecy", "category": "Złożone"},
    {"name": "Wiosłowanie sztangą w opadzie tułowia", "muscle_group": "Plecy", "category": "Złożone"},
    {"name": "Wiosłowanie hantlem w oparciu o ławkę", "muscle_group": "Plecy", "category": "Złożone"},
    {"name": "Ściąganie drążka wyciągu górnego do klatki", "muscle_group": "Plecy", "category": "Izolowane"},
    {"name": "Facepulls", "muscle_group": "Plecy", "category": "Izolowane"},
    {"name": "Przysiady ze sztangą na karku", "muscle_group": "Nogi", "category": "Złożone"},
    {"name": "Wykroki z hantlami", "muscle_group": "Nogi", "category": "Złożone"},
    {"name": "Wyciskanie na suwnicy", "muscle_group": "Nogi", "category": "Złożone"},
    {"name": "Hack Przysiady", "muscle_group": "Nogi", "category": "Złożone"},
    {"name": "Uginanie nóg leżąc (maszyna)", "muscle_group": "Nogi", "category": "Izolowane"},
    {"name": "Prostowanie nóg siedząc (maszyna)", "muscle_group": "Nogi", "category": "Izolowane"},
    {"name": "Wspięcia na palce", "muscle_group": "Nogi", "category": "Izolowane"},
    {"name": "Wyciskanie żołnierskie sztangi", "muscle_group": "Barki", "category": "Złożone"},
    {"name": "Wznosy ramion bokiem z hantlami", "muscle_group": "Barki", "category": "Izolowane"},
    {"name": "Wyciskanie hantli siedząc", "muscle_group": "Barki", "category": "Złożone"},
    {"name": "Podciąganie sztangi wzdłuż tułowia", "muscle_group": "Barki", "category": "Złożone"},
    {"name": "Wznosy ramion w przód z hantlami", "muscle_group": "Barki", "category": "Izolowane"},
    {"name": "Uginanie przedramion ze sztangą", "muscle_group": "Biceps", "category": "Izolowane"},
    {"name": "Uginanie przedramion z hantlami z supinacją", "muscle_group": "Biceps", "category": "Izolowane"},
    {"name": "Uginanie przedramion chwytem młotkowym", "muscle_group": "Biceps", "category": "Izolowane"},
    {"name": "Modlitewnik (uginanie przedramion)", "muscle_group": "Biceps", "category": "Izolowane"},
    {"name": "Wyciskanie francuskie sztangi leżąc", "muscle_group": "Triceps", "category": "Izolowane"},
    {"name": "Prostowanie ramion na wyciągu górnym", "muscle_group": "Triceps", "category": "Izolowane"},
    {"name": "Wyciskanie wąskie sztangi", "muscle_group": "Triceps", "category": "Złożone"},
    {"name": "Dipy na maszynie / ławce", "muscle_group": "Triceps", "category": "Izolowane"},
    {"name": "Plank (deska)", "muscle_group": "Brzuch", "category": "Izolowane"},
    {"name": "Allahy", "muscle_group": "Brzuch", "category": "Izolowane"},
    {"name": "Wznosy nóg w zwisie", "muscle_group": "Brzuch", "category": "Izolowane"},
    {"name": "Russian Twist", "muscle_group": "Brzuch", "category": "Izolowane"},
]

def seed():
    db = SessionLocal()
    try:
        if db.query(models.Exercise).count() == 0:
            print("Wypełnianie bazy danymi początkowymi...")
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
