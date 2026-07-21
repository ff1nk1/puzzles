from sqlalchemy import select, insert
from backend.DB.models import Users
from backend.utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = Users

    async def get_one_by_username(self, username: str) -> Users | None:
        user = await self.session.execute(
            select(self.model).where(self.model.username == username)
        )
        user = user.scalar_one_or_none()
        return user

    async def get_one_by_email(self, email: str) -> str | None:
        email = await self.session.execute(
            select(self.model.email).where(self.model.email == email)
        )
        email = email.scalar_one_or_none()
        return email

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        obj = res.scalar_one()
        # читаем атрибуты, пока объект "жив"
        user_data = {"id": obj.id, "username": obj.username}
        await self.session.commit()
        return user_data
