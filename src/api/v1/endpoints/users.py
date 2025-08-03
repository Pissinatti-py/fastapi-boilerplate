from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.db.session import get_db_session
from src.schemas.core.user import UserCreate, UserRead
from src.db.utils.models.user_manager import user_manager


router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create a new user with validation for unique email and username.
    """
    if await user_manager.exists_by_field(db, "email", user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user.email}' is already registered.",
        )

    # Check if username already exists
    if await user_manager.exists_by_field(db, "username", user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user.username}' is already registered.",
        )

    # Create user using manager
    return await user_manager.create(db, user)


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True, description="Filter only active users"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve a list of users with optional filtering.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        active_only: Filter only active users
        db: Database session
    """
    if active_only:
        return await user_manager.get_active_users(db, skip, limit)

    return await user_manager.get_multi(db, skip, limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve a user by ID.
    """
    user = await user_manager.get_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserRead)
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update a user by ID.
    """
    existing_user = await user_manager.get_by_id(db, user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_update.email != existing_user.email:
        if await user_manager.exists_by_field(db, "email", user_update.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_update.email}' is already registered.",
            )

    if user_update.username != existing_user.username:
        if await user_manager.exists_by_field(
            db,
            "username",
            user_update.username
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Username '{user_update.username}' is already registered."
                ),
            )

    updated_user = await user_manager.update(db, user_id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.delete("/{user_id}/")
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Deactivate a user instead of deleting.
    """
    user = await user_manager.deactivate_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
