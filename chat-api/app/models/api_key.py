import datetime
import uuid
import sqlalchemy
from sqlalchemy import sql, orm
from app.models.sql import Base, MySQLUUID

class SQLAPIKey(Base):
    __tablename__ = 'api_keys'

    key: orm.Mapped[uuid.UUID] = orm.mapped_column(MySQLUUID(), primary_key=True, server_default=sql.text('(UUID_TO_BIN(UUID(), 1))'))
    is_active: orm.Mapped[bool] = orm.mapped_column(sqlalchemy.Boolean, nullable=False, server_default='1')
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(sqlalchemy.DateTime, nullable=False, server_default=sql.func.now())