from datetime import datetime, timedelta

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.database import get_session
from app.models import UserModel
from app.schemas.auth import UserSchema, TokenSchema, UserCreateSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSchema:
    return AuthService.validate_token(token)


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hash(password)

    @staticmethod
    def validate_token(token: str) -> UserSchema:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            raise exception from None

        user_data = payload.get("user")

        try:
            user = UserSchema.parse_obj(user_data)
        except ValidationError:
            raise exception from None

        return user

    @staticmethod
    def create_token(user: UserModel) -> TokenSchema:
        user_data = UserSchema.from_orm(user)

        now = datetime.utcnow()
        payload = {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=settings.jwt_expiration),
            "sub": str(user_data.id),
            "user": user_data.dict()
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

        return TokenSchema(access_token=token)

    async def register_new_user(self, user_data: UserCreateSchema) -> TokenSchema:
        user = UserModel(
            email=user_data.email,
            username=user_data.username,
            password=self.hash_password(user_data.password)
        )

        self.session.add(user)
        await self.session.commit()

        return self.create_token(user)

    async def authenticate_user(self, email: str, password: str) -> TokenSchema:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

        user = await self.session.execute(
            select(UserModel)
            .where(UserModel.email == email)
        )
        user = user.scalar()

        if not user or not self.verify_password(password, user.password):
            raise exception

        return self.create_token(user)
