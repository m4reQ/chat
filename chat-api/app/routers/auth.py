import fastapi
from dependency_injector.wiring import Provide, inject

from app.models.requests.auth import RegisterRequestModel
from app.services.auth import AuthorizationService

@inject
async def auth_post_register(data: RegisterRequestModel,
                             auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])) -> None:
    try:
        user_id = auth_service.register_user(data.usernamem data.email, data.password, data.password_repeat, data.country_code)
    except Exception as exc:
        return fastapi.Response(str(exc), status_code=fastapi.status.HTTP_400_BAD_REQUEST)
    
    

async def auth_post_login() -> None:
    pass

async def auth_post_logout() -> None:
    pass

router = fastapi.APIRouter(
    prefix='/auth',
    routes=[
        fastapi.routing.APIRoute('/register', endpoint=auth_post_register, methods={'post'}),
        fastapi.routing.APIRoute('/login', endpoint=auth_post_login, methods={'post'}),
        fastapi.routing.APIRoute('/logout', endpoint=auth_post_logout, methods={'post'})]
)