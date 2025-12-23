import sqlalchemy
import pydantic
import datetime
from sqlalchemy import sql, orm
from app.models.sql import Base

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

class APIChatRoomUser(pydantic.BaseModel):
    user_id: int
    room_id: int
    joined_at: datetime.datetime