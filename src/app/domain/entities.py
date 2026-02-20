"""Доменные сущности - объекты с идентичностью.

Этот модуль содержит все сущности (entities) доменного слоя.
Сущности отличаются от объектов-значений наличием уникального идентификатора
и изменяемым состоянием в течение жизненного цикла.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from src.app.domain.exceptions import InsufficientStockError
from src.app.domain.value_objects import Email, Money


class OrderStatus(str, Enum):
    """Перечисление статусов заказа.
    
    Определяет возможные состояния заказа в системе.
    Статусы образуют конечный автомат с определенными переходами.
    
    :cvar PENDING: Заказ создан, ожидает оплаты
    :cvar PAID: Заказ оплачен, готов к отправке
    :cvar SHIPPED: Заказ отправлен
    :cvar DELIVERED: Заказ доставлен получателю
    :cvar CANCELLED: Заказ отменен
    """
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class User:
    """Сущность пользователя системы.
    
    Представляет зарегистрированного пользователя e-commerce платформы.
    Является агрегатом в терминах DDD. Содержит личные данные пользователя
    и информацию для аутентификации.
    
    :param id: Уникальный идентификатор пользователя
    :type id: UUID
    :param email: Email пользователя (объект-значение с валидацией)
    :type email: Email
    :param password_hash: Хэш пароля для аутентификации
    :type password_hash: str
    :param username: Имя пользователя для отображения
    :type username: str
    :param is_active: Флаг активности аккаунта (для блокировки)
    :type is_active: bool
    :param created_at: Дата и время создания аккаунта
    :type created_at: datetime
    
    .. note::
       Пароль хранится только в виде хэша для безопасности.
       Используйте фабричный метод :meth:`create` для создания новых пользователей.
    """
    
    id: UUID
    email: Email
    password_hash: str
    username: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        email: Email,
        password_hash: str,
        username: str,
    ) -> "User":
        """Фабричный метод для создания нового пользователя.
        
        Создает пользователя с автоматически сгенерированным UUID
        и текущей датой создания.
        
        :param email: Валидированный email пользователя
        :type email: Email
        :param password_hash: Хэш пароля (уже захешированный)
        :type password_hash: str
        :param username: Имя пользователя
        :type username: str
        :return: Новый экземпляр пользователя
        :rtype: User
        
        :example:
        
        >>> email = Email("user@example.com")
        >>> user = User.create(
        ...     email=email,
        ...     password_hash="$2b$12$...",
        ...     username="john_doe"
        ... )
        """
        return cls(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            username=username,
        )


@dataclass
class Category:
    """Сущность категории товаров.
    
    Представляет категорию в иерархическом каталоге товаров.
    Поддерживает древовидную структуру с помощью самоссылающегося parent_id.
    
    :param id: Уникальный идентификатор категории
    :type id: UUID
    :param name: Название категории
    :type name: str
    :param slug: URL-дружественный идентификатор (для SEO)
    :type slug: str
    :param parent_id: ID родительской категории (None для корневых)
    :type parent_id: UUID | None
    
    :example:
    
    >>> root = Category.create(name="Электроника", slug="electronics")
    >>> child = Category.create(
    ...     name="Смартфоны",
    ...     slug="smartphones",
    ...     parent_id=root.id
    ... )
    """
    
    id: UUID
    name: str
    slug: str
    parent_id: UUID | None = None
    
    @classmethod
    def create(cls, name: str, slug: str, parent_id: UUID | None = None) -> "Category":
        """Фабричный метод для создания новой категории.
        
        :param name: Название категории для отображения
        :type name: str
        :param slug: URL slug (должен быть уникальным)
        :type slug: str
        :param parent_id: ID родительской категории для иерархии
        :type parent_id: UUID | None
        :return: Новая категория
        :rtype: Category
        """
        return cls(
            id=uuid4(),
            name=name,
            slug=slug,
            parent_id=parent_id,
        )


@dataclass
class Product:
    """Сущность товара.
    
    Представляет товар в каталоге e-commerce платформы.
    Содержит информацию о товаре, его цене и остатках на складе.
    
    :param id: Уникальный идентификатор товара
    :type id: UUID
    :param name: Название товара
    :type name: str
    :param description: Описание товара
    :type description: str
    :param price: Цена товара (объект-значение Money)
    :type price: Money
    :param stock: Количество на складе
    :type stock: int
    :param category_id: ID категории товара
    :type category_id: UUID
    :param created_at: Дата добавления товара
    :type created_at: datetime
    
    .. warning::
       Методы изменения остатков проверяют бизнес-правила.
       Нельзя уменьшить остаток ниже нуля.
    """
    
    id: UUID
    name: str
    description: str
    price: Money
    stock: int
    category_id: UUID
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        price: Money,
        stock: int,
        category_id: UUID,
    ) -> "Product":
        """Фабричный метод для создания нового товара.
        
        :param name: Название товара
        :type name: str
        :param description: Подробное описание
        :type description: str
        :param price: Цена товара
        :type price: Money
        :param stock: Начальное количество на складе
        :type stock: int
        :param category_id: ID категории
        :type category_id: UUID
        :return: Новый товар
        :rtype: Product
        """
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )
    
    def decrease_stock(self, quantity: int) -> None:
        """Уменьшить остаток товара на складе.
        
        Проверяет достаточность остатка перед уменьшением.
        Используется при оформлении заказа.
        
        :param quantity: Количество для уменьшения
        :type quantity: int
        :raises InsufficientStockError: Если остатка недостаточно
        
        :example:
        
        >>> product = Product.create(...)
        >>> product.decrease_stock(5)  # Уменьшает stock на 5
        """
        if self.stock < quantity:
            raise InsufficientStockError(str(self.id), quantity, self.stock)
        self.stock -= quantity
    
    def increase_stock(self, quantity: int) -> None:
        """Увеличить остаток товара на складе.
        
        Используется при отмене заказа или поступлении товара.
        
        :param quantity: Количество для увеличения
        :type quantity: int
        """
        self.stock += quantity


@dataclass
class CartItem:
    """Элемент корзины покупок.
    
    Представляет отдельную позицию в корзине пользователя.
    Связывает товар с количеством.
    
    :param id: Уникальный идентификатор элемента
    :type id: UUID
    :param cart_id: ID корзины, которой принадлежит элемент
    :type cart_id: UUID
    :param product_id: ID товара
    :type product_id: UUID
    :param quantity: Количество единиц товара
    :type quantity: int
    """
    
    id: UUID
    cart_id: UUID
    product_id: UUID
    quantity: int
    
    @classmethod
    def create(cls, cart_id: UUID, product_id: UUID, quantity: int) -> "CartItem":
        """Создать новый элемент корзины.
        
        :param cart_id: ID корзины
        :type cart_id: UUID
        :param product_id: ID товара
        :type product_id: UUID
        :param quantity: Количество
        :type quantity: int
        :return: Новый элемент корзины
        :rtype: CartItem
        """
        return cls(
            id=uuid4(),
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )
    
    def update_quantity(self, quantity: int) -> None:
        """Обновить количество товара.
        
        :param quantity: Новое количество (должно быть > 0)
        :type quantity: int
        :raises ValueError: Если количество <= 0
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.quantity = quantity


