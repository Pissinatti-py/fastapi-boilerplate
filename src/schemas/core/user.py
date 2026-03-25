import uuid

from fastapi_users import schemas
from pydantic import field_validator

from src.services.users.validators import validate_password


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for creating a new user via fastapi-users.

    Inherits email, password, is_active, is_superuser, is_verified
    from BaseUserCreate and adds password strength validation.
    """

    username: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password(value)


class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema for updating user data (partial updates allowed).

    Inherits optional email, password, is_active, is_superuser, is_verified
    from BaseUserUpdate.
    """

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return validate_password(v)
