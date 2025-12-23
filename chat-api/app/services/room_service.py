import sqlalchemy
import sqlalchemy.exc
import fastapi
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.models.chat_room import APIChatRoom, RoomType, SQLChatRoom
from app.models.chat_room_user import SQLChatRoomUser
from app.models.user import SQLUser, APIUserForeign
from app.models.errors import ErrorRoomAlreadyExists, ErrorRoomAlreadyJoined, ErrorRoomInternalJoin, ErrorRoomNameTooLong, ErrorRoomNotFound, ErrorRoomNotOwner, ErrorRoomPrivateJoin, ErrorRoomInvalidTypeChange

class RoomService:
    def __init__(self, db_session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._db_session_factory = db_session_factory

    async def update_room(self,
                          room_id: int,
                          user_id: int,
                          name: str | None = None,
                          description: str | None = None,
                          type: RoomType | None = None):
        async with self._db_session_factory() as session:
            query = sqlalchemy.select(SQLChatRoom) \
                .where(SQLChatRoom.id == room_id)
            room = await session.scalar(query)
            if room is None:
                self._raise_room_not_found(room_id)

            if room.owner_id != user_id:
                ErrorRoomNotOwner(room_id=room_id, user_id=user_id) \
                    .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
                
            if name is not None:
                room.name = name
            
            if description is not None:
                room.description = description

            if type is not None:
                if type == RoomType.INTERNAL:
                    ErrorRoomInvalidTypeChange(room_id=room_id, type=type) \
                        .raise_(fastapi.status.HTTP_400_BAD_REQUEST)

                room.type = type
            
            try:
                await session.commit()
            except sqlalchemy.exc.IntegrityError:
                ErrorRoomAlreadyExists(room_name=name) \
                    .raise_(fastapi.status.HTTP_409_CONFLICT)

    async def get_room_by_id(self, room_id: int) -> APIChatRoom:
        async with self._db_session_factory() as session:
            query = sqlalchemy.select(SQLChatRoom) \
                .where(SQLChatRoom.id == room_id)
            room = await session.scalar(query)
            if room is None:
                self._raise_room_not_found(room_id)
            
            return APIChatRoom(
                id=room.id,
                name=room.name,
                description=room.description,
                type=room.type,
                created_at=room.created_at,
                owner=await self._get_room_owner(room.owner_id, session),
                users=await self._get_room_users(room.id, session))
        
    async def create_room(self, owner_id: int, name: str, description: str | None, type: RoomType):
        async with self._db_session_factory(expire_on_commit=False) as session:
            room = SQLChatRoom(
                name=name,
                description=description,
                type=type,
                owner_id=owner_id)
            session.add(room)

            try:
                await session.flush()
            except sqlalchemy.exc.DataError:
                await session.rollback()

                ErrorRoomNameTooLong(room_name=name, room_description=description) \
                    .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
            except sqlalchemy.exc.IntegrityError as e:
                await session.rollback()

                # TODO Check if error originates from user missing or conflicting room names
                ErrorRoomAlreadyExists(room_name=name) \
                    .raise_(fastapi.status.HTTP_409_CONFLICT)
            
            await session.refresh(room)

            room_user = SQLChatRoomUser(
                user_id=owner_id,
                room_id=room.id)
            session.add(room_user)

            # NOTE No need to check integrity here because potential conflict already happens at previous insert.
            # NOTE If an error happens here the database is in invalid state already.
            await session.commit()

            return room.id
    
    async def join_room(self, room_id: int, user_id: int):
        async with self._db_session_factory() as session:
            query = sqlalchemy.select(SQLChatRoom.type) \
                .where(SQLChatRoom.id == room_id)
            room_type = await session.scalar(query)
            if room_type is None:
                self._raise_room_not_found(room_id)

            if room_type == RoomType.PRIVATE:
                ErrorRoomPrivateJoin(room_id=room_id) \
                    .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
            
            if room_type == RoomType.INTERNAL:
                ErrorRoomInternalJoin(room_id=room_id) \
                    .raise_(fastapi.status.HTTP_400_BAD_REQUEST)

            room_user = SQLChatRoomUser(
                room_id=room_id,
                user_id=user_id)
            session.add(room_user)

            try:
                await session.commit()
            except sqlalchemy.exc.IntegrityError:
                await session.rollback()

                # TODO Check if error comes from user or room not existing

                ErrorRoomAlreadyJoined(room_id=room_id, user_id=user_id) \
                    .raise_(fastapi.status.HTTP_409_CONFLICT)
    
    async def _ensure_room_exists_session(self, room_id: int, session: AsyncSession):
        query = sqlalchemy.select(sqlalchemy.exists().where(SQLChatRoom.id == room_id))
        if not await session.scalar(query):
            self._raise_room_not_found(room_id)
            
    def _raise_room_not_found(self, room_id: int):
        ErrorRoomNotFound(room_id=room_id) \
            .raise_(fastapi.status.HTTP_404_NOT_FOUND)
        
    async def _get_room_owner(self, owner_id: int | None, session: AsyncSession) -> APIUserForeign | None:
        if owner_id is None:
            return None
        
        query = sqlalchemy.select(SQLUser) \
            .where(SQLUser.id == owner_id)
        return APIUserForeign.model_validate(await session.scalar(query))
        
    async def _get_room_users(self, room_id: int, session: AsyncSession) -> list[APIUserForeign]:
        query = sqlalchemy.select(SQLUser) \
            .select_from(SQLChatRoomUser) \
            .where(SQLChatRoomUser.room_id == room_id) \
            .join(SQLUser, SQLUser.id == SQLChatRoomUser.user_id)
        return [APIUserForeign.model_validate(x) for x in await session.scalars(query)]