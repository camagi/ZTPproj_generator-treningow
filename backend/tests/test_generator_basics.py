from generator import calculate_suggested_nutrition, get_allowed_equipment
from schemas import TrainingGoal


def test_allowed_equipment_for_dumbbells_limits_to_safe_options():
    assert get_allowed_equipment("dumbbells") == ["dumbbells", "bodyweight"]


def test_nutrition_reduction_has_lower_calories_than_hypertrophy():
    reduction = calculate_suggested_nutrition(80, 180, TrainingGoal.reduction, 3)
    hypertrophy = calculate_suggested_nutrition(80, 180, TrainingGoal.hypertrophy, 3)

    assert reduction.target_calories < hypertrophy.target_calories
    assert reduction.protein_g == 160
    assert reduction.fat_g == 72
