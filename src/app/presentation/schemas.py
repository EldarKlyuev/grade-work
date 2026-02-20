"""Pydantic schemas - Request and response models with validation"""

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


class CreateUserRequest(BaseModel):
    """Create user request"""
    email: EmailStr
    password: SecretStr = Field(min_length=8)
    username: str = Field(min_length=3, max_length=50)
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: SecretStr) -> SecretStr:
        """Validate password has required complexity"""
        password = v.get_secret_value()
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
            raise ValueError("Password must contain at least one special character")
        
        return v
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: SecretStr


class PasswordResetRequestRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirm request"""
    token: str
    new_password: SecretStr = Field(min_length=8)
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: SecretStr) -> SecretStr:
        """Validate password has required complexity"""
        password = v.get_secret_value()
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
            raise ValueError("Password must contain at least one special character")
        
        return v


class UserResponse(BaseModel):
    """User response"""
    id: UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class ProductResponse(BaseModel):
    """Product response"""
    id: UUID
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: UUID
    category_name: str
    created_at: datetime


class ProductListResponse(BaseModel):
    """Product list response"""
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoryResponse(BaseModel):
    """Category response"""
    id: UUID
    name: str
    slug: str
    parent_id: UUID | None


class AddToCartRequest(BaseModel):
    """Add to cart request"""
    product_id: UUID
    quantity: int = Field(gt=0, le=100)


class CartItemResponse(BaseModel):
    """Cart item response"""
    id: UUID
    product_id: UUID
    product_name: str
    product_price: Decimal
    quantity: int
    total_price: Decimal


class CartResponse(BaseModel):
    """Cart response"""
    id: UUID
    user_id: UUID
    items: list[CartItemResponse]
    total_amount: Decimal


class OrderItemResponse(BaseModel):
    """Order item response"""
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderResponse(BaseModel):
    """Order response"""
    id: UUID
    user_id: UUID
    items: list[OrderItemResponse]
    total_amount: Decimal
    status: str
    created_at: datetime


class OrderListResponse(BaseModel):
    """Order list response"""
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ImportProductsRequest(BaseModel):
    """Import products request"""
    csv_content: str
    category_id: UUID


class ResizeImageRequest(BaseModel):
    """Resize image request"""
    width: int = Field(gt=0, le=4000)
    height: int = Field(gt=0, le=4000)
    maintain_aspect_ratio: bool = True


class Base64EncodeRequest(BaseModel):
    """Base64 encode request"""
    data: str


class Base64DecodeRequest(BaseModel):
    """Base64 decode request"""
    encoded_data: str


class JsonToYamlRequest(BaseModel):
    """JSON to YAML request"""
    json_data: str


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
