import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.users.schemas import UserSchema


class BaseCommentSchema(BaseModel):
    text: str
    answer_to: Optional[int] = None

    @validator("answer_to")
    def get_null(cls, value):
        if not value:
            return
        return value


class CommentSchema(BaseCommentSchema):
    id: int
    author: UserSchema
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class CommentCreateSchema(BaseCommentSchema):
    pass


class CommentUpdateSchema(BaseModel):
    text: Optional[str] = None
