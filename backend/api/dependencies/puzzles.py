from arq import ArqRedis
from starlette.requests import Request


async def get_redis_pool(request: Request) -> ArqRedis:
    return request.app.state.arq_pool