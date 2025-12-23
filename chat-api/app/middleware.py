import fastapi
import time
from dependency_injector.wiring import Provide, inject

from app.services.auth_service import AuthorizationService
from app import error

_OPEN_ENDPOINTS = ('/health', '/docs', '/redoc', '/openapi.json')

class ErrorAPIKeyMissing(error.Error):
    error_code: str = 'api_key_missing'
    error_message: str = 'API key must be present in X-Api-Key header to access this endpoint.'

@inject
async def validate_api_key_header(request: fastapi.Request,
                                  call_next,
                                  auth_service: AuthorizationService = Provide['auth_service']):
    if request.url.path not in _OPEN_ENDPOINTS:
        api_key = request.headers.get('x-api-key')
        if api_key is None:
            return fastapi.Response(
                content=ErrorAPIKeyMissing().model_dump_json(),
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                media_type='application/json')
        
        try:
            await auth_service.validate_api_key(api_key)
        except fastapi.HTTPException as e:
            return fastapi.Response(
                content=e.detail,
                headers=e.headers,
                status_code=e.status_code,
                media_type='application/json')
    
    return await call_next(request)

async def add_process_time_header(request: fastapi.Request,
                                  call_next,):
    start_time = time.perf_counter()
    response = await call_next(request)
    response.headers['X-Process-Time'] = str(time.perf_counter() - start_time)
    return response