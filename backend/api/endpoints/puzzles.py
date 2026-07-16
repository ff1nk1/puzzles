from typing import Annotated

from arq import ArqRedis
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.puzzles import Puzzle, UserSolution
from backend.DB.database import connect_to_db
from backend.api.schemas.puzzles import PuzzleTestPD, PuzzleResponse
from backend.api.dependencies.auth import get_current_user
from backend.repositories.puzzles import PuzzlesRepository
from backend.core.custom_exceptions import PuzzleNotFoundError, TestNotFoundError, SubmissionNotFoundError
from backend.services.puzzle import PuzzleService
from backend.repositories.puzzle_test import PuzzleTestRepository
from backend.api.schemas.puzzles import PuzzleTestPDResponse
from backend.api.dependencies.puzzles import get_redis_pool
from backend.repositories.submission import SubmissionRepository
from backend.services.submission import SubmissionService

puzzle_router = APIRouter(
    prefix="/puzzles",
    tags=["Puzzle"]
)


@puzzle_router.get("/{puzzle_id}",response_model=PuzzleResponse)
async def get_puzzle(puzzle_id: int,
                     session: Annotated[AsyncSession, Depends(connect_to_db)]):
    try:
        puzzles_repo = PuzzlesRepository(session)
        puzzle_service = PuzzleService(puzzle_repo=puzzles_repo)
        puzzle = await puzzle_service.get_puzzle(puzzle_id)
        return puzzle
    except PuzzleNotFoundError:
        raise HTTPException(status_code=404, detail="Puzzle not found")


@puzzle_router.post("/create_puzzle",response_model=PuzzleResponse)
async def create_puzzle(puzzle: Puzzle,
                        session: Annotated[AsyncSession, Depends(connect_to_db)]):
    puzzle_repo = PuzzlesRepository(session)
    puzzle_service = PuzzleService(puzzle_repo)
    new_puzzle = await puzzle_service.create_puzzle(puzzle)
    return new_puzzle


@puzzle_router.post("/create_test/{puzzle_id}",response_model=PuzzleTestPDResponse)
async def create_test(puzzle_id:int,
                test: PuzzleTestPD,
                session:Annotated[AsyncSession, Depends(connect_to_db)]):
    try:
        puzzle_repo = PuzzlesRepository(session)
        puzzle_test_repo = PuzzleTestRepository(session)
        puzzle_service = PuzzleService(puzzle_repo=puzzle_repo, puzzle_test_repo=puzzle_test_repo)
        new_test = await puzzle_service.create_test(puzzle_id, test)
        return new_test
    except PuzzleNotFoundError:
        raise HTTPException(status_code=404, detail="Puzzle not found")


@puzzle_router.post("/check_solution")
async def check_user_solution(user_sol: UserSolution,
                        puzzle_id: int,
                        arq_pool: Annotated[ArqRedis, Depends(get_redis_pool)],
                        current_user: Annotated[str, Depends(get_current_user)],
                        session: Annotated[AsyncSession, Depends(connect_to_db)]
                        ):
        puzzle_repo = PuzzlesRepository(session)
        submission_repo = SubmissionRepository(session)
        puzzle_service = PuzzleService(puzzle_repo=puzzle_repo, submission_repo=submission_repo)
        try:
            return await puzzle_service.send_user_solution(puzzle_id, user_sol,arq_pool)
        except PuzzleNotFoundError:
            raise HTTPException(status_code=404, detail="Puzzle not found")


@puzzle_router.delete("/delete/{puzzle_id}")
async def delete_puzzle(puzzle_id: int,
                        session: Annotated[AsyncSession, Depends(connect_to_db)]):
    puzzle_repo = PuzzlesRepository(session)
    puzzle_service = PuzzleService(puzzle_repo=puzzle_repo)
    try:
        del_puzzle = await puzzle_service.delete_puzzle(puzzle_id)
        return {"message": "Puzzle deleted","info":del_puzzle.id}
    except PuzzleNotFoundError:
        raise HTTPException(status_code=404, detail="Puzzle not found. Nothing to delete")



@puzzle_router.get("/get_test/{test_id}")
async def get_test(test_id: int,
                   session: Annotated[AsyncSession, Depends(connect_to_db)]):
    puzzle_test_repo = PuzzleTestRepository(session)
    puzzle_service = PuzzleService(puzzle_test_repo=puzzle_test_repo)
    try:
        test = await puzzle_service.get_test(test_id)
        return test
    except TestNotFoundError:
        raise HTTPException(status_code=404, detail="Test not found.")


@puzzle_router.delete("/test/delete/{test_id}")
async def delete_test(test_id: int,
                      session: Annotated[AsyncSession, Depends(connect_to_db)]):
    try:
        puzzle_test_repo = PuzzleTestRepository(session)
        puzzle_service = PuzzleService(puzzle_test_repo=puzzle_test_repo)
        await puzzle_service.delete_test(test_id)
        return {"message": "Test deleted"}
    except TestNotFoundError:
        raise HTTPException(status_code=404, detail="Test not found.Nothing to be deleted")



@puzzle_router.get("/get_submission/{sub_id}")
async def get_submission(sub_id: int,
                         session: Annotated[AsyncSession, Depends(connect_to_db)]):
    submission_repo = SubmissionRepository(session)
    submission_service = SubmissionService(submission_repo=submission_repo)
    try:
        submission = await submission_service.get_submission(sub_id)
        return submission

    except SubmissionNotFoundError:
        raise HTTPException(status_code=404, detail="Submission not found")
