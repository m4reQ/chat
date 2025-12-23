import uuid
from sqlalchemy import orm
from sqlalchemy import types
from sqlalchemy.ext.asyncio import AsyncAttrs

class MySQLUUID(types.TypeDecorator):
    impl = types.BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, _):
        if value is None:
            return None
        
        if isinstance(value, uuid.UUID):
            return value.bytes
        
        return uuid.UUID(value).bytes
    
    def process_result_value(self, value, _):
        if value is None:
            return None

        return uuid.UUID(bytes=value)

class Base(AsyncAttrs, orm.DeclarativeBase):
    pass