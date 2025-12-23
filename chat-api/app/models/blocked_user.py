from sqlalchemy import sql, orm
from app.models.sql import Base

class BlockedUser(Base):
    __tablename__ = 'blocked_users'
    __table_args__ = (
        sql.UniqueConstraint('blocker_id', 'blocked_id', name='unique_blocked_user'),
        sql.CheckConstraint('blocker_id <> blocked_id', name='check_no_self_block'),
    )

    blocker_id: orm.Mapped[int] = orm.mapped_column(sql.BigInteger, sql.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    blocked_id: orm.Mapped[int] = orm.mapped_column(sql.BigInteger, sql.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)