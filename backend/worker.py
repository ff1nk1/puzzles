
from arq.connections import RedisSettings
from sqlalchemy import select
#arq backend.worker.WorkerSettings
from backend.api.puzzle_funcs import check_solution
from backend.DB.models import Submission, Test
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")



engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def check_submission_task(ctx, submission_id: int):
    print(f"ARQ Воркер взял в работу попытку №{submission_id}")

    async with async_session() as db_session:
        #Считываем попытку решения из базы
        stmt = select(Submission).where(Submission.id == submission_id)
        result = await db_session.execute(stmt)
        submission = result.scalar_one_or_none()

        if not submission:
            print(f"Ошибка: Попытка №{submission_id} не найдена в БД.")
            return

        #Меняем статус на "In Progress"
        submission.status = "In Progress"
        await db_session.commit()

        current_task_id = submission.task_id

        tests_stmt = select(Test).where(Test.task_id == current_task_id)
        tests_result = await db_session.execute(tests_stmt)
        input_data = list(tests_result.scalars().all())

        verdict_data = await check_solution(
            code=submission.code,
            input_data=input_data,
            language=submission.language,
            tl=2.0
        )
        submission.status = "Completed"
        submission.verdict = verdict_data["verdict"]
        submission.detail = verdict_data.get("detail", "")
        await db_session.commit()

        print(f"Попытка №{submission_id} проверена."
              f" Вердикт: {submission.verdict}\n"
              f"Информация: {submission.detail}",sep='\n')


class WorkerSettings:
    functions = [check_submission_task]

    redis_settings = RedisSettings(host='localhost', port=6379)

    max_jobs = 2
