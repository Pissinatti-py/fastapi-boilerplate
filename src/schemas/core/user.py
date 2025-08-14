from pydantic import ConfigDict, BaseModel, EmailStr, Field, field_validator
from typing import Annotated
import re

from src.services.users.validators import (
    validate_username,
    validate_name,
    validate_password,
)


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
            max_length=50,
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

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """
        Validate user's full name.

        Rules:
        - If provided, cannot be empty or only whitespace
        - Cannot contain special characters except spaces, hyphens, and apostrophes
        - Cannot start or end with spaces

        Args:
            v: Name string to validate

        Returns:
            str | None: Validated name or None

        Raises:
            ValueError: If name doesn't meet validation criteria
        """
        return validate_name(v)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format and content.

        Rules:
        - Cannot be empty or only whitespace
        - Must contain only alphanumeric characters, dots, underscores, and hyphens
        - Cannot start or end with special characters
        - Cannot contain consecutive special characters

        Args:
            v: Username string to validate

        Returns:
            str: Validated and stripped username

        Raises:
            ValueError: If username doesn't meet validation criteria
        """
        return validate_username(v)


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
            max_length=128,
            description="Password must be between 8 and 128 characters",
            examples=["MySecureP@ss123"],
        ),
    ]

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
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
            v: Password string to validate

        Returns:
            str: Validated password

        Raises:
            ValueError: If password doesn't meet security criteria
        """
        return validate_password(value)

    def model_post_init(self, __context) -> None:
        """
        Additional validation after model initialization.

        This method runs after all field validators and can access
        multiple fields for cross-field validation.
        """
        # Check if password contains username
        if hasattr(self, "password") and hasattr(self, "username"):
            if self.username.lower() in self.password.lower():
                raise ValueError("Password cannot contain the username")

        # Check if password contains email local part
        if hasattr(self, "password") and hasattr(self, "email"):
            email_local = str(self.email).split("@")[0].lower()
            if len(email_local) >= 3 and email_local in self.password.lower():
                raise ValueError("Password cannot contain parts of the email address")

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
            max_length=50,
            description="Username must be between 3 and 50 characters",
        ),
    ] = None

    email: EmailStr | None = None
    name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    password: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """
        Validate username format and content (for updates).
        """
        if v is None:
            return v

        # Strip whitespace first
        v = v.strip()

        # Check if empty after stripping
        if not v:
            raise ValueError("Username cannot be empty or only whitespace")

        return validate_username(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        """
        Validate password strength and format (for updates).
        """
        if v is None:
            return v

        # Check if empty or only whitespace
        if not v or v.isspace():
            raise ValueError("Password cannot be empty or only whitespace")

        return validate_password(v)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """
        Validate user's full name (for updates).
        """
        if v is None:
            return v

        # Strip whitespace first
        v = v.strip()

        # Check if empty after stripping
        if not v:
            raise ValueError("Name cannot be empty or only whitespace")

        return validate_name(v)

    def model_post_init(self, __context) -> None:
        """
        Additional validation after model initialization.
        """
        # Check if password contains username (only if both are provided)
        if (
            hasattr(self, "password")
            and self.password
            and hasattr(self, "username")
            and self.username
        ):
            if self.username.lower() in self.password.lower():
                raise ValueError("Password cannot contain the username")

        # Check if password contains email local part (only if both are provided)
        if (
            hasattr(self, "password")
            and self.password
            and hasattr(self, "email")
            and self.email
        ):
            email_local = str(self.email).split("@")[0].lower()
            if len(email_local) >= 3 and email_local in self.password.lower():
                raise ValueError("Password cannot contain parts of the email address")

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
