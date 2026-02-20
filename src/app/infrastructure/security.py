"""Сервисы безопасности - JWT и хеширование паролей.

Реализации портов для аутентификации и безопасности.
"""

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from config.settings import settings
from src.app.domain.exceptions import ExpiredTokenError, InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """Сервис хеширования паролей с использованием bcrypt.
    
    Реализует PasswordHasherPort для безопасного хеширования
    и проверки паролей.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Захешировать пароль с использованием bcrypt.
        
        :param password: Пароль в открытом виде
        :type password: str
        :return: Хеш пароля
        :rtype: str
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль против хеша.
        
        :param plain_password: Пароль для проверки
        :type plain_password: str
        :param hashed_password: Хеш для сравнения
        :type hashed_password: str
        :return: True если пароль совпадает
        :rtype: bool
        """
        return pwd_context.verify(plain_password, hashed_password)


class JWTTokenService:
    """Сервис JWT токенов для аутентификации.
    
    Реализует TokenServicePort. Создает и валидирует JWT токены
    с заданным сроком действия.
    """
    
    def __init__(self) -> None:
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire = settings.jwt_access_token_expire_minutes
    
    def create_access_token(self, subject: str, **kwargs: Any) -> str:
        """Создать токен доступа JWT.
        
        :param subject: Subject (обычно ID пользователя)
        :type subject: str
        :param kwargs: Дополнительные claims
        :return: Закодированный JWT токен
        :rtype: str
        """
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
        """Декодировать и валидировать токен.
        
        :param token: JWT токен
        :type token: str
        :return: Payload токена
        :rtype: dict[str, Any]
        :raises ExpiredTokenError: Если токен истек
        :raises InvalidTokenError: Если токен невалиден
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.JWTError:
            raise InvalidTokenError()
    
    def get_subject(self, token: str) -> str:
        """Получить subject из токена.
        
        :param token: JWT токен
        :type token: str
        :return: Subject (ID пользователя)
        :rtype: str
        :raises InvalidTokenError: Если subject отсутствует
        """
        payload = self.decode_token(token)
        subject = payload.get("sub")
        if not subject:
            raise InvalidTokenError()
        return subject
