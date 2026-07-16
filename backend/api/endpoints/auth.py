from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pwdlib import PasswordHash

from backend.DB.database import connect_to_db
from backend.core.custom_exceptions import UserAlreadyExistsError, UserNotFoundError, WrongPasswordError, \
    RefreshTokenExpiredError, RefreshTokenNotFoundError
from backend.repositories.jwt import JWTRepository
from backend.repositories.user import UserRepository
from backend.api.schemas.user import UserRegister, UserResponse
from backend.services.user import UserService

pwd_context = PasswordHash.recommended()

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth_router.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_reg: UserRegister,
                        session: AsyncSession = Depends(connect_to_db)):
    try:
        repo = UserRepository(session)
        service = UserService(repo)
        user = await service.add_user(user_reg)#Придёт словарь с двумя ключами, нужно, чтобы вернуть us и id
        return UserResponse(username=user["username"],id=user["id"])

    except UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="User already exists")


@auth_router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(connect_to_db)):
    repo = UserRepository(session)
    jwt_repo = JWTRepository(session)
    service = UserService(repo,jwt_repo)
    try:
        res = await service.login(form_data)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except WrongPasswordError:
        raise HTTPException(status_code=400, detail="Wrong password")
    return res

@auth_router.post("/refresh")
async def get_refresh_token(refresh_token:str,
                            session: AsyncSession = Depends(connect_to_db)):
    try:
        user_repo = UserRepository(session)
        jwt_repo = JWTRepository(session)
        service = UserService(user_repo,jwt_repo)
        res = await service.refresh(refresh_token)
        return res
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except RefreshTokenExpiredError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except RefreshTokenNotFoundError:
        raise HTTPException(status_code=400, detail="Refresh token not found or smth went wrong")
