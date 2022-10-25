from typing import Optional

from pydantic import BaseModel


class BaseUserSchema(BaseModel):
    username: str


class UserCreateSchema(BaseUserSchema):
    email: str
    password: str


class UserSchema(BaseUserSchema):
    id: int

    class Config:
        orm_mode = True


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
