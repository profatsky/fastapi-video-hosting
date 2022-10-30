from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.schemas.users import UserSchema, UserUpdateSchema, UserInfoSchema
from app.schemas.videos import SimpleVideoSchema
from app.services.auth import get_current_user
from app.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/{user_id}", response_model=UserInfoSchema)
async def get_user_info(
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


@router.get("/{user_id}/subscriptions", response_model=List[UserSchema])
async def get_users_subscriptions(
        user_id: int,
        service: UserService = Depends()
):
    author = await service.get(user_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    return author.subscribe_to


@router.get("/{user_id}/subscribers", response_model=List[UserSchema])
async def get_users_subscribers(
        user_id: int,
        service: UserService = Depends()
):
    author = await service.get(user_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    return author.subscribers


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def subscribe_user(
        user_id: int,
        service: UserService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    if user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't subscribe to yourself"
        )
    author = await service.get(user_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    if user.id in await service.get_subscribers(user_id):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are already subscribed"
        )
    await service.subscribe(user_id, user)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def unsubscribe_user(
        user_id: int,
        service: UserService = Depends(),
        user: UserSchema = Depends(get_current_user)
):
    if user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't unsubscribe from yourself"
        )
    author = await service.get(user_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
    if user.id not in await service.get_subscribers(user_id):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are not subscribed"
        )
    await service.unsubscribe(user_id, user)
    return Response(status_code=status.HTTP_200_OK)
