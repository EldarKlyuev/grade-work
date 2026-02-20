"""Test value objects"""

import pytest

from src.app.domain.exceptions import InvalidEmailError, InvalidMoneyError, InvalidPasswordError
from src.app.domain.value_objects import Email, Money, Password
from decimal import Decimal


def test_email_valid():
    """Test valid email creation"""
    email = Email("test@example.com")
    assert email.value == "test@example.com"


def test_email_invalid():
    """Test invalid email raises error"""
    with pytest.raises(InvalidEmailError):
        Email("invalid-email")
    
    with pytest.raises(InvalidEmailError):
        Email("@example.com")
    
    with pytest.raises(InvalidEmailError):
        Email("test@")


def test_password_valid():
    """Test valid password creation"""
    password = Password("SecurePass123!")
    assert str(password) == "***"


def test_password_weak():
    """Test weak password raises error"""
    with pytest.raises(InvalidPasswordError):
        Password("short")
    
    with pytest.raises(InvalidPasswordError):
        Password("nouppercase123!")
    
    with pytest.raises(InvalidPasswordError):
        Password("NOLOWERCASE123!")
    
    with pytest.raises(InvalidPasswordError):
        Password("NoDigits!")
    
    with pytest.raises(InvalidPasswordError):
        Password("NoSpecialChar123")


def test_money_operations():
    """Test money value object operations"""
    money1 = Money(Decimal("10.50"))
    money2 = Money(Decimal("5.25"))
    
    result = money1 + money2
    assert result.amount == Decimal("15.75")
    
    result = money1 - money2
    assert result.amount == Decimal("5.25")
    
    result = money1 * 2
    assert result.amount == Decimal("21.00")


def test_money_negative():
    """Test negative money raises error"""
    with pytest.raises(InvalidMoneyError):
        Money(Decimal("-10.00"))
