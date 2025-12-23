import datetime
import pydantic
import sqlalchemy
from sqlalchemy import sql, orm
from app.models.sql import Base
from app.models.user import UserActivityStatus

class SQLFriend(Base):
    __tablename__ = 'friends'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('user_id', 'friend_id', name='unique_friends'),
        sqlalchemy.CheckConstraint('user_id <> friend_id', name='check_no_self_friend'),
    )

    user_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True)
    friend_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True)
    accepted_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sql.func.now())

class APIFriend(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    user_id: int
    '''
    Friend user ID
    '''

    username: str
    '''
    Friend username
    '''

    last_active: datetime.datetime
    '''
    When the friend was last active
    '''

    activity_status: UserActivityStatus
    '''
    Current activity status of the friend user
    '''

class APIFriendActivity(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    id: int
    '''
    Friend user ID
    '''

    activity_status: UserActivityStatus
    '''
    Current activity status of the friend user
    '''