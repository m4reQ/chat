import pydantic
import datetime

class APIUser(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    id: int
    username: str
    email: str
    country_code: str
    is_email_verified: bool
    created_at: datetime.datetime

class OAuthToken(pydantic.BaseModel):
    access_token: str
    expires_in: int
    token_type: str = 'Bearer'

class OAuthInvalidClient(pydantic.BaseModel):
    error: str = 'invalid_client'
    error_description: str = 'Invalid username or password provided.'

class OAuthInvalidRequest(pydantic.BaseModel):
    error_description: str
    error: str = 'invalid_request'

class OAuthUnauthorizedClient(pydantic.BaseModel):
    error_description: str
    error: str = 'unauthorized_client'