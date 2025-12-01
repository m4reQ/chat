import fastapi
import fastapi.security
from dependency_injector.wiring import Provide, inject

from app.services import UserService, AuthorizationService
from app.models.responses import APIUser
from app.media_type import MediaType

oauth2_scheme = fastapi.security.oauth2.OAuth2PasswordBearer(tokenUrl='auth/login')

router = fastapi.APIRouter(
    prefix='/user',
    tags=['user'])

@router.get('/')
@inject
async def get_user(user_jwt: str = fastapi.Depends(oauth2_scheme),
                   auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                   user_service: UserService = fastapi.Depends(Provide['user_service'])) -> APIUser:
    return APIUser.model_validate(
        user_service.get_user(
            auth_service.decode_jwt(user_jwt)))

@router.get('/profile-picture')
@inject
async def get_user_profile_picture(user_jwt: str = fastapi.Depends(oauth2_scheme),
                                   auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                                   user_service: UserService = fastapi.Depends(Provide['user_service'])):
    user_id = auth_service.decode_jwt(user_jwt)
    profile_picture_data = user_service.get_user_profile_picture(user_id)
    if profile_picture_data is None:
        return fastapi.Response(
            content=None,
            status_code=fastapi.status.HTTP_204_NO_CONTENT,
            media_type=MediaType.IMAGE_WEBP)
    
    return fastapi.Response(
        content=profile_picture_data,
        media_type=MediaType.IMAGE_JPEG)

@router.post('/change-profile-picture')
@inject
async def change_user_profile_picture(image_file: fastapi.UploadFile,
                                      user_jwt: str = fastapi.Depends(oauth2_scheme),
                                      auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                                      user_service: UserService = fastapi.Depends(Provide['user_service'])):
    user_service.change_user_profile_picture(
        auth_service.decode_jwt(user_jwt),
        image_file)
    return {'message': 'Successfully changed user profile picture'}

@router.get('/profile-picture-caps')
@inject
async def get_profile_picture_caps(user_service: UserService = fastapi.Depends(Provide['user_service'])):
    return user_service.get_profile_picture_capabilities()