from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Main app variables
    APP_NAME: str = "FastAPI Project"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    APP_ENV: str
    DEBUG: bool = Field(default=True)

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # DB
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str

    # CORS
    ALLOWED_ORIGINS: str = ["*"]


settings = Settings()
