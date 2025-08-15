from pydantic import BaseModel, Field, field_validator
from typing import Annotated

from src.services.users.validators import validate_username, validate_password

# Field length constants
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 128


class LoginRequest(BaseModel):
    """
    Schema for user login request with comprehensive field validation.

    This schema validates user credentials ensuring they meet security
    and format requirements before processing authentication.
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

    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=MAX_PASSWORD_LENGTH,
            description="Password must be between 8 and 128 characters",
            examples=["MySecureP@ss123"],
        ),
    ]

    @field_validator("username")
    @classmethod
    def validate_username(cls, username_value: str) -> str:
        """
        Validate username format and content.

        Rules:
        - Cannot be empty or only whitespace
        - Must contain only alphanumeric
            characters, dots, underscores, and hyphens
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

    @field_validator("password")
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
            "example": {"username": "john_doe", "password": "MySecureP@ss123"}
        }
