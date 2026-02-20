"""Data Transfer Objects"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class RegisterUserDTO:
    """Register user DTO"""
    email: str
    password: str
    username: str


@dataclass
class LoginUserDTO:
    """Login user DTO"""
    email: str
    password: str


@dataclass
class RequestPasswordResetDTO:
    """Request password reset DTO"""
    email: str


@dataclass
class ResetPasswordDTO:
    """Reset password DTO"""
    token: str
    new_password: str


@dataclass
class CreateProductDTO:
    """Create product DTO"""
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: UUID


@dataclass
class AddToCartDTO:
    """Add to cart DTO"""
    user_id: UUID
    product_id: UUID
    quantity: int


@dataclass
class RemoveFromCartDTO:
    """Remove from cart DTO"""
    user_id: UUID
    item_id: UUID


@dataclass
class CreateOrderDTO:
    """Create order DTO"""
    user_id: UUID


@dataclass
class ImportProductsDTO:
    """Import products DTO"""
    csv_content: str
    category_id: UUID


@dataclass
class PaginationDTO:
    """Pagination DTO"""
    page: int = 1
    page_size: int = 20


@dataclass
class SearchProductsDTO:
    """Search products DTO"""
    query: str
    pagination: PaginationDTO


@dataclass
class ResizeImageDTO:
    """Resize image DTO"""
    product_id: UUID
    image_data: bytes
    width: int
    height: int
