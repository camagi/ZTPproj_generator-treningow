from pydantic import BaseModel
from typing import List, Optional

class ExerciseBase(BaseModel):
    name: str
    muscle_group: str
    category: Optional[str] = None
    description: Optional[str] = None

class ExerciseResponse(ExerciseBase):
    id: int

    class Config:
        from_attributes = True

class PlanRequest(BaseModel):
    weight: float
    height: float
    days_per_week: int
    contraindicated_muscles: List[str] = []

class WorkoutDayResponse(BaseModel):
    day: int
    focus: str
    exercises: List[ExerciseResponse]

class PlanResponse(BaseModel):
    days: List[WorkoutDayResponse]
