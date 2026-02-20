"""Доменные исключения.

Все исключения, специфичные для доменного слоя.
Представляют нарушения бизнес-правил и инвариантов домена.
"""


class DomainError(Exception):
    """Базовое доменное исключение.
    
    Родительский класс для всех доменных исключений.
    Позволяет отлавливать любые доменные ошибки единообразно.
    """
    pass


class InvalidEmailError(DomainError):
    """Некорректный формат email.
    
    Выбрасывается при попытке создать Email с невалидным форматом.
    
    :param email: Некорректный email адрес
    :type email: str
    """
    
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Invalid email format: {email}")


class InvalidPasswordError(DomainError):
    """Некорректный пароль.
    
    Выбрасывается при попытке создать Password, не соответствующий требованиям безопасности.
    
    :param reason: Причина отклонения пароля
    :type reason: str
    """
    
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid password: {reason}")


class InvalidMoneyError(DomainError):
    """Некорректное денежное значение.
    
    Выбрасывается при попытке создать отрицательную сумму или
    выполнить некорректную операцию с Money (например, разные валюты).
    
    :param value: Некорректное значение
    :type value: float | int | str
    """
    
    def __init__(self, value: float | int | str) -> None:
        self.value = value
        super().__init__(f"Invalid money value: {value}")


class UserNotFoundError(DomainError):
    """Пользователь не найден.
    
    Выбрасывается при попытке получить несуществующего пользователя.
    
    :param identifier: Идентификатор пользователя (ID или email)
    :type identifier: str
    """
    
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"User not found: {identifier}")


class ProductNotFoundError(DomainError):
    """Товар не найден.
    
    Выбрасывается при попытке получить несуществующий товар.
    
    :param product_id: ID товара
    :type product_id: str
    """
    
    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"Product not found: {product_id}")


class CategoryNotFoundError(DomainError):
    """Категория не найдена.
    
    Выбрасывается при попытке получить несуществующую категорию.
    
    :param category_id: ID категории
    :type category_id: str
    """
    
    def __init__(self, category_id: str) -> None:
        self.category_id = category_id
        super().__init__(f"Category not found: {category_id}")


class InsufficientStockError(DomainError):
    """Недостаточно товара на складе.
    
    Выбрасывается при попытке зарезервировать больше товара, чем доступно.
    
    :param product_id: ID товара
    :type product_id: str
    :param requested: Запрошенное количество
    :type requested: int
    :param available: Доступное количество
    :type available: int
    """
    
    def __init__(self, product_id: str, requested: int, available: int) -> None:
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product {product_id}: "
            f"requested {requested}, available {available}"
        )


class InvalidCredentialsError(DomainError):
    """Неверные учетные данные.
    
    Выбрасывается при неудачной попытке аутентификации.
    """
    
    def __init__(self) -> None:
        super().__init__("Invalid credentials")


class UserAlreadyExistsError(DomainError):
    """Пользователь уже существует.
    
    Выбрасывается при попытке зарегистрировать пользователя с существующим email.
    
    :param email: Email, который уже занят
    :type email: str
    """
    
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User already exists: {email}")


class InvalidTokenError(DomainError):
    """Некорректный токен.
    
    Выбрасывается при попытке использовать невалидный токен.
    """
    
    def __init__(self) -> None:
        super().__init__("Invalid token")


class ExpiredTokenError(DomainError):
    """Истек срок действия токена.
    
    Выбрасывается при попытке использовать токен с истекшим сроком.
    """
    
    def __init__(self) -> None:
        super().__init__("Token has expired")
