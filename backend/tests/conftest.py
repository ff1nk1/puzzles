# tests/conftest.py
import time
import random
import pytest
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.DB.database import connect_to_db, Base
from backend.main import app
from backend.repositories.puzzle_test import PuzzleTestRepository
from backend.repositories.puzzles import PuzzlesRepository
from backend.repositories.user import UserRepository
from backend.repositories.submission import SubmissionRepository
from backend.services.security import SecurityService

# Для ddl синхронный
# Для dml асинхронный
ASYNC_DB_URL = "postgresql+asyncpg://ffink:1111@database:5432/puzzles_site"
SYNC_DB_URL = "postgresql://ffink:1111@database:5432/puzzles_site"

sync_engine = create_engine(SYNC_DB_URL)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=sync_engine)
    yield


@pytest.fixture(scope="function")
async def db_session():
    engine = create_async_engine(ASYNC_DB_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()

    await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def override_get_db(db_session: AsyncSession):
    """Подменяем зависимость БД."""

    async def _override():
        yield db_session

    app.dependency_overrides[connect_to_db] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client():
    """Асинхронный HTTP-клиент, подключенный напрямую к FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ===== РЕПОЗИТОРИИ =====

@pytest.fixture
async def puzzle_repo(db_session):
    return PuzzlesRepository(db_session)

@pytest.fixture
async def puzzle_test_repo(db_session):
    return PuzzleTestRepository(db_session)

@pytest.fixture
async def user_repo(db_session):
    return UserRepository(db_session)

@pytest.fixture
async def submission_repo(db_session):
    return SubmissionRepository(db_session)


# ===== ТЕСТОВЫЕ ДАННЫЕ =====

@pytest.fixture
async def test_puzzle(db_session, puzzle_repo):
    puzzle = await puzzle_repo.add_one({
        "title": "puzzle for solution",
        "description": "test_description",
        "difficulty": "easy",
    })
    return puzzle

@pytest.fixture
async def test_test(db_session, puzzle_test_repo, test_puzzle):
    test = await puzzle_test_repo.add_one({
        "input_data": '{"a":1,"b":2}',
        "expected_output": "3",
        "is_private": False,
        "task_id": test_puzzle.id,
    })
    return test


@pytest.fixture
async def test_user(db_session, user_repo):
    """Создаёт тестового пользователя с уникальными данными."""


    # Генерируем уникальные данные для каждого запуска
    unique_suffix = f"{int(time.time())}_{random.randint(1000, 9999)}"
    security_service = SecurityService()

    user_data = {
        "username": f"testuser_{unique_suffix}",
        "hashed_password": await security_service.hash_password("testpass"),
        "email": f"test_{unique_suffix}@example.com",
    }
    user = await user_repo.add_one(user_data)
    return user

@pytest.fixture
async def test_submission(db_session, submission_repo, test_puzzle, test_user):
    """Создаёт тестовый сабмишен."""
    submission_dict = {
        "task_id": test_puzzle.id,  
        "language": "python",
        "code": "print('Hello')",
        "status": "pending",
    }
    submission = await submission_repo.add_one(submission_dict)
    return submission