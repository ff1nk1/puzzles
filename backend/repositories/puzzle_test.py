from sqlalchemy import select

from backend.DB.models import PuzzleTest
from backend.utils.repository import SQLAlchemyRepository


class PuzzleTestRepository(SQLAlchemyRepository):
    model = PuzzleTest

    async def get_all_tests_to_puzzle(self, puzzle_id: int):
        stmt = select(self.model).where(PuzzleTest.task_id == puzzle_id)
        tests_result = await self.session.execute(stmt)
        return tests_result.scalars().all()
