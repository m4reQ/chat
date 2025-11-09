import fastapi
import inspect

from app import routers, dependencies

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
dependency_container.wire(packages=['app.routers'], warn_unresolved=True)

app = fastapi.FastAPI()

@app.get('/health')
async def get_health():
    '''
    Check API health. Returns `ok` if the API is running.
    '''

    return 'ok'

# include all API routers
for (_, router) in inspect.getmembers(routers, lambda x: isinstance(x, fastapi.APIRouter)):
    app.include_router(router)