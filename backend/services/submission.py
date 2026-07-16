from backend.core.custom_exceptions import SubmissionNotFoundError


class SubmissionService:
    def __init__(self,submission_repo = None):
        self.submission_repo = submission_repo


    async def get_submission(self,test_id):
        submission = await self.submission_repo.get_one(test_id)
        if submission is None:
            raise SubmissionNotFoundError()
        return submission

    async def update_submission(self, submission_id: int, **fields):
        updated = await self.submission_repo.update(submission_id, **fields)

        if updated is None:
            raise SubmissionNotFoundError()

        return updated
