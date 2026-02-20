"""Application ports - gateway interfaces"""

from typing import Protocol


class EmailGatewayPort(Protocol):
    """Email gateway port"""
    
    async def send_registration_email(self, to: str, username: str) -> None:
        """Send registration email"""
        ...
    
    async def send_password_reset_email(
        self,
        to: str,
        username: str,
        reset_token: str,
    ) -> None:
        """Send password reset email"""
        ...


class ImageProcessingPort(Protocol):
    """Image processing port"""
    
    def resize_image(
        self,
        image_data: bytes,
        width: int,
        height: int,
        maintain_aspect_ratio: bool = True,
    ) -> bytes:
        """Resize image"""
        ...


class TokenServicePort(Protocol):
    """Token service port"""
    
    def create_access_token(self, subject: str) -> str:
        """Create access token"""
        ...
    
    def decode_token(self, token: str) -> dict:
        """Decode token"""
        ...
    
    def get_subject(self, token: str) -> str:
        """Get subject from token"""
        ...


class PasswordHasherPort(Protocol):
    """Password hasher port"""
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        ...
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        ...
