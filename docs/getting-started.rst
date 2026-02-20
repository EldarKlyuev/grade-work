Быстрый старт
=============

Установка
---------

1. Клонируйте репозиторий::

    git clone <repository-url>
    cd grade-work

2. Установите зависимости с помощью Poetry::

    poetry install

3. Настройте переменные окружения. Создайте файл ``.env``::

    DATABASE_URL=postgresql+asyncpg://user:password@localhost/grade_work
    JWT_SECRET_KEY=your-secret-key
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=your-email@gmail.com
    SMTP_PASSWORD=your-password

4. Примените миграции базы данных::

    poetry run alembic upgrade head

Запуск приложения
-----------------

Запустите сервер разработки::

    poetry run uvicorn src.app.main:app --reload

Приложение будет доступно по адресу: http://localhost:8000

API документация
----------------

После запуска приложения автоматическая документация API доступна по адресам:

* **Swagger UI**: http://localhost:8000/docs
* **ReDoc**: http://localhost:8000/redoc

Базовое использование
---------------------

Регистрация пользователя
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    curl -X POST "http://localhost:8000/api/auth/register" \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "user@example.com",
        "username": "john_doe",
        "password": "SecurePass123!"
      }'

Вход в систему
~~~~~~~~~~~~~~

.. code-block:: bash

    curl -X POST "http://localhost:8000/api/auth/login" \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "user@example.com",
        "password": "SecurePass123!"
      }'

Получение списка товаров
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    curl -X GET "http://localhost:8000/api/products?page=1&page_size=10"

Запуск тестов
-------------

Запустите тесты с помощью pytest::

    poetry run pytest

Генерация документации
-----------------------

Для генерации этой документации локально::

    cd docs
    make html

HTML документация будет доступна в ``docs/_build/html/index.html``.
