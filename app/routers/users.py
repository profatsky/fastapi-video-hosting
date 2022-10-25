from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.schemas.users import UserSchema, UserUpdateSchema
from app.schemas.videos import SimpleVideoSchema
from app.services.auth import get_current_user
from app.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
        user_id: int,
        service: UserService = Depends()
):
    user = await service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    return user


@router.get("/{user_id}/videos", response_model=List[SimpleVideoSchema])
async def get_users_videos(
        user_id: int,
        service: UserService = Depends()
):
    if not await service.get(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    return await service.get_videos(user_id)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
        user_id: int,
        user_data: UserUpdateSchema,
        service: UserService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )
    return await service.update(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        service: UserService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )
    await service.delete(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
