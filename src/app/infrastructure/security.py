"""Security services - JWT and password hashing"""

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from config.settings import settings
from src.app.domain.exceptions import ExpiredTokenError, InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """Password hashing service"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)


class JWTTokenService:
    """JWT token service"""
    
    def __init__(self) -> None:
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire = settings.jwt_access_token_expire_minutes
    
    def create_access_token(self, subject: str, **kwargs: Any) -> str:
        """Create access token"""
        expires_delta = timedelta(minutes=self.access_token_expire)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            **kwargs,
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.JWTError:
            raise InvalidTokenError()
    
    def get_subject(self, token: str) -> str:
        """Get subject from token"""
        payload = self.decode_token(token)
        subject = payload.get("sub")
        if not subject:
            raise InvalidTokenError()
        return subject
