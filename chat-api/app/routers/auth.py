import fastapi
import fastapi.security
import typing as t
from dependency_injector.wiring import Provide, inject
import pydantic

from app.services import DatetimeService, UserService
from app.services.email_service import EmailService
from app.services.auth_service import AuthorizationService
from app.services.location_service import LocationService
from app.models.errors import ErrorEmailNotConfirmed, ErrorInvalidPassword, ErrorIPInfoRetrieveFailed, ErrorEmailCodeExpired, ErrorEmailCodeInvalid, ErrorInvalidPasswordEncoding, ErrorInvalidPasswordFormat, ErrorOAuthInvalidClient, ErrorOAuthInvalidRequest, ErrorOAuthUnauthorizedClient, ErrorUserAlreadyExists, ErrorUserNotFoundID, ErrorEmailNotDelivered, ErrorEmailInvalid, ErrorEmailNotFound, ErrorUserNotFoundUsername
from app.models.oauth import OAuthToken

oauth2_scheme = fastapi.security.oauth2.OAuth2PasswordBearer(tokenUrl='auth/login')

# TODO Add endpoint docs

class RegisterData(pydantic.BaseModel):
    username: str
    email: str
    password: str

class ChangePasswordData(pydantic.BaseModel):
    current_password: str
    new_password: str

class PasswordResetResponse(pydantic.BaseModel):
    message: str = 'Password reset successfully.'

class UserRegisterResponse(pydantic.BaseModel):
    user_id: int
    message: str = 'Successfully created new user.'

class SendVerificationEmailResponse(pydantic.BaseModel):
    user_id: int
    user_email: str
    message: str = 'Successfully sent account verification email for user with given ID.'

class SendVerificationEmailAlreadyVerifiedResponse(pydantic.BaseModel):
    user_id: int
    user_email: str
    message: str = 'Account for the user with given ID was already verified.'

class VerifyEmailResponse(pydantic.BaseModel):
    message: str = 'User account verified successfully.'

class VerifyEmailAlreadyVerifiedResponse(pydantic.BaseModel):
    message: str = 'User account has been already verified.'

class PasswordChangedResponse(pydantic.BaseModel):
    message: str = 'User password changed successfully.'

router = fastapi.APIRouter(
    prefix='/auth',
    tags=['auth'])

@router.get(
    '/password-validation-rules',
    name='Get password validation rules')
@inject
async def auth_get_password_validation_rules(auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])) -> str:
    '''
    Returns password validation regex used to check if provided password is valid on the frontend side.
    '''

    return auth_service.get_password_validation_regex()

@router.post(
    '/register',
    name='Register new user',
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {'model': ErrorInvalidPasswordEncoding},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': t.Union[ErrorInvalidPasswordFormat, ErrorEmailInvalid, ErrorEmailNotFound]},
        fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': t.Union[ErrorIPInfoRetrieveFailed, ErrorEmailNotDelivered]},
        fastapi.status.HTTP_409_CONFLICT: {'model': ErrorUserAlreadyExists}
    })
@inject
async def auth_register(data: RegisterData,
                        request: fastapi.Request,
                        location_service: LocationService = fastapi.Depends(Provide['location_service']),
                        auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                        email_service: EmailService = fastapi.Depends(Provide['email_service'])):
    '''
    Registers new user, using provided info. Adds user to databasde and sends account verification email to the provided email address.
    '''

    await email_service.validate_email(data.email)
    
    user_id = await auth_service.register_user(
        data.username,
        data.email,
        data.password,
        await location_service.get_country_code_from_ip(request.client.host))
    
    await email_service.send_account_verification_email(
        _create_email_confirm_url(auth_service.generate_email_verification_code(user_id)),
        _create_email_confirm_resend_url(user_id),
        data.email)

    return UserRegisterResponse(user_id=user_id)

@router.post(
    '/send-verification-email/{user_id}',
    name='Send verification email',
    responses={
        fastapi.status.HTTP_200_OK: {'model': t.Union[SendVerificationEmailResponse, SendVerificationEmailAlreadyVerifiedResponse]},
        fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': ErrorEmailNotDelivered},
    })
