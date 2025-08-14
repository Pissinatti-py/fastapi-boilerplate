from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def check_password(password: str, hashed_password: str) -> bool:
    """
    Check if the provided password matches the hashed password.

    Args:
        password (str): The plain text password to check.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(password, hashed_password)
