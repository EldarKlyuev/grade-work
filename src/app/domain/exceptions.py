"""Domain exceptions"""


class DomainError(Exception):
    """Base domain exception"""
    pass


class InvalidEmailError(DomainError):
    """Invalid email format"""
    
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Invalid email format: {email}")


class InvalidPasswordError(DomainError):
    """Invalid password"""
    
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid password: {reason}")


class InvalidMoneyError(DomainError):
    """Invalid money value"""
    
    def __init__(self, value: float | int) -> None:
        self.value = value
        super().__init__(f"Invalid money value: {value}")


class UserNotFoundError(DomainError):
    """User not found"""
    
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"User not found: {identifier}")


class ProductNotFoundError(DomainError):
    """Product not found"""
    
    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        super().__init__(f"Product not found: {product_id}")


class CategoryNotFoundError(DomainError):
    """Category not found"""
    
    def __init__(self, category_id: str) -> None:
        self.category_id = category_id
        super().__init__(f"Category not found: {category_id}")


class InsufficientStockError(DomainError):
    """Insufficient stock"""
    
    def __init__(self, product_id: str, requested: int, available: int) -> None:
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product {product_id}: "
            f"requested {requested}, available {available}"
        )


class InvalidCredentialsError(DomainError):
    """Invalid credentials"""
    
    def __init__(self) -> None:
        super().__init__("Invalid credentials")


class UserAlreadyExistsError(DomainError):
    """User already exists"""
    
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User already exists: {email}")


class InvalidTokenError(DomainError):
    """Invalid token"""
    
    def __init__(self) -> None:
        super().__init__("Invalid token")


class ExpiredTokenError(DomainError):
    """Expired token"""
    
    def __init__(self) -> None:
        super().__init__("Token has expired")
