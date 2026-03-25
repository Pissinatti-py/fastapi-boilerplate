import uuid
from typing import Optional

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.models import UP
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db_session
from src.models.core.user import User


class ExtendedSQLAlchemyUserDatabase(SQLAlchemyUserDatabase[User, uuid.UUID]):

    async def get_by_username(self, username: str) -> Optional[UP]:
        """
        Retrieve user by username.

        :param username: The username of the user to retrieve.
        :type username: str
        :return: The user with the given username, or None if not found.
        :rtype: Optional[UP]
        """
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username)
        )
        return await self._get_user(statement)


async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield ExtendedSQLAlchemyUserDatabase(session, User)
