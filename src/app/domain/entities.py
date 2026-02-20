"""Domain entities - objects with identity"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from src.app.domain.exceptions import InsufficientStockError
from src.app.domain.value_objects import Email, Money


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class User:
    """User entity"""
    
    id: UUID
    email: Email
    password_hash: str
    username: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        email: Email,
        password_hash: str,
        username: str,
    ) -> "User":
        """Factory method to create a new user"""
        return cls(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            username=username,
        )


@dataclass
class Category:
    """Category entity with self-referencing hierarchy"""
    
    id: UUID
    name: str
    slug: str
    parent_id: UUID | None = None
    
    @classmethod
    def create(cls, name: str, slug: str, parent_id: UUID | None = None) -> "Category":
        """Factory method to create a new category"""
        return cls(
            id=uuid4(),
            name=name,
            slug=slug,
            parent_id=parent_id,
        )


@dataclass
class Product:
    """Product entity"""
    
    id: UUID
    name: str
    description: str
    price: Money
    stock: int
    category_id: UUID
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        price: Money,
        stock: int,
        category_id: UUID,
    ) -> "Product":
        """Factory method to create a new product"""
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )
    
    def decrease_stock(self, quantity: int) -> None:
        """Decrease product stock"""
        if self.stock < quantity:
            raise InsufficientStockError(str(self.id), quantity, self.stock)
        self.stock -= quantity
    
    def increase_stock(self, quantity: int) -> None:
        """Increase product stock"""
        self.stock += quantity


@dataclass
class CartItem:
    """Cart item entity"""
    
    id: UUID
    cart_id: UUID
    product_id: UUID
    quantity: int
    
    @classmethod
    def create(cls, cart_id: UUID, product_id: UUID, quantity: int) -> "CartItem":
        """Factory method to create a new cart item"""
        return cls(
            id=uuid4(),
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )
    
    def update_quantity(self, quantity: int) -> None:
        """Update item quantity"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.quantity = quantity


@dataclass
class Cart:
    """Cart entity"""
    
    id: UUID
    user_id: UUID
    items: list[CartItem] = field(default_factory=list)
    
    @classmethod
    def create(cls, user_id: UUID) -> "Cart":
        """Factory method to create a new cart"""
        return cls(
            id=uuid4(),
            user_id=user_id,
        )
    
    def add_item(self, product_id: UUID, quantity: int) -> None:
        """Add item to cart or update quantity if exists"""
        for item in self.items:
            if item.product_id == product_id:
                item.update_quantity(item.quantity + quantity)
                return
        
        self.items.append(CartItem.create(self.id, product_id, quantity))
    
    def remove_item(self, item_id: UUID) -> None:
        """Remove item from cart"""
        self.items = [item for item in self.items if item.id != item_id]
    
    def clear(self) -> None:
        """Clear all items from cart"""
        self.items.clear()


@dataclass
class OrderItem:
    """Order item entity"""
    
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Money
    
    @classmethod
    def create(
        cls,
        order_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_price: Money,
    ) -> "OrderItem":
        """Factory method to create a new order item"""
        return cls(
            id=uuid4(),
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
    
    @property
    def total_price(self) -> Money:
        """Calculate total price for this item"""
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Order entity"""
    
    id: UUID
    user_id: UUID
    items: list[OrderItem]
    total_amount: Money
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create_from_cart(
        cls,
        user_id: UUID,
        cart_items: list[tuple[UUID, int, Money]],
    ) -> "Order":
        """Factory method to create order from cart items"""
        order_id = uuid4()
        items = [
            OrderItem.create(order_id, product_id, quantity, unit_price)
            for product_id, quantity, unit_price in cart_items
        ]
        
        total = Money.zero()
        for item in items:
            total = total + item.total_price
        
        return cls(
            id=order_id,
            user_id=user_id,
            items=items,
            total_amount=total,
        )
    
    def mark_as_paid(self) -> None:
        """Mark order as paid"""
        self.status = OrderStatus.PAID
    
    def mark_as_shipped(self) -> None:
        """Mark order as shipped"""
        if self.status != OrderStatus.PAID:
            raise ValueError("Order must be paid before shipping")
        self.status = OrderStatus.SHIPPED
    
    def mark_as_delivered(self) -> None:
        """Mark order as delivered"""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Order must be shipped before delivery")
        self.status = OrderStatus.DELIVERED
    
    def cancel(self) -> None:
        """Cancel order"""
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError("Cannot cancel shipped or delivered orders")
        self.status = OrderStatus.CANCELLED


@dataclass
class PasswordResetToken:
    """Password reset token entity"""
    
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(cls, user_id: UUID, token: str, expires_at: datetime) -> "PasswordResetToken":
        """Factory method to create a new password reset token"""
        return cls(
            id=uuid4(),
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def mark_as_used(self) -> None:
        """Mark token as used"""
        self.used = True
