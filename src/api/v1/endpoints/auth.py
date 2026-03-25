from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users.exceptions import UserNotExists

from src.core.security import auth_backend
from src.schemas.auth.login_request import LoginRequest
from src.schemas.core.user import UserCreate, UserRead
from src.services.users.manager import get_user_manager

auth_router = APIRouter()


@auth_router.post("/login")
async def login(
    credentials: LoginRequest,
    user_manager=Depends(get_user_manager),
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )

    strategy = auth_backend.get_strategy()
    token = await strategy.write_token(user)

    return await auth_backend.transport.get_login_response(token)


@auth_router.post("/register", response_model=UserRead)
async def register(
    user_create: UserCreate,
    user_manager=Depends(get_user_manager),
):
    try:
        existing_user = await user_manager.get_by_email(user_create.email)
    except UserNotExists:
        existing_user = None

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GENERIC_ERROR",
        )

    user = await user_manager.create(user_create)

    return UserRead.model_validate(user)
