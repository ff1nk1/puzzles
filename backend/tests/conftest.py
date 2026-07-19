import pytest
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.DB.database import connect_to_db, Base
from backend.main import app
#Для ddl синхронный
#Для dml асинхронный
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
        yield db_session  # Отдаем сессию тесту и приложению
    app.dependency_overrides[connect_to_db] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client():
    """Асинхронный HTTP-клиент, подключенный напрямую к FastAPI."""
    # Связываем транспорт с вашим FastAPI-приложением 'app'
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac