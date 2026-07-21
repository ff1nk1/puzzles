
from backend.repositories.puzzles import PuzzlesRepository


router = "/puzzles"


class TestPuzzle:

    async def test_create_puzzle(self, client, db_session):
        new_puzzle = {
            "title": "test_title",
            "description": "test_description",
            "difficulty": "test_difficulty",
        }
        response = await client.post(f"{router}/create_puzzle", json=new_puzzle)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "test_title"
        assert data["description"] == "test_description"
        assert data["difficulty"] == "test_difficulty"
        assert data["id"] is not None

    async def test_get_puzzle(self, client, db_session):
        puzzle_repo = PuzzlesRepository(db_session)
        new_puzzle_dict = {
            "title": "test_title",
            "description": "test_description",
            "difficulty": "test_difficulty",
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

    async def test_create_test(self, client, db_session, test_puzzle):
        payload = {
            "input_data": '{"a":1,"b":2}',
            "expected_output": "3",
            "is_private": False,
            "task_id": test_puzzle.id,
        }
        response = await client.post(
            f"{router}/create_test/{test_puzzle.id}", json=payload
        )
        assert response.status_code == 200

    async def test_delete_test(self, client, test_test):
        res = await client.delete(f"{router}/test/delete/{test_test.id}")
        assert res.status_code == 200


    async def test_delete_puzzle_success(self, client, test_puzzle):
        """Успешное удаление пазла."""
        response = await client.delete(f"{router}/delete/{test_puzzle.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Puzzle deleted"
        assert data["info"] == test_puzzle.id

    async def test_delete_puzzle_not_found(self, client):
        """Удаление несуществующего пазла."""
        response = await client.delete(f"{router}/delete/99999")
        assert response.status_code == 404
        assert "Puzzle not found" in response.json()["detail"]

    async def test_get_test_success(self, client, test_test):
        """Успешное получение теста по ID."""
        response = await client.get(f"{router}/get_test/{test_test.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_test.id
        assert data["input_data"] == test_test.input_data
        assert data["expected_output"] == test_test.expected_output
        assert data["is_private"] == test_test.is_private
        assert data["task_id"] == test_test.task_id

    async def test_get_test_not_found(self, client):
        """Получение несуществующего теста."""
        response = await client.get(f"{router}/get_test/99999")
        assert response.status_code == 404
        assert "Test not found" in response.json()["detail"]

    async def test_delete_test_already_deleted(self, client, test_test):
        """Повторное удаление уже удалённого теста."""
        # Первое удаление
        response1 = await client.delete(f"{router}/test/delete/{test_test.id}")
        assert response1.status_code == 200
        assert response1.json()["message"] == "Test deleted"

        # Второе удаление – ошибка
        response2 = await client.delete(f"{router}/test/delete/{test_test.id}")
        assert response2.status_code == 404
        assert "Test not found" in response2.json()["detail"]

    async def test_get_submission_success(self, client, test_submission):
        """Успешное получение сабмишена."""
        response = await client.get(f"{router}/get_submission/{test_submission.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_submission.id
        
        assert data["task_id"] == test_submission.task_id
        assert data["language"] == test_submission.language
        assert data["code"] == test_submission.code
        assert data["status"] == test_submission.status

    async def test_get_submission_not_found(self, client):
        """Получение несуществующего сабмишена."""
        response = await client.get(f"{router}/get_submission/99999")
        assert response.status_code == 404
        assert "Submission not found" in response.json()["detail"]