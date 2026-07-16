from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy.sql.annotation import Annotated


class Puzzle(BaseModel):
    title: str
    description: str
    difficulty: str

class PuzzleResponse(Puzzle):
    id: int

class PuzzleTestPD(BaseModel):
    input_data:str
    expected_output:str
    is_private:bool = Annotated[bool, Field(default=False)]


class UserSolution(BaseModel):
    language:str
    code: str


class SolutionResponse(BaseModel):
    solved: bool
    info: Optional[str]


