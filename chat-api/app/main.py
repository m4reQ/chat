import fastapi
import fastapi.middleware.cors
import inspect

from app import routers, dependencies, middleware
from app.lifespan import lifespan

dependency_container = dependencies.Container()
dependency_container.config.db.username.from_env('DB_USERNAME')
dependency_container.config.db.password.from_env('DB_PASSWORD')
dependency_container.config.db.address.from_env('DB_ADDRESS')
dependency_container.config.ipinfo.access_token.from_env('IPINFO_ACCESS_TOKEN')
dependency_container.config.security.min_password_length.from_env('MIN_PASSWORD_LENGTH')
dependency_container.config.security.password_salt_rounds.from_env('PASSWORD_SALT_ROUNDS')
dependency_container.config.security.jwt_secret.from_env('JWT_SECRET')
dependency_container.config.security.jwt_expire_time.from_env('JWT_EXPIRE_TIME')
dependency_container.config.security.email_verification_key.from_env('EMAIL_VERIFICATION_KEY')
dependency_container.config.security.email_verification_salt.from_env('EMAIL_VERIFICATION_SALT')
dependency_container.config.security.email_confirm_code_max_age.from_env('EMAIL_CONFIRM_CODE_MAX_AGE')
dependency_container.config.security.email_verification_token_salt_rounds.from_env('EMAIL_VERIFICATION_TOKEN_SALT_ROUNDS')
dependency_container.config.smtp.host.from_env('SMTP_HOST')
dependency_container.config.smtp.port.from_env('SMTP_PORT')
dependency_container.config.smtp.user.from_env('SMTP_USER')
dependency_container.config.smtp.password.from_env('SMTP_PASSWORD')
dependency_container.config.fs.data_directory.from_env('FS_DATA_DIRECTORY')
dependency_container.config.user.profile_picture_size.from_env('PROFILE_PICTURE_SIZE')
dependency_container.wire(
    packages=['app.routers'],
    modules=['app.middleware', 'app.lifespan'],
    warn_unresolved=True)

app = fastapi.FastAPI(lifespan=lifespan)
app.middleware('http')(middleware.validate_api_key_header)
app.middleware('http')(middleware.add_process_time_header)
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_credentials=True,
    allow_origins=('*',),
    allow_methods=('*',),
    allow_headers=('*',),
    expose_headers=('x-process-time', ))

@app.exception_handler(fastapi.HTTPException)
async def http_exception_handler(_: fastapi.Request, exc: fastapi.HTTPException):
    return fastapi.responses.JSONResponse(
        content=exc.detail,
        status_code=exc.status_code,
        headers=exc.headers)

# include all API routers
for (_, router) in inspect.getmembers(routers, lambda x: isinstance(x, fastapi.APIRouter)):
    app.include_router(router)

@app.get('/health')
async def get_health():
    '''
    Check API health. Returns `ok` if the API is running.
    '''

    return 'ok'