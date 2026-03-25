from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "core__users"

    username: Mapped[str] = mapped_column(unique=True)
