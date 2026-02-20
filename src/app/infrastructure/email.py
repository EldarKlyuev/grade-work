"""Email service - SMTP email sending"""

import asyncio
from dataclasses import dataclass

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import settings


@dataclass
class EmailMessage:
    """Email message data"""
    
    to: str
    subject: str
    body: str
    html_body: str | None = None


class SmtpEmailService:
    """SMTP email service implementation"""
    
    def __init__(self) -> None:
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.use_tls = settings.smtp_use_tls
    
    async def send_email(self, message: EmailMessage) -> None:
        """Send email message"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["From"] = self.from_email
        msg["To"] = message.to
        
        part1 = MIMEText(message.body, "plain")
        msg.attach(part1)
        
        if message.html_body:
            part2 = MIMEText(message.html_body, "html")
            msg.attach(part2)
        
        await aiosmtplib.send(
            msg,
            hostname=self.host,
            port=self.port,
            username=self.username if self.username else None,
            password=self.password if self.password else None,
            use_tls=self.use_tls,
        )
    
    async def send_registration_email(self, to: str, username: str) -> None:
        """Send registration confirmation email"""
        message = EmailMessage(
            to=to,
            subject="Welcome to E-commerce API!",
            body=f"Hello {username},\n\nWelcome to our platform! "
                 f"Your account has been successfully created.\n\nBest regards,\nThe Team",
            html_body=f"""
            <html>
                <body>
                    <h1>Welcome {username}!</h1>
                    <p>Your account has been successfully created.</p>
                    <p>Best regards,<br>The Team</p>
                </body>
            </html>
            """,
        )
        await self.send_email(message)
    
    async def send_password_reset_email(
        self,
        to: str,
        username: str,
        reset_token: str,
    ) -> None:
        """Send password reset email"""
        reset_url = f"{settings.app_url}/auth/password-reset/confirm?token={reset_token}"
        
        message = EmailMessage(
            to=to,
            subject="Password Reset Request",
            body=f"Hello {username},\n\nYou requested a password reset. "
                 f"Click the link below to reset your password:\n\n{reset_url}\n\n"
                 f"If you didn't request this, please ignore this email.\n\nBest regards,\nThe Team",
            html_body=f"""
            <html>
                <body>
                    <h1>Password Reset Request</h1>
                    <p>Hello {username},</p>
                    <p>You requested a password reset. Click the link below to reset your password:</p>
                    <p><a href="{reset_url}">Reset Password</a></p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p>Best regards,<br>The Team</p>
                </body>
            </html>
            """,
        )
        await self.send_email(message)
