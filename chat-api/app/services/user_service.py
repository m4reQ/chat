import sqlmodel
import fastapi
from sqlalchemy.engine import Engine

from app.models.sql import SQLUser

class UserService:
    def __init__(self, db_engine: Engine) -> None:
        self._db_engine = db_engine

    # TODO Do not return plain SQL model
    def get_user(self, user_id: int) -> SQLUser:
        with sqlmodel.Session(self._db_engine) as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()
        
        if user is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail={
                    'error': 'User with given ID does not exist.',
                    'id': user_id})

        return user