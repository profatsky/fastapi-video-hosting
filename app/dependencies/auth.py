from fastapi import Depends

from app.schemas.users import UserSchema
from app.services.auth import AuthService, oauth2_scheme


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSchema:
    return AuthService.validate_token(token)
