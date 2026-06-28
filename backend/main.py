from contextlib import asynccontextmanager

import uvicorn
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from backend.api.endpoints.puzzles import puzzle_router
from backend.api.endpoints.auth import auth_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте создаем пул подключений к ARQ Redis
    app.state.arq_pool = await create_pool(RedisSettings(host='localhost', port=6379))
    yield
    # При выключении закрываем пул
    await app.state.arq_pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(puzzle_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app")