import uuid
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions, models
from fastapi_users.models import UP

from src.core.settings import settings
from src.db.user_database import get_user_db
from src.models.core.user import User


class UserAuthManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
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
        self, credentials: OAuth2PasswordRequestForm
    ) -> models.UP | None:
        """
        Authenticate and return a user following an email and a password.

        Will automatically upgrade password hash if necessary.

        :param credentials: The user credentials.
        :return: The authenticated user of type models.UP if credentials are valid,
        otherwise None.
        """
        try:
            user = await self.get_by_username(credentials.username)
        except exceptions.UserNotExists:
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user


async def get_user_auth_manager(user_db=Depends(get_user_db)):
    yield UserAuthManager(user_db)
