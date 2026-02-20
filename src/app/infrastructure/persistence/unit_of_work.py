"""Unit of work implementation"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.ports import UnitOfWorkPort


class UnitOfWork(UnitOfWorkPort):
    """SQLAlchemy unit of work implementation"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def begin(self) -> None:
        """Begin transaction"""
        pass
    
    async def commit(self) -> None:
        """Commit transaction"""
        await self.session.commit()
    
    async def rollback(self) -> None:
        """Rollback transaction"""
        await self.session.rollback()
    
    async def __aenter__(self) -> "UnitOfWork":
        """Enter context manager"""
        await self.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager"""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
