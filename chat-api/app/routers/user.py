import fastapi
import fastapi.security
from dependency_injector.wiring import Provide, inject

from app.services import UserService, AuthorizationService

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl='auth/login')
api_key_header = fastapi.security.APIKeyHeader(name='x-api-key')

router = fastapi.APIRouter(
    prefix='/user',
    tags=['user'])

@router.get('/')
@inject
async def get_user(user_jwt: str = fastapi.Depends(oauth2_scheme),
                   api_key: str = fastapi.Security(api_key_header),
                   auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                   user_service: UserService = fastapi.Depends(Provide['user_service'])):
    auth_service.validate_api_key(api_key)
    return fastapi.responses.Response(
        status_code=fastapi.status.HTTP_200_OK,
        media_type='application/json',
        content=user_service.get_user(
            auth_service.decode_jwt(user_jwt)).model_dump_json())