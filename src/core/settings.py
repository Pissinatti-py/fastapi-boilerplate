from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignora variáveis extras não definidas
    )

    # Main app variables
    APP_NAME: str = "FastAPI Project"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1.0"
    APP_ENV: str = "development"
    DEBUG: bool = Field(default=True)

    # Security (com defaults para desenvolvimento)
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 2

    # CORS
    ALLOWED_ORIGINS: str = "*"

    # Quotation service
    COTACAO_SERVICE_URL: str = Field(
        default="http://quotation-service:3000",
        description="Service URL for currency quotation",
    )
    COTACAO_TIMEOUT: float = Field(
        default=10.0, description="Timeout for currency quotation requests"
    )
    COTACAO_LIBRA_WAIT_TIMEOUT: float = Field(
        default=5.0, description="Timeout for waiting Pound quotation webhook"
    )


settings = Settings()
