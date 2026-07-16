
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select, delete, Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from backend.api.schemas.puzzles import Puzzle, UserSolution
from backend.DB.database import connect_to_db
from backend.DB.models import Puzzles, PuzzleTest, Submission
from backend.api.schemas.puzzles import SolutionResponse, PuzzleTestPD, PuzzleResponse
from backend.api.dependencies.auth import get_current_user
from backend.repositories.puzzles import PuzzlesRepository

puzzle_router = APIRouter(
    prefix="/puzzles",
    tags=["Puzzle"]
)


@puzzle_router.get("/{puzzle_id}",response_model=PuzzleResponse)
async def get_puzzle(puzzle_id: int, session: AsyncSession = Depends(connect_to_db)):
    puzzles_repo = PuzzlesRepository(session)
    puzzle = await puzzles_repo.get_one(puzzle_id)
    if puzzle is None:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    return puzzle


@puzzle_router.post("/create_puzzle",response_model=PuzzleResponse)
async def create_puzzle(puzzle: Puzzle, session: AsyncSession = Depends(connect_to_db)):
    new_puzzle = Puzzles(**puzzle.model_dump())
    session.add(new_puzzle)
    await session.commit()
    await session.refresh(new_puzzle)
    return new_puzzle

@puzzle_router.post("/create_test/{puzzle_id}",response_model=PuzzleTestPD)
async def create_test(puzzle_id:int,
                test: PuzzleTestPD,
                session: AsyncSession = Depends(connect_to_db)):
    sql_query = select(Puzzles).where(Puzzles.id == puzzle_id)
    res = await session.execute(sql_query)
    res = res.scalar_one_or_none()
    if res is None:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    new_test = PuzzleTest(**test.model_dump())
    new_test.task_id = puzzle_id
    session.add(new_test)
    await session.commit()
    await session.refresh(new_test)
    return new_test


@puzzle_router.post("/check_solution")
async def check_user_solution(user_sol: UserSolution,
                        task_id: int,
                        request: Request,
                        current_user: str = Depends(get_current_user),
                        session: AsyncSession = Depends(connect_to_db)
                        ):
        check_task_in_db = await session.execute(Select(Puzzles).where(Puzzles.id == task_id))
        check_task_in_db = check_task_in_db.scalar_one_or_none()
        if not check_task_in_db:
            raise HTTPException(status_code=404, detail="Task not found")
        new_submission = Submission(
            task_id = task_id,
            language = user_sol.language,
            code = user_sol.code,
            status="Pending"
        )
        session.add(new_submission)
        await session.commit()
        await session.refresh(new_submission)
        arq_pool = request.app.state.arq_pool
        await arq_pool.enqueue_job('check_submission_task', new_submission.id)
        return {"status": "Pending", "submission_id": new_submission.id}



@puzzle_router.delete("/delete/{puzzle_id}")
async def delete_puzzle(puzzle_id: int,session: AsyncSession = Depends(connect_to_db)):
    sql_query = delete(Puzzles).where(Puzzles.id == puzzle_id).returning(Puzzles)

    del_puzzle = await session.execute(sql_query)
    del_puzzle = del_puzzle.scalar_one_or_none()
    if del_puzzle is None:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    await session.commit()
    return {"message": "Puzzle deleted"}


@puzzle_router.get("/get_test/{test_id}")
async def get_test(test_id: int, session: AsyncSession = Depends(connect_to_db)):
    sql_query = select(PuzzleTest).where(PuzzleTest.id == test_id)
    test = await session.execute(sql_query)
    test = test.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    if test.is_private:
        raise HTTPException(status_code=404, detail="Private test")
    return test


@puzzle_router.delete("/test/delete/{test_id}")
async def delete_test(test_id: int,session: AsyncSession = Depends(connect_to_db)):
    sql_query = delete(PuzzleTest).where(PuzzleTest.id == test_id).returning(PuzzleTest)
    del_test = await session.execute(sql_query)
    del_test = del_test.scalar_one_or_none()
    if del_test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    await session.commit()
    return {"message": "Test deleted"}


@puzzle_router.get("/get_submission/{sub_id}")
async def get_submission(sub_id: int, session: AsyncSession = Depends(connect_to_db)):
    sql_query = select(Submission).where(Submission.id == sub_id)
    submission = await session.execute(sql_query)
    submission = submission.scalar_one_or_none()

    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
###TODO
###1.Ручку для того, чтобы получать джсон с решением от конкретного пользоватея(нужно добавить адекватные скрипты по словарю, чтобы не передавать в json python:3.13-slim - сделано
###2. Регистрация, авторизация и тд + (может переделать в jwt)??? - надо
###Сделать ручки CRUD для задач, тестов! - сделано
###Сделать очередь для проверки задач, чтобы не было куча контейнеров сразу - сделано
###Допилить docker-compose