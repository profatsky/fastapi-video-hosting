from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import TokenSchema
from app.schemas.users import UserCreateSchema
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/sign-up", response_model=TokenSchema)
async def sign_up(
        user_data: UserCreateSchema,
        service: AuthService = Depends()
):
    token = await service.register_new_user(user_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    return token


@router.post("/sign-in", response_model=TokenSchema)
async def sign_in(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AuthService = Depends()
):
    return await service.authenticate_user(
        form_data.username,
        form_data.password
    )
