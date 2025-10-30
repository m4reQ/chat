import sqlmodel

class SQLUser(sqlmodel.SQLModel, table=True):
    id: int | None = sqlmodel.Field(primary_key=True, default=None)
    username: str = sqlmodel.Field(index=True, max_length=256)
    email: str = sqlmodel.Field(index=True, max_length=254)
    password: bytes = sqlmodel.Field(max_length=60)
    country_code: str = sqlmodel.Field(max_length=2)
    email_verified: bool = sqlmodel.Field(default=False)