from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.dependencies.users import valid_user_id
from app.models import UserModel
from app.schemas.users import UserSchema, UserUpdateSchema, UserInfoSchema
from app.schemas.videos import SimpleVideoSchema
from app.dependencies.auth import get_current_user
from app.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/{user_id}", response_model=UserInfoSchema)
async def get_user_info(
        user: UserModel = Depends(valid_user_id)
):
    return user


@router.get("/{user_id}/videos", response_model=List[SimpleVideoSchema])
async def get_users_videos(
        user: UserModel = Depends(valid_user_id),
        service: UserService = Depends()
):
    return await service.get_videos(user.id)


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
        user_data: UserUpdateSchema,
        user: UserModel = Depends(valid_user_id),
        current_user: UserSchema = Depends(get_current_user),
        service: UserService = Depends()
):
    if current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )
    return await service.update(user.id, user_data)


@router.get("/{user_id}/subscriptions", response_model=List[UserSchema])
async def get_users_subscriptions(
        user: UserModel = Depends(valid_user_id)
):
    return user.subscribe_to


@router.get("/{user_id}/subscribers", response_model=List[UserSchema])
async def get_users_subscribers(
        user: UserModel = Depends(valid_user_id)
):
    return user.subscribers


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def subscribe_user(
        service: UserService = Depends(),
        user: UserModel = Depends(valid_user_id),
        current_user: UserSchema = Depends(get_current_user)
):
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't subscribe to yourself"
        )
    await service.subscribe(user.id, current_user)
    return Response(status_code=status.HTTP_200_OK)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def unsubscribe_user(
        service: UserService = Depends(),
        user: UserModel = Depends(valid_user_id),
        current_user: UserSchema = Depends(get_current_user)
):
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't unsubscribe from yourself"
        )
    await service.unsubscribe(user.id, current_user)
    return Response(status_code=status.HTTP_200_OK)
