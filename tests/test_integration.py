"""Интеграционные тесты для API.

Тесты проверяют основные пользовательские сценарии через HTTP API.
"""

import pytest
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.app.main import create_app
from src.app.infrastructure.persistence.models import Base
from config.settings import settings


@pytest.fixture
async def test_engine():
    """Создать тестовую БД."""
    test_db_url = settings.database_url.replace("/grade_work", "/grade_work_test")
    engine = create_async_engine(test_db_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def client(test_engine):
    """Создать тестовый HTTP клиент."""
    app = create_app()
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    """Тест регистрации и входа пользователя.
    
    Сценарий:
    1. Регистрация нового пользователя
    2. Вход в систему с учетными данными
    3. Проверка получения JWT токена
    """
    # Шаг 1: Регистрация
    registration_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    }
    
    response = await client.post("/api/auth/register", json=registration_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    user_id = data["id"]
    assert user_id is not None
    
    # Шаг 2: Вход в систему
    login_data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Шаг 3: Проверка токена
    token = data["access_token"]
    assert len(token) > 0


@pytest.mark.asyncio
async def test_product_catalog_workflow(client: AsyncClient):
    """Тест работы с каталогом товаров.
    
    Сценарий:
    1. Создание категории
    2. Добавление товара в категорию
    3. Получение списка товаров
    4. Поиск товара по названию
    """
    # Регистрация и вход для получения токена
    await client.post("/api/auth/register", json={
        "email": "admin@example.com",
        "username": "admin",
        "password": "AdminPass123!"
    })
    
    login_response = await client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "AdminPass123!"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Шаг 1: Создание категории
    category_data = {
        "name": "Электроника",
        "slug": "electronics"
    }
    
    response = await client.post(
        "/api/categories",
        json=category_data,
        headers=headers
    )
    assert response.status_code == 201
    category_id = response.json()["id"]
    
    # Шаг 2: Добавление товара
    product_data = {
        "name": "Смартфон Samsung Galaxy",
        "description": "Флагманский смартфон с отличной камерой",
        "price": 49999.99,
        "stock": 10,
        "category_id": category_id
    }
    
    response = await client.post(
        "/api/products",
        json=product_data,
        headers=headers
    )
    assert response.status_code == 201
    product = response.json()
    assert product["name"] == "Смартфон Samsung Galaxy"
    assert float(product["price"]) == 49999.99
    
    # Шаг 3: Получение списка товаров
    response = await client.get("/api/products?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["items"][0]["name"] == "Смартфон Samsung Galaxy"
    
    # Шаг 4: Поиск товара
    response = await client.get("/api/products/search?query=Samsung&page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert "Samsung" in data["items"][0]["name"]


@pytest.mark.asyncio
async def test_shopping_cart_and_order_creation(client: AsyncClient):
    """Тест создания заказа через корзину.
    
    Сценарий:
    1. Регистрация пользователя
    2. Создание категории и товаров
    3. Добавление товаров в корзину
    4. Просмотр корзины
    5. Оформление заказа
    6. Проверка списка заказов
    """
    # Шаг 1: Регистрация пользователя
    await client.post("/api/auth/register", json={
        "email": "customer@example.com",
        "username": "customer",
        "password": "Customer123!"
    })
    
    login_response = await client.post("/api/auth/login", json={
        "email": "customer@example.com",
        "password": "Customer123!"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Шаг 2: Создание категории и товаров
    category_response = await client.post(
        "/api/categories",
        json={"name": "Книги", "slug": "books"},
        headers=headers
    )
    category_id = category_response.json()["id"]
    
    # Добавляем первый товар
    product1_response = await client.post(
        "/api/products",
        json={
            "name": "Python для начинающих",
            "description": "Отличная книга для изучения Python",
            "price": 1500.00,
            "stock": 50,
            "category_id": category_id
        },
        headers=headers
    )
    product1_id = product1_response.json()["id"]
    
    # Добавляем второй товар
    product2_response = await client.post(
        "/api/products",
        json={
            "name": "Clean Architecture",
            "description": "Книга о чистой архитектуре",
            "price": 2000.00,
            "stock": 30,
            "category_id": category_id
        },
        headers=headers
    )
    product2_id = product2_response.json()["id"]
    
    # Шаг 3: Добавление товаров в корзину
    response = await client.post(
        "/api/cart/items",
        json={"product_id": product1_id, "quantity": 2},
        headers=headers
    )
    assert response.status_code == 201
    
    response = await client.post(
        "/api/cart/items",
        json={"product_id": product2_id, "quantity": 1},
        headers=headers
    )
    assert response.status_code == 201
    
    # Шаг 4: Просмотр корзины
    response = await client.get("/api/cart", headers=headers)
    assert response.status_code == 200
    cart = response.json()
    assert len(cart["items"]) == 2
    
    # Проверяем общую сумму: 2 * 1500 + 1 * 2000 = 5000
    expected_total = 2 * 1500.00 + 1 * 2000.00
    assert float(cart["total_amount"]) == expected_total
    
    # Шаг 5: Оформление заказа
    response = await client.post("/api/orders", headers=headers)
    assert response.status_code == 201
    order = response.json()
    assert "id" in order
    order_id = order["id"]
    
    # Проверяем, что корзина очистилась
    response = await client.get("/api/cart", headers=headers)
    cart_after_order = response.json()
    assert len(cart_after_order.get("items", [])) == 0 or cart_after_order is None
    
    # Шаг 6: Проверка списка заказов
    response = await client.get("/api/orders?page=1&page_size=10", headers=headers)
    assert response.status_code == 200
    orders = response.json()
    assert orders["total"] >= 1
    assert len(orders["items"]) >= 1
    
    # Проверяем детали заказа
    order_item = orders["items"][0]
    assert order_item["id"] == order_id
    assert order_item["status"] == "pending"
    assert float(order_item["total_amount"]) == expected_total
    assert len(order_item["items"]) == 2
