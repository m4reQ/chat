import fastapi
import fastapi.security
from dependency_injector.wiring import inject, Provide

from app.services import ChatRoomService, AuthorizationService
from app.models.responses import APIChatRoom, APIChatRoomUser

oauth2_scheme = fastapi.security.oauth2.OAuth2PasswordBearer(tokenUrl='auth/login')

router = fastapi.APIRouter(
    prefix='/room',
    tags=['room'])

@router.get('/{room_id}')
@inject
async def get_room(room_id: int,
                   user_jwt: str = fastapi.Depends(oauth2_scheme),
                   auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                   chat_room_service: ChatRoomService = fastapi.Depends(Provide['chat_room_service'])) -> APIChatRoom:
    auth_service.decode_jwt(user_jwt)
    return APIChatRoom.model_validate(chat_room_service.get_room_info(room_id))

@router.get('/{room_id}/users')
@inject
async def get_room_users(room_id: int,
                         user_jwt: str = fastapi.Depends(oauth2_scheme),
                         auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                         chat_room_service: ChatRoomService = fastapi.Depends(Provide['chat_room_service'])) -> list[APIChatRoomUser]:
    auth_service.decode_jwt(user_jwt)
    return [
        APIChatRoomUser.model_validate(x)
        for x in chat_room_service.get_room_users(room_id)]