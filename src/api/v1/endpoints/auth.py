from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth.authentication_service import AuthenticationService
from src.schemas.core.auth import LoginRequest
from src.schemas.auth.token_response_schema import TokenResponse
from src.db.session import get_db_session
from src.db.utils.models.user_manager import user_manager


router = APIRouter()

DEFAULT_DB_SESSION = Depends(get_db_session)
DEFAULT_AUTHORIZATION_HEADER = Header(None)


@router.post("/login/")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = DEFAULT_DB_SESSION,
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
    authorization: str = DEFAULT_AUTHORIZATION_HEADER
):
    """
    Endpoint to check if the token is valid.
    This is a placeholder implementation.
    """
    auth_service = AuthenticationService()

    try:
        return auth_service.verify_token(authorization)

    except ValueError as auth_exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(auth_exception)
        )

    except Exception as unexpected_exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred {str(unexpected_exception)}"
        )
