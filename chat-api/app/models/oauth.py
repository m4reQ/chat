import pydantic

class OAuthToken(pydantic.BaseModel):
    access_token: str
    expires_in: int
    token_type: str = 'Bearer'