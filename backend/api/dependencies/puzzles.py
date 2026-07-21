from arq import ArqRedis
from starlette.requests import Request
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.DB.database import connect_to_db
from backend.repositories.puzzles import PuzzlesRepository
from backend.repositories.puzzle_test import PuzzleTestRepository
from backend.repositories.user import UserRepository
from backend.repositories.jwt import JWTRepository
from backend.repositories.submission import SubmissionRepository
from backend.services.puzzle import PuzzleService
from backend.services.user import UserService
from backend.services.security import SecurityService
from backend.services.security import JWTService
from backend.services.submission import SubmissionService


# ============================================
# ГРУППЫ РЕПОЗИТОРИЕВ
# ============================================


async def get_redis_pool(request: Request) -> ArqRedis:
    return request.app.state.arq_pool


class PuzzleRepositories(BaseModel):
    puzzle_repo: PuzzlesRepository
    puzzle_test_repo: PuzzleTestRepository
    submission_repo: SubmissionRepository

    class Config:
        arbitrary_types_allowed = True


# ============================================
# ОТДЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РЕПОЗИТОРИЕВ
# ============================================


async def get_puzzles_repository(
    session: Annotated[AsyncSession, Depends(connect_to_db)],
) -> PuzzlesRepository:
    return PuzzlesRepository(session)


async def get_puzzle_test_repository(
    session: Annotated[AsyncSession, Depends(connect_to_db)],
) -> PuzzleTestRepository:
    return PuzzleTestRepository(session)


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(connect_to_db)],
) -> UserRepository:
    return UserRepository(session)


async def get_jwt_repository(
    session: Annotated[AsyncSession, Depends(connect_to_db)],
) -> JWTRepository:
    return JWTRepository(session)


async def get_submission_repository(
    session: Annotated[AsyncSession, Depends(connect_to_db)],
) -> SubmissionRepository:
    return SubmissionRepository(session)


# ============================================
# ГРУППЫ РЕПОЗИТОРИЕВ (функции)
# ============================================


async def get_puzzle_repositories(
    puzzles_repo: Annotated[PuzzlesRepository, Depends(get_puzzles_repository)],
    puzzle_test_repo: Annotated[
        PuzzleTestRepository, Depends(get_puzzle_test_repository)
    ],
    submission_repo: Annotated[
        SubmissionRepository, Depends(get_submission_repository)
    ],
) -> PuzzleRepositories:
    return PuzzleRepositories(
        puzzle_repo=puzzles_repo,
        puzzle_test_repo=puzzle_test_repo,
        submission_repo=submission_repo,
    )


# ============================================
# СЕРВИСЫ
# ============================================


async def get_puzzle_service(
    repos: Annotated[PuzzleRepositories, Depends(get_puzzle_repositories)],
) -> PuzzleService:
    return PuzzleService(
        puzzle_repo=repos.puzzle_repo,
        puzzle_test_repo=repos.puzzle_test_repo,
        submission_repo=repos.submission_repo,
    )


async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    jwt_repo: Annotated[JWTRepository, Depends(get_jwt_repository)],
) -> UserService:
    return UserService(user_repo=user_repo, jwt_repo=jwt_repo)


async def get_security_service() -> SecurityService:
    return SecurityService()


async def get_jwt_service() -> JWTService:
    return JWTService()


async def get_submission_service(
    submission_repo: Annotated[
        SubmissionRepository, Depends(get_submission_repository)
    ],
) -> SubmissionService:
    return SubmissionService(submission_repo=submission_repo)
