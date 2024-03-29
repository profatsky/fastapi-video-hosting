from fastapi import Depends, HTTPException, status

from .models import UserModel
from app.users.services import UserService


async def valid_user_id(
        user_id: int,
        service: UserService = Depends()
) -> UserModel:
    user = await service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    return user
