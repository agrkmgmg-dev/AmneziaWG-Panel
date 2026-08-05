"""
Application configuration management.

Uses:
- Pydantic v2 Settings
- Environment variables
- .env file support

Production ready configuration layer.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Global application settings.

    Values are loaded from:
    1. Environment variables
    2. .env file
    """

    # -------------------------------------------------
    # Application
    # -------------------------------------------------

    APP_NAME: str = Field(
        default="AmneziaWG-Panel"
    )

    APP_VERSION: str = Field(
        default="0.1.0"
    )

    ENVIRONMENT: str = Field(
        default="development"
    )

    DEBUG: bool = Field(
        default=False
    )


    # -------------------------------------------------
    # Server
    # -------------------------------------------------

    HOST: str = Field(
        default="0.0.0.0"
    )

    PORT: int = Field(
        default=8000
    )


    # -------------------------------------------------
    # Security
    # -------------------------------------------------

    SECRET_KEY: str = Field(
        default="change_this_secret_key"
    )

    JWT_ALGORITHM: str = Field(
        default="HS256"
    )

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30
    )

    SESSION_TIMEOUT_MINUTES: int = Field(
        default=60
    )


    # -------------------------------------------------
    # Database
    # -------------------------------------------------

    DATABASE_URL: str = Field(
        default="sqlite:///./amnezia_panel.db"
    )


    # -------------------------------------------------
    # Logging
    # -------------------------------------------------

    LOG_LEVEL: str = Field(
        default="INFO"
    )

    LOG_FILE: str = Field(
        default="logs/app.log"
    )


    # -------------------------------------------------
    # AmneziaWG
    # -------------------------------------------------

    AWG_INTERFACE: str = Field(
        default="awg0"
    )

    AWG_CONFIG_PATH: str = Field(
        default="/etc/amnezia/amneziawg/awg0.conf"
    )

    AWG_AUTO_SYNC: bool = Field(
        default=False
    )


    # -------------------------------------------------
    # Docker
    # -------------------------------------------------

    DOCKER_ENABLED: bool = Field(
        default=True
    )

    DOCKER_SOCKET: str = Field(
        default="/var/run/docker.sock"
    )

    AWG_CONTAINER_NAME: str = Field(
        default="amnezia-awg"
    )


    # -------------------------------------------------
    # Traffic
    # -------------------------------------------------

    TRAFFIC_MONITOR_ENABLED: bool = Field(
        default=True
    )

    TRAFFIC_UNIT: str = Field(
        default="GB"
    )


    # -------------------------------------------------
    # Security Features
    # -------------------------------------------------

    ENABLE_CSRF: bool = Field(
        default=True
    )

    ENABLE_ACTIVITY_LOG: bool = Field(
        default=True
    )


    # -------------------------------------------------
    # Admin Bootstrap
    # -------------------------------------------------

    ADMIN_USERNAME: str = Field(
        default="admin"
    )

    ADMIN_EMAIL: str = Field(
        default="admin@example.com"
    )

    ADMIN_PASSWORD: str = Field(
        default="change_this_password"
    )


    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.

    Prevents loading environment repeatedly.
    """

    return Settings()


settings = get_settings()