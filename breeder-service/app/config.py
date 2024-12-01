from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    APP_NAME: str = Field("Breeder", env="APP_NAME")
    DEBUG: bool = (
        Field(False, env="DEBUG")
        if os.getenv("FASTAPI_ENV") == "production"
        else Field(True, env="DEBUG")
    )

    JWT_SECRET_KEY: str = Field(os.getenv("JWT_SECRET_KEY"), env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(os.getenv("JWT_ALGORITHM"), env="JWT_ALGORITHM")
    JWT_REFRESH_SECRET: str = Field(
        os.getenv("JWT_REFRESH_SECRET"), env="JWT_REFRESH_SECRET"
    )

    # Database settings
    # DATABASE_URL: str = Field(os.getenv(""), env="DATABASE_URL")

    # Security settings
    # SECRET_KEY: str = Field(..., env="SECRET_KEY")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # External service settings
    # REDIS_URL: str = Field(None, env="REDIS_URL")
    # SENTRY_DSN: str = Field(None, env="SENTRY_DSN")

    class Config:
        # Specify that settings are case-insensitive
        case_sensitive = False
        # Environment variable prefix (optional)
        # env_prefix = "MYAPP_"


# Instantiate settings object to be used throughout the application
settings = Settings()
