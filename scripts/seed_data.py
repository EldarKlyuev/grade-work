"""Test data seeder"""

import sys
import asyncio
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.entities import Category, Product, User
from src.app.domain.value_objects import Email, Money, Password
from src.app.infrastructure.persistence.database import async_session_maker
from src.app.infrastructure.persistence.repositories import (
    CategoryRepository,
    ProductRepository,
    UserRepository,
)
from src.app.infrastructure.security import PasswordHasher


async def seed_data() -> None:
    """Seed database with sample data"""
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        category_repo = CategoryRepository(session)
        product_repo = ProductRepository(session)
        hasher = PasswordHasher()
        
        print("Creating sample user...")
        user = User.create(
            email=Email("admin@example.com"),
            password_hash=hasher.hash_password("Admin123!"),
            username="admin",
        )
        await user_repo.save(user)
        
        print("Creating categories...")
        electronics = Category.create(
            name="Electronics",
            slug="electronics",
        )
        await category_repo.save(electronics)
        
        clothing = Category.create(
            name="Clothing",
            slug="clothing",
        )
        await category_repo.save(clothing)
        
        books = Category.create(
            name="Books",
            slug="books",
        )
        await category_repo.save(books)
        
        print("Creating products...")
        products = [
            Product.create(
                name="Laptop",
                description="High-performance laptop for work and gaming",
                price=Money(Decimal("1299.99")),
                stock=10,
                category_id=electronics.id,
            ),
            Product.create(
                name="Smartphone",
                description="Latest smartphone with advanced features",
                price=Money(Decimal("899.99")),
                stock=25,
                category_id=electronics.id,
            ),
            Product.create(
                name="Headphones",
                description="Wireless noise-cancelling headphones",
                price=Money(Decimal("199.99")),
                stock=50,
                category_id=electronics.id,
            ),
            Product.create(
                name="T-Shirt",
                description="Comfortable cotton t-shirt",
                price=Money(Decimal("29.99")),
                stock=100,
                category_id=clothing.id,
            ),
            Product.create(
                name="Jeans",
                description="Classic blue jeans",
                price=Money(Decimal("59.99")),
                stock=75,
                category_id=clothing.id,
            ),
            Product.create(
                name="Python Programming Book",
                description="Learn Python programming from scratch",
                price=Money(Decimal("39.99")),
                stock=30,
                category_id=books.id,
            ),
            Product.create(
                name="Clean Architecture Book",
                description="Software architecture patterns and best practices",
                price=Money(Decimal("44.99")),
                stock=20,
                category_id=books.id,
            ),
        ]
        
        await product_repo.save_many(products)
        
        await session.commit()
        print("✓ Sample data created successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
