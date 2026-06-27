import uvicorn
from fastapi import FastAPI

from backend.api.endpoints.puzzles import puzzle_router
from backend.api.endpoints.auth import auth_router

app = FastAPI()
app.include_router(puzzle_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app")