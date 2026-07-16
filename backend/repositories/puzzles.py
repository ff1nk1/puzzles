from sqlalchemy import select,insert


from backend.DB.models import Puzzles, PuzzleTest
from backend.utils.repository import SQLAlchemyRepository


class PuzzlesRepository(SQLAlchemyRepository):
    model = Puzzles





