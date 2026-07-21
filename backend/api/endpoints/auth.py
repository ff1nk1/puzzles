from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from starlette import status
from pwdlib import PasswordHash

from backend.core.custom_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    WrongPasswordError,
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
)
from backend.api.schemas.user import UserRegister, UserResponse
from backend.services.user import UserService
from backend.api.dependencies.puzzles import get_user_service

pwd_context = PasswordHash.recommended()

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.post(
    "/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_reg: UserRegister,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    try:
        user = await user_service.add_user(user_reg)
        return UserResponse(username=user["username"], id=user["id"])
    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User already exists")


@auth_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    try:
        res = await user_service.login(form_data)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except WrongPasswordError:
        raise HTTPException(status_code=400, detail="Wrong password")
    return res


@auth_router.post("/refresh")
async def get_refresh_token(
    refresh_token: str, user_service: Annotated[UserService, Depends(get_user_service)]
):
    try:
        res = await user_service.refresh(refresh_token)
        return res
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except RefreshTokenExpiredError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except RefreshTokenNotFoundError:
        raise HTTPException(
            status_code=400, detail="Refresh token not found or smth went wrong"
        )
