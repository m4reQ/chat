import aiosmtplib
import email_validator
import fastapi
import fastapi.security
import typing as t
from dependency_injector.wiring import Provide, inject

from app.models.requests import ChangePasswordData, RegisterData
from app.models.responses import OAuthInvalidRequest, OAuthToken, OAuthInvalidClient, OAuthUnauthorizedClient
from app.services import AuthorizationService, DatetimeService, EmailService

oauth2_scheme = fastapi.security.oauth2.OAuth2PasswordBearer(tokenUrl='auth/login')

# TODO Add endpoint docs

# TODO Return password requirements from some endpoint
# password regex: 

router = fastapi.APIRouter(
    prefix='/auth',
    tags=['auth'])

@router.get('/password-validation-rules')
@inject
async def auth_get_password_validation_rules(auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    return {
        'regex': auth_service.get_password_validation_regex(),
        'min_password_length': auth_service.get_min_password_length()}

@router.post('/register')
@inject
async def auth_register(data: RegisterData,
                        request: fastapi.Request,
                        auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                        email_service: EmailService = fastapi.Depends(Provide['email_service'])):
    try:
        await email_service.validate_email(data.email)
    except email_validator.EmailSyntaxError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                'error': 'Provided email address is not valid.',
                'error_code': 'email_invalid'})
    except email_validator.EmailUndeliverableError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                'error': 'Provided email address does not exist.',
                'error_code': 'email_doesnt_exist'})
    
    user_id = auth_service.register_user(
        data.username,
        data.email,
        data.password,
        request.client.host)
    verification_code = auth_service.generate_email_verification_code(user_id)
    verification_url = f'http://localhost:3000/verify-email?code={verification_code}'
    resend_url = f'http://localhost:8000/send-verify-msg?user_id={user_id}'

    try:
        await email_service.send_account_verification_email(verification_url, resend_url, data.email)
    except aiosmtplib.SMTPException:
        auth_service.unregister_user(user_id)
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'error': 'Failed to send account verification email.',
                'error_code': 'verification_email_fail'})

    return fastapi.responses.JSONResponse(
        content={
            'message': 'Successfully created new user.',
            'user_id': user_id},
        headers={'Location': f'http://localhost:8000/user/{user_id}'},
        status_code=fastapi.status.HTTP_201_CREATED)

@router.post('/send-verification-email/{user_id}')
@inject
async def auth_send_verification_email(user_id: int,
                                       auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    email_sent = auth_service.send_verification_email(user_id)
    if email_sent:
        return fastapi.responses.JSONResponse(
            content={
                'message': 'Successfully sent account verification email for user with given ID.',
                'user_id': user_id},
            status_code=fastapi.status.HTTP_200_OK)

    return fastapi.responses.JSONResponse(
        content={
            'message': 'Account for the user with given ID was already verified.',
            'user_id': user_id},
            status_code=fastapi.status.HTTP_204_NO_CONTENT)

@router.post('/verify-email/{verification_code}')
@inject
async def auth_verify_email(verification_code: str,
                            auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    email_confirmed = auth_service.confirm_user_email(verification_code)
    if email_confirmed:
        return fastapi.Response(status_code=fastapi.status.HTTP_200_OK)
    
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)

@router.post('/reset-password/{username}')
@inject
async def auth_reset_password(username: str,
                              auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    auth_service.reset_user_password(username)
    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_200_OK,
        content={
            'message': 'Password reset email has been sent to a given user.',
            'username': username})

@router.post('/change-password')
@inject
async def auth_change_password(data: ChangePasswordData,
                               user_jwt: str = fastapi.Depends(oauth2_scheme),
                               auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service'])):
    user_id = auth_service.decode_jwt(user_jwt)
    auth_service.change_user_password(user_id, data.current_password, data.new_password)

    return fastapi.responses.JSONResponse(
        status_code=fastapi.status.HTTP_200_OK,
        content={'message': 'Successfully changed user password.'})

@router.post(
    path='/login',
    responses={
        fastapi.status.HTTP_200_OK: {'model': OAuthToken },
        fastapi.status.HTTP_401_UNAUTHORIZED: {'model': OAuthInvalidClient},
        fastapi.status.HTTP_400_BAD_REQUEST: {'model': t.Union[OAuthInvalidRequest, OAuthUnauthorizedClient]}})
@inject
async def auth_login(login_data: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
                     auth_service: AuthorizationService = fastapi.Depends(Provide['auth_service']),
                     datetime_service: DatetimeService = fastapi.Depends(Provide['datetime_service'])):
    return fastapi.responses.JSONResponse(
        content=OAuthToken(
            access_token=auth_service.login_user(
                login_data.username,
                login_data.password,
                datetime_service.get_datetime_utc_now()),
            expires_in=auth_service.get_jwt_expire_time().seconds).model_dump(),
        headers={'Cache-Control': 'no-store'})

async def auth_logout() -> None:
    pass