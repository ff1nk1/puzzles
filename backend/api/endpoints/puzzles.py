from termios import TIOCPKT_DOSTOP

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic.v1 import NoneIsNotAllowedError
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from backend.api.schemas.puzzles import Puzzle, UserSolution
from backend.DB.database import connect_to_db
from backend.DB.models import Puzzles, Test, Submission
from endpoints.auth import auth_user
from puzzle_funcs import check_solution
from schemas.puzzles import SolutionResponse, PuzzleTest
from schemas.user import User

puzzle_router = APIRouter(
    prefix="/puzzles",
    tags=["Puzzle"]
)


@puzzle_router.get("{puzzle_id}",response_model=Puzzle)
async def get_puzzle(puzzle_id: int, session: AsyncSession = Depends(connect_to_db)):
    puzzle = await session.execute(select(Puzzles).where(Puzzles.id == puzzle_id))#возвращает итератор по объектам таблицы
    puzzle = puzzle.scalar_one_or_none()#
    if puzzle is None:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    return puzzle


@puzzle_router.post("/create_puzzle",response_model=Puzzle)
async def create_puzzle(puzzle: Puzzle, session: AsyncSession = Depends(connect_to_db)):
    new_puzzle = Puzzles(**puzzle.model_dump())
    session.add(new_puzzle)
    await session.commit()
    await session.refresh(new_puzzle)
    return new_puzzle

@puzzle_router.post("/create_test/{puzzle_id}",response_model=PuzzleTest)
async def create_test(puzzle_id:int,
                test: PuzzleTest,
                user: User = Depends(auth_user),
                session: AsyncSession = Depends(connect_to_db)):
    sql_query = select(Puzzles).where(Puzzles.id == puzzle_id)
    res = await session.execute(sql_query)
    res = res.scalar_one_or_none()
    if res is None:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    new_test = Test(**test.model_dump())
    new_test.task_id = puzzle_id
    session.add(new_test)
    await session.commit()
    await session.refresh(new_test)
    return new_test


@puzzle_router.post("/check_solution")
async def check_user_solution(user_sol: UserSolution,
                        task_id: int,
                        request: Request,
                        user: User = Depends(auth_user),
                        session: AsyncSession = Depends(connect_to_db)
                        ):
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



@puzzle_router.delete("delete/{puzzle_id}")
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
    sql_query = select(Test).where(Test.id == test_id)
    test = await session.execute(sql_query)
    test = test.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")
    if test.is_private:
        raise HTTPException(status_code=404, detail="Private test")
    return test


@puzzle_router.delete("/test/delete/{test_id}")
async def delete_test(test_id: int,session: AsyncSession = Depends(connect_to_db)):
    sql_query = delete(Test).where(Test.id == test_id).returning(Test)
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