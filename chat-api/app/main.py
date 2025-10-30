import fastapi
import inspect
from app import routers, dependencies

dependency_container = dependencies.Container()
dependency_container.config.db.url.from_env('DB_URL')
dependency_container.config.security.min_password_length.url.from_env('MIN_PASSWORD_LENGTH')
dependency_container.config.security.password_salt_rounds.url.from_env('PASSWORD_SALT_ROUNDS')

app = fastapi.FastAPI()

# include all API routers
for router in inspect.getmembers(routers, lambda x: isinstance(x, fastapi.APIRouter)):
    app.include_router(router)