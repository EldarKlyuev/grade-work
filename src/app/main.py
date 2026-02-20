"""Main FastAPI application"""

import logging

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from config.settings import settings
from src.app.di import (
    DatabaseProvider,
    InteractorProvider,
    QueryServiceProvider,
    RepositoryProvider,
    ServiceProvider,
)
from src.app.infrastructure.persistence.database import async_session_maker
from src.app.infrastructure.sitemap import SitemapGenerator
from src.app.presentation.api import auth, cart, categories, orders, products, utils
from src.app.presentation.middleware import SlowRequestLoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.app_name,
        description="E-commerce API with Clean Architecture, CQRS, and DDD patterns",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(SlowRequestLoggingMiddleware)
    
    container = make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        InteractorProvider(),
        QueryServiceProvider(),
    )
    setup_dishka(container, app)
    
    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(categories.router)
    app.include_router(cart.router)
    app.include_router(orders.router)
    app.include_router(utils.router)
    
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint"""
        return {
            "message": "E-commerce API",
            "version": "0.1.0",
            "docs": "/docs",
        }
    
    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint"""
        return {"status": "healthy"}
    
    @app.get("/sitemap.xml", response_class=Response)
    async def sitemap() -> Response:
        """
        Generate and return sitemap.xml
        
        This endpoint automatically generates a sitemap based on current
        database content (products, categories). The sitemap is regenerated
        on each request, ensuring it's always up-to-date.
        """
        async with async_session_maker() as session:
            generator = SitemapGenerator(session)
            xml_content = await generator.generate()
        
        return Response(content=xml_content, media_type="application/xml")
    
    @app.on_event("startup")
    async def startup_event() -> None:
        """Application startup"""
        logger.info(f"Starting {settings.app_name}")
        logger.info(f"Database URL: {settings.database_url.split('@')[-1]}")
    
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Application shutdown"""
        logger.info("Shutting down application")
    
    return app


app = create_app()