@dataclass
class Cart:
    """Корзина покупок пользователя.
    
    Агрегат, управляющий элементами корзины пользователя.
    Поддерживает добавление, удаление и обновление товаров.
    
    :param id: Уникальный идентификатор корзины
    :type id: UUID
    :param user_id: ID пользователя-владельца корзины
    :type user_id: UUID
    :param items: Список элементов в корзине
    :type items: list[CartItem]
    
    .. note::
       У каждого пользователя может быть только одна активная корзина.
       При добавлении товара, который уже есть в корзине, увеличивается количество.
    """
    
    id: UUID
    user_id: UUID
    items: list[CartItem] = field(default_factory=list)
    
    @classmethod
    def create(cls, user_id: UUID) -> "Cart":
        """Создать новую пустую корзину для пользователя.
        
        :param user_id: ID пользователя
        :type user_id: UUID
        :return: Новая корзина
        :rtype: Cart
        """
        return cls(
            id=uuid4(),
            user_id=user_id,
        )
    
    def add_item(self, product_id: UUID, quantity: int) -> None:
        """Добавить товар в корзину или обновить количество.
        
        Если товар уже есть в корзине, увеличивает его количество.
        В противном случае создает новый элемент.
        
        :param product_id: ID товара для добавления
        :type product_id: UUID
        :param quantity: Количество единиц товара
        :type quantity: int
        
        :example:
        
        >>> cart = Cart.create(user_id=user.id)
        >>> cart.add_item(product_id, 2)
        >>> cart.add_item(product_id, 3)  # Теперь quantity = 5
        """
        for item in self.items:
            if item.product_id == product_id:
                item.update_quantity(item.quantity + quantity)
                return
        
        self.items.append(CartItem.create(self.id, product_id, quantity))
    
    def remove_item(self, item_id: UUID) -> None:
        """Удалить элемент из корзины.
        
        :param item_id: ID элемента для удаления
        :type item_id: UUID
        """
        self.items = [item for item in self.items if item.id != item_id]
    
    def clear(self) -> None:
        """Очистить все элементы из корзины.
        
        Используется после создания заказа.
        """
        self.items.clear()


