import datetime

from pydantic import BaseModel

from app.schemas.auth import UserSchema


class BaseVideoSchema(BaseModel):
    title: str
    description: str
    author: UserSchema


class VideoSchema(BaseVideoSchema):
    id: int
    created_at: datetime.datetime
    file: str

    class Config:
        orm_mode = True


class VideoCreateSchema(BaseVideoSchema):
    pass
