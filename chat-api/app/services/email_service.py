import aiosmtplib
import email_validator
import asyncio
from email.mime.text import MIMEText

import itsdangerous

class EmailService:
    def __init__(self,
                 smtp_host: str,
                 smtp_port: int,
                 smtp_user: str,
                 smtp_password: str,
                 verification_template_path: str,
                 password_reset_template_path: str) -> None:
        self._smtp_user = smtp_user
        self._smtp_client = aiosmtplib.SMTP(
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            use_tls=True)
        self._verification_template = self._read_template(verification_template_path)
        self._password_reset_template = self._read_template(password_reset_template_path)
    
    async def validate_email(self, email_address: str) -> None:
        '''
        :raises: email_validator.EmailSyntaxError: When email address format is invalid.
        :raises: email_validator.EmailUndeliverableError: When email address does not exist.
        '''
        await asyncio.to_thread(email_validator.validate_email, email_address)
    
    async def send_password_reset_email(self,
                                        new_password: str,
                                        email_address: str) -> None:
        '''
        :raises aiosmtplib.SMTPException: When account verification email couldn't be delivered.
        '''
        
        content = self._password_reset_template.format(new_password=new_password)
        message = self._build_html_message(
            content,
            'Password reset',
            email_address)

        await self._send_email(message, email_address)

    async def send_account_verification_email(self,
                                              verification_url: str,
                                              resend_url: str,
                                              email_address: str) -> None:
        content = self._verification_template.format(
            verification_url=verification_url,
            resend_url=resend_url)
        message = self._build_html_message(
            content,
            'Account verification',
            email_address)
        
        await self._send_email(message, email_address)
            
    async def _send_email(self, message: MIMEText, email_address) -> None:
        async with self._smtp_client:
            await self._smtp_client.sendmail(
                self._smtp_user,
                (email_address,),
                message.as_bytes())

    def _build_html_message(self, content: str, subject: str, to: str) -> MIMEText:
        message = MIMEText(content, 'html')
        message.add_header('Subject', subject)
        message.add_header('From', self._smtp_user)
        message.add_header('To', to)
        
        return message
        
    def _read_template(self, path: str) -> str:
        with open(path, 'r') as f:
            return f.read()