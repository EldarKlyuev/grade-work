"""Mappers - convert between domain entities and SQLAlchemy models"""

from decimal import Decimal

from src.app.domain.entities import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    OrderStatus,
    PasswordResetToken,
    Product,
    User,
)
from src.app.domain.value_objects import Email, Money
from src.app.infrastructure.persistence.models import (
    CartItemModel,
    CartModel,
    CategoryModel,
    OrderItemModel,
    OrderModel,
    PasswordResetTokenModel,
    ProductModel,
    UserModel,
)


class UserMapper:
    """Map between User entity and UserModel"""
    
    @staticmethod
    def to_domain(model: UserModel) -> User:
        """Convert model to domain entity"""
        return User(
            id=model.id,
            email=Email(model.email),
            password_hash=model.password_hash,
            username=model.username,
            is_active=model.is_active,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Convert domain entity to model"""
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            password_hash=entity.password_hash,
            username=entity.username,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )


class CategoryMapper:
    """Map between Category entity and CategoryModel"""
    
    @staticmethod
    def to_domain(model: CategoryModel) -> Category:
        """Convert model to domain entity"""
        return Category(
            id=model.id,
            name=model.name,
            slug=model.slug,
            parent_id=model.parent_id,
        )
    
    @staticmethod
    def to_model(entity: Category) -> CategoryModel:
        """Convert domain entity to model"""
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            slug=entity.slug,
            parent_id=entity.parent_id,
        )


class ProductMapper:
    """Map between Product entity and ProductModel"""
    
    @staticmethod
    def to_domain(model: ProductModel) -> Product:
        """Convert model to domain entity"""
        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            price=Money(model.price),
            stock=model.stock,
            category_id=model.category_id,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: Product) -> ProductModel:
        """Convert domain entity to model"""
        return ProductModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            price=entity.price.amount,
            stock=entity.stock,
            category_id=entity.category_id,
            created_at=entity.created_at,
        )


class CartItemMapper:
    """Map between CartItem entity and CartItemModel"""
    
    @staticmethod
    def to_domain(model: CartItemModel) -> CartItem:
        """Convert model to domain entity"""
        return CartItem(
            id=model.id,
            cart_id=model.cart_id,
            product_id=model.product_id,
            quantity=model.quantity,
        )
    
    @staticmethod
    def to_model(entity: CartItem) -> CartItemModel:
        """Convert domain entity to model"""
        return CartItemModel(
            id=entity.id,
            cart_id=entity.cart_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
        )


class CartMapper:
    """Map between Cart entity and CartModel"""
    
    @staticmethod
    def to_domain(model: CartModel) -> Cart:
        """Convert model to domain entity"""
        items = [CartItemMapper.to_domain(item) for item in model.items]
        return Cart(
            id=model.id,
            user_id=model.user_id,
            items=items,
        )
    
    @staticmethod
    def to_model(entity: Cart) -> CartModel:
        """Convert domain entity to model"""
        model = CartModel(
            id=entity.id,
            user_id=entity.user_id,
        )
        model.items = [CartItemMapper.to_model(item) for item in entity.items]
        return model


class OrderItemMapper:
    """Map between OrderItem entity and OrderItemModel"""
    
    @staticmethod
    def to_domain(model: OrderItemModel) -> OrderItem:
        """Convert model to domain entity"""
        return OrderItem(
            id=model.id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=model.quantity,
            unit_price=Money(model.unit_price),
        )
    
    @staticmethod
    def to_model(entity: OrderItem) -> OrderItemModel:
        """Convert domain entity to model"""
        return OrderItemModel(
            id=entity.id,
            order_id=entity.order_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            unit_price=entity.unit_price.amount,
        )


class OrderMapper:
    """Map between Order entity and OrderModel"""
    
    @staticmethod
    def to_domain(model: OrderModel) -> Order:
        """Convert model to domain entity"""
        items = [OrderItemMapper.to_domain(item) for item in model.items]
        return Order(
            id=model.id,
            user_id=model.user_id,
            items=items,
            total_amount=Money(model.total_amount),
            status=OrderStatus(model.status),
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: Order) -> OrderModel:
        """Convert domain entity to model"""
        model = OrderModel(
            id=entity.id,
            user_id=entity.user_id,
            total_amount=entity.total_amount.amount,
            status=entity.status.value,
            created_at=entity.created_at,
        )
        model.items = [OrderItemMapper.to_model(item) for item in entity.items]
        return model


class PasswordResetTokenMapper:
    """Map between PasswordResetToken entity and PasswordResetTokenModel"""
    
    @staticmethod
    def to_domain(model: PasswordResetTokenModel) -> PasswordResetToken:
        """Convert model to domain entity"""
        return PasswordResetToken(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            expires_at=model.expires_at,
            used=model.used,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: PasswordResetToken) -> PasswordResetTokenModel:
        """Convert domain entity to model"""
        return PasswordResetTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            token=entity.token,
            expires_at=entity.expires_at,
            used=entity.used,
            created_at=entity.created_at,
        )
