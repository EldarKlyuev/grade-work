"""Cart router"""

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status

from src.app.application.dto import AddToCartDTO, RemoveFromCartDTO
from src.app.application.interactors import AddToCartInteractor, RemoveFromCartInteractor
from src.app.application.queries import GetCartQueryService
from src.app.domain.exceptions import DomainError
from src.app.presentation.dependencies import CurrentUser
from src.app.presentation.schemas import AddToCartRequest, CartItemResponse, CartResponse

router = APIRouter(prefix="/cart", tags=["Cart"], route_class=DishkaRoute)


@router.get("", response_model=CartResponse | None)
async def get_cart(
    current_user: CurrentUser,
    query_service: Annotated[GetCartQueryService, FromDishka()],
) -> CartResponse | None:
    """Get user's cart"""
    cart = await query_service(current_user.id)
    
    if not cart:
        return None
    
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_price=item.product_price,
                quantity=item.quantity,
                total_price=item.total_price,
            )
            for item in cart.items
        ],
        total_amount=cart.total_amount,
    )


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: CurrentUser,
    interactor: Annotated[AddToCartInteractor, FromDishka()],
) -> dict[str, str]:
    """Add item to cart"""
    try:
        await interactor(
            AddToCartDTO(
                user_id=current_user.id,
                product_id=request.product_id,
                quantity=request.quantity,
            )
        )
        return {"message": "Item added to cart"}
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: str,
    current_user: CurrentUser,
    interactor: Annotated[RemoveFromCartInteractor, FromDishka()],
) -> None:
    """Remove item from cart"""
    from uuid import UUID
    
    await interactor(
        RemoveFromCartDTO(
            user_id=current_user.id,
            item_id=UUID(item_id),
        )
    )
