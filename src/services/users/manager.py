import uuid
from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions, models
from fastapi_users.models import UP
from fastapi.security import OAuth2PasswordRequestForm

from src.core.settings import settings
from src.db.user_database import get_user_db
from src.models.core.user import User


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):

    reset_password_token_secret = settings.SECRET_KEY

    verification_token_secret = settings.SECRET_KEY

    def get_by_username(self, username: str) -> Optional[UP]:
        """
        Retrieve user by username.

        :param username: The username of the user to retrieve.
        :type username: str
        :return: The user with the given username, or None if not found.
        :rtype: Optional[UP]
        """
        return self.user_db.get_by_username(username)

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm,
    ) -> models.UP | None:
        try:
            user = await self.get_by_username(credentials.username)
        except exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password,
        )
        if not verified:
            return None

        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
