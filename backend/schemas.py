import json
from pydantic import BaseModel, ConfigDict, Field, field_validator
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
    name_pl: Optional[str] = None
    muscle_group: str
    sub_muscle: Optional[str] = None
    category: Optional[str] = None
    is_warmup: Optional[int] = 0
    equipment: Optional[str] = "gym"
    description: Optional[str] = None
    images: Optional[List[str]] = Field(default_factory=list)
    gif_url: Optional[str] = None
    instructions: Optional[List[str]] = Field(default_factory=list)
    instructions_pl: Optional[List[str]] = Field(default_factory=list)

    @field_validator('images', 'instructions', 'instructions_pl', mode='before')
    @classmethod
    def parse_json_string(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return v

class ExerciseResponse(ExerciseBase):
    id: int
    sets: Optional[int] = None
    reps: Optional[str] = None
    rest_time: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
class PlanRequest(BaseModel):
    weight: float = Field(..., ge=30, le=300)
    height: float = Field(..., ge=100, le=250)
    days_per_week: int = Field(..., ge=1, le=5)
    contraindicated_muscles: List[str] = Field(default_factory=list)
    experience_level: ExperienceLevel = ExperienceLevel.intermediate
    workout_type: Optional[WorkoutType] = None
    goal: TrainingGoal = TrainingGoal.hypertrophy
    equipment: EquipmentType = EquipmentType.gym
    duration: WorkoutDuration = WorkoutDuration.medium
    include_warmup: bool = True

class NutritionResponse(BaseModel):
    target_calories: int
    protein_g: int
    fat_g: int
    carbs_g: int

class ReplaceExerciseRequest(BaseModel):
    current_exercise_id: int
    muscle_group: str
    category: Optional[str] = None
    equipment: str

class WorkoutDayResponse(BaseModel):
    day: int
    focus: str
    exercises: List[ExerciseResponse]
    warmup: List[ExerciseResponse] = Field(default_factory=list)

class PlanResponse(BaseModel):
    days: List[WorkoutDayResponse]
    nutrition: Optional[NutritionResponse] = None
