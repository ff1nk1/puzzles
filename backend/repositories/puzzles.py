from backend.DB.models import Puzzles
from backend.utils.repository import SQLAlchemyRepository


class PuzzlesRepository(SQLAlchemyRepository):
    model = Puzzles
