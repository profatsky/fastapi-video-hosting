from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import TokenSchema
from app.exceptions_schemas import MessageSchema
from app.users.schemas import UserCreateSchema
from .services import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/sign-up",
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": TokenSchema,
            "description": "Successfully created a new account"
        },
        status.HTTP_409_CONFLICT: {
            "model": MessageSchema,
            "description": "User with this email already exists"
        }
    }
)
async def sign_up(
        user_data: UserCreateSchema,
        service: AuthService = Depends()
):
    """
    Create a new account

    **user_data**: username, email and password for registration
    """
    token = await service.register_new_user(user_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    return token


@router.post(
    "/sign-in",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": TokenSchema,
            "description": "Successful login"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": MessageSchema,
            "description": "Could not validate credentials"
        }
    }
)
async def sign_in(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AuthService = Depends()
):
    """
    Authorization

    **form_data**: password and email for authorization
    """
    return await service.authenticate_user(
        form_data.username,
        form_data.password
    )
