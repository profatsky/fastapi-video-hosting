import datetime
from typing import List, Optional

from pydantic import BaseModel, validator

from app.schemas.users import UserSchema
from app.schemas.comments import CommentSchema


class BaseVideoSchema(BaseModel):
    title: str
    description: str


class SimpleVideoSchema(BaseVideoSchema):
    id: int
    created_at: datetime.datetime
    file: str

    class Config:
        orm_mode = True


class VideoSchema(SimpleVideoSchema):
    comments: List[CommentSchema] = []
    author: UserSchema
    likes: List[UserSchema]

    @validator("likes")
    def get_amount(cls, lst):
        return len(lst)


class VideoCreateSchema(BaseVideoSchema):
    author: UserSchema


class VideoUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
