"""CSV importer with generator pattern"""

import csv
from collections.abc import Generator
from decimal import Decimal
from io import StringIO
from pathlib import Path
from typing import Any
from uuid import UUID

from src.app.domain.entities import Product
from src.app.domain.value_objects import Money


def read_csv_rows(file_path: Path) -> Generator[dict[str, str], None, None]:
    """
    Generator to read CSV file row by row
    
    Args:
        file_path: Path to CSV file
        
    Yields:
        Dictionary for each row
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def read_csv_from_string(csv_content: str) -> Generator[dict[str, str], None, None]:
    """
    Generator to read CSV from string
    
    Args:
        csv_content: CSV content as string
        
    Yields:
        Dictionary for each row
    """
    f = StringIO(csv_content)
    reader = csv.DictReader(f)
    for row in reader:
        yield row


def parse_product_from_csv_row(row: dict[str, str], category_id: UUID) -> Product:
    """
    Parse Product entity from CSV row
    
    Args:
        row: CSV row as dictionary
        category_id: Category ID for the product
        
    Returns:
        Product entity
        
    Expected CSV columns:
        - name: Product name
        - description: Product description
        - price: Product price (decimal)
        - stock: Stock quantity (integer)
    """
    return Product.create(
        name=row['name'],
        description=row['description'],
        price=Money(Decimal(row['price'])),
        stock=int(row['stock']),
        category_id=category_id,
    )


def products_from_csv_generator(
    csv_content: str,
    category_id: UUID,
) -> Generator[Product, None, None]:
    """
    Generator that yields Product entities from CSV content
    
    Args:
        csv_content: CSV content as string
        category_id: Category ID for products
        
    Yields:
        Product entities
    """
    for row in read_csv_from_string(csv_content):
        yield parse_product_from_csv_row(row, category_id)


def batch_generator(
    items: list[Any],
    batch_size: int,
) -> Generator[list[Any], None, None]:
    """
    Generator that yields items in batches
    
    Args:
        items: List of items
        batch_size: Size of each batch
        
    Yields:
        Batches of items
        
    Example:
        >>> list(batch_generator([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def infinite_id_generator(start: int = 1) -> Generator[int, None, None]:
    """
    Infinite generator for ID sequence
    
    Args:
        start: Starting number
        
    Yields:
        Sequential integers
        
    Example:
        >>> gen = infinite_id_generator()
        >>> next(gen)
        1
        >>> next(gen)
        2
    """
    current = start
    while True:
        yield current
        current += 1


def fibonacci_generator(limit: int) -> Generator[int, None, None]:
    """
    Generator for Fibonacci sequence up to limit
    
    Args:
        limit: Maximum value
        
    Yields:
        Fibonacci numbers
        
    Example:
        >>> list(fibonacci_generator(100))
        [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    """
    a, b = 0, 1
    while a <= limit:
        yield a
        a, b = b, a + b
