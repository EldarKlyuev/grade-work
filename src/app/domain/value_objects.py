"""Value objects - immutable domain primitives"""

import re
from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.exceptions import InvalidEmailError, InvalidMoneyError, InvalidPasswordError


@dataclass(frozen=True)
class Email:
    """Email value object with validation"""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self._is_valid_format(self.value):
            raise InvalidEmailError(self.value)
    
    @staticmethod
    def _is_valid_format(email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with strength validation"""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self._is_strong_enough(self.value):
            raise InvalidPasswordError(
                "Password must be at least 8 characters long and contain "
                "uppercase, lowercase, digit, and special character"
            )
    
    @staticmethod
    def _is_strong_enough(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def __str__(self) -> str:
        return "***"


@dataclass(frozen=True)
class Money:
    """Money value object with precision handling"""
    
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidMoneyError(float(self.amount))
        
        object.__setattr__(self, 'amount', self.amount.quantize(Decimal('0.01')))
    
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise InvalidMoneyError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise InvalidMoneyError("Cannot subtract different currencies")
        result = self.amount - other.amount
        if result < 0:
            raise InvalidMoneyError(float(result))
        return Money(result, self.currency)
    
    def __mul__(self, multiplier: int | Decimal) -> "Money":
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
    
    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        return cls(Decimal("0.00"), currency)


@dataclass(frozen=True)
class Pagination:
    """Pagination value object"""
    
    page: int
    page_size: int
    
    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("Page must be >= 1")
        if self.page_size < 1:
            raise ValueError("Page size must be >= 1")
        if self.page_size > 100:
            raise ValueError("Page size must be <= 100")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size