@dataclass
class OrderItem:
    """Элемент заказа.
    
    Представляет товар в оформленном заказе.
    В отличие от CartItem, хранит фиксированную цену на момент заказа.
    
    :param id: Уникальный идентификатор элемента
    :type id: UUID
    :param order_id: ID заказа
    :type order_id: UUID
    :param product_id: ID товара
    :type product_id: UUID
    :param quantity: Количество единиц товара
    :type quantity: int
    :param unit_price: Цена за единицу на момент заказа
    :type unit_price: Money
    
    .. note::
       Цена фиксируется при создании заказа и не меняется,
       даже если цена товара изменилась.
    """
    
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Money
    
    @classmethod
    def create(
        cls,
        order_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_price: Money,
    ) -> "OrderItem":
        """Создать новый элемент заказа.
        
        :param order_id: ID заказа
        :type order_id: UUID
        :param product_id: ID товара
        :type product_id: UUID
        :param quantity: Количество
        :type quantity: int
        :param unit_price: Цена за единицу
        :type unit_price: Money
        :return: Новый элемент заказа
        :rtype: OrderItem
        """
        return cls(
            id=uuid4(),
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
    
    @property
    def total_price(self) -> Money:
        """Вычислить общую стоимость элемента.
        
        :return: Цена за единицу, умноженная на количество
        :rtype: Money
        """
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Заказ пользователя.
    
    Агрегат, представляющий оформленный заказ с элементами и статусом.
    Управляет жизненным циклом заказа через переходы между статусами.
    
    :param id: Уникальный идентификатор заказа
    :type id: UUID
    :param user_id: ID пользователя, сделавшего заказ
    :type user_id: UUID
    :param items: Список элементов заказа
    :type items: list[OrderItem]
    :param total_amount: Общая сумма заказа
    :type total_amount: Money
    :param status: Текущий статус заказа
    :type status: OrderStatus
    :param created_at: Дата создания заказа
    :type created_at: datetime
    
    .. warning::
       Переходы между статусами ограничены бизнес-правилами.
       Например, нельзя отменить отгруженный заказ.
    """
    
    id: UUID
    user_id: UUID
    items: list[OrderItem]
    total_amount: Money
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create_from_cart(
        cls,
        user_id: UUID,
        cart_items: list[tuple[UUID, int, Money]],
    ) -> "Order":
        """Создать заказ из элементов корзины.
        
        Фиксирует цены на момент создания заказа и вычисляет общую сумму.
        
        :param user_id: ID пользователя
        :type user_id: UUID
        :param cart_items: Список кортежей (product_id, quantity, unit_price)
        :type cart_items: list[tuple[UUID, int, Money]]
        :return: Новый заказ со статусом PENDING
        :rtype: Order
        
        :example:
        
        >>> cart_data = [
        ...     (product1_id, 2, Money(Decimal("100.00"))),
        ...     (product2_id, 1, Money(Decimal("50.00")))
        ... ]
        >>> order = Order.create_from_cart(user.id, cart_data)
        >>> order.total_amount  # Money(Decimal("250.00"))
        """
        order_id = uuid4()
        items = [
            OrderItem.create(order_id, product_id, quantity, unit_price)
            for product_id, quantity, unit_price in cart_items
        ]
        
        total = Money.zero()
        for item in items:
            total = total + item.total_price
        
        return cls(
            id=order_id,
            user_id=user_id,
            items=items,
            total_amount=total,
        )
    
    def mark_as_paid(self) -> None:
        """Пометить заказ как оплаченный.
        
        Переводит заказ в статус PAID.
        """
        self.status = OrderStatus.PAID
    
    def mark_as_shipped(self) -> None:
        """Пометить заказ как отправленный.
        
        :raises ValueError: Если заказ не оплачен
        """
        if self.status != OrderStatus.PAID:
            raise ValueError("Order must be paid before shipping")
        self.status = OrderStatus.SHIPPED
    
    def mark_as_delivered(self) -> None:
        """Пометить заказ как доставленный.
        
        :raises ValueError: Если заказ не отправлен
        """
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Order must be shipped before delivery")
        self.status = OrderStatus.DELIVERED
    
    def cancel(self) -> None:
        """Отменить заказ.
        
        :raises ValueError: Если заказ уже отправлен или доставлен
        """
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError("Cannot cancel shipped or delivered orders")
        self.status = OrderStatus.CANCELLED


@dataclass
class PasswordResetToken:
    """Токен для сброса пароля.
    
    Одноразовый токен с ограниченным сроком действия для восстановления пароля.
    После использования помечается как использованный.
    
    :param id: Уникальный идентификатор токена
    :type id: UUID
    :param user_id: ID пользователя, запросившего сброс
    :type user_id: UUID
    :param token: Строка токена для проверки
    :type token: str
    :param expires_at: Дата истечения срока действия
    :type expires_at: datetime
    :param used: Флаг использования токена
    :type used: bool
    :param created_at: Дата создания токена
    :type created_at: datetime
    
    .. note::
       Токен одноразовый - после успешного сброса пароля
       помечается как использованный и больше не может быть применен.
    """
    
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(cls, user_id: UUID, token: str, expires_at: datetime) -> "PasswordResetToken":
        """Создать новый токен сброса пароля.
        
        :param user_id: ID пользователя
        :type user_id: UUID
        :param token: Строка токена (должна быть криптографически безопасной)
        :type token: str
        :param expires_at: Время истечения срока
        :type expires_at: datetime
        :return: Новый токен
        :rtype: PasswordResetToken
        """
        return cls(
            id=uuid4(),
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
    
    def is_expired(self) -> bool:
        """Проверить, истек ли срок действия токена.
        
        :return: True если токен истек, иначе False
        :rtype: bool
        """
        return datetime.utcnow() > self.expires_at
    
    def mark_as_used(self) -> None:
        """Пометить токен как использованный.
        
        Вызывается после успешного сброса пароля.
        """
        self.used = True
