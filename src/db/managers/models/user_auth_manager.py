import uuid
from typing import Optional

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
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


async def get_user_auth_manager(user_db=Depends(get_user_db)):
    yield UserAuthManager(user_db)
