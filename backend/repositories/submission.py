from sqlalchemy import update

from backend.DB.models import Submission
from backend.utils.repository import SQLAlchemyRepository


class SubmissionRepository(SQLAlchemyRepository):
    model = Submission

    async def update(self, obj_id: int, **fields):
        if not fields:
            return  # Ничего не обновляем

        stmt = update(self.model).where(self.model.id == obj_id).values(**fields)
        await self.session.execute(stmt)
        await self.session.commit()
