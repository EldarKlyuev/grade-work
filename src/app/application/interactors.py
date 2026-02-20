"""Интеракторы - обработчики команд (CQRS).

Этот модуль содержит команды (Command handlers) в паттерне CQRS.
Каждый интерактор представляет одну бизнес-операцию и оркеструет
взаимодействие между доменными объектами и портами.
"""

import secrets
from datetime import datetime, timedelta
from uuid import UUID

from src.app.application.dto import (
    AddToCartDTO,
    CreateOrderDTO,
    ImportProductsDTO,
    LoginUserDTO,
    RegisterUserDTO,
    RemoveFromCartDTO,
    RequestPasswordResetDTO,
    ResetPasswordDTO,
)
from src.app.application.ports import (
    EmailGatewayPort,
    PasswordHasherPort,
    TokenServicePort,
)
from src.app.domain.entities import Cart, PasswordResetToken, User
from src.app.domain.exceptions import (
    ExpiredTokenError,
    InvalidCredentialsError,
    ProductNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.app.domain.ports import (
    CartRepositoryPort,
    OrderRepositoryPort,
    PasswordResetTokenRepositoryPort,
    ProductRepositoryPort,
    UnitOfWorkPort,
    UserRepositoryPort,
)
from src.app.domain.value_objects import Email, Money, Password
from src.app.infrastructure.utils.csv_importer import products_from_csv_generator


class RegisterUserInteractor:
    """Интерактор регистрации пользователя.
    
    Обрабатывает регистрацию нового пользователя в системе.
    Проверяет уникальность email, хеширует пароль и отправляет
    приветственное письмо.
    
    :param user_repository: Репозиторий пользователей
    :type user_repository: UserRepositoryPort
    :param password_hasher: Сервис хеширования паролей
    :type password_hasher: PasswordHasherPort
    :param email_gateway: Сервис отправки email
    :type email_gateway: EmailGatewayPort
    :param uow: Unit of Work для управления транзакцией
    :type uow: UnitOfWorkPort
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        email_gateway: EmailGatewayPort,
        uow: UnitOfWorkPort,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.email_gateway = email_gateway
        self.uow = uow
    
    async def __call__(self, data: RegisterUserDTO) -> UUID:
        """Зарегистрировать нового пользователя.
        
        :param data: DTO с данными регистрации
        :type data: RegisterUserDTO
        :return: ID созданного пользователя
        :rtype: UUID
        :raises UserAlreadyExistsError: Если email уже занят
        :raises InvalidEmailError: Если формат email некорректен
        :raises InvalidPasswordError: Если пароль не соответствует требованиям
        
        :example:
        
        >>> dto = RegisterUserDTO(
        ...     email="user@example.com",
        ...     password="SecurePass123!",
        ...     username="john_doe"
        ... )
        >>> user_id = await interactor(dto)
        """
        email = Email(data.email)
        
        if await self.user_repository.exists_by_email(email):
            raise UserAlreadyExistsError(data.email)
        
        password = Password(data.password)
        password_hash = self.password_hasher.hash_password(password.value)
        
        user = User.create(
            email=email,
            password_hash=password_hash,
            username=data.username,
        )
        
        await self.user_repository.save(user)
        await self.uow.commit()
        
        await self.email_gateway.send_registration_email(
            to=email.value,
            username=user.username,
        )
        
        return user.id


class LoginUserInteractor:
    """Интерактор входа в систему.
    
    Аутентифицирует пользователя и возвращает JWT токен.
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service
    
    async def __call__(self, data: LoginUserDTO) -> str:
        """Аутентифицировать пользователя и вернуть токен.
        
        :param data: DTO с учетными данными
        :type data: LoginUserDTO
        :return: JWT токен доступа
        :rtype: str
        :raises InvalidCredentialsError: Если учетные данные неверны
        """
        email = Email(data.email)
        user = await self.user_repository.find_by_email(email)
        
        if not user:
            raise InvalidCredentialsError()
        
        if not self.password_hasher.verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError()
        
        if not user.is_active:
            raise InvalidCredentialsError()
        
        token = self.token_service.create_access_token(subject=str(user.id))
        return token


class RequestPasswordResetInteractor:
    """Request password reset interactor"""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        token_repository: PasswordResetTokenRepositoryPort,
        email_gateway: EmailGatewayPort,
        uow: UnitOfWorkPort,
    ) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.email_gateway = email_gateway
        self.uow = uow
    
    async def __call__(self, data: RequestPasswordResetDTO) -> None:
        """Request password reset"""
        email = Email(data.email)
        user = await self.user_repository.find_by_email(email)
        
        if not user:
            return
        
        token_str = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        token = PasswordResetToken.create(
            user_id=user.id,
            token=token_str,
            expires_at=expires_at,
        )
        
        await self.token_repository.save(token)
        await self.uow.commit()
        
        await self.email_gateway.send_password_reset_email(
            to=email.value,
            username=user.username,
            reset_token=token_str,
        )


