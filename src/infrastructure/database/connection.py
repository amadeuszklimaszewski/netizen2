from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from src.settings import settings

engine = create_async_engine(settings.postgres_url, echo=False)


async def get_db() -> AsyncGenerator[AsyncConnection, None]:
    async with engine.begin() as conn:
        yield conn
