from datetime import datetime

from pydantic import BaseModel


class WorkoutLogBase(BaseModel):
    summary: str
    completed: bool = False


class WorkoutLogCreate(WorkoutLogBase):
    user_id: int


class WorkoutLogRead(WorkoutLogBase):
    id: int
    created_at: datetime
