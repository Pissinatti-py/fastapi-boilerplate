from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


from src.db.session import get_db_session
from src.models.core.user import User
from src.schemas.core.user import UserCreate, UserRead
from src.utils.security import get_password_hash


router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Create a new user with validation for unique email and username.
    """

    # Check if email already exists
    email_check = await db.execute(select(User).where(User.email == user.email))
    if email_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user.email}' is already registered.",
        )

    # Check if username already exists
    username_check = await db.execute(
        select(User).where(User.username == user.username)
    )
    if username_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user.username}' is already registered.",
        )

    # Hash password
    hashed_password = get_password_hash(user.password)

    # Create ORM instance
    db_user = User(
        username=user.username,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        hashed_password=hashed_password,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.get("/", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve a list of all users.
    """
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Retrieve a user by ID using SQLAlchemy select.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, user_update: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    """
    Update a user by ID using SQLAlchemy update.
    """
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**user_update.dict())
        .returning(User)
    )
    result = await db.execute(stmt)
    await db.commit()
    updated_user = result.fetchone()

    if updated_user:
        return UserRead.model_validate(updated_user._mapping)
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Delete a user by ID using SQLAlchemy delete.
    """
    stmt = delete(User).where(User.id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return
