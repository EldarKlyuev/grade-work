"""Query services - Read side (CQRS)"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.application.dto import PaginationDTO, SearchProductsDTO
from src.app.domain.value_objects import Pagination
from src.app.infrastructure.persistence.models import (
    CartItemModel,
    CartModel,
    CategoryModel,
    OrderItemModel,
    OrderModel,
    ProductModel,
    UserModel,
)
from src.app.infrastructure.search import PostgresSearchService


@dataclass
class ProductReadModel:
    """Product read model"""
    id: UUID
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: UUID
    category_name: str
    created_at: datetime


@dataclass
class CategoryReadModel:
    """Category read model"""
    id: UUID
    name: str
    slug: str
    parent_id: UUID | None


@dataclass
class CartItemReadModel:
    """Cart item read model"""
    id: UUID
    product_id: UUID
    product_name: str
    product_price: Decimal
    quantity: int
    total_price: Decimal


@dataclass
class CartReadModel:
    """Cart read model"""
    id: UUID
    user_id: UUID
    items: list[CartItemReadModel]
    total_amount: Decimal


@dataclass
class OrderItemReadModel:
    """Order item read model"""
    id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass
class OrderReadModel:
    """Order read model"""
    id: UUID
    user_id: UUID
    items: list[OrderItemReadModel]
    total_amount: Decimal
    status: str
    created_at: datetime


@dataclass
class PaginatedResult:
    """Paginated result"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class ListProductsQueryService:
    """List products query service with pagination"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def __call__(
        self,
        pagination: PaginationDTO,
        category_id: UUID | None = None,
    ) -> PaginatedResult:
        """List products with pagination"""
        page = Pagination(pagination.page, pagination.page_size)
        
        stmt = select(ProductModel, CategoryModel).join(
            CategoryModel,
            ProductModel.category_id == CategoryModel.id,
        )
        
        if category_id:
            stmt = stmt.where(ProductModel.category_id == category_id)
        
        count_stmt = select(func.count()).select_from(ProductModel)
        if category_id:
            count_stmt = count_stmt.where(ProductModel.category_id == category_id)
        
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()
        
        stmt = stmt.order_by(ProductModel.created_at.desc()).offset(page.offset).limit(page.limit)
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        products = [
            ProductReadModel(
                id=product.id,
                name=product.name,
                description=product.description,
                price=product.price,
                stock=product.stock,
                category_id=product.category_id,
                category_name=category.name,
                created_at=product.created_at,
            )
            for product, category in rows
        ]
        
        return PaginatedResult(
            items=products,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )


class SearchProductsQueryService:
    """Search products query service"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.search_service = PostgresSearchService(session)
    
    async def __call__(self, data: SearchProductsDTO) -> PaginatedResult:
        """Search products using full-text search"""
        pagination = Pagination(data.pagination.page, data.pagination.page_size)
        
        products, total = await self.search_service.search_products(
            query=data.query,
            pagination=pagination,
        )
        
        product_models = []
        for product in products:
            stmt = select(CategoryModel).where(CategoryModel.id == product.category_id)
            result = await self.session.execute(stmt)
            category = result.scalar_one()
            
            product_models.append(
                ProductReadModel(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    stock=product.stock,
                    category_id=product.category_id,
                    category_name=category.name,
                    created_at=product.created_at,
                )
            )
        
        return PaginatedResult(
            items=product_models,
            total=total,
            page=data.pagination.page,
            page_size=data.pagination.page_size,
            total_pages=(total + data.pagination.page_size - 1) // data.pagination.page_size,
        )


class GetProductQueryService:
    """Get product query service"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def __call__(self, product_id: UUID) -> ProductReadModel | None:
        """Get product by ID"""
        stmt = select(ProductModel, CategoryModel).join(
            CategoryModel,
            ProductModel.category_id == CategoryModel.id,
        ).where(ProductModel.id == product_id)
        
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        
        if not row:
            return None
        
        product, category = row
        return ProductReadModel(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            category_id=product.category_id,
            category_name=category.name,
            created_at=product.created_at,
        )


class ListCategoriesQueryService:
    """List categories query service"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def __call__(self) -> list[CategoryReadModel]:
        """List all categories"""
        stmt = select(CategoryModel).order_by(CategoryModel.name)
        result = await self.session.execute(stmt)
        categories = result.scalars().all()
        
        return [
            CategoryReadModel(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                parent_id=cat.parent_id,
            )
            for cat in categories
        ]


class GetCartQueryService:
    """Get cart query service"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def __call__(self, user_id: UUID) -> CartReadModel | None:
        """Get cart for user"""
        stmt = select(CartModel).where(CartModel.user_id == user_id)
        result = await self.session.execute(stmt)
        cart = result.scalar_one_or_none()
        
        if not cart:
            return None
        
        items = []
        total_amount = Decimal("0.00")
        
        for item_model in cart.items:
            stmt = select(ProductModel).where(ProductModel.id == item_model.product_id)
            result = await self.session.execute(stmt)
            product = result.scalar_one()
            
            item_total = product.price * item_model.quantity
            total_amount += item_total
            
            items.append(
                CartItemReadModel(
                    id=item_model.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=item_model.quantity,
                    total_price=item_total,
                )
            )
        
        return CartReadModel(
            id=cart.id,
            user_id=cart.user_id,
            items=items,
            total_amount=total_amount,
        )


class ListOrdersQueryService:
    """List orders query service"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def __call__(self, user_id: UUID, pagination: PaginationDTO) -> PaginatedResult:
        """List orders for user"""
        page = Pagination(pagination.page, pagination.page_size)
        
        count_stmt = select(func.count()).select_from(OrderModel).where(
            OrderModel.user_id == user_id
        )
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()
        
        stmt = (
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset(page.offset)
            .limit(page.limit)
        )
        
        result = await self.session.execute(stmt)
        orders = result.scalars().all()
        
        order_models = []
        for order in orders:
            items = []
            for item_model in order.items:
                stmt = select(ProductModel).where(ProductModel.id == item_model.product_id)
                result = await self.session.execute(stmt)
                product = result.scalar_one()
                
                items.append(
                    OrderItemReadModel(
                        id=item_model.id,
                        product_id=product.id,
                        product_name=product.name,
                        quantity=item_model.quantity,
                        unit_price=item_model.unit_price,
                        total_price=item_model.unit_price * item_model.quantity,
                    )
                )
            
            order_models.append(
                OrderReadModel(
                    id=order.id,
                    user_id=order.user_id,
                    items=items,
                    total_amount=order.total_amount,
                    status=order.status,
                    created_at=order.created_at,
                )
            )
        
        return PaginatedResult(
            items=order_models,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )
