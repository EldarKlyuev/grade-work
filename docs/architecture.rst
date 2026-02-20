Архитектура проекта
===================

grade-work построен на принципах **Clean Architecture** с использованием паттернов **CQRS** (Command Query Responsibility Segregation) и тактических паттернов **Domain-Driven Design** (DDD).

Обзор архитектуры
-----------------

Проект организован в виде концентрических слоев, где зависимости направлены от внешних слоев к внутренним:

.. code-block:: text

    ┌─────────────────────────────────────────┐
    │     Presentation Layer (API)            │
    │  ┌───────────────────────────────────┐  │
    │  │   Infrastructure Layer            │  │
    │  │  ┌─────────────────────────────┐  │  │
    │  │  │  Application Layer          │  │  │
    │  │  │  ┌───────────────────────┐  │  │  │
    │  │  │  │   Domain Layer        │  │  │  │
    │  │  │  │   (Business Logic)    │  │  │  │
    │  │  │  └───────────────────────┘  │  │  │
    │  │  └─────────────────────────────┘  │  │
    │  └───────────────────────────────────┘  │
    └─────────────────────────────────────────┘

Правило зависимостей
--------------------

**Зависимости всегда направлены внутрь.** Внутренние слои не знают о существовании внешних:

* **Domain Layer** не зависит ни от чего
* **Application Layer** зависит только от Domain
* **Infrastructure Layer** зависит от Domain и Application
* **Presentation Layer** зависит от всех остальных слоев

Слои архитектуры
----------------

Domain Layer (Доменный слой)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Расположение: ``src/app/domain/``

Содержит ядро бизнес-логики приложения:

* **Entities** (Сущности) — объекты с идентификатором:
  
  * ``User`` — пользователь системы
  * ``Product`` — товар
  * ``Category`` — категория товаров
  * ``Cart`` — корзина покупок
  * ``Order`` — заказ

* **Value Objects** (Объекты-значения) — неизменяемые объекты без идентификатора:
  
  * ``Email`` — email с валидацией
  * ``Password`` — пароль с проверкой сложности
  * ``Money`` — денежная сумма с точностью
  * ``Pagination`` — параметры пагинации

* **Domain Services** — сложная бизнес-логика, которая не относится к конкретной сущности

* **Ports** (Порты) — интерфейсы для внешних зависимостей:
  
  * ``UserRepositoryPort`` — интерфейс репозитория пользователей
  * ``ProductRepositoryPort`` — интерфейс репозитория товаров
  * ``UnitOfWorkPort`` — интерфейс для управления транзакциями

* **Exceptions** — доменные исключения

**Принципы:**

* Не содержит зависимостей от фреймворков
* Независим от баз данных, UI, внешних сервисов
* Содержит чистую бизнес-логику

Application Layer (Слой приложения)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Расположение: ``src/app/application/``

Оркеструет бизнес-логику и реализует use cases:

* **Interactors** (Интеракторы) — обработчики команд (CQRS):
  
  * ``RegisterUserInteractor`` — регистрация пользователя
  * ``LoginUserInteractor`` — вход в систему
  * ``AddToCartInteractor`` — добавление товара в корзину
  * ``CreateOrderInteractor`` — создание заказа

* **Query Services** — обработчики запросов (CQRS):
  
  * ``ListProductsQueryService`` — получение списка товаров
  * ``SearchProductsQueryService`` — поиск товаров
  * ``GetCartQueryService`` — получение корзины пользователя

* **DTOs** (Data Transfer Objects) — объекты для передачи данных между слоями

* **Application Ports** — интерфейсы для внешних сервисов:
  
  * ``EmailGatewayPort`` — отправка email
  * ``TokenServicePort`` — работа с JWT токенами
  * ``PasswordHasherPort`` — хеширование паролей

**Принципы:**

* Интеракторы stateless и не вызывают друг друга
* Один интерактор = одна бизнес-операция
* Использует порты для внешних зависимостей

Infrastructure Layer (Инфраструктурный слой)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Расположение: ``src/app/infrastructure/``

Реализует технические детали и адаптеры для внешних систем:

