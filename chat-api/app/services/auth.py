import sqlmodel
import bcrypt
import email_validator
import string
import pycountry

from app.models.sql import SQLUser
from sqlalchemy.engine import Engine

class AuthorizationService:
    def __init__(self,
                 db_engine: Engine,
                 min_password_length: int,
                 password_salt_rounds: int) -> None:
        # postgresql://postgres:Bright#1270@localhost/fastapi
        self._db_engine = db_engine
        self._min_password_length = min_password_length
        self._password_salt_rounds = password_salt_rounds
    
    def register_user(self,
                      username: str,
                      email: str,
                      password: str,
                      password_repeat: str,
                      country_code: str) -> int:
        # validate email
        try:
            email_validator.validate_email(email, check_deliverability=True)
        except email_validator.EmailNotValidError as e:
            raise ValueError('Provided user email is not valid.')
        
        # validate password
        if password != password_repeat:
            raise ValueError('Provided passwords do not match.')
        
        if len(password) < self._min_password_length:
            raise ValueError(f'Password must be at least {self._min_password_length} characters long.')
        
        if not any(digit in password for digit in string.digits):
            raise ValueError('Password must contain at least one digit.')
        
        if not any(special in password for special in string.punctuation):
            raise ValueError('Password must contain at least one punctuation character.')
        
        # validate country code
        # TODO Accept country code as enum to simplify validation
        country_info = pycountry.countries.get(alpha_2=country_code)
        if country_info is None:
            raise ValueError('Invalid country code provided.')
        
        # normalize country code
        country_code = country_info.alpha_2

        # hash password
        try:
            password_utf8 = password.encode()
        except UnicodeEncodeError as e:
            raise ValueError('Password must ve a valid UTF-8.')
        
        password_hash = bcrypt.hashpw(
            password_utf8,
            bcrypt.gensalt(rounds=self._password_salt_rounds))

        sql_user = SQLUser(
            username=username,
            email=email,
            password=password_hash,
            country_code=country_code)
        
        with sqlmodel.Session(self._db_engine) as session:
            session.add(sql_user)
            session.commit(sql_user)
            session.refresh(sql_user)

        return sql_user.id

