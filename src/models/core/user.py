from sqlalchemy import Column, Integer, String, Boolean
from src.db.base import Base


class User(Base):

    __tablename__ = "core__users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    name = Column(String, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    is_superuser = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return (
            f"User(id={self.id}, username='{self.username}', "
            f"email='{self.email}')"
        )
