from typing import Optional, List

from pydantic import BaseModel, validator


class BaseUserSchema(BaseModel):
    username: str


class UserCreateSchema(BaseUserSchema):
    email: str
    password: str


class UserSchema(BaseUserSchema):
    id: int

    class Config:
        orm_mode = True


class UserInfoSchema(UserSchema):
    bio: Optional[str]
    subscribers: List[UserSchema]

    @validator("subscribers")
    def get_amount(cls, lst):
        return len(lst)


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
