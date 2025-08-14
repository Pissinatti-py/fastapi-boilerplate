from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from enum import Enum

from src.core.settings import settings


class TokenType(str, Enum):
    """Enum for different token types."""

    ACCESS = "access"
    REFRESH = "refresh"


class TokenPair:
    """
    Data class to hold access and refresh tokens.
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        refresh_expires_in: int,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.refresh_expires_in = refresh_expires_in
        self.token_type = "bearer"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "refresh_expires_in": self.refresh_expires_in,
        }


class AuthenticationService:
    """
    Enhanced Authentication service with access and refresh token support.

    This service provides methods for creating, verifying, and managing both
    access tokens (short-lived) and refresh tokens (long-lived) for JWT auth.

    Features:
    - Access token: Short-lived (default 15 minutes) for API access
    - Refresh token: Long-lived (default 7 days) for getting new access tokens
    - Token type identification
    - Cross-token validation
    """

    def __init__(self):
        """
        Initialize the AuthenticationService with settings from configuration.
        """
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = getattr(
            settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 15
        )
        self.refresh_token_expire_days = getattr(
            settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7
        )

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token with an expiration time.

        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta

        Returns:
            str: Encoded JWT access token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(tz=timezone.utc) + expires_delta
        else:
            expire = datetime.now(tz=timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        # Add token type and expiration
        to_encode.update(
            {
                "exp": expire,
                "token_type": TokenType.ACCESS.value,
                "iat": datetime.now(tz=timezone.utc),  # Issued at
            }
        )

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token with a longer expiration time.

        Args:
            data: Data to encode in the token (usually minimal user info)
            expires_delta: Optional expiration time delta

        Returns:
            str: Encoded JWT refresh token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(tz=timezone.utc) + expires_delta
        else:
            expire = datetime.now(tz=timezone.utc) + timedelta(
                days=self.refresh_token_expire_days
            )

        # Add token type and expiration
        to_encode.update(
            {
                "exp": expire,
                "token_type": TokenType.REFRESH.value,
                "iat": datetime.now(tz=timezone.utc),  # Issued at
            }
        )

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_token_pair(
        self,
        user_data: dict,
        access_expires_delta: Optional[timedelta] = None,
        refresh_expires_delta: Optional[timedelta] = None,
    ) -> TokenPair:
        """
        Create both access and refresh tokens for a user.

        Args:
            user_data: User data to encode in tokens
            access_expires_delta: Optional custom expiration for access token
            refresh_expires_delta: Optional custom expiration for refresh token

        Returns:
            TokenPair: Object containing both tokens and metadata
        """
        # Create access token with full user data
        access_token = self.create_access_token(
            user_data, access_expires_delta
        )

        # Create refresh token with minimal data (security best practice)
        refresh_data = {
            "sub": user_data.get("sub"),
            "user_id": user_data.get("user_id"),
            "token_family": user_data.get(
                "token_family", "default"
            ),  # For token rotation
        }

        refresh_token = self.create_refresh_token(
            refresh_data, refresh_expires_delta
        )

        # Calculate expiration times in seconds
        access_expires_in = (
            access_expires_delta or timedelta(
                minutes=self.access_token_expire_minutes
            )
        ).total_seconds()
        refresh_expires_in = (
            refresh_expires_delta or timedelta(
                days=self.refresh_token_expire_days
            )
        ).total_seconds()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expires_in),
            refresh_expires_in=int(refresh_expires_in),
        )

    def verify_token(
        self, token: str, expected_type: Optional[TokenType] = None
    ) -> dict:
        """
        Verify a JWT token and return the decoded data.

        Args:
            token: JWT token to verify
            expected_type: Expected token type (access or refresh)

        Returns:
            dict: Decoded token data if valid

        Raises:
            ValueError: If token verification fails or type mismatch

        """
        # TODO token type check method / Bearer format
        try:
            token = token.split(" ")[1] if " " in token else token

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            if expected_type:
                token_type = payload.get("token_type")

                if token_type != expected_type.value:
                    raise ValueError(
                        f"Invalid token type. Expected {expected_type.value}, "
                        f"got {token_type}"
                    )

            return payload

        except IndexError:
            raise ValueError(
                "Invalid token format. Expected 'Bearer <token>' format."
            )

        except JWTError as e:
            raise ValueError(f"Token verification failed: {str(e)}")

    def refresh_access_token(
        self, refresh_token: str, additional_data: Optional[dict] = None
    ) -> TokenPair:
        """
        Create a new access token using a valid refresh token.

        Args:
            refresh_token: Valid refresh token
            additional_data: Additional data to include in new access token

        Returns:
            TokenPair: New token pair with fresh access token

        Raises:
            ValueError: If refresh token is invalid or expired

        """
        try:
            payload = self.verify_token(refresh_token, TokenType.REFRESH)
        except ValueError:
            raise ValueError("Invalid or expired refresh token")

        user_data = {
            "sub": payload.get("sub"),
            "user_id": payload.get("user_id"),
            "token_family": payload.get("token_family", "default"),
        }

        if additional_data:
            user_data.update(additional_data)

        return self.create_token_pair(user_data)

    def get_current_user(
        self, token: str, token_type: TokenType = TokenType.ACCESS
    ) -> Optional[dict]:
        """
        Get the current user from a JWT token (safe version).

        Args:
            token: JWT token to decode
            token_type: Expected token type

        Returns:
            Optional[dict]: Decoded user data if valid, None if invalid

        """
        try:
            payload = self.verify_token(token, token_type)
            return payload

        except ValueError:
            return None

    def revoke_token_family(self, token_family: str) -> bool:
        """
        Revoke all tokens in a token family (for logout from all devices).

        Note: This would typically work with a token blacklist in production.

        Args:
            token_family: Token family identifier

        Returns:
            bool: True if tokens were revoked successfully
        """
        # In a real implementation, you would:
        # 1. Add the token_family to a blacklist/database
        # 2. Check this blacklist in verify_token method
        # 3. Implement cleanup for expired blacklist entries

        # For now, return True (placeholder implementation)
        return True
