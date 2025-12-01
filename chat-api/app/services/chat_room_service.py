import sqlmodel
import fastapi
import typing as t
from dependency_injector.providers import Factory

from app.models.sql import SQLChatRoom, SQLChatRoomUser, SQLUser
from app.models.responses import APIChatRoomUser

class ChatRoomService:
    def __init__(self,
                 db_session_factory: Factory[sqlmodel.Session]) -> None:
        self._db_session_factory = db_session_factory

    def get_room_info(self, room_id: int) -> SQLChatRoom:
        with self._db_session_factory(expire_on_commit=False) as session:
            query = sqlmodel.select(SQLChatRoom).where(SQLChatRoom.id == room_id)
            room = session.exec(query).one_or_none()
            if room is None:
                self._raise_room_does_not_exist(room_id)

        return room

    def get_room_users(self, room_id: int) -> list[APIChatRoomUser]:
        with self._db_session_factory(expire_on_commit=False) as session:
            query = sqlmodel.select(SQLChatRoom).where(SQLChatRoom.id == room_id)
            room = session.exec(query).one_or_none()
            if room is None:
                self._raise_room_does_not_exist(room_id)

            query = sqlmodel.select(SQLChatRoomUser) \
                .where(SQLChatRoomUser.room_id == room_id) \
                .join(SQLUser, SQLUser.id == SQLChatRoomUser.user_id) \
                .join(SQLChatRoom, SQLChatRoom.id == SQLChatRoomUser.room_id)
            result = session.exec(query).all()
            pass
    
    def _raise_room_does_not_exist(self, room_id: int) -> t.NoReturn:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail={
                'error': 'Chat room with given ID was not found.',
                'room_id': room_id})