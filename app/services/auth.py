from datetime import datetime, timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models import UserModel
from app.schemas.auth import TokenSchema
from app.schemas.users import UserSchema, UserCreateSchema
from app.services.base import BaseService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")


class AuthService(BaseService):
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

    async def register_new_user(self, user_data: UserCreateSchema) -> TokenSchema | None:
        user = UserModel(
            email=user_data.email,
            username=user_data.username,
            password=self.hash_password(user_data.password)
        )
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError:
            return

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
