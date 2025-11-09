import datetime
import uuid
import sqlmodel

class SQLUser(sqlmodel.SQLModel, table=True):
    __tablename__ = 'users'

    id: int | None = sqlmodel.Field(primary_key=True)
    username: str = sqlmodel.Field(max_length=256, index=True)
    email: str = sqlmodel.Field(max_length=254, index=True)
    password_hash: bytes = sqlmodel.Field(max_length=60)
    country_code: str = sqlmodel.Field(max_length=2)
    is_email_verified: bool = sqlmodel.Field(default=False)
    created_at: datetime.datetime = sqlmodel.Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class SQLAPIKey(sqlmodel.SQLModel, table=True):
    __tablename__ = 'api_keys'

    id: int | None = sqlmodel.Field(primary_key=True)
    is_active: bool = sqlmodel.Field(default=True)
    api_key: uuid.UUID = sqlmodel.Field(index=True, default_factory=uuid.uuid4)
    created_at: datetime.datetime = sqlmodel.Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))