from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.db.session import get_db_session
from src.schemas.core.user import UserCreate, UserRead, UserUpdate
from src.db.utils.models.user_manager import user_manager


router = APIRouter()

DEFAULT_DB_SESSION = Depends(get_db_session)
DEFAULT_SKIP = Query(0, ge=0)
DEFAULT_LIMIT = Query(100, ge=1, le=1000)
DEFAULT_ACTIVE_ONLY = Query(True, description="Filter only active users")
USER_NOT_FOUND = "User not found"
USER_ALREADY_EXISTS = "Email or Username is already registered."


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = DEFAULT_DB_SESSION,
):
    """
    Create a new user with validation for unique email and username.
    """
    if await user_manager.exists_by_field(db, "email", user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USER_ALREADY_EXISTS,
        )

    # Check if username already exists
    if await user_manager.exists_by_field(db, "username", user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USER_ALREADY_EXISTS,
        )

    # Create user using manager
    return await user_manager.create(db, user)


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = DEFAULT_SKIP,
    limit: int = DEFAULT_LIMIT,
    active_only: bool = DEFAULT_ACTIVE_ONLY,
    db: AsyncSession = DEFAULT_DB_SESSION,
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


@router.get("/{user_id}/", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = DEFAULT_DB_SESSION):
    """
    Retrieve a user by ID.
    """
    user = await user_manager.get_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )

    return user


@router.put("/{user_id}", response_model=UserRead)
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = DEFAULT_DB_SESSION,
):
    """
    Update a user by ID.
    """
    existing_user = await user_manager.get_by_id(db, user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )

    conflicts = []

    if user_update.email != existing_user.email:
        if await user_manager.exists_by_field(db, "email", user_update.email):
            conflicts.append(USER_ALREADY_EXISTS)

    if user_update.username != existing_user.username:
        if await user_manager.exists_by_field(db, "username", user_update.username):
            conflicts.append(USER_ALREADY_EXISTS)

    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=" ".join(conflicts[-1:]),
        )

    updated_user = await user_manager.update(db, user_id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )

    return updated_user


@router.delete("/{user_id}/")
async def deactivate_user(user_id: int, db: AsyncSession = DEFAULT_DB_SESSION):
    """
    Deactivate a user instead of deleting.
    """
    user = await user_manager.deactivate_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
