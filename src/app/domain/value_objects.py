"""Объекты-значения - неизменяемые доменные примитивы.

Этот модуль содержит все Value Objects доменного слоя.
Value Objects отличаются от сущностей отсутствием идентификатора
и равенством по значению, а не по ID.
"""

import re
from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.exceptions import InvalidEmailError, InvalidMoneyError, InvalidPasswordError


@dataclass(frozen=True)
class Email:
    """Объект-значение email с валидацией.
    
    Неизменяемый объект, представляющий валидированный email адрес.
    Обеспечивает соблюдение бизнес-правил для email на уровне домена.
    
    :param value: Строка email адреса
    :type value: str
    :raises InvalidEmailError: Если формат email некорректен
    
    :example:
    
    >>> email = Email("user@example.com")
    >>> str(email)  # "user@example.com"
    >>> Email("invalid")  # Raises InvalidEmailError
    
    .. note::
       Email неизменяем (frozen=True), что гарантирует
       валидность в течение всего жизненного цикла.
    """
    
    value: str
    
    def __post_init__(self) -> None:
        """Валидация email при создании.
        
        :raises InvalidEmailError: Если формат некорректен
        """
        if not self._is_valid_format(self.value):
            raise InvalidEmailError(self.value)
    
    @staticmethod
    def _is_valid_format(email: str) -> bool:
        """Проверить формат email адреса.
        
        Проверяет базовые требования:
        - Не пустой
        - Длина не более 254 символов (RFC 5321)
        - Соответствует регулярному выражению
        
        :param email: Строка для проверки
        :type email: str
        :return: True если формат корректен
        :rtype: bool
        """
        if not email or len(email) > 254:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        """Строковое представление email.
        
        :return: Email адрес
        :rtype: str
        """
        return self.value


@dataclass(frozen=True)
class Password:
    """Объект-значение пароля с проверкой сложности.
    
    Представляет пароль в открытом виде с валидацией требований безопасности.
    Используется только при регистрации и смене пароля, после чего хешируется.
    
    :param value: Пароль в открытом виде
    :type value: str
    :raises InvalidPasswordError: Если пароль не соответствует требованиям
    
    :example:
    
    >>> password = Password("SecurePass123!")
    >>> str(password)  # "***" (скрыт в строковом представлении)
    
    .. warning::
       Не храните пароли в открытом виде!
       Сразу после создания объекта хешируйте пароль.
    """
    
    value: str
    
    def __post_init__(self) -> None:
        """Валидация требований к паролю при создании.
        
        :raises InvalidPasswordError: Если требования не выполнены
        """
        if not self._is_strong_enough(self.value):
            raise InvalidPasswordError(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, digit, and special character"
            )
    
    @staticmethod
    def _is_strong_enough(password: str) -> bool:
        """Проверить сложность пароля.
        
        Требования к паролю:
        - Минимум 8 символов
        - Хотя бы одна заглавная буква
        - Хотя бы одна строчная буква
        - Хотя бы одна цифра
        - Хотя бы один специальный символ
        
        :param password: Пароль для проверки
        :type password: str
        :return: True если пароль достаточно сложный
        :rtype: bool
        """
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def __str__(self) -> str:
        """Строковое представление (скрыто для безопасности).
        
        :return: Замаскированная строка
        :rtype: str
        """
        return "***"


@dataclass(frozen=True)
class Money:
    """Объект-значение денежной суммы с точным представлением.
    
    Представляет денежную сумму с использованием Decimal для точности.
    Поддерживает арифметические операции с проверкой валюты.
    
    :param amount: Сумма денег (автоматически округляется до 2 знаков)
    :type amount: Decimal
    :param currency: Код валюты (по умолчанию USD)
    :type currency: str
    :raises InvalidMoneyError: Если сумма отрицательная
    
    :example:
    
    >>> price = Money(Decimal("100.50"))
    >>> tax = Money(Decimal("10.05"))
    >>> total = price + tax  # Money(Decimal("110.55"))
    >>> doubled = price * 2  # Money(Decimal("201.00"))
    
    .. note::
       Используется Decimal вместо float для точных денежных вычислений
       и избежания ошибок округления.
    """
    
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self) -> None:
        """Валидация и нормализация суммы при создании.
        
        :raises InvalidMoneyError: Если сумма отрицательная
        """
        if self.amount < 0:
            raise InvalidMoneyError(float(self.amount))
        
        object.__setattr__(self, 'amount', self.amount.quantize(Decimal('0.01')))
    
    def __add__(self, other: "Money") -> "Money":
        """Сложение денежных сумм.
        
        :param other: Другая денежная сумма
        :type other: Money
        :return: Сумма
        :rtype: Money
        :raises InvalidMoneyError: Если валюты различаются
        """
        if self.currency != other.currency:
            raise InvalidMoneyError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        """Вычитание денежных сумм.
        
        :param other: Другая денежная сумма
        :type other: Money
        :return: Разность
        :rtype: Money
        :raises InvalidMoneyError: Если валюты различаются или результат отрицательный
        """
        if self.currency != other.currency:
            raise InvalidMoneyError("Cannot subtract different currencies")
        result = self.amount - other.amount
        if result < 0:
            raise InvalidMoneyError(float(result))
        return Money(result, self.currency)
    
    def __mul__(self, multiplier: int | Decimal) -> "Money":
        """Умножение денежной суммы на число.
        
        :param multiplier: Множитель (целое число или Decimal)
        :type multiplier: int | Decimal
        :return: Произведение
        :rtype: Money
        """
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __str__(self) -> str:
        """Строковое представление суммы.
        
        :return: Сумма с валютой, например "100.50 USD"
        :rtype: str
        """
        return f"{self.amount} {self.currency}"
    
    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        """Создать нулевую денежную сумму.
        
        Удобный фабричный метод для инициализации.
        
        :param currency: Код валюты
        :type currency: str
        :return: Нулевая сумма
        :rtype: Money
        
        :example:
        
        >>> total = Money.zero()
        >>> for item in items:
        ...     total = total + item.price
        """
        return cls(Decimal("0.00"), currency)


@dataclass(frozen=True)
class Pagination:
    """Объект-значение для параметров пагинации.
    
    Инкапсулирует логику пагинации с валидацией параметров.
    Используется в query services для получения списков с ограничением.
    
    :param page: Номер страницы (начиная с 1)
    :type page: int
    :param page_size: Размер страницы (количество элементов)
    :type page_size: int
    :raises ValueError: Если параметры некорректны
    
    :example:
    
    >>> pagination = Pagination(page=2, page_size=20)
    >>> pagination.offset  # 20
    >>> pagination.limit   # 20
    """
    
    page: int
    page_size: int
    
    def __post_init__(self) -> None:
        """Валидация параметров пагинации.
        
        :raises ValueError: Если page < 1, page_size < 1 или page_size > 100
        """
        if self.page < 1:
            raise ValueError("Page must be >= 1")
        if self.page_size < 1:
            raise ValueError("Page size must be >= 1")
        if self.page_size > 100:
            raise ValueError("Page size must be <= 100")
    
    @property
    def offset(self) -> int:
        """Вычислить offset для SQL запроса.
        
        Используется для пропуска элементов предыдущих страниц.
        
        :return: Количество элементов для пропуска
        :rtype: int
        
        :example:
        
        >>> Pagination(page=1, page_size=10).offset  # 0
        >>> Pagination(page=3, page_size=10).offset  # 20
        """
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Получить лимит элементов для SQL запроса.
        
        :return: Размер страницы
        :rtype: int
        """
        return self.page_size
