import fastapi
import inspect

from app import routers, dependencies, middleware
from app.lifespan import app_lifespan

dependency_container = dependencies.Container()
dependency_container.config.db.username.from_env('DB_USERNAME')
dependency_container.config.db.password.from_env('DB_PASSWORD')
dependency_container.config.db.address.from_env('DB_ADDRESS')
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
dependency_container.config.fs.endpoint.from_env('FS_ENDPOINT')
dependency_container.config.fs.user.from_env('FS_USER')
dependency_container.config.fs.password.from_env('FS_PASSWORD')
dependency_container.config.fs.region.from_env('FS_REGION')
dependency_container.config.fs.profile_images_bucket.from_value('profile-images')
dependency_container.config.fs.attachments_bucket.from_value('attachments')
dependency_container.config.user.profile_picture_size.from_env('PROFILE_PICTURE_SIZE')
dependency_container.wire(
    packages=['app.routers'],
    modules=['app.lifespan', 'app.middleware'],
    warn_unresolved=True)

app = fastapi.FastAPI(lifespan=app_lifespan)
app.middleware('http')(middleware.validate_api_key_header)
app.middleware('http')(middleware.add_process_time_header)

# include all API routers
for (_, router) in inspect.getmembers(routers, lambda x: isinstance(x, fastapi.APIRouter)):
    app.include_router(router)

@app.get('/health')
async def get_health():
    '''
    Check API health. Returns `ok` if the API is running.
    '''

    return 'ok'