"""Dependency injection container using Dishka"""

from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.application.interactors import (
    AddToCartInteractor,
    CreateOrderInteractor,
    ImportProductsFromCSVInteractor,
    LoginUserInteractor,
    RegisterUserInteractor,
    RemoveFromCartInteractor,
    RequestPasswordResetInteractor,
    ResetPasswordInteractor,
)
from src.app.application.ports import (
    EmailGatewayPort,
    PasswordHasherPort,
    TokenServicePort,
)
from src.app.application.queries import (
    GetCartQueryService,
    GetProductQueryService,
    ListCategoriesQueryService,
    ListOrdersQueryService,
    ListProductsQueryService,
    SearchProductsQueryService,
)
from src.app.domain.ports import (
    CartRepositoryPort,
    CategoryRepositoryPort,
    OrderRepositoryPort,
    PasswordResetTokenRepositoryPort,
    ProductRepositoryPort,
    UnitOfWorkPort,
    UserRepositoryPort,
)
from src.app.infrastructure.email import SmtpEmailService
from src.app.infrastructure.persistence.database import async_session_maker
from src.app.infrastructure.persistence.repositories import (
    CartRepository,
    CategoryRepository,
    OrderRepository,
    PasswordResetTokenRepository,
    ProductRepository,
    UserRepository,
)
from src.app.infrastructure.persistence.unit_of_work import UnitOfWork
from src.app.infrastructure.security import JWTTokenService, PasswordHasher


class DatabaseProvider(Provider):
    """Database session provider"""
    
    @provide(scope=Scope.REQUEST)
    async def provide_session(self) -> AsyncIterator[AsyncSession]:
        """Provide async database session"""
        async with async_session_maker() as session:
            yield session


class RepositoryProvider(Provider):
    """Repository provider"""
    
    @provide(scope=Scope.REQUEST)
    def provide_user_repository(self, session: AsyncSession) -> UserRepositoryPort:
        return UserRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_product_repository(self, session: AsyncSession) -> ProductRepositoryPort:
        return ProductRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_category_repository(self, session: AsyncSession) -> CategoryRepositoryPort:
        return CategoryRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_cart_repository(self, session: AsyncSession) -> CartRepositoryPort:
        return CartRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_order_repository(self, session: AsyncSession) -> OrderRepositoryPort:
        return OrderRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_password_reset_token_repository(
        self,
        session: AsyncSession,
    ) -> PasswordResetTokenRepositoryPort:
        return PasswordResetTokenRepository(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_unit_of_work(self, session: AsyncSession) -> UnitOfWorkPort:
        return UnitOfWork(session)


class ServiceProvider(Provider):
    """Service provider"""
    
    @provide(scope=Scope.APP)
    def provide_jwt_token_service_impl(self) -> JWTTokenService:
        """Provide concrete JWTTokenService"""
        return JWTTokenService()
    
    @provide(scope=Scope.APP)
    def provide_jwt_token_service(self, service: JWTTokenService) -> TokenServicePort:
        """Provide JWTTokenService as TokenServicePort"""
        return service
    
    @provide(scope=Scope.APP)
    def provide_password_hasher(self) -> PasswordHasherPort:
        return PasswordHasher()
    
    @provide(scope=Scope.APP)
    def provide_email_gateway(self) -> EmailGatewayPort:
        return SmtpEmailService()


class InteractorProvider(Provider):
    """Interactor provider"""
    
    @provide(scope=Scope.REQUEST)
    def provide_register_user_interactor(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        email_gateway: EmailGatewayPort,
        uow: UnitOfWorkPort,
    ) -> RegisterUserInteractor:
        return RegisterUserInteractor(user_repository, password_hasher, email_gateway, uow)
    
    @provide(scope=Scope.REQUEST)
    def provide_login_user_interactor(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ) -> LoginUserInteractor:
        return LoginUserInteractor(user_repository, password_hasher, token_service)
    
    @provide(scope=Scope.REQUEST)
    def provide_request_password_reset_interactor(
        self,
        user_repository: UserRepositoryPort,
        token_repository: PasswordResetTokenRepositoryPort,
        email_gateway: EmailGatewayPort,
        uow: UnitOfWorkPort,
    ) -> RequestPasswordResetInteractor:
        return RequestPasswordResetInteractor(
            user_repository,
            token_repository,
            email_gateway,
            uow,
        )
    
    @provide(scope=Scope.REQUEST)
    def provide_reset_password_interactor(
        self,
        user_repository: UserRepositoryPort,
        token_repository: PasswordResetTokenRepositoryPort,
        password_hasher: PasswordHasherPort,
        uow: UnitOfWorkPort,
    ) -> ResetPasswordInteractor:
        return ResetPasswordInteractor(
            user_repository,
            token_repository,
            password_hasher,
            uow,
        )
    
    @provide(scope=Scope.REQUEST)
    def provide_add_to_cart_interactor(
        self,
        cart_repository: CartRepositoryPort,
        product_repository: ProductRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> AddToCartInteractor:
        return AddToCartInteractor(cart_repository, product_repository, uow)
    
    @provide(scope=Scope.REQUEST)
    def provide_remove_from_cart_interactor(
        self,
        cart_repository: CartRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> RemoveFromCartInteractor:
        return RemoveFromCartInteractor(cart_repository, uow)
    
    @provide(scope=Scope.REQUEST)
    def provide_create_order_interactor(
        self,
        cart_repository: CartRepositoryPort,
        product_repository: ProductRepositoryPort,
        order_repository: OrderRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> CreateOrderInteractor:
        return CreateOrderInteractor(
            cart_repository,
            product_repository,
            order_repository,
            uow,
        )
    
    @provide(scope=Scope.REQUEST)
    def provide_import_products_interactor(
        self,
        product_repository: ProductRepositoryPort,
        uow: UnitOfWorkPort,
    ) -> ImportProductsFromCSVInteractor:
        return ImportProductsFromCSVInteractor(product_repository, uow)


class QueryServiceProvider(Provider):
    """Query service provider"""
    
    @provide(scope=Scope.REQUEST)
    def provide_list_products_query_service(
        self,
        session: AsyncSession,
    ) -> ListProductsQueryService:
        return ListProductsQueryService(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_search_products_query_service(
        self,
        session: AsyncSession,
    ) -> SearchProductsQueryService:
        return SearchProductsQueryService(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_product_query_service(
        self,
        session: AsyncSession,
    ) -> GetProductQueryService:
        return GetProductQueryService(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_list_categories_query_service(
        self,
        session: AsyncSession,
    ) -> ListCategoriesQueryService:
        return ListCategoriesQueryService(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_get_cart_query_service(
        self,
        session: AsyncSession,
    ) -> GetCartQueryService:
        return GetCartQueryService(session)
    
    @provide(scope=Scope.REQUEST)
    def provide_list_orders_query_service(
        self,
        session: AsyncSession,
    ) -> ListOrdersQueryService:
        return ListOrdersQueryService(session)
