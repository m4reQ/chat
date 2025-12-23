import asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.message import MessageIncoming, SQLMessage

class MessageService:
    def __init__(self,
                 db_sessionmaker: async_sessionmaker[AsyncSession],
                 db_writer_tasks: int,
                 message_queue_size: int,
                 message_upload_batch_size: int,
                 message_upload_batch_timeout: float) -> None:
        self._db_sessionmaker = db_sessionmaker
        self._message_upload_batch_size = message_upload_batch_size
        self._message_upload_batch_timeout = message_upload_batch_timeout
        self._message_queue = asyncio.Queue[MessageIncoming](maxsize=message_queue_size)
        self._db_writer_task: asyncio.Task | None = None

    def start_db_writer_task(self) -> None:
        assert self._db_writer_task is None, 'Writer task already running'
        self._db_writer_task = asyncio.create_task(self._db_writer())

    async def shutdown_db_writer_task(self) -> None:
        if self._db_writer_task is not None:
            self._db_writer_task.cancel()
            await self._db_writer_task

            self._db_writer_task = None
    
    async def upload_message(self, message: MessageIncoming) -> None:
        await self._message_queue.put(message)

    async def _db_writer(self):
        try:
            while True:
                batch = list[MessageIncoming]()

                item = await self._message_queue.get()
                batch.append(item)

                deadline = asyncio.get_event_loop().time() + self._message_upload_batch_timeout

                while len(batch) < self._message_upload_batch_size:
                    timeout = deadline - asyncio.get_event_loop().time()
                    if timeout <= 0.0:
                        break

                    try:
                        item = await asyncio.wait_for(self._message_queue.get(), timeout)
                        batch.append(item)
                    except asyncio.TimeoutError:
                        break
                
                await asyncio.shield(self._upload_message_batch(batch))
        except asyncio.CancelledError:
            await self._flush_remaining_messages()
            raise

    async def _flush_remaining_messages(self):
        items = list[MessageIncoming]()
        while not self._message_queue.empty():
            items.append(self._message_queue.get_nowait())
        
        if len(items) > 0:
            await asyncio.shield(self._upload_message_batch(items))
    
    async def _upload_message_batch(self, batch: list[MessageIncoming]) -> None:
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.insert(SQLMessage).values([x.model_dump() for x in batch])
            await session.execute(query)

            try:
                await session.commit()
            except IntegrityError as e:
                await session.rollback()

                print(e)
                # TODO Check which message caused error, remove it and send info to the client that posted it
                pass
