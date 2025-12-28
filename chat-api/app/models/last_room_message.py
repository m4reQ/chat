import sqlalchemy

from app.models.message import SQLMessage
from app.models.user import SQLUser
from app.models.sql import Base

_last_message_subquery = (
    sqlalchemy.select(
        SQLMessage.id,
        SQLMessage.room_id,
        SQLMessage.type,
        SQLMessage.content,
        SQLMessage.sent_at,
        SQLMessage.sender_id,
        SQLUser.username.label('sender_username'),
    )
    .join(SQLUser, SQLUser.id == SQLMessage.sender_id)
    .where(
        SQLMessage.sent_at == sqlalchemy.select(
            sqlalchemy.func.max(SQLMessage.sent_at)
        )
        .where(SQLMessage.room_id == SQLMessage.room_id)
        .correlate(SQLMessage)
        .scalar_subquery()
    )
    .subquery()
)

class SQLLastRoomMessage(Base):
    __table__ = _last_message_subquery
    __mapper_args__ = {'primary_key': [_last_message_subquery.c.id]}