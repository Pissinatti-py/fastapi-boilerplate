from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """
    Schema for token pair response.

    Example:
        ```python
        response = TokenResponse(
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            refresh_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            token_type="bearer",
            expires_in=900,
            refresh_expires_in=604800
        )
        ```
    """

    access_token: str = Field(description="JWT access token for authenticated requests")

    refresh_token: str = Field(
        description="JWT refresh token for obtaining new access tokens"
    )

    token_type: str = Field(
        default="bearer", description="Type of the token (always 'bearer')"
    )

    expires_in: int = Field(description="Access token expiration time in seconds")

    refresh_expires_in: int = Field(
        description="Refresh token expiration time in seconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 900,
                "refresh_expires_in": 604800,
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token request.
    """

    refresh_token: str = Field(
        description="Valid refresh token to exchange for new access token"
    )

    class Config:
        json_schema_extra = {
            "example": {"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
        }
