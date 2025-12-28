import typing
import sqlalchemy
import pydantic
import datetime
from sqlalchemy import sql, orm
from app.models.sql import Base

if typing.TYPE_CHECKING:
    from app.models.user import SQLUser, UserActivityStatus
    from app.models.chat_room import SQLChatRoom

class SQLChatRoomUser(Base):
    __tablename__ = 'chat_room_users'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('user_id', 'room_id', name='unique_chat_room_user'),
    )
    
    user_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True)
    room_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey('chat_rooms.id', ondelete='CASCADE'),
        primary_key=True)
    joined_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sql.func.now())
    
    room: orm.Mapped['SQLChatRoom'] = orm.relationship(
        'SQLChatRoom',
        back_populates='users')
    user: orm.Mapped['SQLUser'] = orm.relationship(
        'SQLUser',
        back_populates='rooms')

    @property
    def is_owner(self) -> bool:
        return self.room.owner_id == self.user.id
    
    @property
    def username(self) -> str:
        return self.user.username
    
    @property
    def activity_status(self) -> UserActivityStatus:
        return self.user.activity_status
    
    @property
    def last_active(self) -> datetime.datetime:
        return self.user.last_active

class APIChatRoomUser(pydantic.BaseModel):
    user_id: int
    room_id: int
    joined_at: datetime.datetime