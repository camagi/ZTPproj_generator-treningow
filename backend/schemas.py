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

class ExerciseBase(BaseModel):
    name: str
    muscle_group: str
    category: Optional[str] = None
    description: Optional[str] = None

class ExerciseResponse(ExerciseBase):
    id: int
    sets: Optional[int] = None
    reps: Optional[str] = None

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

class WorkoutDayResponse(BaseModel):
    day: int
    focus: str
    exercises: List[ExerciseResponse]

class PlanResponse(BaseModel):
    days: List[WorkoutDayResponse]
