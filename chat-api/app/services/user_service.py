import sqlmodel
import fastapi
import minio
import io
import typing as t
from dependency_injector.providers import Factory
from PIL import Image

from app.models.sql import SQLUser
from app.media_type import MediaType

_SUPPORTED_MEDIA_TYPES = [
    MediaType.IMAGE_JPEG,
    MediaType.IMAGE_PNG,
    MediaType.IMAGE_WEBP,
    MediaType.IMAGE_GIF,
    MediaType.IMAGE_BMP,
    MediaType.IMAGE_TIFF,
    MediaType.IMAGE_ICON]

# _MIME_TYPE_TO_PIL_FORMAT = {
#     MediaType.IMAGE_JPEG: 'JPEG',
#     MediaType.IMAGE_PNG: 'PNG',
#     MediaType.IMAGE_WEBP: 'WEBP',
#     MediaType.IMAGE_GIF: 'GIF',
#     MediaType.IMAGE_BMP: 'BMP',
#     MediaType.IMAGE_TIFF: 'TIFF',
#     MediaType.IMAGE_ICON: 'ICO'}

class UserService:
    def __init__(self,
                 db_session_factory: Factory[sqlmodel.Session],
                 fs_client: minio.Minio,
                 profile_picture_size: int) -> None:
        self._db_session_factory = db_session_factory
        self._fs_client = fs_client
        self._profile_picture_size = profile_picture_size

    # TODO Do not return plain SQL model
    def get_user(self, user_id: int) -> SQLUser:
        return self._get_user_by_id(user_id)
    
    def get_user_profile_picture(self, user_id: int) -> bytes | None:
        user = self._get_user_by_id(user_id)

        try:
            result = self._fs_client.get_object('profile-images', user.username)
            return result.data
        except minio.S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    'error': 'Failed to retrieve user profile picture.',
                    'user_id': user_id})

    def change_user_profile_picture(self, user_id: int, image_file: fastapi.UploadFile) -> None:
        self._check_image_file_valid_media_type(image_file.content_type)
        
        with self._db_session_factory() as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()

            if user is None:
                self._raise_user_not_found(user_id)

            # TODO Move old picture deletion and new picture upload to a separate task
            self._fs_client.remove_object('profile-images', user.username)

            with Image.open(image_file.file) as img:
                img = img.resize(
                    size=(self._profile_picture_size, self._profile_picture_size),
                    resample=Image.Resampling.LANCZOS)
                
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG') # TODO Unhardcode save format
                img_buffer.seek(0)

            # TODO try ... except around put_object ?
            self._fs_client.put_object(
                bucket_name='profile-images',
                object_name=user.username,
                data=img_buffer,
                length=img_buffer.getbuffer().nbytes,
                content_type=MediaType.IMAGE_JPEG)
            
            session.commit()
    
    def get_profile_picture_capabilities(self) -> dict[str, t.Any]:
        return {
            'max_size': self._profile_picture_size,
            'supported_media_types': _SUPPORTED_MEDIA_TYPES}

    def _check_image_file_valid_media_type(self, media_type: str) -> None:
        if media_type not in _SUPPORTED_MEDIA_TYPES:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    'error': 'Invalid media type of image file.',
                    'media-type': media_type})
        
    def _get_user_by_id(self, user_id: int, expire_on_commit: bool = True) -> SQLUser:
        with self._db_session_factory(expire_on_commit=expire_on_commit) as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()

        if user is None:
            self._raise_user_not_found(user_id)

        return user

    def _raise_user_not_found(self, user_id: int) -> t.NoReturn:
        raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail={
                    'error': 'User with given ID does not exist.',
                    'id': user_id})