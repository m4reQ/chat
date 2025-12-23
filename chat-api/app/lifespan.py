import contextlib
import fastapi
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine
from dependency_injector.wiring import inject, Provide

from app.models.sql import Base

@contextlib.asynccontextmanager
@inject
async def lifespan(app: fastapi.FastAPI, db_engine: AsyncEngine = Provide['db_engine']):
    # startup
    async with db_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    
    yield

    #cleanup