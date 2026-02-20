"""Порты уровня приложения - интерфейсы шлюзов.

Определяет контракты для внешних сервисов, используемых в интеракторах.
Реализации находятся в инфраструктурном слое.
"""

from typing import Protocol


class EmailGatewayPort(Protocol):
    """Интерфейс шлюза для отправки email."""
    
    async def send_registration_email(self, to: str, username: str) -> None:
        """Отправить приветственное письмо при регистрации."""
        ...
    
    async def send_password_reset_email(
        self,
        to: str,
        username: str,
        reset_token: str,
    ) -> None:
        """Отправить письмо для сброса пароля."""
        ...


class ImageProcessingPort(Protocol):
    """Интерфейс для обработки изображений."""
    
    def resize_image(
        self,
        image_data: bytes,
        width: int,
        height: int,
        maintain_aspect_ratio: bool = True,
    ) -> bytes:
        """Изменить размер изображения."""
        ...


class TokenServicePort(Protocol):
    """Интерфейс сервиса JWT токенов."""
    
    def create_access_token(self, subject: str) -> str:
        """Создать токен доступа."""
        ...
    
    def decode_token(self, token: str) -> dict:
        """Декодировать токен."""
        ...
    
    def get_subject(self, token: str) -> str:
        """Получить subject (ID пользователя) из токена."""
        ...


class PasswordHasherPort(Protocol):
    """Интерфейс сервиса хеширования паролей."""
    
    def hash_password(self, password: str) -> str:
        """Хешировать пароль."""
        ...
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить соответствие пароля хешу."""
        ...
