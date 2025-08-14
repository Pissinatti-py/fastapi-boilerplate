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
        """
        Return a string representation of the User instance.

        :return: String representation of the User instance.
        :rtype: str
        """
        return (
            f"User(id={self.id}, username='{self.username}', "
            f"email='{self.email}')"
        )

    def check_password(self, password: str) -> bool:
        """
        Return a boolean of whether the password was correct.
        Handles hashing formats behind the scenes.

        Args:
            password: The raw password to check

        Returns:
            True if the password matches, False otherwise
        """
        from src.utils.security.hashers import check_password

        return check_password(password, self.hashed_password)
