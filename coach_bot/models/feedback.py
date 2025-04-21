from datetime import datetime

from pydantic import Field

from coach_bot.models import BaseModel


class FeedbackBase(BaseModel):
    mood: int = Field(..., ge=1, le=10)
    difficulty_notes: str
    pulse: int | None = None


class FeedbackCreate(FeedbackBase):
    user_id: int


class FeedbackRead(FeedbackBase):
    id: int
    created_at: datetime
