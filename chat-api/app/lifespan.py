import contextlib
import fastapi
from sqlalchemy.ext.asyncio import AsyncEngine
from dependency_injector.wiring import inject, Provide

from app.models.sql import Base
from app.services.message_service import MessageService

@contextlib.asynccontextmanager
@inject
async def lifespan(app: fastapi.FastAPI,
                   db_engine: AsyncEngine = Provide['db_engine'],
                   message_service: MessageService = Provide['message_service']):
    # startup
    async with db_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    
    message_service.start_db_writer_task()
    
    yield

    #cleanup
    await message_service.shutdown_db_writer_task()