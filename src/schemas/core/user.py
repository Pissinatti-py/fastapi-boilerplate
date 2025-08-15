from pydantic import ConfigDict, BaseModel, EmailStr, Field, field_validator
from typing import Annotated

from src.services.users.validators import (
    validate_username,
    validate_name,
    validate_password,
)

MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 128
FIELD_NAME = "name"
FIELD_USERNAME = "username"
FIELD_PASSWORD = "password"


class UserBase(BaseModel):
    """
    Base schema for user data with validation for common fields.

    :param BaseModel: Base class for Pydantic models.
    :type BaseModel: BaseModel
    """

    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=MAX_USERNAME_LENGTH,
            description="Username must be between 3 and 50 characters",
            examples=["john_doe", "user123", "alice.smith"],
        ),
    ]

    email: EmailStr = Field(
        description="Valid email address",
        examples=["user@example.com", "john.doe@company.org"],
    )

    name: Annotated[
        str | None,
        Field(
            min_length=1,
            max_length=100,
            description="Full name of the user",
            examples=["John Doe", "Alice Smith"],
        ),
    ] = None

    is_active: bool = Field(
        default=True, description="Whether the user account is active"
    )

    is_superuser: bool = Field(
        default=False, description="Whether the user has superuser privileges"
    )

    @field_validator(FIELD_NAME)
    @classmethod
    def validate_name(cls, name_value: str | None) -> str | None:
        """
        Validate user's full name.

        Rules:
        - If provided, cannot be empty or only whitespace
        - Cannot contain special characters except spaces, hyphens, and apostrophes
        - Cannot start or end with spaces

        Args:
            name_value: Name string to validate

        Returns:
            str | None: Validated name or None

        Raises:
            ValueError: If name doesn't meet validation criteria
        """
        return validate_name(name_value)

    @field_validator(FIELD_USERNAME)
    @classmethod
    def validate_username(cls, username_value: str) -> str:
        """
        Validate username format and content.

        Rules:
        - Cannot be empty or only whitespace
        - Must contain only alphanumeric characters, dots, underscores, and hyphens
        - Cannot start or end with special characters
        - Cannot contain consecutive special characters

        Args:
            username_value: Username string to validate

        Returns:
            str: Validated and stripped username

        Raises:
            ValueError: If username doesn't meet validation criteria
        """
        return validate_username(username_value)


class UserCreate(UserBase):
    """
    Schema for creating a new user with comprehensive validation.

    This schema extends UserBase and adds password validation with
    strong security requirements.
    """

    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=MAX_PASSWORD_LENGTH,
            description="Password must be between 8 and 128 characters",
            examples=["MySecureP@ss123"],
        ),
    ]

    @field_validator(FIELD_PASSWORD)
    @classmethod
    def validate_password(cls, password_value: str) -> str:
        """
        Validate password strength and format.

        Rules:
        - Cannot be empty or only whitespace
        - Must contain at least one uppercase letter
        - Must contain at least one lowercase letter
        - Must contain at least one digit
        - Must contain at least one special character
        - Cannot contain common weak patterns
        - Cannot be entirely numeric
        - Cannot contain username (validated at model level)

        Args:
            password_value: Password string to validate

        Returns:
            str: Validated password

        Raises:
            ValueError: If password doesn't meet security criteria
        """
        return validate_password(password_value)

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True  # Automatically strip whitespace
        validate_assignment = True  # Validate on assignment
        extra = "forbid"  # Forbid extra fields

        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "name": "John Doe",
                "password": "MySecureP@ss123",
                "is_active": True,
                "is_superuser": False,
            }
        }


class UserUpdate(BaseModel):
    """
    Schema for updating user data (partial updates allowed).

    All fields are optional for PATCH operations.
    """

    username: Annotated[
        str | None,
        Field(
            min_length=3,
            max_length=MAX_USERNAME_LENGTH,
            description="Username must be between 3 and 50 characters",
        ),
    ] = None

    email: EmailStr | None = None
    name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    password: str | None = None

    @field_validator(FIELD_USERNAME)
    @classmethod
    def validate_username(cls, username_value: str | None) -> str | None:
        """
        Validate username format and content (for updates).
        """
        if username_value is None:
            return username_value

        # Strip whitespace first
        username_value = username_value.strip()

        # Check if empty after stripping
        if not username_value:
            raise ValueError("Username cannot be empty or only whitespace")

        return validate_username(username_value)

    @field_validator(FIELD_PASSWORD)
    @classmethod
    def validate_password(cls, password_value: str | None) -> str | None:
        """
        Validate password strength and format (for updates).
        """
        if password_value is None:
            return password_value

        # Check if empty or only whitespace
        if not password_value or password_value.isspace():
            raise ValueError("Password cannot be empty or only whitespace")

        return validate_password(password_value)

    @field_validator(FIELD_NAME)
    @classmethod
    def validate_name(cls, name_value: str | None) -> str | None:
        """
        Validate user's full name (for updates).
        """
        if name_value is None:
            return name_value

        # Strip whitespace first
        name_value = name_value.strip()

        # Check if empty after stripping
        if not name_value:
            raise ValueError("Name cannot be empty or only whitespace")

        return validate_name(name_value)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "john_doe_updated",
                "email": "john.updated@example.com",
                "name": "John Doe Updated",
                "is_active": True,
                "is_superuser": False,
            }
        },
    )


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
