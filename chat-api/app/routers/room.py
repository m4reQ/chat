import typing
import fastapi
import fastapi.security
import pydantic
from dependency_injector.wiring import inject, Provide

from app.services.room_service import RoomService
from app.services.auth_service import AuthorizationService
from app.models.chat_room import RoomType
from app.models.errors import ErrorRoomAlreadyExists, ErrorRoomAlreadyJoined, ErrorRoomInternalJoin, ErrorRoomInvalidTypeChange, ErrorRoomNameTooLong, ErrorRoomNotFound, ErrorRoomNotOwner, ErrorRoomPrivateJoin, ErrorUserJWTExpired, ErrorUserJWTInvalid

class CreateRoomData(pydantic.BaseModel):
    name: str
    description: str | None
    type: RoomType

class UpdateRoomData(pydantic.BaseModel):
    name: str | None = None
    description: str | None = None
    type: RoomType | None = None

class CreateRoomResponse(pydantic.BaseModel):
    room_id: int

oauth2_scheme = fastapi.security.oauth2.OAuth2PasswordBearer(tokenUrl='auth/login')
router = fastapi.APIRouter(
    prefix='/room',
    tags=['room'])

@inject
def get_user_id_from_jwt(user_jwt: str = fastapi.Depends(oauth2_scheme),
                         auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])) -> int:
    return auth_service.decode_jwt(user_jwt)

@router.get(
    '/{room_id}',
    name='Get chat room')
@inject
async def get_room(room_id: int,
                   room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    return await room_service.get_room_by_id(room_id)

@router.put(
    '/{room_id}',
    name='Update room',
    responses={
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': ErrorRoomInvalidTypeChange},
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorRoomAlreadyExists},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorRoomNotFound},
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': typing.Union[ErrorRoomNotOwner, ErrorUserJWTExpired, ErrorUserJWTInvalid]}
    })
@inject
async def update_room(room_id: int,
                      data: UpdateRoomData,
                      user_id: int = fastapi.Depends(get_user_id_from_jwt),
                      room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    await room_service.update_room(room_id, user_id, data.name, data.description, data.type)

@router.post(
    '/{room_id}/join',
    name='Join chat room',
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': typing.Union[ErrorUserJWTExpired, ErrorUserJWTInvalid]},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorRoomNotFound},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': typing.Union[ErrorRoomPrivateJoin, ErrorRoomInternalJoin]},
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorRoomAlreadyJoined},
    })
@inject
async def join_chat_room(room_id: int,
                         user_id: int = fastapi.Depends(get_user_id_from_jwt),
                         room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    await room_service.join_room(room_id, user_id)

@router.post(
    '/',
    name='Create chat room',
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=CreateRoomResponse,
    responses={
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorRoomAlreadyExists},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': ErrorRoomNameTooLong},
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': typing.Union[ErrorUserJWTExpired, ErrorUserJWTInvalid]}
    })
@inject
async def create_room(data: CreateRoomData,
                      user_jwt: str = fastapi.Depends(oauth2_scheme),
                      auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                      room_service: RoomService = fastapi.Depends(Provide['room_service'])):
    user_id = auth_service.decode_jwt(user_jwt)
    room_id = await room_service.create_room(user_id, data.name, data.description, data.type)
    return CreateRoomResponse(room_id=room_id)