@inject
async def auth_send_verification_email(user_id: int,
                                       user_service: UserService = fastapi.Depends(Provide['user_service']),
                                       auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                                       email_service: EmailService = fastapi.Depends(Provide['email_service'])):
    '''
    Sends a new email with verification code for a given user. If user email have been verified before no action is taken.
    '''

    user_email, email_verified = await user_service.get_user_email_info(user_id)
    
    if not email_verified:
        await email_service.send_account_verification_email(
            _create_email_confirm_url(auth_service.generate_email_verification_code(user_id)),
            _create_email_confirm_resend_url(user_id),
            user_email)
        return SendVerificationEmailResponse(user_id=user_id, user_email=user_email)
    
    return SendVerificationEmailAlreadyVerifiedResponse(user_id=user_id, user_email=user_email)

@router.post(
    '/verify-email/{verification_code}',
    name='Verify email',
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': t.Union[ErrorEmailCodeExpired, ErrorEmailCodeInvalid]},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorUserNotFoundID},
        fastapi.status.HTTP_200_OK: {'model': t.Union[VerifyEmailResponse, VerifyEmailAlreadyVerifiedResponse]},
    })
@inject
async def auth_verify_email(verification_code: str,
                            auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    '''
    Tries to verify user account with the code from verification email. If the code is valid then user account can be logged into.
    Otherwise an appropriate error is thrown.
    '''

    email_confirmed = await auth_service.confirm_user_email(verification_code)
    if email_confirmed:
        return VerifyEmailResponse()
    
    return VerifyEmailAlreadyVerifiedResponse()

@router.post(
    '/reset-password/{username}',
    name='Reset password',
    responses={
        fastapi.status.HTTP_403_FORBIDDEN: {'model': ErrorEmailNotConfirmed},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorUserNotFoundUsername},
        fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR: {'model': ErrorEmailNotDelivered},
    })
@inject
async def auth_reset_password(username: str,
                              auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                              email_service: EmailService = fastapi.Depends(Provide['email_service'])):
    user_email, new_password = await auth_service.reset_user_password(username)
    await email_service.send_password_reset_email(new_password, user_email)
    
    return PasswordResetResponse()

@router.post(
    '/change-password',
    name='Change password',
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': ErrorInvalidPassword},
        fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {'model': ErrorInvalidPasswordEncoding},
        fastapi.status.HTTP_404_NOT_FOUND: {'model': ErrorUserNotFoundID},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': ErrorInvalidPasswordFormat},
    })
@inject
async def auth_change_password(data: ChangePasswordData,
                               user_jwt: str = fastapi.Depends(oauth2_scheme),
                               auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    await auth_service.change_user_password(
        auth_service.decode_jwt(user_jwt),
        data.current_password,
        data.new_password)

    return PasswordChangedResponse()

@router.post(
    '/validate-jwt',
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    response_description='User JWT is valid.',
    responses={
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': None, 'description': 'User JWT is not valid. Re-login is required.'}})
@inject
async def validate_jwt(user_jwt: str = fastapi.Depends(oauth2_scheme),
                       auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    '''
    Checks if provided user JWT is valid, returning 204 if it is, 401 otherwise.
    '''

    try:
        auth_service.decode_jwt(user_jwt)
        return fastapi.responses.JSONResponse(
            content=None,
            status_code=fastapi.status.HTTP_204_NO_CONTENT)
    except fastapi.HTTPException:
        return fastapi.responses.JSONResponse(
            content=None,
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED)

@router.post(
    path='/login',
    responses={
        fastapi.status.HTTP_200_OK: {'model': OAuthToken},
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': ErrorOAuthInvalidClient},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': t.Union[ErrorOAuthInvalidRequest, ErrorOAuthUnauthorizedClient]}})
@inject
async def auth_login(login_data: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
                     auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                     datetime_service: DatetimeService = fastapi.Depends(Provide['datetime_service']),
                     user_service: UserService = fastapi.Depends(Provide['user_service'])) -> OAuthToken:
    user_id, access_token = await auth_service.login_user(
        login_data.username,
        login_data.password,
        datetime_service.get_datetime_utc_now())
    await user_service.refresh_user_activity(user_id, datetime_service.get_datetime_utc_now())
    
    return fastapi.responses.JSONResponse(
        content=OAuthToken(
            access_token=access_token,
            expires_in=auth_service.get_jwt_expire_time().seconds).model_dump(),
        headers={'Cache-Control': 'no-store'})

async def auth_logout() -> None:
    pass

def _create_email_confirm_url(confirmation_code: str) -> str:
    return f'http://localhost:3000/confirm-email?code={confirmation_code}'

def _create_email_confirm_resend_url(user_id: int) -> str:
    return f'http://localhost:3000/send-confirmation-email/{user_id}'