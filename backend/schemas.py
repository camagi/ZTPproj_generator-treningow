from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ExperienceLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class WorkoutType(str, Enum):
    fbw = "FBW"
    ppl = "PPL"
    split = "Split"

class TrainingGoal(str, Enum):
    reduction = "reduction"
    hypertrophy = "hypertrophy"
    strength = "strength"

class EquipmentType(str, Enum):
    gym = "gym"
    dumbbells = "dumbbells"
    bodyweight = "bodyweight"
    bands = "bands"

class WorkoutDuration(str, Enum):
    short = "short"  # 45 min
    medium = "medium" # 60 min
    long = "long"  # 90 min

class ExerciseBase(BaseModel):
    name: str
    muscle_group: str
    category: Optional[str] = None
    equipment: Optional[str] = "gym"
    description: Optional[str] = None

class ExerciseResponse(ExerciseBase):
    id: int
    sets: Optional[int] = None
    reps: Optional[str] = None
    rest_time: Optional[str] = None

    class Config:
        from_attributes = True

class PlanRequest(BaseModel):
    weight: float
    height: float
    days_per_week: int
    contraindicated_muscles: List[str] = []
    experience_level: ExperienceLevel = ExperienceLevel.intermediate
    workout_type: Optional[WorkoutType] = None
    goal: TrainingGoal = TrainingGoal.hypertrophy
    equipment: EquipmentType = EquipmentType.gym
    duration: WorkoutDuration = WorkoutDuration.medium

class NutritionResponse(BaseModel):
    target_calories: int
    protein_g: int
    fat_g: int
    carbs_g: int

class WorkoutDayResponse(BaseModel):
    day: int
    focus: str
    exercises: List[ExerciseResponse]

class PlanResponse(BaseModel):
    days: List[WorkoutDayResponse]
    nutrition: Optional[NutritionResponse] = None
