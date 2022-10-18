import datetime
from typing import List

from pydantic import BaseModel

from app.schemas.auth import UserSchema
from app.schemas.comments import CommentSchema


class BaseVideoSchema(BaseModel):
    title: str
    description: str
    author: UserSchema


class VideoSchema(BaseVideoSchema):
    id: int
    created_at: datetime.datetime
    file: str
    comments: List[CommentSchema] = []

    class Config:
        orm_mode = True


class VideoCreateSchema(BaseVideoSchema):
    pass
