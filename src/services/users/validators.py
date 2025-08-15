import re


def _check_password_basic_requirements(password: str) -> None:
    """Check basic password requirements."""
    if not password or password.isspace():
        raise ValueError("Password cannot be empty or only whitespace")

    if password.isdigit():
        raise ValueError("Password cannot be entirely numeric")


def _check_password_character_requirements(password: str) -> None:
    """Check password character type requirements."""
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number")

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        raise ValueError(
            "Password must contain at least one special character "
            "(!@#$%^&*()_+-=[]{};'\":|,.<>/?)"
        )


def _check_password_patterns_and_common(password: str) -> None:
    """Check for weak patterns and common passwords."""
    weak_patterns = [
        r"(.)\1{2,}",  # 3 or more consecutive identical characters
        r"(012|123|234|345|456|567|678|789|890)",  # Sequential numbers
        (
            r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|"
            r"opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)"
        ),  # Sequential letters
    ]

    for pattern in weak_patterns:
        if re.search(pattern, password.lower()):
            raise ValueError(
                "Password contains weak patterns (consecutive characters, "
                "sequential numbers/letters)"
            )

    common_weak_passwords = [
        "password", "password123", "12345678", "qwerty123", "admin123",
        "letmein123", "welcome123", "monkey123", "dragon123", "master123",
        "shadow123", "abc12345",
    ]

    if password.lower() in common_weak_passwords:
        raise ValueError("Password is too common and easily guessable")


def _check_name_characters(name: str) -> None:
    """Check if name contains only valid characters."""
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", name):
        raise ValueError(
            "Name can only contain letters, spaces, hyphens, and apostrophes"
        )


def _check_name_format(name: str) -> None:
    """Check name format rules."""
    if re.search(r"\s{2,}", name):
        raise ValueError("Name cannot contain multiple consecutive spaces")

    if re.match(r"^[-']|[-']$", name):
        raise ValueError("Name cannot start or end with hyphen or apostrophe")


def validate_name(name_input: str | None) -> str | None:
    """
    Validate user's full name.

    Rules:
    - If provided, cannot be empty or only whitespace
    - Cannot contain special characters except spaces, hyphens, and apostrophes
    - Cannot start or end with spaces

    Args:
        name_input: Name string to validate

    Returns:
        str | None: Validated name or None

    Raises:
        ValueError: If name doesn't meet validation criteria
    """
    if name_input is None:
        return name_input

    # Strip whitespace
    name_input = name_input.strip()

    # If empty after stripping, return None
    if not name_input:
        return None

    _check_name_characters(name_input)
    _check_name_format(name_input)

    return name_input


def _check_username_format(username: str) -> None:
    """Check basic username format rules."""
    if not re.match(r"^[a-zA-Z0-9._-]+$", username):
        raise ValueError(
            "Username can only contain letters, numbers, dots (.), "
            "underscores (_), and hyphens (-)"
        )

    if re.match(r"^[._-]|[._-]$", username):
        raise ValueError(
            "Username cannot start or end with dots, underscores, or hyphens"
        )

    if re.search(r"[._-]{2,}", username):
        raise ValueError("Username cannot contain consecutive special characters")


def _check_forbidden_usernames(username: str) -> None:
    """Check against forbidden username list."""
    forbidden_patterns = [
        "admin", "root", "administrator", "system", "test", "null",
        "undefined", "anonymous", "guest", "user", "support", "help",
        "info", "contact", "service",
    ]

    if username.lower() in forbidden_patterns:
        raise ValueError(f'Username "{username}" is not allowed for security reasons')


def validate_username(username_input: str) -> str:
    """
    Validate username format and content.

    Rules:
    - Cannot be empty or only whitespace
    - Must contain only alphanumeric characters, dots, underscores, and hyphens
    - Cannot start or end with special characters
    - Cannot contain consecutive special characters
    - Cannot be a reserved/forbidden username

    Args:
        username_input: Username string to validate

    Returns:
        str: Validated and stripped username

    Raises:
        ValueError: If username doesn't meet validation criteria
    """
    # Remove leading/trailing whitespace
    username_input = username_input.strip()

    # Check if empty after stripping
    if not username_input:
        raise ValueError("Username cannot be empty or only whitespace")

    _check_username_format(username_input)
    _check_forbidden_usernames(username_input)

    return username_input


def validate_password(password_value: str) -> str:
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
    _check_password_basic_requirements(password_value)
    _check_password_character_requirements(password_value)
    _check_password_patterns_and_common(password_value)

    return password_value
