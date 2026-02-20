"""Orders router"""

from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Query, status

from src.app.application.dto import CreateOrderDTO, PaginationDTO
from src.app.application.interactors import CreateOrderInteractor
from src.app.application.queries import ListOrdersQueryService
from src.app.domain.exceptions import DomainError
from src.app.presentation.dependencies import CurrentUser
from src.app.presentation.schemas import OrderItemResponse, OrderListResponse, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"], route_class=DishkaRoute)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    current_user: CurrentUser,
    query_service: Annotated[ListOrdersQueryService, FromDishka()],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> OrderListResponse:
    """List user's orders with pagination"""
    result = await query_service(
        user_id=current_user.id,
        pagination=PaginationDTO(page=page, page_size=page_size),
    )
    
    return OrderListResponse(
        items=[
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        total_price=item.total_price,
                    )
                    for item in order.items
                ],
                total_amount=order.total_amount,
                status=order.status,
                created_at=order.created_at,
            )
            for order in result.items
        ],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    current_user: CurrentUser,
    interactor: Annotated[CreateOrderInteractor, FromDishka()],
) -> dict[str, str]:
    """Create order from cart"""
    try:
        order_id = await interactor(CreateOrderDTO(user_id=current_user.id))
        return {"order_id": str(order_id)}
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
