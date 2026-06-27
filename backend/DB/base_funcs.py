from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DB.database import connect_to_db
from backend.DB.models import Users


async def get_user_from_db(username:str, session: AsyncSession = Depends(connect_to_db)) -> Users | None:
    user = await session.execute(select(Users).where(Users.username == username))
    user = user.scalar_one_or_none()
    return user

async def get_email_from_db(email: str, session: AsyncSession = Depends(connect_to_db)):
    email = await session.execute(select(Users.email).where(Users.email == email))
    email = email.scalar_one_or_none()
    return email