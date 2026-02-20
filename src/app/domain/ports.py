"""Domain ports - interfaces for external dependencies"""

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
    """User repository port"""
    
    async def find_by_id(self, user_id: UUID) -> User | None:
        """Find user by ID"""
        ...
    
    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email"""
        ...
    
    async def save(self, user: User) -> None:
        """Save user"""
        ...
    
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""
        ...


class ProductRepositoryPort(Protocol):
    """Product repository port"""
    
    async def find_by_id(self, product_id: UUID) -> Product | None:
        """Find product by ID"""
        ...
    
    async def save(self, product: Product) -> None:
        """Save product"""
        ...
    
    async def save_many(self, products: list[Product]) -> None:
        """Save multiple products"""
        ...


class CategoryRepositoryPort(Protocol):
    """Category repository port"""
    
    async def find_by_id(self, category_id: UUID) -> Category | None:
        """Find category by ID"""
        ...
    
    async def find_by_slug(self, slug: str) -> Category | None:
        """Find category by slug"""
        ...
    
    async def save(self, category: Category) -> None:
        """Save category"""
        ...


class CartRepositoryPort(Protocol):
    """Cart repository port"""
    
    async def find_by_user_id(self, user_id: UUID) -> Cart | None:
        """Find cart by user ID"""
        ...
    
    async def save(self, cart: Cart) -> None:
        """Save cart"""
        ...
    
    async def delete(self, cart: Cart) -> None:
        """Delete cart"""
        ...


class OrderRepositoryPort(Protocol):
    """Order repository port"""
    
    async def find_by_id(self, order_id: UUID) -> Order | None:
        """Find order by ID"""
        ...
    
    async def save(self, order: Order) -> None:
        """Save order"""
        ...


class PasswordResetTokenRepositoryPort(Protocol):
    """Password reset token repository port"""
    
    async def find_by_token(self, token: str) -> PasswordResetToken | None:
        """Find token by token string"""
        ...
    
    async def save(self, token: PasswordResetToken) -> None:
        """Save token"""
        ...


class UnitOfWorkPort(Protocol):
    """Unit of work port for transaction management"""
    
    async def begin(self) -> None:
        """Begin transaction"""
        ...
    
    async def commit(self) -> None:
        """Commit transaction"""
        ...
    
    async def rollback(self) -> None:
        """Rollback transaction"""
        ...
    
    async def __aenter__(self) -> "UnitOfWorkPort":
        """Enter context manager"""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager"""
        ...
