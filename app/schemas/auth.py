from pydantic import BaseModel


class BaseUserSchema(BaseModel):
    email: str
    username: str


class UserCreateSchema(BaseUserSchema):
    password: str


class UserSchema(BaseUserSchema):
    id: int

    class Config:
        orm_mode = True


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
