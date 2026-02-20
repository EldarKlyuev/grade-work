"""Dependencies - Dependency injection helpers"""

from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.domain.entities import User
from src.app.domain.exceptions import ExpiredTokenError, InvalidTokenError
from src.app.domain.ports import UserRepositoryPort
from src.app.infrastructure.security import JWTTokenService

security = HTTPBearer()


@inject
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: FromDishka[JWTTokenService],
    user_repository: FromDishka[UserRepositoryPort],
) -> User:
    """
    Get current user from JWT token.
    
    Demonstrates usage of FastAPI Depends combined with Dishka DI.
    This function extracts the JWT token from the Authorization header,
    validates it, and retrieves the corresponding user.
    
    Args:
        credentials: Bearer token from Authorization header
        token_service: JWT token service (injected via Dishka)
        user_repository: User repository (injected via Dishka)
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        user_id_str = token_service.get_subject(token)
        user_id = UUID(user_id_str)
    except (InvalidTokenError, ExpiredTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_repository.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
