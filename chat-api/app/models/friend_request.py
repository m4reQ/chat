import datetime
import pydantic
import sqlalchemy
from sqlalchemy import sql, orm
from app.models.sql import Base
from app.models.user import UserActivityStatus

class SQLFriendRequest(Base):
    __tablename__ = 'friend_requests'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('sender_id', 'receiver_id', name='unique_friend_request'),
        sqlalchemy.CheckConstraint('sender_id <> receiver_id', name='check_no_self_friend_request'),
    )

    sender_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey(
            'users.id',
            ondelete='CASCADE',
            name='friend_requests_fk_sender'),
        primary_key=True)
    receiver_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey(
            'users.id',
            ondelete='CASCADE',
            name='friend_requests_fk_receiver'),
        primary_key=True)
    sent_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sql.func.now())

class APIFriendRequest(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    user_id: int
    '''
    ID of user that sent the request
    '''

    username: str
    '''
    Name of user that sent the request
    '''

    last_active: datetime.datetime
    '''
    When user that sent the request was last active
    '''

    activity_status: UserActivityStatus
    '''
    Current activity status of user that sent the request.
    '''

    sent_at: datetime.datetime
    '''
    When the request waas sent
    '''