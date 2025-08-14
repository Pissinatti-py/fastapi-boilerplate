from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth.authentication_service import AuthenticationService
from src.schemas.core.auth import LoginRequest
from src.schemas.auth.token_response_schema import TokenResponse
from src.db.session import get_db_session
from src.db.utils.models.user_manager import user_manager


router = APIRouter()


@router.post("/login/")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    user = await user_manager.get_by_field(
        db, "username", credentials.username
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.check_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    user_data = {
        "sub": user.email,
        "user_id": user.id,
        "username": user.username,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "token_family": f"user_{user.id}_{int(datetime.now().timestamp())}",
    }

    # Create token pair
    auth_service = AuthenticationService()
    token_pair = auth_service.create_token_pair(user_data)

    return TokenResponse(**token_pair.to_dict())


@router.get("/check-token/")
async def check_token(
    db: AsyncSession = Depends(get_db_session),
    authorization: str = Header(None)
):
    """
    Endpoint to check if the token is valid.
    This is a placeholder implementation.
    """
    # For now, return True (placeholder implementation)
    print(f"Authorization header: {authorization}")
    auth_service = AuthenticationService()
    response = auth_service.verify_token(authorization)
    print(f"Token verification response: {response}")

    return {"valid": True}
