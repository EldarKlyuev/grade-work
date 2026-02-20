"""PostgreSQL full-text search service"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.value_objects import Pagination
from src.app.infrastructure.persistence.models import ProductModel


class PostgresSearchService:
    """PostgreSQL full-text search implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def search_products(
        self,
        query: str,
        pagination: Pagination,
    ) -> tuple[list[ProductModel], int]:
        """
        Search products using PostgreSQL full-text search
        
        Args:
            query: Search query string
            pagination: Pagination parameters
            
        Returns:
            Tuple of (products list, total count)
        """
        tsquery = func.plainto_tsquery('english', query)
        
        search_filter = ProductModel.search_vector.op('@@')(tsquery)
        
        count_stmt = select(func.count()).select_from(ProductModel).where(search_filter)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()
        
        rank = func.ts_rank(ProductModel.search_vector, tsquery).label('rank')
        
        stmt = (
            select(ProductModel)
            .where(search_filter)
            .order_by(rank.desc())
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        
        result = await self.session.execute(stmt)
        products = result.scalars().all()
        
        return list(products), total
    
    async def update_search_vector(self, product_id: UUID) -> None:
        """Manually update search vector for a product"""
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self.session.execute(stmt)
        product = result.scalar_one_or_none()
        
        if product:
            await self.session.execute(
                ProductModel.__table__.update()
                .where(ProductModel.id == product_id)
                .values(
                    search_vector=func.to_tsvector(
                        'english',
                        func.concat(product.name, ' ', product.description)
                    )
                )
            )