* **Repositories** — имплементации портов репозиториев:
  
  * ``SqlUserRepository`` — работа с пользователями в PostgreSQL
  * ``SqlProductRepository`` — работа с товарами

* **Services** — имплементации портов сервисов:
  
  * ``JWTTokenService`` — генерация и валидация JWT токенов
  * ``BcryptPasswordHasher`` — хеширование паролей с bcrypt
  * ``SmtpEmailService`` — отправка email через SMTP

* **Persistence** — работа с базой данных:
  
  * ``models.py`` — SQLAlchemy модели
  * ``mappers.py`` — маппинг между доменными сущностями и моделями БД
  * ``database.py`` — настройка подключения к БД

* **Utils** — утилиты (импорт CSV, обработка изображений и т.д.)

**Принципы:**

* Реализует интерфейсы, определенные в Domain/Application
* Не содержит бизнес-логики
* Изолирует технические детали от бизнес-логики

Presentation Layer (Слой представления)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Расположение: ``src/app/presentation/``

Обрабатывает HTTP запросы и ответы:

* **API Routers** — FastAPI роутеры:
  
  * ``auth.py`` — эндпоинты аутентификации
  * ``products.py`` — управление товарами
  * ``cart.py`` — операции с корзиной
  * ``orders.py`` — управление заказами

* **Schemas** — Pydantic модели для валидации:
  
  * Request schemas — валидация входящих данных
  * Response schemas — форматирование ответов

* **Dependencies** — FastAPI зависимости
* **Middleware** — промежуточное ПО

**Принципы:**

* Только HTTP-логика, никакой бизнес-логики
* Использует Dishka для DI вместо FastAPI Depends
* Валидация структуры данных (не бизнес-правил)

CQRS Pattern
------------

Проект разделяет команды (изменения) и запросы (чтения):

Команды (Commands)
~~~~~~~~~~~~~~~~~~

Обрабатываются **Interactors**:

* Изменяют состояние системы
* Используют полные доменные модели
* Возвращают минимум данных (обычно ID)
* Проходят через Unit of Work для транзакций

Пример:

.. code-block:: python

    class CreateOrderInteractor:
        async def __call__(self, data: CreateOrderDTO) -> UUID:
            # Бизнес-логика создания заказа
            order = Order.create_from_cart(...)
            await self.order_repository.save(order)
            await self.uow.commit()
            return order.id

Запросы (Queries)
~~~~~~~~~~~~~~~~~

Обрабатываются **Query Services**:

* Только чтение данных
* Используют оптимизированные read models
* Могут обращаться напрямую к БД (минуя домен)
* Поддерживают пагинацию и фильтрацию

Пример:

.. code-block:: python

    class ListProductsQueryService:
        async def __call__(self, pagination: PaginationDTO) -> PaginatedResult:
            # Оптимизированный запрос для чтения
            products = await self.session.execute(...)
            return PaginatedResult(items=products, ...)

Dependency Injection
--------------------

Проект использует **Dishka** для внедрения зависимостей вместо FastAPI's ``Depends``:

.. code-block:: python

    # ❌ Плохо - утечка FastAPI в application layer
    class CreateUserInteractor:
        def __init__(self, session: Session = Depends(get_session)):
            ...

    # ✅ Хорошо - чистая DI без привязки к фреймворку
    class CreateUserInteractor:
        def __init__(self, user_gateway: UserGatewayPort):
            ...

    # В presentation layer используем Dishka
    @router.post("/users")
    async def create_user(interactor: FromDishka[CreateUserInteractor]):
        ...

Преимущества архитектуры
-------------------------

1. **Независимость от фреймворков** — бизнес-логика не зависит от FastAPI
2. **Тестируемость** — легко тестировать каждый слой изолированно
3. **Гибкость** — можно заменить БД, фреймворк, внешние сервисы
4. **Разделение ответственности** — каждый слой имеет четкую роль
5. **Масштабируемость** — легко добавлять новые фичи

Дополнительные ресурсы
----------------------

* Robert C. Martin — "Clean Architecture"
* Eric Evans — "Domain-Driven Design"
* Martin Fowler — "Patterns of Enterprise Application Architecture"
