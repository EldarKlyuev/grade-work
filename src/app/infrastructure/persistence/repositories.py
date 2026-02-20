"""Реализации репозиториев для работы с базой данных.

Содержит SQL-адаптеры для доменных портов репозиториев.
Использует SQLAlchemy для взаимодействия с PostgreSQL.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.domain.entities import (
    Cart,
    Category,
    Order,
    PasswordResetToken,
    Product,
    User,
)
from src.app.domain.ports import (
    CartRepositoryPort,
    CategoryRepositoryPort,
    OrderRepositoryPort,
    PasswordResetTokenRepositoryPort,
    ProductRepositoryPort,
    UserRepositoryPort,
)
from src.app.domain.value_objects import Email
from src.app.infrastructure.persistence.mappers import (
    CartMapper,
    CategoryMapper,
    OrderMapper,
    PasswordResetTokenMapper,
    ProductMapper,
    UserMapper,
)
from src.app.infrastructure.persistence.models import (
    CartModel,
    CategoryModel,
    OrderModel,
    PasswordResetTokenModel,
    ProductModel,
    UserModel,
)


class UserRepository(UserRepositoryPort):
    """User repository implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None
    
    async def find_by_email(self, email: Email) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email.value)
        )
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None
    
    async def save(self, user: User) -> None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.email = user.email.value
            existing.password_hash = user.password_hash
            existing.username = user.username
            existing.is_active = user.is_active
        else:
            model = UserMapper.to_model(user)
            self.session.add(model)
    
    async def exists_by_email(self, email: Email) -> bool:
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email.value)
        )
        return result.scalar_one_or_none() is not None


class ProductRepository(ProductRepositoryPort):
    """Product repository implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def find_by_id(self, product_id: UUID) -> Product | None:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        return ProductMapper.to_domain(model) if model else None
    
    async def save(self, product: Product) -> None:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.name = product.name
            existing.description = product.description
            existing.price = product.price.amount
            existing.stock = product.stock
            existing.category_id = product.category_id
        else:
            model = ProductMapper.to_model(product)
            self.session.add(model)
    
    async def save_many(self, products: list[Product]) -> None:
        for product in products:
            await self.save(product)


class CategoryRepository(CategoryRepositoryPort):
    """Category repository implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def find_by_id(self, category_id: UUID) -> Category | None:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id)
        )
        model = result.scalar_one_or_none()
        return CategoryMapper.to_domain(model) if model else None
    
    async def find_by_slug(self, slug: str) -> Category | None:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return CategoryMapper.to_domain(model) if model else None
    
    async def save(self, category: Category) -> None:
        result = await self.session.execute(
            select(CategoryModel).where(CategoryModel.id == category.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.name = category.name
            existing.slug = category.slug
            existing.parent_id = category.parent_id
        else:
            model = CategoryMapper.to_model(category)
            self.session.add(model)


class CartRepository(CartRepositoryPort):
    """Cart repository implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def find_by_user_id(self, user_id: UUID) -> Cart | None:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.user_id == user_id)
            .options(selectinload(CartModel.items))
        )
        model = result.scalar_one_or_none()
        return CartMapper.to_domain(model) if model else None
    
    async def save(self, cart: Cart) -> None:
        result = await self.session.execute(
            select(CartModel)
            .where(CartModel.id == cart.id)
            .options(selectinload(CartModel.items))
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            await self.session.delete(existing)
            await self.session.flush()
        
        model = CartMapper.to_model(cart)
        self.session.add(model)
    
    async def delete(self, cart: Cart) -> None:
        result = await self.session.execute(
            select(CartModel).where(CartModel.id == cart.id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)


class OrderRepository(OrderRepositoryPort):
    """Order repository implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def find_by_id(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items))
        )
        model = result.scalar_one_or_none()
        return OrderMapper.to_domain(model) if model else None
    
    async def save(self, order: Order) -> None:
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.id == order.id)
            .options(selectinload(OrderModel.items))
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.status = order.status.value
            existing.total_amount = order.total_amount.amount
        else:
            model = OrderMapper.to_model(order)
            self.session.add(model)


class PasswordResetTokenRepository(PasswordResetTokenRepositoryPort):
    """Password reset token repository implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def find_by_token(self, token: str) -> PasswordResetToken | None:
        result = await self.session.execute(
            select(PasswordResetTokenModel).where(PasswordResetTokenModel.token == token)
        )
        model = result.scalar_one_or_none()
        return PasswordResetTokenMapper.to_domain(model) if model else None
    
    async def save(self, token: PasswordResetToken) -> None:
        result = await self.session.execute(
            select(PasswordResetTokenModel).where(PasswordResetTokenModel.id == token.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.used = token.used
        else:
            model = PasswordResetTokenMapper.to_model(token)
            self.session.add(model)
