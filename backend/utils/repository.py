from abc import ABC, abstractmethod
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DB.database import connect_to_db


class AbstractRepository(ABC):
    model = None
    @abstractmethod
    async def add_one(self):
        raise NotImplementedError
    @abstractmethod
    async def delete_one(self):
        raise NotImplementedError
    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

class SQLAlchemyRepository(AbstractRepository):

    def __init__(self,session:AsyncSession = connect_to_db()):
        self.session = session


    async def add_one(self, data:dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        obj = res.scalar_one()
        await self.session.commit()
        return obj


    async def get_one(self, obj_id:int):
        stmt = select(self.model).where(obj_id == self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_one(self, obj_id:int):
        stmt = select(self.model).where(self.model.id == obj_id)
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if obj:
            await self.session.delete(obj)  # ← правильное удаление
            await self.session.commit()
        return obj

    async def get_all(self):
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        res = res.all()
        return res