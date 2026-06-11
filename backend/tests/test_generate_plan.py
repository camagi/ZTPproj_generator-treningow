import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
import schemas
from database import Base
from generator import generate_workout_plan, get_alternative_exercise, get_allowed_equipment


BASE_EXERCISES = [
    ("Squat", "Nogi", "Złożone"),
    ("Leg Curl", "Nogi", "Izolowane"),
    ("Calf Raise", "Nogi", "Izolowane"),
    ("Lunge", "Nogi", "Złożone"),
    ("Bench Press", "Klatka", "Złożone"),
    ("Incline Push-up", "Klatka", "Złożone"),
    ("Chest Fly", "Klatka", "Izolowane"),
    ("Dips Chest", "Klatka", "Złożone"),
    ("Lat Pulldown", "Plecy", "Złożone"),
    ("Seated Row", "Plecy", "Złożone"),
    ("Pull-up", "Plecy", "Złożone"),
    ("Dumbbell Row", "Plecy", "Złożone"),
    ("Shoulder Press", "Barki", "Złożone"),
    ("Lateral Raise", "Barki", "Izolowane"),
    ("Rear Delt Raise", "Barki", "Izolowane"),
    ("Face Pull", "Barki", "Izolowane"),
    ("Barbell Curl", "Biceps", "Izolowane"),
    ("Hammer Curl", "Biceps", "Izolowane"),
    ("Preacher Curl", "Biceps", "Izolowane"),
    ("Triceps Pushdown", "Triceps", "Izolowane"),
    ("Overhead Extension", "Triceps", "Izolowane"),
    ("French Press", "Triceps", "Izolowane"),
    ("Plank", "Brzuch", "Izolowane"),
    ("Crunch", "Brzuch", "Izolowane"),
    ("Leg Raise", "Brzuch", "Izolowane"),
    ("Russian Twist", "Brzuch", "Izolowane"),
]


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_exercise(name, muscle, category="Złożone", equipment="bodyweight", is_warmup=0):
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
        is_warmup=is_warmup,
    )


def seed_catalog(db):
    for equipment in ["gym", "dumbbells", "bodyweight", "bands"]:
        for idx, (name, muscle, category) in enumerate(BASE_EXERCISES):
            db.add(make_exercise(f"{equipment.title()} {name} {idx}", muscle, category, equipment))

    for equipment in ["gym", "dumbbells", "bodyweight", "bands"]:
        db.add(make_exercise(f"{equipment.title()} Warmup Mobility", "Barki", "Izolowane", equipment, is_warmup=1))

    db.commit()


def make_request(**overrides):
    payload = {
        "weight": 80,
        "height": 180,
        "days_per_week": 3,
        "experience_level": schemas.ExperienceLevel.intermediate,
        "goal": schemas.TrainingGoal.hypertrophy,
        "equipment": schemas.EquipmentType.gym,
        "duration": schemas.WorkoutDuration.medium,
        "include_warmup": False,
        "contraindicated_muscles": [],
    }
    payload.update(overrides)
    return schemas.PlanRequest(**payload)


def main_exercises(plan):
    return [exercise for day in plan.days for exercise in day.exercises]


def test_generate_workout_plan_returns_requested_number_of_days(db_session):
    seed_catalog(db_session)

    plan = generate_workout_plan(db_session, make_request(days_per_week=2))

    assert len(plan.days) == 2
    assert all(day.exercises for day in plan.days)
    assert plan.nutrition is not None


def test_generate_workout_plan_raises_when_no_exercises_are_available(db_session):
    with pytest.raises(ValueError, match="No exercises available"):
        generate_workout_plan(db_session, make_request())


def test_contraindicated_muscles_are_excluded_from_plan(db_session):
    seed_catalog(db_session)

    plan = generate_workout_plan(
        db_session,
        make_request(workout_type=schemas.WorkoutType.fbw, contraindicated_muscles=["Klatka"]),
    )

    assert all(exercise.muscle_group != "Klatka" for exercise in main_exercises(plan))


@pytest.mark.parametrize(
    ("workout_type", "days"),
    [
        (schemas.WorkoutType.fbw, 2),
        (schemas.WorkoutType.ppl, 3),
        (schemas.WorkoutType.split, 4),
    ],
)
def test_each_workout_type_generates_non_empty_days(db_session, workout_type, days):
    seed_catalog(db_session)

    plan = generate_workout_plan(db_session, make_request(workout_type=workout_type, days_per_week=days))

    assert len(plan.days) == days
    assert all(1 <= len(day.exercises) <= 8 for day in plan.days)


@pytest.mark.parametrize("equipment", list(schemas.EquipmentType))
def test_generated_plan_respects_requested_equipment(db_session, equipment):
    seed_catalog(db_session)

    plan = generate_workout_plan(db_session, make_request(equipment=equipment))
    allowed_equipment = set(get_allowed_equipment(equipment.value))

    assert main_exercises(plan)
    assert {exercise.equipment for exercise in main_exercises(plan)} <= allowed_equipment


def test_generated_plan_does_not_duplicate_main_exercises(db_session):
    seed_catalog(db_session)

    plan = generate_workout_plan(
        db_session,
        make_request(
            workout_type=schemas.WorkoutType.split,
            experience_level=schemas.ExperienceLevel.advanced,
            days_per_week=5,
            duration=schemas.WorkoutDuration.long,
        ),
    )
    exercise_ids = [exercise.id for exercise in main_exercises(plan)]

    assert len(exercise_ids) == len(set(exercise_ids))


def test_replace_exercise_returns_allowed_alternative(db_session):
    current = make_exercise("Current Bench Press", "Klatka", "Złożone", "gym")
    dumbbell_alternative = make_exercise("Dumbbells Bench Press Alternative", "Klatka", "Złożone", "dumbbells")
    bodyweight_alternative = make_exercise("Bodyweight Push-up Alternative", "Klatka", "Złożone", "bodyweight")
    wrong_category = make_exercise("Dumbbells Chest Fly Alternative", "Klatka", "Izolowane", "dumbbells")
    db_session.add_all([current, dumbbell_alternative, bodyweight_alternative, wrong_category])
    db_session.commit()

    alternative = get_alternative_exercise(
        db_session,
        schemas.ReplaceExerciseRequest(
            current_exercise_id=current.id,
            muscle_group="Klatka",
            category="Złożone",
            equipment="dumbbells",
        ),
    )

    assert alternative is not None
    assert alternative.id != current.id
    assert alternative.category == "Złożone"
    assert alternative.equipment in {"dumbbells", "bodyweight"}
