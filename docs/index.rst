Документация grade-work
========================

Добро пожаловать в документацию **grade-work** — e-commerce API, построенного на принципах Clean Architecture с использованием паттернов CQRS и Domain-Driven Design (DDD).

О проекте
---------

grade-work — это веб-приложение для электронной коммерции, разработанное с использованием:

* **FastAPI** — современный асинхронный веб-фреймворк
* **SQLAlchemy** — ORM для работы с PostgreSQL
* **Clean Architecture** — архитектурный подход с разделением на слои
* **CQRS** — разделение команд и запросов
* **DDD** — тактические паттерны Domain-Driven Design

Основные возможности
---------------------

* Регистрация и аутентификация пользователей
* Управление каталогом товаров и категорий
* Корзина покупок
* Создание и управление заказами
* Полнотекстовый поиск по товарам
* Импорт товаров из CSV

Содержание
----------

.. toctree::
   :maxdepth: 2
   :caption: Начало работы

   getting-started
   architecture

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/domain
   api/application
   api/infrastructure
   api/presentation

Индексы и таблицы
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
