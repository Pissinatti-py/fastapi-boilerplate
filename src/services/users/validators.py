import re


def validate_name(value: str | None) -> str | None:
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
    if value is None:
        return value

    # Strip whitespace
    value = value.strip()

    # If empty after stripping, return None
    if not value:
        return None

    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", value):
        raise ValueError(
            "Name can only contain letters, spaces, hyphens, and apostrophes"
        )

    # Cannot have multiple consecutive spaces
    if re.search(r"\s{2,}", value):
        raise ValueError("Name cannot contain multiple consecutive spaces")

    # Cannot start or end with hyphen or apostrophe
    if re.match(r"^[-']|[-']$", value):
        raise ValueError("Name cannot start or end with hyphen or apostrophe")

    return value


def validate_username(value: str) -> str:
    """
    Validate username format and content.

    Rules:
    - Cannot be empty or only whitespace
    - Must contain only alphanumeric characters, dots, underscores, and hyphens
    - Cannot start or end with special characters
    - Cannot contain consecutive special characters
    - Cannot be a reserved/forbidden username

    Args:
        v: Username string to validate

    Returns:
        str: Validated and stripped username

    Raises:
        ValueError: If username doesn't meet validation criteria
    """
    # Remove leading/trailing whitespace
    value = value.strip()

    # Check if empty after stripping
    if not value:
        raise ValueError("Username cannot be empty or only whitespace")

    # Check for valid characters (alphanumeric, dots, underscores, hyphens)
    if not re.match(r"^[a-zA-Z0-9._-]+$", value):
        raise ValueError(
            "Username can only contain letters, numbers, dots (.), "
            "underscores (_), and hyphens (-)"
        )

    # Cannot start or end with special characters
    if re.match(r"^[._-]|[._-]$", value):
        raise ValueError(
            "Username cannot start or end with dots, underscores, or hyphens"
        )

    # Cannot have consecutive special characters
    if re.search(r"[._-]{2,}", value):
        raise ValueError("Username cannot contain consecutive special characters")

    # Additional security check - common invalid patterns
    forbidden_patterns = [
        "admin",
        "root",
        "administrator",
        "system",
        "test",
        "null",
        "undefined",
        "anonymous",
        "guest",
        "user",
        "support",
        "help",
        "info",
        "contact",
        "service",
    ]

    if value.lower() in forbidden_patterns:
        raise ValueError(f'Username "{value}" is not allowed for security reasons')

    return value


def validate_password(value: str) -> str:
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
        v: Password string to validate

    Returns:
        str: Validated password

    Raises:
        ValueError: If password doesn't meet security criteria
    """
    # Check if empty or only whitespace
    if not value or value.isspace():
        raise ValueError("Password cannot be empty or only whitespace")

    # Check for at least one uppercase letter
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")

    # Check for at least one lowercase letter
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")

    # Check for at least one digit
    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one number")

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', value):
        raise ValueError(
            "Password must contain at least one special character "
            "(!@#$%^&*()_+-=[]{};'\":|,.<>/?)"
        )

    # Cannot be entirely numeric
    if value.isdigit():
        raise ValueError("Password cannot be entirely numeric")

    # Check for common weak patterns
    weak_patterns = [
        r"(.)\1{2,}",  # 3 or more consecutive identical characters
        r"(012|123|234|345|456|567|678|789|890)",  # Sequential numbers
        r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",  # Sequential letters
    ]

    for pattern in weak_patterns:
        if re.search(pattern, value.lower()):
            raise ValueError(
                "Password contains weak patterns (consecutive characters, "
                "sequential numbers/letters)"
            )

    # Check for common weak passwords
    common_weak_passwords = [
        "password",
        "password123",
        "12345678",
        "qwerty123",
        "admin123",
        "letmein123",
        "welcome123",
        "monkey123",
        "dragon123",
        "master123",
        "shadow123",
        "abc12345",
    ]

    if value.lower() in common_weak_passwords:
        raise ValueError("Password is too common and easily guessable")

    return value
