
from arq import ArqRedis

from backend.DB.models import Puzzles
from backend.core.custom_exceptions import PuzzleNotFoundError, TestNotFoundError
from backend.api.schemas.puzzles import (
    Puzzle,
    PuzzleTestPD,
    UserSolution,
    SubmissionToAdd,
)


class PuzzleService:
    model = Puzzles

    def __init__(
        self, puzzle_repo=None, puzzle_test_repo=None, submission_repo=None
    ) -> None:
        self.puzzle_repo = puzzle_repo
        self.puzzle_test_repo = puzzle_test_repo
        self.submission_repo = submission_repo

    async def get_puzzle(self, puzzle_id: int):
        puzzle = await self.puzzle_repo.get_one(puzzle_id)
        if puzzle is None:
            raise PuzzleNotFoundError()
        return puzzle

    async def create_puzzle(self, puzzle: Puzzle):
        new_puzzle = await self.puzzle_repo.add_one(data=puzzle.model_dump())
        return new_puzzle

    async def create_test(self, puzzle_id: int, puzzle_test: PuzzleTestPD):
        puzzle = await self.puzzle_repo.get_one(puzzle_id)
        if puzzle is None:
            raise PuzzleNotFoundError()
        new_test_dict = puzzle_test.model_dump()
        new_test_dict["task_id"] = puzzle_id
        new_test = await self.puzzle_test_repo.add_one(data=new_test_dict)
        return new_test

    async def send_user_solution(
        self, puzzle_id: int, user_sol: UserSolution, arq_pool: ArqRedis
    ):
        puzzle = await self.puzzle_repo.get_one(puzzle_id)
        if puzzle is None:
            raise PuzzleNotFoundError()

        solution_dict = user_sol.model_dump()
        solution_dict["task_id"] = puzzle_id
        solution_dict["status"] = "Pending"

        new_submission = SubmissionToAdd(**solution_dict)
        new_submission_db = await self.submission_repo.add_one(
            new_submission.model_dump()
        )


        await arq_pool.enqueue_job("check_submission_task", new_submission_db.id)

        return {"status": "Pending", "submission_id": new_submission_db.id}

    async def delete_puzzle(self, puzzle_id: int):
        del_puzzle = await self.puzzle_repo.delete_one(puzzle_id)
        if del_puzzle is None:
            raise PuzzleNotFoundError()
        return del_puzzle

    async def get_test(self, test_id: int):
        test = await self.puzzle_test_repo.get_one(test_id)
        if test is None:
            raise TestNotFoundError()
        return test

    async def get_all_tests_to_puzzle(self, puzzle_id: int):
        all_tests = await self.puzzle_test_repo.get_all_tests_to_puzzle(puzzle_id)
        return list(all_tests)

    async def delete_test(self, test_id: int):
        del_test = await self.puzzle_test_repo.delete_one(test_id)
        if del_test is None:
            raise TestNotFoundError()
