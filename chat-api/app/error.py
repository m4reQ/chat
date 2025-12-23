import pydantic
import typing
import fastapi

class _ErrorBase(pydantic.BaseModel):
    def raise_(self,
               status: int = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
               headers: dict[str, str] | None = None) -> typing.NoReturn:
        raise fastapi.HTTPException(
            status,
            detail=self.model_dump(),
            headers=headers)

class Error(_ErrorBase):
    error_code: str
    error_message: str

class OAuthError(_ErrorBase):
    error: str
    error_description: str

def raise_error(code: str,
                message: str,
                status: int = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) -> typing.NoReturn:
    raise_error_obj(Error(error_code=code, error_message=message), status)

def raise_error_obj(error: Error,
                    status: int = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) -> typing.NoReturn:
    raise fastapi.HTTPException(status, detail=error.model_dump_json())