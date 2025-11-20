import smtplib
import sqlalchemy.exc
import sqlmodel
import secrets
import re
import jwt
import bcrypt
import uuid
import email_validator
import pycountry
import fastapi
import datetime
import itsdangerous
from email.mime.text import MIMEText
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
                 db_session_factory: Factory[sqlmodel.Session],
                 min_password_length: int,
                 password_salt_rounds: int,
                 jwt_secret: bytes,
                 jwt_expire_time: datetime.timedelta,
                 email_verification_key: bytes,
                 email_verification_salt: bytes,
                 email_verification_token_salt_rounds: int,
                 email_confirm_code_max_age: int,
                 smtp_user: str,
                 smtp_client_factory: Factory[smtplib.SMTP]) -> None:
        self._db_session_factory = db_session_factory
        self._min_password_length = min_password_length
        self._password_salt_rounds = password_salt_rounds
        self._jwt_secret = jwt_secret
        self._jwt_expire_time = jwt_expire_time
        self._email_verification_key = email_verification_key
        self._email_confirm_code_max_age = email_confirm_code_max_age
        self._url_token_generator = itsdangerous.URLSafeTimedSerializer(
            email_verification_key,
            email_verification_salt)
        self._smtp_client_factory = smtp_client_factory
        self._smtp_user = smtp_user
        self._email_verification_token_salt_rounds = email_verification_token_salt_rounds
    
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
        self._validate_password(new_password)
        
        try:
            current_password_encoded = current_password.encode('utf-8')
            new_password_encoded = new_password.encode('utf-8')
        except UnicodeEncodeError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    'error': 'Current password and new password must be valid UTF-8 strings.',
                    'current_password': current_password,
                    'new_password': new_password})
        
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
            user_id: int = self._url_token_generator.loads(
                confirmation_code,
                max_age=self._email_confirm_code_max_age)
        except itsdangerous.SignatureExpired:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail={
                    'error': 'Email verification code has expired.',
                    'code': confirmation_code})
        except itsdangerous.BadSignature:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail={
                    'error': 'Email verification code is invalid.',
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
                      country_code: str) -> int:
        self._validate_password(password)
        password_encoded = self._encode_password(password)

        self._validate_country_code(country_code)

        self._validate_email(email)

        user = SQLUser(
                username=username,
                email=email,
                password_hash=bcrypt.hashpw(
                    password_encoded,
                    bcrypt.gensalt(rounds=self._password_salt_rounds)),
                country_code=country_code)
        
        with self._db_session_factory() as session:
            session.add(user)

            try:
                session.commit()
            except sqlalchemy.exc.IntegrityError:
                session.rollback()

                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_409_CONFLICT,
                    detail={
                        'error': 'User with this name or email already exists.',
                        'username': username,
                        'email': email})
            
            session.refresh(user)

        # generate and send verification code
        self._send_verification_email(user.id, user.email)
        
        return user.id
    
    def _validate_password(self, password: str) -> None:
        self._check_password_valid_length(password)
        self._check_password_contains_digits(password)
        self._check_password_contains_special_chars(password)
    
    def _send_password_reset_email(self, new_password: str, email: str) -> None:
        self._send_email_to(
            email,
            'Password reset',
            f'Your password has been reset.\n Please log in with new password: {new_password}.\nIt is recommended to change the password immediately after login.')
    
    def _send_verification_email(self, user_id: int, email: str) -> None:
        verification_code = self._url_token_generator.dumps(user_id)
        
        # TODO Get url from request or fastapi base URL instead of using hardcoded value
        verification_url = f'http://localhost:8000/auth/verify-email?code={verification_code}'
        
        # TODO Create email from static template
        self._send_email_to(
            email,
            'Account verification',
            f'Your user account has been successfully created.\nTo activate it, please visit {verification_url}.')
            
    def _send_email_to(self, email: str, subject: str, text: str) -> None:
        content = MIMEText(text)
        content['Subject'] = subject
        content['From'] = self._smtp_user
        content['To'] = email

        with self._smtp_client_factory() as smtp_client:
            smtp_client.sendmail(
                self._smtp_user,
                (email,),
                content.as_bytes())

    def _validate_country_code(self, country_code: str) -> None:
        country_info = pycountry.countries.get(alpha_2=country_code)
        if country_info is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': 'Country code must be a valid ISO 3166 country code.',
                    'field': 'country_code'})
    
    def _validate_email(self, email: str) -> None:
        try:
            email_validator.validate_email(email)
        except email_validator.EmailSyntaxError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': 'Provided email address is not valid.',
                    'field': 'email'})
        except email_validator.EmailUndeliverableError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': 'Provided email address does not exist.',
                    'field': 'email'})

    def _check_password_valid_length(self, password: str) -> None:
        if len(password) < self._min_password_length:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': f'Password must be at least {self._min_password_length} characters long.',
                    'password': password})
    
    def _check_password_contains_digits(self, password: str) -> None:
        if not re.search(r'\d', password):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': 'Password must contain at least one digit.',
                    'password': password})

    def _check_password_contains_special_chars(self, password: str) -> None:
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>_\-+=~`]', password):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail={
                    'error': 'Password must contain at least one special character.',
                    'password': password})
    
    def _encode_password(self, password: str) -> bytes:
        try:
            return password.encode('utf-8')
        except UnicodeEncodeError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    'error': 'Password must be a valid UTF-8 string.',
                    'password': password})