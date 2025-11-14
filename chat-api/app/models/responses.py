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