import asyncpg
import os
from dotenv import load_dotenv
from pgvector.asyncpg import register_vector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_pool: asyncpg.Pool | None = None


async def init_db_pool():
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=2,
        max_size=10,
        init=register_vector,
    )
    return _pool


async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("The DB pool has not been initialized yet")
    return _pool