"""Products router"""

from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from src.app.application.dto import ImportProductsDTO, PaginationDTO, SearchProductsDTO
from src.app.application.interactors import ImportProductsFromCSVInteractor
from src.app.application.queries import (
    GetProductQueryService,
    ListProductsQueryService,
    SearchProductsQueryService,
)
from src.app.infrastructure.image import PillowImageService
from src.app.presentation.dependencies import CurrentUser
from src.app.presentation.schemas import (
    ImportProductsRequest,
    ProductListResponse,
    ProductResponse,
    ResizeImageRequest,
)

router = APIRouter(prefix="/products", tags=["Products"], route_class=DishkaRoute)


@router.get("", response_model=ProductListResponse)
async def list_products(
    query_service: Annotated[ListProductsQueryService, FromDishka()],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: UUID | None = None,
) -> ProductListResponse:
    """List products with pagination"""
    result = await query_service(
        pagination=PaginationDTO(page=page, page_size=page_size),
        category_id=category_id,
    )
    
    return ProductListResponse(
        items=[
            ProductResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                stock=item.stock,
                category_id=item.category_id,
                category_name=item.category_name,
                created_at=item.created_at,
            )
            for item in result.items
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/search", response_model=ProductListResponse)
async def search_products(
    q: str,
    query_service: Annotated[SearchProductsQueryService, FromDishka()],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ProductListResponse:
    """Search products using full-text search"""
    result = await query_service(
        SearchProductsDTO(
            query=q,
            pagination=PaginationDTO(page=page, page_size=page_size),
        )
    )
    
    return ProductListResponse(
        items=[
            ProductResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                stock=item.stock,
                category_id=item.category_id,
                category_name=item.category_name,
                created_at=item.created_at,
            )
            for item in result.items
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    query_service: Annotated[GetProductQueryService, FromDishka()],
) -> ProductResponse:
    """Get product by ID"""
    product = await query_service(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id,
        category_name=product.category_name,
        created_at=product.created_at,
    )


@router.post("/import")
async def import_products(
    request: ImportProductsRequest,
    interactor: Annotated[ImportProductsFromCSVInteractor, FromDishka()],
    current_user: CurrentUser,
) -> dict[str, int]:
    """Import products from CSV"""
    count = await interactor(
        ImportProductsDTO(
            csv_content=request.csv_content,
            category_id=request.category_id,
        )
    )
    
    return {"imported": count}


@router.post("/{product_id}/resize-image")
async def resize_product_image(
    product_id: UUID,
    image: UploadFile = File(...),
    width: int = Query(..., gt=0, le=4000),
    height: int = Query(..., gt=0, le=4000),
    maintain_aspect_ratio: bool = Query(True),
    current_user: CurrentUser = None,
) -> dict[str, str]:
    """Resize product image using Pillow"""
    image_data = await image.read()
    
    image_service = PillowImageService()
    resized_data = image_service.resize_image(
        image_data=image_data,
        width=width,
        height=height,
        maintain_aspect_ratio=maintain_aspect_ratio,
    )
    
    return {
        "message": "Image resized successfully",
        "original_size": len(image_data),
        "resized_size": len(resized_data),
    }
