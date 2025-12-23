import typing as t
import ipinfo
import sqlalchemy
import secrets
import re
import jwt
import bcrypt
import uuid
import fastapi
import datetime
import itsdangerous
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from app import error
from app.models.errors import ErrorAPIKeyInactive, ErrorAPIKeyInvalid, ErrorAPIKeyMalformed, ErrorEmailCodeExpired, ErrorEmailCodeInvalid, ErrorEmailNotConfirmed, ErrorInvalidPassword, ErrorInvalidPasswordEncoding, ErrorInvalidPasswordFormat, ErrorOAuthInvalidClient, ErrorOAuthInvalidRequest, ErrorOAuthUnauthorizedClient, ErrorUserAlreadyExists, ErrorUserJWTExpired, ErrorUserJWTInvalid, ErrorUserNotFoundID, ErrorUserNotFoundUsername
from app.models.api_key import SQLAPIKey
from app.models.user import SQLUser

class AuthorizationService:
    def __init__(self,
                 ipinfo_handler: ipinfo.Handler,
                 db_sessionmaker: async_sessionmaker[AsyncSession],
                 min_password_length: int,
                 password_salt_rounds: int,
                 jwt_secret: bytes,
                 jwt_expire_time: datetime.timedelta,
                 email_verification_key: bytes,
                 email_confirm_code_max_age: int) -> None:
        self._ipinfo_handler = ipinfo_handler
        self._db_sessionmaker = db_sessionmaker
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

    async def validate_api_key(self, api_key: str | uuid.UUID) -> None:
        if isinstance(api_key, str):
            try:
                api_key = uuid.UUID(api_key)
            except ValueError:
                error.raise_error_obj(
                    ErrorAPIKeyMalformed(api_key=api_key),
                    fastapi.status.HTTP_400_BAD_REQUEST)
            
        async with self._db_sessionmaker() as db_session:
            query = sqlalchemy.select(SQLAPIKey.is_active).where(SQLAPIKey.key == api_key)
            result = await db_session.execute(query)
            is_active = result.scalar_one_or_none()

        if is_active is None:
            ErrorAPIKeyInvalid(api_key=api_key) \
                .raise_(fastapi.status.HTTP_404_NOT_FOUND)
        
        if not is_active:
            ErrorAPIKeyInactive(api_key=api_key) \
                .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
            
    # TODO JWT refreshing  
    # def refresh_jwt(self) -> None: ...

    def generate_email_verification_code(self, user_id: int) -> str:
        return self._verification_code_generator.dumps(user_id)
    
    async def unregister_user(self, user_id: int) -> None:
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(SQLUser).where(SQLUser.id == user_id)
            user = (await session.execute(query)).scalar_one_or_none()
            if user is None:
                self._raise_user_not_found(user_id)

            await session.delete(user)
            await session.commit()

    def decode_jwt(self, token: str) -> int:
        try:
            return int(
                jwt.decode(
                    token,
                    self._jwt_secret,
                    ('HS256',))['sub']) # TODO Get JWT algo from env
        except jwt.ExpiredSignatureError:
            ErrorUserJWTExpired(token=token) \
                .raise_(fastapi.status.HTTP_401_UNAUTHORIZED, {'WWW-Authenticate': 'Bearer'})
        except jwt.DecodeError:
            ErrorUserJWTInvalid(token=token) \
                .raise_(fastapi.status.HTTP_401_UNAUTHORIZED, {'WWW-Authenticate': 'Bearer'})
        
    async def login_user(self,
                         username: str,
                         password: str,
                         utc_now: datetime.datetime) -> tuple[int, str]:
        # TODO Add rate limitter to prevent brute force attacks

        try:
            password_encoded = password.encode('utf-8')
        except UnicodeEncodeError:
            ErrorOAuthInvalidRequest(error_description='User password must be a valid UTF-8 string.') \
                .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
        
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(SQLUser.id, SQLUser.password_hash, SQLUser.is_email_verified) \
                .where(SQLUser.username == username)
            result = (await session.execute(query)).one_or_none()

        if result is None:
            ErrorOAuthInvalidClient() \
                .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
        
        if not bcrypt.checkpw(password_encoded, result.password_hash):
            ErrorOAuthInvalidClient() \
                .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
            
        # for security reasons we only tell user that it's email is verified after
        # it provided correct username and password combination.
        # This results in slower check but doesn't leak email if password is invalid.
        if not result.is_email_verified:
            ErrorOAuthUnauthorizedClient(error_description='User email has to be verified before login.') \
                .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
        
        try:
            token = jwt.encode(
                payload={
                    'iss': 'chat',
                    'sub': str(result.id),
                    'iat': utc_now,
                    'exp': utc_now + self._jwt_expire_time},
                key=self._jwt_secret,
                algorithm='HS256')
        except jwt.InvalidTokenError:
            ErrorOAuthInvalidRequest(error_description='Failed to encode JWT for the provided user.') \
                .raise_(fastapi.status.HTTP_400_BAD_REQUEST)
        
        return (result.id, token)

    # TODO Implement user logout
    def logout_user(self) -> None: ...

    async def change_user_password(self, user_id: int, current_password: str, new_password: str) -> None:
        try:
            current_password_encoded = current_password.encode('utf-8')
        except UnicodeEncodeError:
            ErrorInvalidPasswordEncoding(password=current_password) \
                .raise_(fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            
        try:
            new_password_encoded = new_password.encode('utf-8')
        except UnicodeEncodeError:
            ErrorInvalidPasswordEncoding(password=new_password) \
                .raise_(fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            
        self._validate_password(new_password)
        
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(SQLUser).where(SQLUser.id == user_id)
            user = (await session.execute(query)).scalar_one_or_none()
        
            if user is None:
                # safe to raise 404 here as this already requires valid JWT before enter
                self._raise_user_not_found(user_id)
            
            # double check password here to protect from scenario when
            # user has valid JWT stolen and someone tries to change the password
            if not bcrypt.checkpw(current_password_encoded, user.password_hash):
                ErrorInvalidPassword(password=current_password) \
                    .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
            
            user.password_hash = self._hash_password(new_password_encoded)

            await session.commit()

            # TODO Invalidate JWT (with external function called from endpoint)

    async def confirm_user_email(self, confirmation_code: str) -> None:
        try:
            user_id: int = self._verification_code_generator.loads(
                confirmation_code,
                max_age=self._email_confirm_code_max_age)
        except itsdangerous.SignatureExpired:
            ErrorEmailCodeExpired(code=confirmation_code) \
                .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)
        except itsdangerous.BadSignature:
            ErrorEmailCodeInvalid(code=confirmation_code) \
                .raise_(fastapi.status.HTTP_401_UNAUTHORIZED)

        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(SQLUser).where(SQLUser.id == user_id)
            user = (await session.execute(query)).scalar_one_or_none()

            if user is None:
                self._raise_user_not_found(user_id)
            
            if user.is_email_verified:
                return False
            
            user.is_email_verified = True

            await session.commit()

        return True

    async def reset_user_password(self, username: str) -> tuple[str, bytes]:
        # NOTE This enables some bad actor to reset password of any user

        # TODO 2-step password reset (first request reset and send email with request code, then pass request code to another endpoint which resets password)
        async with self._db_sessionmaker() as session:
            query = sqlalchemy.select(SQLUser).where(SQLUser.username == username)
            user = (await session.execute(query)).scalar_one_or_none()

            if user is None:
                ErrorUserNotFoundUsername(username=username) \
                    .raise_(fastapi.status.HTTP_404_NOT_FOUND)
            
            if not user.is_email_verified:
                ErrorEmailNotConfirmed() \
                    .raise_(fastapi.status.HTTP_403_FORBIDDEN)

            new_password = secrets.token_hex(8)

            # No need to check password encoding here as it is generated by us
            user.password_hash = self._hash_password(new_password)

            await session.commit()

            return (user.email, new_password)
    
    async def register_user(self, username: str, email: str, password: str, country_code: str) -> int:
        try:
            password_encoded = password.encode('utf-8')
        except UnicodeEncodeError:
            ErrorInvalidPasswordEncoding(password=password) \
                .raise_(fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        self._validate_password(password)
        password_hash = self._hash_password(password_encoded)
        
        async with self._db_sessionmaker() as session:
            user = SQLUser(
                username=username,
                email=email,
                password_hash=password_hash)
            session.add(user)
            
            try:
                await session.flush()
            except IntegrityError:
                await session.rollback()
                
                ErrorUserAlreadyExists(username=username, email=email) \
                    .raise_(fastapi.status.HTTP_409_CONFLICT)

            await session.commit()
            await session.refresh(user)

            return user.id
    
    def _hash_password(self, password: bytes):
        # TODO Possibly move password hashing to coroutine
        return bcrypt.hashpw(
            password,
            bcrypt.gensalt(rounds=self._password_salt_rounds))
    
    def _raise_user_not_found(self, user_id: int) -> t.NoReturn:
        error.raise_error_obj(
            ErrorUserNotFoundID(user_id=user_id),
            fastapi.status.HTTP_404_NOT_FOUND)
    
    def _validate_password(self, password: str) -> None:
        if not self._password_validation_regex.search(password):
            ErrorInvalidPasswordFormat(
                password=password,
                validation_regex=self.get_password_validation_regex()) \
                .raise_(fastapi.status.HTTP_400_BAD_REQUEST)