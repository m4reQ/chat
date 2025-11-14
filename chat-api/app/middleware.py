import fastapi
import time
from dependency_injector.wiring import Provide, inject

from app.services.auth_service import AuthorizationService

_OPEN_ENDPOINTS = ('/health', '/docs', '/redoc', '/openapi.json')

@inject
async def validate_api_key_header(request: fastapi.Request,
                                  call_next,
                                  auth_service: AuthorizationService = Provide['auth_service']):
    if request.url.path in _OPEN_ENDPOINTS:
        return await call_next(request)
    
    api_key = request.headers.get('x-api-key')
    if api_key is None:
        return fastapi.responses.JSONResponse(
            content={
                'error': 'API key is required to access this endpoint',
                'header': 'X-Api-Key'},
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
    
    try:
        auth_service.validate_api_key(api_key)
    except fastapi.HTTPException as e:
        return fastapi.responses.JSONResponse(
            content=e.detail,
            status_code=e.status_code)

    return await call_next(request)

async def add_process_time_header(request: fastapi.Request,
                                  call_next,):
    start_time = time.perf_counter()
    response = await call_next(request)
    response.headers['X-Process-Time'] = str(time.perf_counter() - start_time)
    return response