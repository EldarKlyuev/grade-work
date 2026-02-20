"""Categories router"""

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from src.app.application.queries import ListCategoriesQueryService
from src.app.presentation.schemas import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"], route_class=DishkaRoute)


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    query_service: Annotated[ListCategoriesQueryService, FromDishka()],
) -> list[CategoryResponse]:
    """List all categories"""
    categories = await query_service()
    
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            parent_id=cat.parent_id,
        )
        for cat in categories
    ]
