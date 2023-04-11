from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.users.dependencies import valid_user_id
from .models import UserModel
from app.exceptions_schemas import MessageSchema
from app.users.schemas import UserSchema, UserUpdateSchema, UserInfoSchema
from app.videos.schemas import SimpleVideoSchema
from app.auth.dependencies import get_current_user
from app.users.services import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get(
    "/{user_id}",
    response_model=UserInfoSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserInfoSchema,
            "description": "User information received"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "User doesn't exist"
        }
    }
)
async def get_user_info(
        user: UserModel = Depends(valid_user_id)
):
    """
    Get user info

    **user_id**: user id
    """
    return user


@router.get(
    "/{user_id}/videos",
    response_model=List[SimpleVideoSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[SimpleVideoSchema],
            "description": "Received list of user's videos"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "User doesn't exist"
        }
    }
)
async def get_user_videos(
        user: UserModel = Depends(valid_user_id),
        service: UserService = Depends()
):
    """
    Get user videos

    **user_id**: user id
    """
    return await service.get_videos(user.id)


@router.patch(
    "/{user_id}",
    response_model=UserInfoSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserInfoSchema,
            "description": "User info updated"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": MessageSchema,
            "description": "Don't have permission"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "User doesn't exist"
        }
    }
)
async def update_user_info(
        user_data: UserUpdateSchema,
        user: UserModel = Depends(valid_user_id),
        current_user: UserSchema = Depends(get_current_user),
        service: UserService = Depends()
):
    """
    Update user info

    **user_id**: user id\n
    **user_data**: new username and bio
    """
    if current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have permission"
        )
    return await service.update(user.id, user_data)


@router.get(
    "/{user_id}/subscriptions",
    response_model=List[UserSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserSchema,
            "description": "Received list of user's subscriptions"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "User doesn't exist"
        }
    }
)
async def get_user_subscriptions(
        user: UserModel = Depends(valid_user_id)
):
    """
    Get user subscriptions

    **user_id**: user id
    """
    return user.subscribe_to


@router.get(
    "/{user_id}/subscribers",
    response_model=List[UserSchema],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserSchema,
            "description": "Received list of user's subscribers"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "User doesn't exist"
        }
    }
)
async def get_user_subscribers(
        user: UserModel = Depends(valid_user_id)
):
    """
    Get users subscribers

    **user_id**: user id
    """
    return user.subscribers


@router.put(
    "/{user_id}/subscribers",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": MessageSchema,
            "description": "Subscribed successfully"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "User doesn't exist"
        },
        status.HTTP_405_METHOD_NOT_ALLOWED: {
            "model": MessageSchema,
            "description": "You can't subscribe to yourself"
        }
    }
)
async def subscribe_user(
        service: UserService = Depends(),
        user: UserModel = Depends(valid_user_id),
        current_user: UserSchema = Depends(get_current_user)
):
    """
    Subscribe to user

    **user_id**: user id
    """
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't subscribe to yourself"
        )
    await service.subscribe(user.id, current_user)
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    "/{user_id}/subscribers",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": MessageSchema,
            "description": "Unsubscribed successfully"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": MessageSchema,
            "description": "User doesn't exist"
        },
        status.HTTP_405_METHOD_NOT_ALLOWED: {
            "model": MessageSchema,
            "description": "You can't unsubscribe from yourself"
        }
    }
)
async def unsubscribe_user(
        service: UserService = Depends(),
        user: UserModel = Depends(valid_user_id),
        current_user: UserSchema = Depends(get_current_user)
):
    """
    Unsubscribe user

    **user_id**: user id
    """
    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't unsubscribe from yourself"
        )
    await service.unsubscribe(user.id, current_user)
    return Response(status_code=status.HTTP_200_OK)
