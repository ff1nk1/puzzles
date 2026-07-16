import os
from dotenv import load_dotenv
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from arq.connections import RedisSettings

from backend.DB.models import Submission
from backend.api.puzzle_funcs import check_solution
from backend.repositories.puzzle_test import PuzzleTestRepository
from backend.repositories.submission import SubmissionRepository
from backend.services.puzzle import PuzzleService
from backend.services.submission import SubmissionService
from backend.core.custom_exceptions import SubmissionNotFoundError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def check_submission_task(ctx, submission_id: int):
    print(f"🔍 Воркер взял в работу попытку №{submission_id}")

    async with async_session() as db_session:
        submission_repo = SubmissionRepository(db_session)
        submission_service = SubmissionService(submission_repo)
        puzzle_test_repo = PuzzleTestRepository(db_session)
        puzzle_service = PuzzleService(puzzle_test_repo=puzzle_test_repo)

        try:
            # 1. Получаем объект
            submission = await submission_service.get_submission(submission_id)
            print(f"✅ Найдена попытка №{submission.id}: статус={submission.status}")

            # 2. Обновляем статус напрямую (без вызова сервиса)
            submission.status = "In Progress"
            await db_session.commit()  # сохраняем изменения

            # 3. Получаем тесты
            tests = await puzzle_service.get_all_tests_to_puzzle(submission.task_id)

            # 4. Запускаем проверку
            verdict_data = await check_solution(
                code=submission.code,
                input_data=tests,
                language=submission.language,
                tl=2.0
            )

            # 5. Обновляем результат напрямую
            submission.status = "Completed"
            submission.verdict = verdict_data["verdict"]
            submission.detail = verdict_data.get("detail", "")
            await db_session.commit()  # сохраняем финальные изменения

            print(f"✅ Попытка №{submission_id} проверена. Вердикт: {verdict_data['verdict']}")

        except SubmissionNotFoundError:
            print(f"❌ Ошибка: Попытка №{submission_id} не найдена в БД.")

class WorkerSettings:
    functions = [check_submission_task]
    redis_settings = RedisSettings(host=REDIS_HOST, port=6379)
    max_jobs = 2