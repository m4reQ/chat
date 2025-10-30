import sqlmodel
from dependency_injector import containers, providers

from app.services import AuthorizationService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=['app.routers'])

    config = providers.Configuration()
    db_engine = providers.Singleton(
        sqlmodel.create_engine,
        config.db.url)
    auth_service = providers.Factory(
        AuthorizationService,
        db_engine,
        config.security.min_password_length,
        config.security.password_salt_rounds)