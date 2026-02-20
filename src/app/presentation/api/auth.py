"""Authentication router"""

from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status

from src.app.application.dto import (
    LoginUserDTO,
    RegisterUserDTO,
    RequestPasswordResetDTO,
    ResetPasswordDTO,
)
from src.app.application.interactors import (
    LoginUserInteractor,
    RegisterUserInteractor,
    RequestPasswordResetInteractor,
    ResetPasswordInteractor,
)
from src.app.domain.exceptions import (
    DomainError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from src.app.presentation.schemas import (
    CreateUserRequest,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequestRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"], route_class=DishkaRoute)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: CreateUserRequest,
    interactor: Annotated[RegisterUserInteractor, FromDishka()],
) -> dict[str, UUID]:
    """Register a new user"""
    try:
        user_id = await interactor(
            RegisterUserDTO(
                email=request.email,
                password=request.password.get_secret_value(),
                username=request.username,
            )
        )
        return {"id": user_id}
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login")
async def login(
    request: LoginRequest,
    interactor: Annotated[LoginUserInteractor, FromDishka()],
) -> TokenResponse:
    """Login and get JWT token"""
    try:
        token = await interactor(
            LoginUserDTO(
                email=request.email,
                password=request.password.get_secret_value(),
            )
        )
        return TokenResponse(access_token=token)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    request: PasswordResetRequestRequest,
    interactor: Annotated[RequestPasswordResetInteractor, FromDishka()],
) -> dict[str, str]:
    """Request password reset"""
    await interactor(RequestPasswordResetDTO(email=request.email))
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    interactor: Annotated[ResetPasswordInteractor, FromDishka()],
) -> dict[str, str]:
    """Confirm password reset with token"""
    try:
        await interactor(
            ResetPasswordDTO(
                token=request.token,
                new_password=request.new_password.get_secret_value(),
            )
        )
        return {"message": "Password has been reset successfully"}
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
