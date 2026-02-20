"""Доменные порты - интерфейсы для внешних зависимостей.

Определяет контракты (Protocol) для репозиториев и других внешних сервисов.
Реализации находятся в инфраструктурном слое.
"""

from typing import Protocol
from uuid import UUID

from src.app.domain.entities import (
    Cart,
    Category,
    Order,
    PasswordResetToken,
    Product,
    User,
)
from src.app.domain.value_objects import Email


class UserRepositoryPort(Protocol):
    """Интерфейс репозитория пользователей.
    
    Определяет контракт для работы с хранилищем пользователей.
    Реализуется в инфраструктурном слое.
    """
    
    async def find_by_id(self, user_id: UUID) -> User | None:
        """Найти пользователя по ID.
        
        :param user_id: Уникальный идентификатор пользователя
        :type user_id: UUID
        :return: Пользователь или None если не найден
        :rtype: User | None
        """
        ...
    
    async def find_by_email(self, email: Email) -> User | None:
        """Найти пользователя по email.
        
        :param email: Email пользователя
        :type email: Email
        :return: Пользователь или None если не найден
        :rtype: User | None
        """
        ...
    
    async def save(self, user: User) -> None:
        """Сохранить пользователя (создать или обновить).
        
        :param user: Сущность пользователя
        :type user: User
        """
        ...
    
    async def exists_by_email(self, email: Email) -> bool:
        """Проверить существование пользователя по email.
        
        :param email: Email для проверки
        :type email: Email
        :return: True если пользователь существует
        :rtype: bool
        """
        ...


class ProductRepositoryPort(Protocol):
    """Интерфейс репозитория товаров."""
    
    async def find_by_id(self, product_id: UUID) -> Product | None:
        """Найти товар по ID."""
        ...
    
    async def save(self, product: Product) -> None:
        """Сохранить товар."""
        ...
    
    async def save_many(self, products: list[Product]) -> None:
        """Сохранить несколько товаров (пакетная операция)."""
        ...


class CategoryRepositoryPort(Protocol):
    """Интерфейс репозитория категорий."""
    
    async def find_by_id(self, category_id: UUID) -> Category | None:
        """Найти категорию по ID."""
        ...
    
    async def find_by_slug(self, slug: str) -> Category | None:
        """Найти категорию по slug."""
        ...
    
    async def save(self, category: Category) -> None:
        """Сохранить категорию."""
        ...


class CartRepositoryPort(Protocol):
    """Интерфейс репозитория корзин."""
    
    async def find_by_user_id(self, user_id: UUID) -> Cart | None:
        """Найти корзину пользователя."""
        ...
    
    async def save(self, cart: Cart) -> None:
        """Сохранить корзину."""
        ...
    
    async def delete(self, cart: Cart) -> None:
        """Удалить корзину."""
        ...


class OrderRepositoryPort(Protocol):
    """Интерфейс репозитория заказов."""
    
    async def find_by_id(self, order_id: UUID) -> Order | None:
        """Найти заказ по ID."""
        ...
    
    async def save(self, order: Order) -> None:
        """Сохранить заказ."""
        ...


class PasswordResetTokenRepositoryPort(Protocol):
    """Интерфейс репозитория токенов сброса пароля."""
    
    async def find_by_token(self, token: str) -> PasswordResetToken | None:
        """Найти токен по строке."""
        ...
    
    async def save(self, token: PasswordResetToken) -> None:
        """Сохранить токен."""
        ...


class UnitOfWorkPort(Protocol):
    """Интерфейс Unit of Work для управления транзакциями.
    
    Обеспечивает атомарность операций с несколькими репозиториями.
    """
    
    async def begin(self) -> None:
        """Начать транзакцию."""
        ...
    
    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        ...
    
    async def rollback(self) -> None:
        """Откатить транзакцию."""
        ...
    
    async def __aenter__(self) -> "UnitOfWorkPort":
        """Войти в контекстный менеджер."""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выйти из контекстного менеджера."""
        ...
