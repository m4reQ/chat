from fastapi import Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordBearer
from dependency_injector.wiring import Provide, inject

from app.services.user_service import UserService
from app.services.auth_service import AuthorizationService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
router = APIRouter(
    prefix='/search',
    tags=['search'])

@inject
def get_user_id_from_jwt(user_jwt: str = Depends(oauth2_scheme),
                         auth_service: AuthorizationService = Depends(Provide['auth_service'])):
    return auth_service.decode_jwt(user_jwt)

@router.get('/user/{search_str}')
@inject
async def get_search_users(search_str: str,
                           limit: int = 20,
                           offset: int = 0,
                           user_id: int = Depends(get_user_id_from_jwt),
                           user_service: UserService = Depends(Provide['user_service'])):
    return await user_service.search_users_by_username(user_id, search_str, limit, offset)