import logging
import ipinfo
import sqlalchemy.exc
import sqlmodel
import secrets
import re
import jwt
import bcrypt
import uuid
import fastapi
import datetime
import itsdangerous
from dependency_injector.providers import Factory

from app.models.sql import SQLAPIKey, SQLUser
from app.models.responses import OAuthInvalidRequest, OAuthInvalidClient, OAuthUnauthorizedClient

class OAuthInvalidRequestException(fastapi.HTTPException):
    def __init__(self, description: str) -> None:
        super().__init__(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=OAuthInvalidRequest(error_description=description).model_dump())

class OAuthInvalidClientException(fastapi.HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=OAuthInvalidClient().model_dump())

class OAuthUnauthorizedClientException(fastapi.HTTPException):
    def __init__(self, description: str) -> None:
        super().__init__(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=OAuthUnauthorizedClient(error_description=description).model_dump())

class AuthorizationService:
    def __init__(self,
                 ipinfo_handler: ipinfo.Handler,
                 db_session_factory: Factory[sqlmodel.Session],
                 min_password_length: int,
                 password_salt_rounds: int,
                 jwt_secret: bytes,
                 jwt_expire_time: datetime.timedelta,
                 email_verification_key: bytes,
                 email_confirm_code_max_age: int) -> None:
        self._ipinfo_handler = ipinfo_handler
        self._db_session_factory = db_session_factory
        self._min_password_length = min_password_length
        self._password_validation_regex = re.compile(fr'^(?=.{{{min_password_length},}})(?=.*\d)(?=.*[A-Z])(?=.*[^A-Za-z0-9]).*$')
        self._password_salt_rounds = password_salt_rounds
        self._jwt_secret = jwt_secret
        self._jwt_expire_time = jwt_expire_time
        self._email_confirm_code_max_age = email_confirm_code_max_age
        self._verification_code_generator = itsdangerous.URLSafeTimedSerializer(email_verification_key)

    def get_min_password_length(self) -> int:
        return self._min_password_length
    
    def get_password_validation_regex(self) -> str:
        return self._password_validation_regex.pattern
    
    def get_jwt_expire_time(self) -> datetime.timedelta:
        return self._jwt_expire_time

    def validate_api_key(self, api_key: str | uuid.UUID) -> None:
        if isinstance(api_key, str):
            try:
                api_key = uuid.UUID(api_key)
            except ValueError:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                    detail={
                        'error': 'Badly formatted API key.',
                        'api_key': str(api_key)})
            
        with self._db_session_factory() as db_session:
            query = sqlmodel.select(SQLAPIKey).where(SQLAPIKey.api_key == api_key)
            result = db_session.exec(query)
            api_key_data = result.one_or_none()
        
        if api_key_data is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail={
                    'error': 'Unknown API key provided.',
                    'api_key': str(api_key)})
        
        if not api_key_data.is_active:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail={
                    'error': 'Provided API key is inactive.',
                    'api_key': str(api_key)})

    # TODO JWT refreshing  
    # def refresh_jwt(self) -> None: ...

    def generate_email_verification_code(self, user_id: int) -> str:
        return self._verification_code_generator.dumps(user_id)
    
    def unregister_user(self, user_id: int) -> None:
        with self._db_session_factory() as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()
            if user is None:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_404_NOT_FOUND,
                    detail={
                        'error': 'User with given ID not found.',
                        'user_id': user_id})

            session.exec(sqlmodel.delete(SQLUser).where(SQLUser.id == user_id))
            session.commit()

    def decode_jwt(self, token: str) -> int:
        try:
            return int(
                jwt.decode(
                    token,
                    self._jwt_secret,
                    ('HS256',))['sub']) # TODO Get JWT algo from env
        except jwt.ExpiredSignatureError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                headers={'WWW-Authenticate': 'Bearer'},
                detail={
                    'error': 'User JWT expired.',
                    'token': token})
        except jwt.DecodeError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                headers={'WWW-Authenticate': 'Bearer'},
                detail={
                    'error': 'User JWT is invalid.',
                    'token': token})

    def login_user(self,
                   username: str,
                   password: str,
                   utc_now: datetime.datetime) -> str:
        # TODO Add rate limitter to prevent brute force attacks

        try:
            password_encoded = password.encode('utf-8')
        except UnicodeEncodeError:
            raise OAuthInvalidRequestException('User password must be a valid UTF-8 string.')
        
        with self._db_session_factory() as session:
            stmt = sqlmodel.select(SQLUser).where(SQLUser.username == username)
            user = session.exec(stmt).one_or_none()
        
        if user is None or not bcrypt.checkpw(password_encoded, user.password_hash):
            raise OAuthInvalidClientException()
        
        # for security reasons we only tell user that it's email is verified after
        # it provided correct username and password combination.
        # This results in slower check but better security.
        if not user.is_email_verified:
            raise OAuthUnauthorizedClientException('User email has to be verified before login.')
        
        try:
            return jwt.encode(
                payload={
                    'iss': 'chat',
                    'sub': str(user.id),
                    'iat': utc_now,
                    'exp': utc_now + self._jwt_expire_time},
                key=self._jwt_secret,
                algorithm='HS256') # TODO Get JWT algo from env
        except jwt.InvalidTokenError:
            raise OAuthInvalidRequestException('Failed to encode JWT for the provided user.')

    # TODO Implement user logout
    def logout_user(self) -> None: ...

    def change_user_password(self,
                            user_id: int,
                            current_password: str,
                            new_password: str) -> None:
        current_password_encoded = self._check_string_utf8_encodable(
            current_password,
            fastapi.HTTPException(
                status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    'error': 'Current password must be a valid UTF-8 string.',
                    'current_password': current_password}))
        new_password_encoded = self._check_string_utf8_encodable(
            new_password,
            fastapi.HTTPException(
                status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    'error': 'New password must be a valid UTF-8 string.',
                    'new_password': new_password}))

        self._validate_password(new_password)
        
        with self._db_session_factory() as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()
        
            if user is None:
                # safe to raise 404 here as this already requires valid JWT before enter
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_404_NOT_FOUND,
                    detail={
                        'error': 'User with given ID was not found.',
                        'id': user_id})
            
            # double check password here to protect from scenario when
            # user has valid JWT stolen and someone tries to change the password
            if not bcrypt.checkpw(current_password_encoded, user.password_hash):
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                    detail={
                        'error': 'Invalid password',
                        'password': current_password})
            
            user.password_hash = bcrypt.hashpw(
                new_password_encoded,
                bcrypt.gensalt(self._password_salt_rounds))
            session.commit()

            # TODO Invalidate JWT (with external function called from endpoint)

    def confirm_user_email(self, confirmation_code: str) -> None:
        try:
            user_id: int = self._verification_code_generator.loads(
                confirmation_code,
                max_age=self._email_confirm_code_max_age)
        except itsdangerous.SignatureExpired:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail={
                    'error': 'Email verification code has expired.',
                    'error_code': 'code_expired',
                    'code': confirmation_code})
        except itsdangerous.BadSignature:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail={
                    'error': 'Email verification code is invalid.',
                    'error_code': 'code_invalid',
                    'code': confirmation_code})
        
        with self._db_session_factory() as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()

            if user is None:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_404_NOT_FOUND,
                    detail={
                        'error': 'User with given ID was not found.',
                        'id': user_id})
            
            if user.is_email_verified:
                return False
            
            user.is_email_verified = True
            session.commit()

        return True

    def send_verification_email(self, user_id: int) -> bool:
        with self._db_session_factory() as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.id == user_id)
            user = session.exec(query).one_or_none()
        
        if user is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail={
                    'error': 'User with given ID was not found.',
                    'error_code': 'user_not_found',
                    'id': user_id})
        
        if user.is_email_verified:
            return False
        
        self._send_verification_email(user.id, user.email)

        return True

    def reset_user_password(self, username: str) -> None:
        with self._db_session_factory(expire_on_commit=False) as session:
            query = sqlmodel.select(SQLUser).where(SQLUser.username == username)
            user = session.exec(query).one_or_none()

            if user is None:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_404_NOT_FOUND,
                    detail={
                        'error': 'User with given username does not exist.',
                        'username': username})
            
            if not user.is_email_verified:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_403_FORBIDDEN,
                    detail={
                        'error': 'Password reset requires user to have their email verified first.',
                        'username': username,
                        'email': user.email})

            new_password = secrets.token_hex(8)

            # No need to check password encoding here as it is generated by us
            user.password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt(self._password_salt_rounds))
            session.commit()

        self._send_password_reset_email(new_password, user.email)
    
    def register_user(self,
                      username: str,
                      email: str,
                      password: str,
                      ip_address: str) -> int:
        password_encoded = self._check_string_utf8_encodable(
            password,
            fastapi.HTTPException(
                status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    'error': 'Password must be a valid UTF-8 string.',
                    'error_code': 'password_encoding_invalid',
                    'password': password}))

        self._validate_password(password)
        
        country_code = self._get_country_code_from_ip(ip_address)
        password_hash = bcrypt.hashpw(
            password_encoded,
            bcrypt.gensalt(rounds=self._password_salt_rounds))
        
        with self._db_session_factory(expire_on_commit=False) as session:
            user = SQLUser(
                username=username,
                email=email,
                password_hash=password_hash,
                country_code=country_code)
            session.add(user)

            try:
                session.flush()
            except sqlalchemy.exc.IntegrityError:
                session.rollback()

                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_409_CONFLICT,
                    detail={
                        'error': 'User with this name or email already exists.',
                        'error_code': 'user_already_exists',
                        'username': username,
                        'email': email})
            
            session.refresh(user, attribute_names=('id',))
            session.commit()
        
        return user.id
    
    def _get_country_code_from_ip(self, ip_address: str) -> str:
        try:
            # TODO More intelligent handling of bogon address for production
            ip_info = self._ipinfo_handler.getDetails(ip_address).all
            return 'PL' if ip_info['bogon'] else ip_info['country']
        except Exception:
            _logger.exception('Failed to retreive IP info')
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    'error': 'Failed to retrieve IP info',
                    'error_code': 'ipinfo_retrieve_fail',
                    'ip_address': ip_address})
    
    def _check_string_utf8_encodable(self, value: str, exc: Exception) -> bytes:
        try:
            return value.encode('utf-8')
        except UnicodeEncodeError:
            raise exc
    
    def _validate_password(self, password: str) -> None:
        if not self._password_validation_regex.search(password):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': f'Password must be at least {self._min_password_length} characters_long and contain at least: one capital letter, one digit, one special character.',
                    'error_code': 'password_format_invalid',
                    'validation_regex': self.get_password_validation_regex(),
                    'password': password})

_logger = logging.getLogger(__name__)