class ResetPasswordInteractor:
    """Reset password interactor"""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        token_repository: PasswordResetTokenRepositoryPort,
        password_hasher: PasswordHasherPort,
        uow: UnitOfWorkPort,
    ) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.password_hasher = password_hasher
        self.uow = uow
    
    async def __call__(self, data: ResetPasswordDTO) -> None:
        """Reset user password"""
        token = await self.token_repository.find_by_token(data.token)
        
        if not token or token.used:
            raise ExpiredTokenError()
        
        if token.is_expired():
            raise ExpiredTokenError()
        
        user = await self.user_repository.find_by_id(token.user_id)
        if not user:
            raise UserNotFoundError(str(token.user_id))
        
        password = Password(data.new_password)
        user.password_hash = self.password_hasher.hash_password(password.value)
        
        token.mark_as_used()
        
        await self.user_repository.save(user)
        await self.token_repository.save(token)
        await self.uow.commit()


class AddToCartInteractor:
    """Add to cart interactor"""
    
    def __init__(
        self,
        cart_repository: CartRepositoryPort,
        product_repository: ProductRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> None:
        self.cart_repository = cart_repository
        self.product_repository = product_repository
        self.uow = uow
    
    async def __call__(self, data: AddToCartDTO) -> UUID:
        """Add item to cart"""
        product = await self.product_repository.find_by_id(data.product_id)
        if not product:
            raise ProductNotFoundError(str(data.product_id))
        
        cart = await self.cart_repository.find_by_user_id(data.user_id)
        if not cart:
            cart = Cart.create(user_id=data.user_id)
        
        cart.add_item(data.product_id, data.quantity)
        
        await self.cart_repository.save(cart)
        await self.uow.commit()
        
        return cart.id


class RemoveFromCartInteractor:
    """Remove from cart interactor"""
    
    def __init__(
        self,
        cart_repository: CartRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> None:
        self.cart_repository = cart_repository
        self.uow = uow
    
    async def __call__(self, data: RemoveFromCartDTO) -> None:
        """Remove item from cart"""
        cart = await self.cart_repository.find_by_user_id(data.user_id)
        if not cart:
            return
        
        cart.remove_item(data.item_id)
        
        await self.cart_repository.save(cart)
        await self.uow.commit()


class CreateOrderInteractor:
    """Интерактор создания заказа.
    
    Создает заказ из корзины пользователя, резервирует товары
    и очищает корзину.
    """
    
    def __init__(
        self,
        cart_repository: CartRepositoryPort,
        product_repository: ProductRepositoryPort,
        order_repository: OrderRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> None:
        self.cart_repository = cart_repository
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.uow = uow
    
    async def __call__(self, data: CreateOrderDTO) -> UUID:
        """Создать заказ из корзины пользователя.
        
        :param data: DTO с ID пользователя
        :type data: CreateOrderDTO
        :return: ID созданного заказа
        :rtype: UUID
        :raises ValueError: Если корзина пуста
        :raises ProductNotFoundError: Если товар не найден
        :raises InsufficientStockError: Если товара недостаточно на складе
        """
        cart = await self.cart_repository.find_by_user_id(data.user_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty")
        
        cart_items_data = []
        for item in cart.items:
            product = await self.product_repository.find_by_id(item.product_id)
            if not product:
                raise ProductNotFoundError(str(item.product_id))
            
            product.decrease_stock(item.quantity)
            await self.product_repository.save(product)
            
            cart_items_data.append((item.product_id, item.quantity, product.price))
        
        from src.app.domain.entities import Order
        order = Order.create_from_cart(data.user_id, cart_items_data)
        
        await self.order_repository.save(order)
        
        cart.clear()
        await self.cart_repository.save(cart)
        
        await self.uow.commit()
        
        return order.id


class ImportProductsFromCSVInteractor:
    """Import products from CSV interactor"""
    
    def __init__(
        self,
        product_repository: ProductRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> None:
        self.product_repository = product_repository
        self.uow = uow
    
    async def __call__(self, data: ImportProductsDTO) -> int:
        """Import products from CSV using generator"""
        products = list(products_from_csv_generator(
            csv_content=data.csv_content,
            category_id=data.category_id,
        ))
        
        await self.product_repository.save_many(products)
        await self.uow.commit()
        
        return len(products)
