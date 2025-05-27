from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using the configured hashing algorithm.

    :param password: The plain-text password to be hashed.
    :type password: str
    :return: The hashed password as a string.
    :rtype: str
    """
    return pwd_context.hash(password)
