import aiosmtplib
import asyncio
import pathlib
import email_validator
import fastapi
from email.mime.text import MIMEText

from app import error
from app.models.errors import ErrorEmailNotDelivered, ErrorEmailInvalid, ErrorEmailNotFound

class _MessageTemplate:
    def __init__(self, filepath: pathlib.Path, sender: str, title: str) -> None:
        self._template_string = filepath.read_text()
        self._sender = sender
        self._title = title
    
    def build(self,
              recipient: str,
              **format_args) -> MIMEText:
        message = MIMEText(self._template_string.format(**format_args), 'html')
        message.add_header('Subject', self._title)
        message.add_header('From', self._sender)
        message.add_header('To', recipient)
        
        return message

class EmailService:
    def __init__(self,
                 smtp_host: str,
                 smtp_port: int,
                 smtp_user: str,
                 smtp_password: str,
                 data_directory: pathlib.Path) -> None:
        self._smtp_user = smtp_user
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._smtp_client = aiosmtplib.SMTP(
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            use_tls=True,
            validate_certs=False)
        self._verification_template = _MessageTemplate(
            data_directory / 'email_templates' / 'account_verification.html',
            smtp_user,
            'Chatter - Account verification')
        self._password_reset_template = _MessageTemplate(
            data_directory / 'email_templates' / 'password_reset.html',
            smtp_user,
            'Chatter - Password reset')
    
    async def validate_email(self, email_address: str) -> None:
        try:
            await asyncio.to_thread(email_validator.validate_email, email_address)
        except email_validator.EmailSyntaxError:
            error.raise_error_obj(
                ErrorEmailInvalid(email=email_address),
                fastapi.status.HTTP_400_BAD_REQUEST)
        except email_validator.EmailUndeliverableError:
            error.raise_error_obj(
                ErrorEmailNotFound(email=email_address),
                fastapi.status.HTTP_400_BAD_REQUEST)
    
    async def send_password_reset_email(self, new_password: str, email_address: str) -> None:
        try:
            await self._send_email(
                self._password_reset_template.build(
                    email_address,
                    new_password=new_password),
                email_address)
        except aiosmtplib.SMTPException:
            ErrorEmailNotDelivered(email=email_address) \
                .raise_()

    async def send_account_verification_email(self,
                                              verification_url: str,
                                              resend_url: str,
                                              email_address: str) -> None:
        try:
            await self._send_email(
                self._verification_template.build(
                    email_address,
                    verification_url=verification_url,
                    resend_url=resend_url),
                email_address)
        except aiosmtplib.SMTPException:
            error.raise_error_obj(ErrorEmailNotDelivered(email=email_address))
            
    async def _send_email(self, message: MIMEText, email_address: str) -> None:
        async with self._smtp_client:
            await self._smtp_client.sendmail(
                self._smtp_user,
                (email_address,),
                message.as_bytes())