import pydantic

class RegisterRequestModel(pydantic.BaseModel):
    username: str
    email: pydantic.EmailStr
    password: str
    password_repeat: str
    country_code: str