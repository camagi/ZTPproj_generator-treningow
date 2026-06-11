from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
import schemas
from database import Base
from generator import generate_workout_plan


def make_exercise(name, muscle, category="Złożone", equipment="bodyweight"):
    return models.Exercise(
        name=name,
        name_pl=name,
        muscle_group=muscle,
        sub_muscle=None,
        category=category,
        equipment=equipment,
        description="demo",
        images="[]",
        instructions='["step"]',
        instructions_pl='["krok"]',
        is_warmup=0,
    )


def test_generate_workout_plan_returns_requested_number_of_days():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        for idx, muscle in enumerate(["Klatka", "Plecy", "Nogi", "Barki", "Biceps", "Triceps", "Brzuch"]):
            db.add(make_exercise(f"{muscle} basic {idx}", muscle))
            db.add(make_exercise(f"{muscle} accessory {idx}", muscle, category="Izolowane"))
        db.commit()

        request = schemas.PlanRequest(
            weight=80,
            height=180,
            days_per_week=2,
            experience_level=schemas.ExperienceLevel.beginner,
            goal=schemas.TrainingGoal.hypertrophy,
            equipment=schemas.EquipmentType.bodyweight,
            duration=schemas.WorkoutDuration.short,
            include_warmup=False,
        )

        plan = generate_workout_plan(db, request)

        assert len(plan.days) == 2
        assert all(day.exercises for day in plan.days)
        assert plan.nutrition is not None
    finally:
        db.close()
