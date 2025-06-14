from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.utils.base_manager import BaseManager
from src.models.core.user import User
from src.schemas.core.user import UserCreate, UserRead
from src.utils.security import get_password_hash


class UserManager(BaseManager[User, UserCreate, UserRead]):
    """
    User-specific CRUD manager with additional methods.

    Extends the base BaseManager with user-specific operations.
    """

    def __init__(self):
        super().__init__(User)

    async def create(
        self,
        db: AsyncSession,
        user_in: UserCreate
    ) -> User:
        """
        Create a new user with password hashing.

        Args:
            db: Database session
            user_in: User creation data

        Returns:
            The created user instance
        """
        # Hash the password
        user_data = user_in.model_dump(exclude_unset=True)
        user_data["hashed_password"] = get_password_hash(
            user_data.pop("password")
        )

        return await super().create(db, user_data)

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Get user by email address."""
        return await self.get_by_field(db, "email", email)

    async def get_by_username(
        self,
        db: AsyncSession,
        username: str
    ) -> Optional[User]:
        """Get user by username."""
        return await self.get_by_field(db, "username", username)

    async def get_active_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ):
        """Get all active users."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"is_active": True}
        )

    async def get_superusers(self, db: AsyncSession):
        """Get all superusers."""
        return await self.get_multi(
            db,
            filters={"is_superuser": True}
        )

    async def deactivate_user(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        """Deactivate a user instead of deleting."""
        return await self.update(db, user_id, {"is_active": False})

    async def activate_user(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        """Activate a user."""
        return await self.update(db, user_id, {"is_active": True})


# Create a global instance to use throughout the application
user_manager = UserManager()
