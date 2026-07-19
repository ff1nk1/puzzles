import pytest

from backend.repositories.puzzles import PuzzlesRepository

router = "/puzzles"
class TestPuzzle:
    async def test_create_puzzle(self,client,db_session):
        new_puzzle = {  "title": "test_title",
                        "description": "test_description",
                        "difficulty": "test_difficulty"
                     }
        response = await client.post(f"{router}/create_puzzle",json=new_puzzle)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "test_title"
        assert data["description"] == "test_description"
        assert data["difficulty"] == "test_difficulty"
        assert data["id"] is not None

    async def test_get_puzzle(self,client,db_session):
        puzzle_repo = PuzzlesRepository(db_session)
        new_puzzle_dict = {"title": "test_title",
                      "description": "test_description",
                      "difficulty": "test_difficulty"
                      }
        new_puzzle = await puzzle_repo.add_one(new_puzzle_dict)
        new_puzzle_id = new_puzzle.id
        res = await client.get(f"{router}/{new_puzzle_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "test_title"
        assert data["description"] == "test_description"
        assert data["difficulty"] == "test_difficulty"
        assert data["id"] == new_puzzle_id
