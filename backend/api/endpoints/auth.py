from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.DB.base_funcs import get_user_from_db, get_email_from_db
from backend.api.schemas.puzzles import Puzzle
from backend.DB.database import connect_to_db
from backend.DB.models import Puzzles, Users
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from schemas.user import UserRegister, User

security = HTTPBasic()
auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth_router.post("/register/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister,
                  credentials: HTTPBasicCredentials = Depends(security),
                  session: AsyncSession = Depends(connect_to_db)):
    if  await get_user_from_db(user.username,session) is not None or  await get_email_from_db(user.email,session) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    user = Users(**user.model_dump())###Нужно обязательно добавить хэширование пароля перед добавлением в бд
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def auth_user(credentials: HTTPBasicCredentials = Depends(security),
                session:AsyncSession = Depends(connect_to_db)):
    user = await get_user_from_db(credentials.username, session)
    if user is None or user.password != user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

