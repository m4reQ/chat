import sqlmodel
import fastapi
import minio
from dependency_injector.providers import Factory

from app.models.sql import SQLUser

class UserService:
    def __init__(self,
                 db_session_factory: Factory[sqlmodel.Session],
                 fs_client: minio.Minio) -> None:
        self._db_session_factory = db_session_factory
        self._fs_client = fs_client

    # TODO Do not return plain SQL model
    def get_user(self, user_id: int) -> SQLUser:
        with self._db_session_factory() as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()
        
        if user is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail={
                    'error': 'User with given ID does not exist.',
                    'id': user_id})

        return user