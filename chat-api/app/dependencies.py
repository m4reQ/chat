import sqlmodel
import datetime
import smtplib
import minio
from dependency_injector import containers, providers

from app.services import AuthorizationService, DatetimeService, UserService

def _create_smtp_client(host: str, port: int, user: str, password: str) -> smtplib.SMTP:
    smtp = smtplib.SMTP(host, port)
    smtp.starttls()
    smtp.login(user, password)

    return smtp

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=['app.routers'])

    config = providers.Configuration()
    db_engine = providers.Singleton(
        lambda username, password, address: sqlmodel.create_engine(f'mysql+mysqldb://{username}:{password}@{address}/chat'),
        config.db.username,
        config.db.password,
        config.db.address)
    db_session_factory = providers.Factory(
        sqlmodel.Session,
        db_engine)
    smtp_client_factory = providers.Factory(
        _create_smtp_client,
        config.smtp.host,
        config.smtp.port.as_int(),
        config.smtp.user,
        config.smtp.password)
    fs_client = providers.Singleton(
        minio.Minio,
        endpoint=config.fs.endpoint,
        access_key=config.fs.user,
        secret_key=config.fs.password,
        region=config.fs.region,
        secure=False)
    auth_service = providers.Factory(
        AuthorizationService,
        db_session_factory.provider,
        config.security.min_password_length.as_int(),
        config.security.password_salt_rounds.as_int(),
        config.security.jwt_secret,
        config.security.jwt_expire_time.as_(lambda x: datetime.timedelta(seconds=int(x))),
        config.security.email_verification_key,
        config.security.email_verification_salt,
        config.security.email_verification_token_salt_rounds.as_int(),
        config.security.email_confirm_code_max_age.as_int(),
        config.smtp.user,
        smtp_client_factory.provider)
    datetime_service = providers.Singleton(DatetimeService)
    user_service = providers.Factory(
        UserService,
        db_session_factory.provider,
        fs_client,
        config.user.profile_picture_size.as_int())