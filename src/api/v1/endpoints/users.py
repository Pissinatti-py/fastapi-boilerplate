from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import current_active_user
from src.db.managers.models.user_manager import UserRepository
from src.db.session import get_db_session
from src.schemas.core.user import UserRead, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True, description="Filter only active users"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    List users with pagination and optional filtering for active users.

    :param skip: Number of records to skip for pagination, defaults to Query(0, ge=0)
    :type skip: int, optional
    :param limit: Maximum number of records to return, defaults to Query(100, ge=1, le=1000)
    :type limit: int, optional
    :param active_only: Whether to filter only active users, defaults to Query(True)
    :type active_only: bool, optional
    :param db: Database session dependency, defaults to Depends(get_db_session)
    :type db: AsyncSession, optional
    :return: List of users matching the criteria
    :rtype: List[UserRead]
    """
    user_manager = UserRepository()

    if active_only:
        return await user_manager.get_active_users(db, skip, limit)

    return await user_manager.get_multi(db, skip, limit)


@router.get("/{user_id}/", response_model=UserRead)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve a user by ID.
    """
    user_manager = UserRepository()
    user = await user_manager.get_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserRead)
@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update a user by ID.
    """
    user_manager = UserRepository()
    existing_user = await user_manager.get_by_id(db, user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_update.email != existing_user.email:
        if await user_manager.exists_by_field(db, "email", user_update.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_update.email}' is already registered.",
            )

    if user_update.username != existing_user.username:
        if await user_manager.exists_by_field(db, "username", user_update.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(f"Username '{user_update.username}' is already registered."),
            )

    updated_user = await user_manager.update(db, user_id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return updated_user


@router.delete("/{user_id}/")
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _current_user=Depends(current_active_user),
):
    """
    Deactivate a user instead of deleting.
    """
    user_manager = UserRepository()
    user = await user_manager.deactivate_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if _current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only deactivate your own account.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
